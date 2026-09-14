from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.inventory import StockMovementType
from app.models.user import User, UserRole
from app.schemas.inventory import InventoryItem, ProductInventoryDetail, StockMovementRead
from app.services.inventory_service import (
    get_product_inventory_detail,
    list_inventory,
    list_stock_movements,
)

router = APIRouter(tags=["Inventory"])

INVENTORY_VIEW_ROLES = (
    UserRole.ADMINISTRATOR,
    UserRole.INVENTORY_MANAGER,
    UserRole.WAREHOUSE_OFFICER,
    UserRole.AUDITOR,
)


@router.get("/inventory", response_model=list[InventoryItem])
def inventory_index(
    search: str | None = None,
    warehouse_id: int | None = None,
    category_id: int | None = None,
    supplier_id: int | None = None,
    stock_status: str | None = Query(default=None, pattern="^(NORMAL|LOW_STOCK|OUT_OF_STOCK)$"),
    _: User = Depends(require_roles(*INVENTORY_VIEW_ROLES)),
    db: Session = Depends(get_db),
) -> list[InventoryItem]:
    return list_inventory(db, search, warehouse_id, category_id, supplier_id, stock_status)


@router.get("/inventory/{product_id}", response_model=ProductInventoryDetail)
def inventory_detail(
    product_id: int,
    _: User = Depends(require_roles(*INVENTORY_VIEW_ROLES)),
    db: Session = Depends(get_db),
) -> ProductInventoryDetail:
    return get_product_inventory_detail(db, product_id)


@router.get("/stock-movements", response_model=list[StockMovementRead])
def stock_movement_index(
    product_id: int | None = None,
    warehouse_id: int | None = None,
    movement_type: StockMovementType | None = None,
    search: str | None = None,
    limit: int = Query(default=100, ge=1, le=250),
    _: User = Depends(require_roles(*INVENTORY_VIEW_ROLES)),
    db: Session = Depends(get_db),
) -> list[StockMovementRead]:
    return list_stock_movements(db, product_id, warehouse_id, movement_type, search, limit)
