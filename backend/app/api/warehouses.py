from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseCreate, WarehouseRead, WarehouseUpdate
from app.services.catalog_service import create_warehouse, update_warehouse

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.get("", response_model=list[WarehouseRead])
def list_warehouses(
    search: str | None = None,
    active: bool | None = True,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Warehouse]:
    stmt = select(Warehouse)
    if active is not None:
        stmt = stmt.where(Warehouse.active.is_(active))
    if search:
        needle = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Warehouse.name.ilike(needle),
                Warehouse.code.ilike(needle),
                Warehouse.location.ilike(needle),
            )
        )
    return list(db.scalars(stmt.order_by(Warehouse.name)))


@router.post("", response_model=WarehouseRead, status_code=status.HTTP_201_CREATED)
def add_warehouse(
    payload: WarehouseCreate,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER)),
    db: Session = Depends(get_db),
) -> Warehouse:
    return create_warehouse(db, payload, current_user)


@router.put("/{warehouse_id}", response_model=WarehouseRead)
def edit_warehouse(
    warehouse_id: int,
    payload: WarehouseUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER)),
    db: Session = Depends(get_db),
) -> Warehouse:
    warehouse = db.get(Warehouse, warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found.")
    return update_warehouse(db, warehouse, payload, current_user)
