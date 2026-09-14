from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.warehouse_ops import StockRequestStatus
from app.schemas.warehouse_ops import StockRequestCreate, StockRequestRead
from app.services.warehouse_service import approve_stock_request, create_stock_request, issue_stock_request, list_stock_requests, reject_stock_request

router = APIRouter(prefix="/stock-requests", tags=["Stock Requests"])


@router.get("", response_model=list[StockRequestRead])
def index(
    status: StockRequestStatus | None = None,
    search: str | None = None,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER, UserRole.WAREHOUSE_OFFICER, UserRole.DEPARTMENT_REQUESTER, UserRole.AUDITOR)),
    db: Session = Depends(get_db),
) -> list[StockRequestRead]:
    return list_stock_requests(db, current_user, status, search)


@router.post("", response_model=StockRequestRead, status_code=201)
def create(
    payload: StockRequestCreate,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.DEPARTMENT_REQUESTER)),
    db: Session = Depends(get_db),
) -> StockRequestRead:
    return create_stock_request(db, payload, current_user)


@router.post("/{request_id}/approve", response_model=StockRequestRead)
def approve(
    request_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER)),
    db: Session = Depends(get_db),
) -> StockRequestRead:
    return approve_stock_request(db, request_id, current_user)


@router.post("/{request_id}/reject", response_model=StockRequestRead)
def reject(
    request_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER)),
    db: Session = Depends(get_db),
) -> StockRequestRead:
    return reject_stock_request(db, request_id, current_user)


@router.post("/{request_id}/issue", response_model=StockRequestRead)
def issue(
    request_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.WAREHOUSE_OFFICER)),
    db: Session = Depends(get_db),
) -> StockRequestRead:
    return issue_stock_request(db, request_id, current_user)
