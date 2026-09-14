from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.department import Department
from app.models.inventory import StockMovementType
from app.models.procurement import (
    GoodsReceipt,
    GoodsReceiptItem,
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseOrderStatus,
    PurchaseRequest,
    PurchaseRequestItem,
    PurchaseRequestStatus,
)
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.user import User, UserRole
from app.models.warehouse import Warehouse
from app.schemas.procurement import (
    GoodsReceiptCreate,
    GoodsReceiptItemRead,
    GoodsReceiptRead,
    PurchaseOrderCreate,
    PurchaseOrderItemRead,
    PurchaseOrderRead,
    PurchaseRequestCreate,
    PurchaseRequestItemRead,
    PurchaseRequestRead,
)
from app.services.audit_service import record_audit_log
from app.services.inventory_service import record_stock_movement
from app.services.notification_service import create_notification, notify_roles
from app.services.reference_service import next_reference

TAX_RATE = Decimal("0.15")


def money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"))


def product_or_404(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return product


def department_or_404(db: Session, department_id: int) -> Department:
    department = db.get(Department, department_id)
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found.")
    return department


def purchase_request_to_read(request: PurchaseRequest) -> PurchaseRequestRead:
    return PurchaseRequestRead(
        id=request.id,
        reference_number=request.reference_number,
        requested_by=request.requested_by,
        requested_by_name=request.requested_by_user.full_name,
        department_id=request.department_id,
        department_name=request.department.name,
        purpose=request.purpose,
        priority=request.priority,
        status=request.status,
        created_at=request.created_at,
        updated_at=request.updated_at,
        items=[
            PurchaseRequestItemRead(
                id=item.id,
                product_id=item.product_id,
                product_sku=item.product.sku if item.product else None,
                product_name=item.product.name if item.product else None,
                description=item.description,
                quantity=item.quantity,
                estimated_unit_price=item.estimated_unit_price,
            )
            for item in request.items
        ],
    )


def purchase_order_to_read(order: PurchaseOrder) -> PurchaseOrderRead:
    return PurchaseOrderRead(
        id=order.id,
        po_number=order.po_number,
        supplier_id=order.supplier_id,
        supplier_name=order.supplier.name,
        purchase_request_id=order.purchase_request_id,
        purchase_request_reference=order.purchase_request.reference_number if order.purchase_request else None,
        order_date=order.order_date,
        expected_delivery_date=order.expected_delivery_date,
        status=order.status,
        subtotal=order.subtotal,
        tax=order.tax,
        total=order.total,
        notes=order.notes,
        created_by=order.created_by,
        created_by_name=order.created_by_user.full_name,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=[
            PurchaseOrderItemRead(
                id=item.id,
                product_id=item.product_id,
                product_sku=item.product.sku,
                product_name=item.product.name,
                description=item.description,
                quantity_ordered=item.quantity_ordered,
                quantity_received=item.quantity_received,
                unit_price=item.unit_price,
                line_total=item.line_total,
                remaining_quantity=item.quantity_ordered - item.quantity_received,
            )
            for item in order.items
        ],
    )


def goods_receipt_to_read(receipt: GoodsReceipt) -> GoodsReceiptRead:
    return GoodsReceiptRead(
        id=receipt.id,
        receipt_number=receipt.receipt_number,
        purchase_order_id=receipt.purchase_order_id,
        purchase_order_number=receipt.purchase_order.po_number,
        warehouse_id=receipt.warehouse_id,
        warehouse_name=receipt.warehouse.name,
        received_by=receipt.received_by,
        received_by_name=receipt.received_by_user.full_name,
        received_date=receipt.received_date,
        notes=receipt.notes,
        created_at=receipt.created_at,
        items=[
            GoodsReceiptItemRead(
                id=item.id,
                purchase_order_item_id=item.purchase_order_item_id,
                product_id=item.product_id,
                product_sku=item.product.sku,
                product_name=item.product.name,
                quantity_received=item.quantity_received,
                quantity_rejected=item.quantity_rejected,
                notes=item.notes,
            )
            for item in receipt.items
        ],
    )


def purchase_request_options():
    return (
        selectinload(PurchaseRequest.department),
        selectinload(PurchaseRequest.requested_by_user),
        selectinload(PurchaseRequest.items).selectinload(PurchaseRequestItem.product),
    )


def purchase_order_options():
    return (
        selectinload(PurchaseOrder.supplier),
        selectinload(PurchaseOrder.purchase_request),
        selectinload(PurchaseOrder.created_by_user),
        selectinload(PurchaseOrder.items).selectinload(PurchaseOrderItem.product),
    )


def receipt_options():
    return (
        selectinload(GoodsReceipt.purchase_order),
        selectinload(GoodsReceipt.warehouse),
        selectinload(GoodsReceipt.received_by_user),
        selectinload(GoodsReceipt.items).selectinload(GoodsReceiptItem.product),
        selectinload(GoodsReceipt.items).selectinload(GoodsReceiptItem.purchase_order_item),
    )


def list_purchase_requests(db: Session, current_user: User, status_filter: PurchaseRequestStatus | None = None, search: str | None = None) -> list[PurchaseRequestRead]:
    stmt = select(PurchaseRequest).options(*purchase_request_options())
    if current_user.role == UserRole.DEPARTMENT_REQUESTER:
        stmt = stmt.where(PurchaseRequest.requested_by == current_user.id)
    if status_filter is not None:
        stmt = stmt.where(PurchaseRequest.status == status_filter)
    if search:
        needle = f"%{search.strip()}%"
        stmt = stmt.where(or_(PurchaseRequest.reference_number.ilike(needle), PurchaseRequest.purpose.ilike(needle)))
    requests = db.scalars(stmt.order_by(desc(PurchaseRequest.created_at), desc(PurchaseRequest.id))).unique()
    return [purchase_request_to_read(request) for request in requests]


def create_purchase_request(db: Session, payload: PurchaseRequestCreate, actor: User) -> PurchaseRequestRead:
    try:
        department_id = payload.department_id or actor.department_id
        if department_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Department is required.")
        department_or_404(db, department_id)
        request = PurchaseRequest(
            reference_number=next_reference(db, PurchaseRequest, PurchaseRequest.reference_number, "PR"),
            requested_by=actor.id,
            department_id=department_id,
            purpose=payload.purpose.strip(),
            priority=payload.priority,
            status=PurchaseRequestStatus.DRAFT,
        )
        db.add(request)
        db.flush()
        for item_payload in payload.items:
            product = product_or_404(db, item_payload.product_id) if item_payload.product_id else None
            request.items.append(
                PurchaseRequestItem(
                    product_id=product.id if product else None,
                    description=item_payload.description.strip(),
                    quantity=item_payload.quantity,
                    estimated_unit_price=item_payload.estimated_unit_price,
                )
            )
        record_audit_log(db, actor, "PURCHASE_REQUEST_CREATED", "PurchaseRequest", request.id, f"{actor.full_name} created {request.reference_number}.")
        db.commit()
        db.refresh(request)
        return purchase_request_to_read(load_purchase_request(db, request.id))
    except Exception:
        db.rollback()
        raise


def load_purchase_request(db: Session, request_id: int) -> PurchaseRequest:
    request = db.scalar(select(PurchaseRequest).where(PurchaseRequest.id == request_id).options(*purchase_request_options()))
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase request not found.")
    return request


def submit_purchase_request(db: Session, request_id: int, actor: User) -> PurchaseRequestRead:
    try:
        request = load_purchase_request(db, request_id)
        if actor.role == UserRole.DEPARTMENT_REQUESTER and request.requested_by != actor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only submit your own purchase requests.")
        if request.status != PurchaseRequestStatus.DRAFT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft purchase requests can be submitted.")
        request.status = PurchaseRequestStatus.SUBMITTED
        notify_roles(
            db,
            [UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER],
            f"{request.reference_number} requires approval",
            f"Purchase request {request.reference_number} is waiting for review.",
            "PurchaseRequest",
            request.id,
            "/purchase-requests",
        )
        record_audit_log(db, actor, "PURCHASE_REQUEST_SUBMITTED", "PurchaseRequest", request.id, f"{actor.full_name} submitted {request.reference_number}.")
        db.commit()
        return purchase_request_to_read(load_purchase_request(db, request.id))
    except Exception:
        db.rollback()
        raise


def approve_purchase_request(db: Session, request_id: int, actor: User) -> PurchaseRequestRead:
    try:
        request = load_purchase_request(db, request_id)
        if request.status != PurchaseRequestStatus.SUBMITTED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only submitted purchase requests can be approved.")
        request.status = PurchaseRequestStatus.APPROVED
        create_notification(
            db,
            f"{request.reference_number} approved",
            f"Purchase request {request.reference_number} is ready for procurement.",
            request.requested_by,
            "PurchaseRequest",
            request.id,
            "/purchase-requests",
        )
        notify_roles(
            db,
            [UserRole.PROCUREMENT_OFFICER],
            f"{request.reference_number} ready for PO",
            f"Approved purchase request {request.reference_number} can now be converted to a purchase order.",
            "PurchaseRequest",
            request.id,
            "/purchase-orders",
        )
        record_audit_log(db, actor, "PURCHASE_REQUEST_APPROVED", "PurchaseRequest", request.id, f"{actor.full_name} approved {request.reference_number}.")
        db.commit()
        return purchase_request_to_read(load_purchase_request(db, request.id))
    except Exception:
        db.rollback()
        raise


def reject_purchase_request(db: Session, request_id: int, actor: User) -> PurchaseRequestRead:
    try:
        request = load_purchase_request(db, request_id)
        if request.status != PurchaseRequestStatus.SUBMITTED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only submitted purchase requests can be rejected.")
        request.status = PurchaseRequestStatus.REJECTED
        create_notification(
            db,
            f"{request.reference_number} rejected",
            f"Purchase request {request.reference_number} was rejected during review.",
            request.requested_by,
            "PurchaseRequest",
            request.id,
            "/purchase-requests",
        )
        record_audit_log(db, actor, "PURCHASE_REQUEST_REJECTED", "PurchaseRequest", request.id, f"{actor.full_name} rejected {request.reference_number}.")
        db.commit()
        return purchase_request_to_read(load_purchase_request(db, request.id))
    except Exception:
        db.rollback()
        raise


def list_purchase_orders(db: Session, status_filter: PurchaseOrderStatus | None = None, search: str | None = None) -> list[PurchaseOrderRead]:
    stmt = select(PurchaseOrder).options(*purchase_order_options())
    if status_filter is not None:
        stmt = stmt.where(PurchaseOrder.status == status_filter)
    if search:
        needle = f"%{search.strip()}%"
        stmt = stmt.join(Supplier).where(or_(PurchaseOrder.po_number.ilike(needle), Supplier.name.ilike(needle)))
    orders = db.scalars(stmt.order_by(desc(PurchaseOrder.created_at), desc(PurchaseOrder.id))).unique()
    return [purchase_order_to_read(order) for order in orders]


def load_purchase_order(db: Session, order_id: int) -> PurchaseOrder:
    order = db.scalar(select(PurchaseOrder).where(PurchaseOrder.id == order_id).options(*purchase_order_options()))
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase order not found.")
    return order


def create_purchase_order(db: Session, payload: PurchaseOrderCreate, actor: User) -> PurchaseOrderRead:
    try:
        supplier = db.get(Supplier, payload.supplier_id)
        if supplier is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found.")

        purchase_request = None
        if payload.purchase_request_id is not None:
            purchase_request = load_purchase_request(db, payload.purchase_request_id)
            if purchase_request.status != PurchaseRequestStatus.APPROVED:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only approved purchase requests can be converted to purchase orders.")

        order = PurchaseOrder(
            po_number=next_reference(db, PurchaseOrder, PurchaseOrder.po_number, "PO"),
            supplier_id=supplier.id,
            purchase_request_id=purchase_request.id if purchase_request else None,
            order_date=date.today(),
            expected_delivery_date=payload.expected_delivery_date,
            status=PurchaseOrderStatus.DRAFT,
            notes=payload.notes,
            created_by=actor.id,
        )
        db.add(order)
        db.flush()
        subtotal = Decimal("0.00")
        for item_payload in payload.items:
            product = product_or_404(db, item_payload.product_id)
            line_total = money(Decimal(item_payload.quantity_ordered) * item_payload.unit_price)
            subtotal += line_total
            order.items.append(
                PurchaseOrderItem(
                    product_id=product.id,
                    description=item_payload.description or product.name,
                    quantity_ordered=item_payload.quantity_ordered,
                    quantity_received=0,
                    unit_price=item_payload.unit_price,
                    line_total=line_total,
                )
            )
        order.subtotal = money(subtotal)
        order.tax = money(order.subtotal * TAX_RATE)
        order.total = money(order.subtotal + order.tax)
        if purchase_request is not None:
            purchase_request.status = PurchaseRequestStatus.CONVERTED_TO_PO
        record_audit_log(db, actor, "PURCHASE_ORDER_CREATED", "PurchaseOrder", order.id, f"{actor.full_name} created {order.po_number}.")
        db.commit()
        return purchase_order_to_read(load_purchase_order(db, order.id))
    except Exception:
        db.rollback()
        raise


def issue_purchase_order(db: Session, order_id: int, actor: User) -> PurchaseOrderRead:
    try:
        order = load_purchase_order(db, order_id)
        if order.status != PurchaseOrderStatus.DRAFT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft purchase orders can be issued.")
        order.status = PurchaseOrderStatus.ISSUED
        notify_roles(
            db,
            [UserRole.WAREHOUSE_OFFICER, UserRole.ADMINISTRATOR],
            f"{order.po_number} awaiting delivery",
            f"Purchase order {order.po_number} has been issued and is ready for goods receiving.",
            "PurchaseOrder",
            order.id,
            "/goods-receiving",
        )
        record_audit_log(db, actor, "PURCHASE_ORDER_ISSUED", "PurchaseOrder", order.id, f"{actor.full_name} issued {order.po_number}.")
        db.commit()
        return purchase_order_to_read(load_purchase_order(db, order.id))
    except Exception:
        db.rollback()
        raise


def receive_goods(db: Session, payload: GoodsReceiptCreate, actor: User) -> GoodsReceiptRead:
    try:
        order = load_purchase_order(db, payload.purchase_order_id)
        if order.status not in {PurchaseOrderStatus.ISSUED, PurchaseOrderStatus.PARTIALLY_RECEIVED}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Purchase order is not awaiting receipt.")
        warehouse = db.get(Warehouse, payload.warehouse_id)
        if warehouse is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found.")

        order_items = {item.id: item for item in order.items}
        received_any = False
        receipt = GoodsReceipt(
            receipt_number=next_reference(db, GoodsReceipt, GoodsReceipt.receipt_number, "GRN"),
            purchase_order_id=order.id,
            warehouse_id=warehouse.id,
            received_by=actor.id,
            received_date=payload.received_date or date.today(),
            notes=payload.notes,
        )
        db.add(receipt)
        db.flush()

        for item_payload in payload.items:
            order_item = order_items.get(item_payload.purchase_order_item_id)
            if order_item is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Purchase order item does not belong to this purchase order.")
            remaining = order_item.quantity_ordered - order_item.quantity_received
            if item_payload.quantity_received > remaining:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity received exceeds remaining order quantity.")
            if item_payload.quantity_received == 0 and item_payload.quantity_rejected == 0:
                continue
            received_any = received_any or item_payload.quantity_received > 0
            receipt.items.append(
                GoodsReceiptItem(
                    purchase_order_item_id=order_item.id,
                    product_id=order_item.product_id,
                    quantity_received=item_payload.quantity_received,
                    quantity_rejected=item_payload.quantity_rejected,
                    notes=item_payload.notes,
                )
            )
            if item_payload.quantity_received > 0:
                order_item.quantity_received += item_payload.quantity_received
                record_stock_movement(
                    db,
                    order_item.product,
                    warehouse,
                    StockMovementType.GOODS_RECEIPT,
                    item_payload.quantity_received,
                    actor,
                    "GOODS_RECEIPT",
                    receipt.receipt_number,
                    f"Received against {order.po_number}.",
                )

        if not received_any:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one item must have a received quantity.")

        if all(item.quantity_received >= item.quantity_ordered for item in order.items):
            order.status = PurchaseOrderStatus.RECEIVED
        else:
            order.status = PurchaseOrderStatus.PARTIALLY_RECEIVED

        create_notification(
            db,
            f"{receipt.receipt_number} recorded",
            f"Goods receipt {receipt.receipt_number} updated inventory for {order.po_number}.",
            order.created_by,
            "GoodsReceipt",
            receipt.id,
            "/goods-receiving",
        )
        record_audit_log(db, actor, "GOODS_RECEIVED", "GoodsReceipt", receipt.id, f"{actor.full_name} recorded {receipt.receipt_number}.")
        db.commit()
        loaded = db.scalar(select(GoodsReceipt).where(GoodsReceipt.id == receipt.id).options(*receipt_options()))
        return goods_receipt_to_read(loaded)
    except Exception:
        db.rollback()
        raise


def list_goods_receipts(db: Session, search: str | None = None) -> list[GoodsReceiptRead]:
    stmt = select(GoodsReceipt).options(*receipt_options())
    if search:
        needle = f"%{search.strip()}%"
        stmt = stmt.join(PurchaseOrder).where(or_(GoodsReceipt.receipt_number.ilike(needle), PurchaseOrder.po_number.ilike(needle)))
    receipts = db.scalars(stmt.order_by(desc(GoodsReceipt.created_at), desc(GoodsReceipt.id))).unique()
    return [goods_receipt_to_read(receipt) for receipt in receipts]
