from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.inventory import LowStockItem
from app.services.inventory_service import list_low_stock_items

router = APIRouter(prefix="/low-stock", tags=["Low Stock"])


@router.get("", response_model=list[LowStockItem])
def index(
    _: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER, UserRole.WAREHOUSE_OFFICER, UserRole.AUDITOR)),
    db: Session = Depends(get_db),
) -> list[LowStockItem]:
    return list_low_stock_items(db)
