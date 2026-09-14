from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.warehouse_ops import StockAdjustmentCreate, StockAdjustmentRead
from app.services.warehouse_service import create_adjustment, list_adjustments

router = APIRouter(prefix="/stock-adjustments", tags=["Stock Adjustments"])


@router.get("", response_model=list[StockAdjustmentRead])
def index(
    _: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER, UserRole.AUDITOR)),
    db: Session = Depends(get_db),
) -> list[StockAdjustmentRead]:
    return list_adjustments(db)


@router.post("", response_model=StockAdjustmentRead, status_code=201)
def create(
    payload: StockAdjustmentCreate,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER)),
    db: Session = Depends(get_db),
) -> StockAdjustmentRead:
    return create_adjustment(db, payload, current_user)
