from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.database import get_db
from app.models.supplier import Supplier
from app.models.user import User, UserRole
from app.schemas.supplier import SupplierCreate, SupplierRead, SupplierUpdate
from app.services.catalog_service import create_supplier, update_supplier

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("", response_model=list[SupplierRead])
def list_suppliers(
    search: str | None = None,
    active: bool | None = True,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Supplier]:
    stmt = select(Supplier)
    if active is not None:
        stmt = stmt.where(Supplier.active.is_(active))
    if search:
        needle = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Supplier.name.ilike(needle),
                Supplier.supplier_code.ilike(needle),
                Supplier.contact_person.ilike(needle),
            )
        )
    return list(db.scalars(stmt.order_by(Supplier.name)))


@router.post("", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
def add_supplier(
    payload: SupplierCreate,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.PROCUREMENT_OFFICER)),
    db: Session = Depends(get_db),
) -> Supplier:
    return create_supplier(db, payload, current_user)


@router.get("/{supplier_id}", response_model=SupplierRead)
def get_supplier(
    supplier_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Supplier:
    supplier = db.get(Supplier, supplier_id)
    if supplier is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found.")
    return supplier


@router.put("/{supplier_id}", response_model=SupplierRead)
def edit_supplier(
    supplier_id: int,
    payload: SupplierUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.PROCUREMENT_OFFICER)),
    db: Session = Depends(get_db),
) -> Supplier:
    supplier = db.get(Supplier, supplier_id)
    if supplier is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found.")
    return update_supplier(db, supplier, payload, current_user)
