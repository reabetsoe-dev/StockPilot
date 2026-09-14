from fastapi import HTTPException, status
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.base import utc_now
from app.models.department import Department
from app.models.inventory import StockMovementType
from app.models.product import Product
from app.models.user import User, UserRole
from app.models.warehouse import Warehouse
from app.models.warehouse_ops import (
    StockAdjustment,
    StockAdjustmentType,
    StockRequest,
    StockRequestItem,
    StockRequestStatus,
    StockTransfer,
    StockTransferItem,
    StockTransferStatus,
)
from app.schemas.warehouse_ops import (
    StockAdjustmentCreate,
    StockAdjustmentRead,
    StockRequestCreate,
    StockRequestItemRead,
    StockRequestRead,
    StockTransferCreate,
    StockTransferItemRead,
    StockTransferRead,
)
from app.services.audit_service import record_audit_log
from app.services.inventory_service import available_quantity, get_or_create_balance, record_stock_movement
from app.services.notification_service import create_notification, notify_roles
from app.services.reference_service import next_reference


def product_or_404(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return product


def warehouse_or_404(db: Session, warehouse_id: int) -> Warehouse:
    warehouse = db.get(Warehouse, warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found.")
    return warehouse


def department_or_404(db: Session, department_id: int) -> Department:
    department = db.get(Department, department_id)
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found.")
    return department


def stock_request_options():
    return (
        selectinload(StockRequest.department),
        selectinload(StockRequest.requested_by_user),
        selectinload(StockRequest.source_warehouse),
        selectinload(StockRequest.issued_by_user),
        selectinload(StockRequest.items).selectinload(StockRequestItem.product),
    )


def transfer_options():
    return (
        selectinload(StockTransfer.source_warehouse),
        selectinload(StockTransfer.destination_warehouse),
        selectinload(StockTransfer.requested_by_user),
        selectinload(StockTransfer.completed_by_user),
        selectinload(StockTransfer.items).selectinload(StockTransferItem.product),
    )


def stock_request_to_read(request: StockRequest) -> StockRequestRead:
    return StockRequestRead(
        id=request.id,
        reference_number=request.reference_number,
        department_id=request.department_id,
        department_name=request.department.name,
        requested_by=request.requested_by,
        requested_by_name=request.requested_by_user.full_name,
        source_warehouse_id=request.source_warehouse_id,
        source_warehouse_name=request.source_warehouse.name,
        purpose=request.purpose,
        status=request.status,
        issued_by_name=request.issued_by_user.full_name if request.issued_by_user else None,
        issued_at=request.issued_at,
        created_at=request.created_at,
        updated_at=request.updated_at,
        items=[
            StockRequestItemRead(
                id=item.id,
                product_id=item.product_id,
                product_sku=item.product.sku,
                product_name=item.product.name,
                quantity_requested=item.quantity_requested,
                quantity_issued=item.quantity_issued,
            )
            for item in request.items
        ],
    )


def transfer_to_read(transfer: StockTransfer) -> StockTransferRead:
    return StockTransferRead(
        id=transfer.id,
        transfer_number=transfer.transfer_number,
        source_warehouse_id=transfer.source_warehouse_id,
        source_warehouse_name=transfer.source_warehouse.name,
        destination_warehouse_id=transfer.destination_warehouse_id,
        destination_warehouse_name=transfer.destination_warehouse.name,
        status=transfer.status,
        requested_by=transfer.requested_by,
        requested_by_name=transfer.requested_by_user.full_name,
        completed_by_name=transfer.completed_by_user.full_name if transfer.completed_by_user else None,
        completed_at=transfer.completed_at,
        created_at=transfer.created_at,
        updated_at=transfer.updated_at,
        items=[
            StockTransferItemRead(
                id=item.id,
                product_id=item.product_id,
                product_sku=item.product.sku,
                product_name=item.product.name,
                quantity=item.quantity,
            )
            for item in transfer.items
        ],
    )


def adjustment_to_read(adjustment: StockAdjustment) -> StockAdjustmentRead:
    return StockAdjustmentRead(
        id=adjustment.id,
        adjustment_number=adjustment.adjustment_number,
        product_id=adjustment.product_id,
        product_sku=adjustment.product.sku,
        product_name=adjustment.product.name,
        warehouse_id=adjustment.warehouse_id,
        warehouse_name=adjustment.warehouse.name,
        adjustment_type=adjustment.adjustment_type,
        quantity=adjustment.quantity,
        reason=adjustment.reason,
        notes=adjustment.notes,
        performed_by_name=adjustment.performed_by_user.full_name,
        created_at=adjustment.created_at,
    )


def list_stock_requests(db: Session, user: User, status_filter: StockRequestStatus | None = None, search: str | None = None) -> list[StockRequestRead]:
    stmt = select(StockRequest).options(*stock_request_options())
    if user.role == UserRole.DEPARTMENT_REQUESTER:
        stmt = stmt.where(StockRequest.requested_by == user.id)
    if status_filter is not None:
        stmt = stmt.where(StockRequest.status == status_filter)
    if search:
        needle = f"%{search.strip()}%"
        stmt = stmt.where(or_(StockRequest.reference_number.ilike(needle), StockRequest.purpose.ilike(needle)))
    requests = db.scalars(stmt.order_by(desc(StockRequest.created_at), desc(StockRequest.id))).unique()
    return [stock_request_to_read(request) for request in requests]


def create_stock_request(db: Session, payload: StockRequestCreate, actor: User) -> StockRequestRead:
    try:
        department_id = payload.department_id or actor.department_id
        if department_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Department is required.")
        department_or_404(db, department_id)
        warehouse_or_404(db, payload.source_warehouse_id)
        request = StockRequest(
            reference_number=next_reference(db, StockRequest, StockRequest.reference_number, "SR"),
            department_id=department_id,
            requested_by=actor.id,
            source_warehouse_id=payload.source_warehouse_id,
            purpose=payload.purpose.strip(),
            status=StockRequestStatus.SUBMITTED,
        )
        db.add(request)
        db.flush()
        for item_payload in payload.items:
            product = product_or_404(db, item_payload.product_id)
            request.items.append(
                StockRequestItem(
                    product_id=product.id,
                    quantity_requested=item_payload.quantity_requested,
                    quantity_issued=0,
                )
            )
        notify_roles(
            db,
            [UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER],
            f"{request.reference_number} requires stock approval",
            f"Internal stock request {request.reference_number} is waiting for review.",
            "StockRequest",
            request.id,
            "/stock-requests",
        )
        record_audit_log(db, actor, "STOCK_REQUEST_CREATED", "StockRequest", request.id, f"{actor.full_name} created {request.reference_number}.")
        db.commit()
        return stock_request_to_read(load_stock_request(db, request.id))
    except Exception:
        db.rollback()
        raise


def load_stock_request(db: Session, request_id: int) -> StockRequest:
    request = db.scalar(select(StockRequest).where(StockRequest.id == request_id).options(*stock_request_options()))
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock request not found.")
    return request


def approve_stock_request(db: Session, request_id: int, actor: User) -> StockRequestRead:
    try:
        request = load_stock_request(db, request_id)
        if request.status != StockRequestStatus.SUBMITTED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only submitted stock requests can be approved.")
        request.status = StockRequestStatus.APPROVED
        create_notification(db, f"{request.reference_number} approved", f"Stock request {request.reference_number} is approved for issuing.", request.requested_by, "StockRequest", request.id, "/stock-requests")
        notify_roles(db, [UserRole.WAREHOUSE_OFFICER], f"{request.reference_number} ready to issue", f"Approved stock request {request.reference_number} can be issued from warehouse.", "StockRequest", request.id, "/stock-requests")
        record_audit_log(db, actor, "STOCK_REQUEST_APPROVED", "StockRequest", request.id, f"{actor.full_name} approved {request.reference_number}.")
        db.commit()
        return stock_request_to_read(load_stock_request(db, request.id))
    except Exception:
        db.rollback()
        raise


def reject_stock_request(db: Session, request_id: int, actor: User) -> StockRequestRead:
    try:
        request = load_stock_request(db, request_id)
        if request.status != StockRequestStatus.SUBMITTED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only submitted stock requests can be rejected.")
        request.status = StockRequestStatus.REJECTED
        create_notification(db, f"{request.reference_number} rejected", f"Stock request {request.reference_number} was rejected.", request.requested_by, "StockRequest", request.id, "/stock-requests")
        record_audit_log(db, actor, "STOCK_REQUEST_REJECTED", "StockRequest", request.id, f"{actor.full_name} rejected {request.reference_number}.")
        db.commit()
        return stock_request_to_read(load_stock_request(db, request.id))
    except Exception:
        db.rollback()
        raise


def issue_stock_request(db: Session, request_id: int, actor: User) -> StockRequestRead:
    try:
        request = load_stock_request(db, request_id)
        if request.status != StockRequestStatus.APPROVED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only approved stock requests can be issued.")
        for item in request.items:
            balance = get_or_create_balance(db, item.product_id, request.source_warehouse_id)
            if available_quantity(balance) < item.quantity_requested:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock for one or more requested items.")
        for item in request.items:
            record_stock_movement(
                db,
                item.product,
                request.source_warehouse,
                StockMovementType.STOCK_ISSUE,
                item.quantity_requested,
                actor,
                "STOCK_REQUEST",
                request.reference_number,
                f"Issued stock for {request.reference_number}.",
            )
            item.quantity_issued = item.quantity_requested
        request.status = StockRequestStatus.ISSUED
        request.issued_by = actor.id
        request.issued_at = utc_now()
        create_notification(db, f"{request.reference_number} issued", f"Stock request {request.reference_number} has been issued.", request.requested_by, "StockRequest", request.id, "/stock-requests")
        record_audit_log(db, actor, "STOCK_ISSUED", "StockRequest", request.id, f"{actor.full_name} issued {request.reference_number}.")
        db.commit()
        return stock_request_to_read(load_stock_request(db, request.id))
    except Exception:
        db.rollback()
        raise


def list_transfers(db: Session, status_filter: StockTransferStatus | None = None, search: str | None = None) -> list[StockTransferRead]:
    stmt = select(StockTransfer).options(*transfer_options())
    if status_filter is not None:
        stmt = stmt.where(StockTransfer.status == status_filter)
    if search:
        needle = f"%{search.strip()}%"
        stmt = stmt.where(StockTransfer.transfer_number.ilike(needle))
    transfers = db.scalars(stmt.order_by(desc(StockTransfer.created_at), desc(StockTransfer.id))).unique()
    return [transfer_to_read(transfer) for transfer in transfers]


def load_transfer(db: Session, transfer_id: int) -> StockTransfer:
    transfer = db.scalar(select(StockTransfer).where(StockTransfer.id == transfer_id).options(*transfer_options()))
    if transfer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock transfer not found.")
    return transfer


def create_transfer(db: Session, payload: StockTransferCreate, actor: User) -> StockTransferRead:
    try:
        if payload.source_warehouse_id == payload.destination_warehouse_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Source and destination warehouses must be different.")
        warehouse_or_404(db, payload.source_warehouse_id)
        warehouse_or_404(db, payload.destination_warehouse_id)
        transfer = StockTransfer(
            transfer_number=next_reference(db, StockTransfer, StockTransfer.transfer_number, "TRF"),
            source_warehouse_id=payload.source_warehouse_id,
            destination_warehouse_id=payload.destination_warehouse_id,
            status=StockTransferStatus.DRAFT,
            requested_by=actor.id,
        )
        db.add(transfer)
        db.flush()
        for item_payload in payload.items:
            product = product_or_404(db, item_payload.product_id)
            transfer.items.append(StockTransferItem(product_id=product.id, quantity=item_payload.quantity))
        record_audit_log(db, actor, "STOCK_TRANSFER_CREATED", "StockTransfer", transfer.id, f"{actor.full_name} created {transfer.transfer_number}.")
        db.commit()
        return transfer_to_read(load_transfer(db, transfer.id))
    except Exception:
        db.rollback()
        raise


def dispatch_transfer(db: Session, transfer_id: int, actor: User) -> StockTransferRead:
    try:
        transfer = load_transfer(db, transfer_id)
        if transfer.status != StockTransferStatus.DRAFT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft transfers can be dispatched.")
        for item in transfer.items:
            balance = get_or_create_balance(db, item.product_id, transfer.source_warehouse_id)
            if available_quantity(balance) < item.quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock for transfer.")
        for item in transfer.items:
            record_stock_movement(db, item.product, transfer.source_warehouse, StockMovementType.TRANSFER_OUT, item.quantity, actor, "STOCK_TRANSFER", transfer.transfer_number, f"Transfer dispatched to {transfer.destination_warehouse.code}.")
        transfer.status = StockTransferStatus.IN_TRANSIT
        notify_roles(db, [UserRole.WAREHOUSE_OFFICER], f"{transfer.transfer_number} in transit", f"Transfer {transfer.transfer_number} is ready for receipt.", "StockTransfer", transfer.id, "/stock-transfers")
        record_audit_log(db, actor, "STOCK_TRANSFER_DISPATCHED", "StockTransfer", transfer.id, f"{actor.full_name} dispatched {transfer.transfer_number}.")
        db.commit()
        return transfer_to_read(load_transfer(db, transfer.id))
    except Exception:
        db.rollback()
        raise


def receive_transfer(db: Session, transfer_id: int, actor: User) -> StockTransferRead:
    try:
        transfer = load_transfer(db, transfer_id)
        if transfer.status != StockTransferStatus.IN_TRANSIT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only in-transit transfers can be received.")
        for item in transfer.items:
            record_stock_movement(db, item.product, transfer.destination_warehouse, StockMovementType.TRANSFER_IN, item.quantity, actor, "STOCK_TRANSFER", transfer.transfer_number, f"Transfer received from {transfer.source_warehouse.code}.")
        transfer.status = StockTransferStatus.COMPLETED
        transfer.completed_by = actor.id
        transfer.completed_at = utc_now()
        record_audit_log(db, actor, "STOCK_TRANSFER_COMPLETED", "StockTransfer", transfer.id, f"{actor.full_name} completed {transfer.transfer_number}.")
        db.commit()
        return transfer_to_read(load_transfer(db, transfer.id))
    except Exception:
        db.rollback()
        raise


def create_adjustment(db: Session, payload: StockAdjustmentCreate, actor: User) -> StockAdjustmentRead:
    try:
        product = product_or_404(db, payload.product_id)
        warehouse = warehouse_or_404(db, payload.warehouse_id)
        movement_type = (
            StockMovementType.ADJUSTMENT_INCREASE
            if payload.adjustment_type == StockAdjustmentType.INCREASE
            else StockMovementType.ADJUSTMENT_DECREASE
        )
        adjustment = StockAdjustment(
            adjustment_number=next_reference(db, StockAdjustment, StockAdjustment.adjustment_number, "ADJ"),
            product_id=product.id,
            warehouse_id=warehouse.id,
            adjustment_type=payload.adjustment_type,
            quantity=payload.quantity,
            reason=payload.reason.strip(),
            notes=payload.notes,
            performed_by=actor.id,
        )
        db.add(adjustment)
        db.flush()
        record_stock_movement(db, product, warehouse, movement_type, payload.quantity, actor, "STOCK_ADJUSTMENT", adjustment.adjustment_number, payload.reason.strip())
        record_audit_log(db, actor, "STOCK_ADJUSTED", "StockAdjustment", adjustment.id, f"{actor.full_name} adjusted {product.sku} at {warehouse.code}.")
        db.commit()
        loaded = db.scalar(
            select(StockAdjustment)
            .where(StockAdjustment.id == adjustment.id)
            .options(selectinload(StockAdjustment.product), selectinload(StockAdjustment.warehouse), selectinload(StockAdjustment.performed_by_user))
        )
        return adjustment_to_read(loaded)
    except Exception:
        db.rollback()
        raise


def list_adjustments(db: Session) -> list[StockAdjustmentRead]:
    adjustments = db.scalars(
        select(StockAdjustment)
        .options(selectinload(StockAdjustment.product), selectinload(StockAdjustment.warehouse), selectinload(StockAdjustment.performed_by_user))
        .order_by(desc(StockAdjustment.created_at), desc(StockAdjustment.id))
        .limit(100)
    )
    return [adjustment_to_read(adjustment) for adjustment in adjustments]
