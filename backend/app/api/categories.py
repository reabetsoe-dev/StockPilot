from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.database import get_db
from app.models.category import Category
from app.models.user import User, UserRole
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.catalog_service import create_category, update_category

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Category]:
    return list(db.scalars(select(Category).order_by(Category.name)))


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def add_category(
    payload: CategoryCreate,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER)),
    db: Session = Depends(get_db),
) -> Category:
    return create_category(db, payload, current_user)


@router.put("/{category_id}", response_model=CategoryRead)
def edit_category(
    category_id: int,
    payload: CategoryUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER)),
    db: Session = Depends(get_db),
) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
    return update_category(db, category, payload, current_user)
