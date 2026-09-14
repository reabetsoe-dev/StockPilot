from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.procurement import GoodsReceiptCreate, GoodsReceiptRead
from app.services.procurement_service import list_goods_receipts, receive_goods

router = APIRouter(prefix="/goods-receipts", tags=["Goods Receipts"])


@router.get("", response_model=list[GoodsReceiptRead])
def index(
    search: str | None = None,
    _: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.PROCUREMENT_OFFICER, UserRole.WAREHOUSE_OFFICER, UserRole.AUDITOR)),
    db: Session = Depends(get_db),
) -> list[GoodsReceiptRead]:
    return list_goods_receipts(db, search)


@router.post("", response_model=GoodsReceiptRead, status_code=201)
def create(
    payload: GoodsReceiptCreate,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.WAREHOUSE_OFFICER)),
    db: Session = Depends(get_db),
) -> GoodsReceiptRead:
    return receive_goods(db, payload, current_user)
