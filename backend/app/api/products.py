from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user, require_roles
from app.core.database import get_db
from app.models.product import Product
from app.models.user import User, UserRole
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services.catalog_service import create_product, update_product

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[ProductRead])
def list_products(
    search: str | None = None,
    category_id: int | None = None,
    supplier_id: int | None = None,
    active: bool | None = Query(default=True),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Product]:
    stmt = select(Product).options(
        selectinload(Product.category),
        selectinload(Product.preferred_supplier),
    )
    if active is not None:
        stmt = stmt.where(Product.active.is_(active))
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
    return list(db.scalars(stmt.order_by(Product.name)))


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def add_product(
    payload: ProductCreate,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER)),
    db: Session = Depends(get_db),
) -> Product:
    return create_product(db, payload, current_user)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Product:
    product = db.scalar(
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.category), selectinload(Product.preferred_supplier))
    )
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return product


@router.put("/{product_id}", response_model=ProductRead)
def edit_product(
    product_id: int,
    payload: ProductUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER)),
    db: Session = Depends(get_db),
) -> Product:
    product = db.scalar(
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.category), selectinload(Product.preferred_supplier))
    )
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return update_product(db, product, payload, current_user)
