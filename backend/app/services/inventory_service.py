from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.category import Category
from app.models.inventory import InventoryBalance, StockMovement, StockMovementType
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.user import User
from app.models.warehouse import Warehouse
from app.schemas.inventory import (
    InventoryBalanceRead,
    InventoryItem,
    ProductInventoryDetail,
    StockMovementRead,
)
from app.services.audit_service import record_audit_log

INCREASE_TYPES = {
    StockMovementType.OPENING_BALANCE,
    StockMovementType.GOODS_RECEIPT,
    StockMovementType.TRANSFER_IN,
    StockMovementType.ADJUSTMENT_INCREASE,
    StockMovementType.RETURN,
}
DECREASE_TYPES = {
    StockMovementType.STOCK_ISSUE,
    StockMovementType.TRANSFER_OUT,
    StockMovementType.ADJUSTMENT_DECREASE,
}


def available_quantity(balance: InventoryBalance) -> int:
    return balance.quantity_on_hand - balance.quantity_reserved


def stock_status_for(available: int, reorder_level: int) -> str:
    if available <= 0:
        return "OUT_OF_STOCK"
    if available <= reorder_level:
        return "LOW_STOCK"
    return "NORMAL"


def inventory_value(quantity_on_hand: int, cost_price: Decimal) -> Decimal:
    return Decimal(quantity_on_hand) * Decimal(cost_price)


def movement_delta(movement_type: StockMovementType, quantity: int) -> int:
    if quantity < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be zero or greater.")
    if movement_type in DECREASE_TYPES:
        return -quantity
    return quantity


def get_or_create_balance(db: Session, product_id: int, warehouse_id: int) -> InventoryBalance:
    balance = db.scalar(
        select(InventoryBalance).where(
            InventoryBalance.product_id == product_id,
            InventoryBalance.warehouse_id == warehouse_id,
        )
    )
    if balance is not None:
        return balance

    balance = InventoryBalance(
        product_id=product_id,
        warehouse_id=warehouse_id,
        quantity_on_hand=0,
        quantity_reserved=0,
    )
    db.add(balance)
    db.flush()
    return balance


def record_stock_movement(
    db: Session,
    product: Product,
    warehouse: Warehouse,
    movement_type: StockMovementType,
    quantity: int,
    actor: User | None,
    reference_type: str | None,
    reference_id: str | None,
    reason: str,
) -> StockMovement:
    delta = movement_delta(movement_type, quantity)
    balance = get_or_create_balance(db, product.id, warehouse.id)
    next_on_hand = balance.quantity_on_hand + delta
    if next_on_hand < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stock cannot become negative.")
    if balance.quantity_reserved > next_on_hand:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reserved quantity cannot exceed stock on hand.")

    balance.quantity_on_hand = next_on_hand
    movement = StockMovement(
        product_id=product.id,
        warehouse_id=warehouse.id,
        movement_type=movement_type,
        quantity=delta,
        reference_type=reference_type,
        reference_id=reference_id,
        reason=reason,
        performed_by=actor.id if actor else None,
    )
    db.add(movement)
    db.flush()
    if actor is not None:
        record_audit_log(
            db,
            actor,
            "STOCK_MOVEMENT_RECORDED",
            "StockMovement",
            movement.id,
            f"{actor.full_name} recorded {movement_type.value} for {product.sku} at {warehouse.code}.",
        )
    return movement


def record_opening_balance(
    db: Session,
    product: Product,
    warehouse: Warehouse,
    quantity_on_hand: int,
    quantity_reserved: int,
    actor: User | None,
) -> InventoryBalance:
    if quantity_on_hand < 0 or quantity_reserved < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Opening stock quantities cannot be negative.")
    if quantity_reserved > quantity_on_hand:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reserved quantity cannot exceed stock on hand.")

    reference_id = f"{product.sku}:{warehouse.code}"
    existing_movement = db.scalar(
        select(StockMovement).where(
            StockMovement.product_id == product.id,
            StockMovement.warehouse_id == warehouse.id,
            StockMovement.movement_type == StockMovementType.OPENING_BALANCE,
            StockMovement.reference_type == "OPENING_STOCK",
            StockMovement.reference_id == reference_id,
        )
    )
    balance = get_or_create_balance(db, product.id, warehouse.id)
    if existing_movement is not None:
        return balance

    record_stock_movement(
        db,
        product,
        warehouse,
        StockMovementType.OPENING_BALANCE,
        quantity_on_hand,
        actor,
        "OPENING_STOCK",
        reference_id,
        "Seeded opening balance for the StockPilot demonstration ledger.",
    )
    balance.quantity_reserved = quantity_reserved
    db.flush()
    return balance


def balance_to_read(balance: InventoryBalance) -> InventoryBalanceRead:
    available = available_quantity(balance)
    product = balance.product
    return InventoryBalanceRead(
        id=balance.id,
        warehouse=balance.warehouse,
        product_id=balance.product_id,
        quantity_on_hand=balance.quantity_on_hand,
        quantity_reserved=balance.quantity_reserved,
        available_quantity=available,
        inventory_value=inventory_value(balance.quantity_on_hand, product.cost_price),
        stock_status=stock_status_for(available, product.reorder_level),
        updated_at=balance.updated_at,
    )


def movement_to_read(movement: StockMovement) -> StockMovementRead:
    return StockMovementRead(
        id=movement.id,
        product_id=movement.product_id,
        product_sku=movement.product.sku,
        product_name=movement.product.name,
        warehouse_id=movement.warehouse_id,
        warehouse_code=movement.warehouse.code,
        warehouse_name=movement.warehouse.name,
        movement_type=movement.movement_type,
        quantity=movement.quantity,
        reference_type=movement.reference_type,
        reference_id=movement.reference_id,
        reason=movement.reason,
        performed_by=movement.performed_by,
        performed_by_name=movement.performed_by_user.full_name if movement.performed_by_user else None,
        created_at=movement.created_at,
    )


def list_inventory(
    db: Session,
    search: str | None = None,
    warehouse_id: int | None = None,
    category_id: int | None = None,
    supplier_id: int | None = None,
    stock_status: str | None = None,
) -> list[InventoryItem]:
    stmt = select(Product).options(
        selectinload(Product.category),
        selectinload(Product.preferred_supplier),
        selectinload(Product.inventory_balances).selectinload(InventoryBalance.warehouse),
    )
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    if supplier_id is not None:
        stmt = stmt.where(Product.preferred_supplier_id == supplier_id)
    if search:
        needle = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Product.name.ilike(needle),
                Product.sku.ilike(needle),
                Product.barcode.ilike(needle),
            )
        )

    items: list[InventoryItem] = []
    for product in db.scalars(stmt.order_by(Product.name)):
        balances = list(product.inventory_balances)
        if warehouse_id is not None:
            balances = [balance for balance in balances if balance.warehouse_id == warehouse_id]
        total_on_hand = sum(balance.quantity_on_hand for balance in balances)
        total_reserved = sum(balance.quantity_reserved for balance in balances)
        total_available = total_on_hand - total_reserved
        item_status = stock_status_for(total_available, product.reorder_level)
        if stock_status and item_status != stock_status:
            continue
        items.append(
            InventoryItem(
                product_id=product.id,
                sku=product.sku,
                product_name=product.name,
                category_name=product.category.name,
                preferred_supplier_name=product.preferred_supplier.name if product.preferred_supplier else None,
                unit_of_measure=product.unit_of_measure,
                reorder_level=product.reorder_level,
                total_on_hand=total_on_hand,
                total_reserved=total_reserved,
                available_quantity=total_available,
                inventory_value=inventory_value(total_on_hand, product.cost_price),
                stock_status=item_status,
                warehouse_count=len([balance for balance in balances if balance.quantity_on_hand > 0 or balance.quantity_reserved > 0]),
            )
        )

    status_order = {"OUT_OF_STOCK": 0, "LOW_STOCK": 1, "NORMAL": 2}
    return sorted(items, key=lambda item: (status_order.get(item.stock_status, 9), item.product_name))


def get_product_inventory_detail(db: Session, product_id: int) -> ProductInventoryDetail:
    product = db.scalar(
        select(Product)
        .where(Product.id == product_id)
        .options(
            selectinload(Product.category),
            selectinload(Product.preferred_supplier),
            selectinload(Product.inventory_balances).selectinload(InventoryBalance.warehouse),
        )
    )
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    balances = sorted(product.inventory_balances, key=lambda balance: balance.warehouse.name)
    total_on_hand = sum(balance.quantity_on_hand for balance in balances)
    total_reserved = sum(balance.quantity_reserved for balance in balances)
    total_available = total_on_hand - total_reserved
    movements = db.scalars(
        select(StockMovement)
        .where(StockMovement.product_id == product.id)
        .options(
            selectinload(StockMovement.product),
            selectinload(StockMovement.warehouse),
            selectinload(StockMovement.performed_by_user),
        )
        .order_by(desc(StockMovement.created_at), desc(StockMovement.id))
        .limit(12)
    )

    return ProductInventoryDetail(
        product=product,
        total_on_hand=total_on_hand,
        total_reserved=total_reserved,
        available_quantity=total_available,
        inventory_value=inventory_value(total_on_hand, product.cost_price),
        stock_status=stock_status_for(total_available, product.reorder_level),
        balances=[balance_to_read(balance) for balance in balances],
        recent_movements=[movement_to_read(movement) for movement in movements],
    )


def list_stock_movements(
    db: Session,
    product_id: int | None = None,
    warehouse_id: int | None = None,
    movement_type: StockMovementType | None = None,
    search: str | None = None,
    limit: int = 100,
) -> list[StockMovementRead]:
    stmt = select(StockMovement).join(Product).join(Warehouse).options(
        selectinload(StockMovement.product),
        selectinload(StockMovement.warehouse),
        selectinload(StockMovement.performed_by_user),
    )
    if product_id is not None:
        stmt = stmt.where(StockMovement.product_id == product_id)
    if warehouse_id is not None:
        stmt = stmt.where(StockMovement.warehouse_id == warehouse_id)
    if movement_type is not None:
        stmt = stmt.where(StockMovement.movement_type == movement_type)
    if search:
        needle = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Product.name.ilike(needle),
                Product.sku.ilike(needle),
                Warehouse.name.ilike(needle),
                Warehouse.code.ilike(needle),
                StockMovement.reference_id.ilike(needle),
            )
        )
    rows = db.scalars(stmt.order_by(desc(StockMovement.created_at), desc(StockMovement.id)).limit(min(limit, 250)))
    return [movement_to_read(movement) for movement in rows]


def inventory_snapshot_metrics(db: Session) -> dict[str, int | Decimal]:
    products = db.scalars(
        select(Product).options(selectinload(Product.inventory_balances))
    )
    inventory_total = Decimal("0.00")
    low_stock_items = 0
    out_of_stock_items = 0
    for product in products:
        total_on_hand = sum(balance.quantity_on_hand for balance in product.inventory_balances)
        total_reserved = sum(balance.quantity_reserved for balance in product.inventory_balances)
        available = total_on_hand - total_reserved
        inventory_total += inventory_value(total_on_hand, product.cost_price)
        item_status = stock_status_for(available, product.reorder_level)
        if item_status == "LOW_STOCK":
            low_stock_items += 1
        elif item_status == "OUT_OF_STOCK":
            out_of_stock_items += 1

    return {
        "inventory_value": inventory_total,
        "low_stock_items": low_stock_items,
        "out_of_stock_items": out_of_stock_items,
    }
