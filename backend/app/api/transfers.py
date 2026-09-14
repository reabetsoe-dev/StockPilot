from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.warehouse_ops import StockTransferStatus
from app.schemas.warehouse_ops import StockTransferCreate, StockTransferRead
from app.services.warehouse_service import create_transfer, dispatch_transfer, list_transfers, receive_transfer

router = APIRouter(prefix="/transfers", tags=["Stock Transfers"])


@router.get("", response_model=list[StockTransferRead])
def index(
    status: StockTransferStatus | None = None,
    search: str | None = None,
    _: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER, UserRole.WAREHOUSE_OFFICER, UserRole.AUDITOR)),
    db: Session = Depends(get_db),
) -> list[StockTransferRead]:
    return list_transfers(db, status, search)


@router.post("", response_model=StockTransferRead, status_code=201)
def create(
    payload: StockTransferCreate,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER, UserRole.WAREHOUSE_OFFICER)),
    db: Session = Depends(get_db),
) -> StockTransferRead:
    return create_transfer(db, payload, current_user)


@router.post("/{transfer_id}/dispatch", response_model=StockTransferRead)
def dispatch(
    transfer_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.WAREHOUSE_OFFICER)),
    db: Session = Depends(get_db),
) -> StockTransferRead:
    return dispatch_transfer(db, transfer_id, current_user)


@router.post("/{transfer_id}/receive", response_model=StockTransferRead)
def receive(
    transfer_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.WAREHOUSE_OFFICER)),
    db: Session = Depends(get_db),
) -> StockTransferRead:
    return receive_transfer(db, transfer_id, current_user)
