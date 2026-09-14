from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.database import get_db
from app.models.procurement import PurchaseRequestStatus
from app.models.user import User, UserRole
from app.schemas.procurement import PurchaseRequestCreate, PurchaseRequestRead
from app.services.procurement_service import (
    approve_purchase_request,
    create_purchase_request,
    list_purchase_requests,
    reject_purchase_request,
    submit_purchase_request,
)

router = APIRouter(prefix="/purchase-requests", tags=["Purchase Requests"])


@router.get("", response_model=list[PurchaseRequestRead])
def index(
    status: PurchaseRequestStatus | None = None,
    search: str | None = None,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER, UserRole.PROCUREMENT_OFFICER, UserRole.DEPARTMENT_REQUESTER, UserRole.AUDITOR)),
    db: Session = Depends(get_db),
) -> list[PurchaseRequestRead]:
    return list_purchase_requests(db, current_user, status, search)


@router.post("", response_model=PurchaseRequestRead, status_code=201)
def create(
    payload: PurchaseRequestCreate,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.DEPARTMENT_REQUESTER)),
    db: Session = Depends(get_db),
) -> PurchaseRequestRead:
    return create_purchase_request(db, payload, current_user)


@router.post("/{request_id}/submit", response_model=PurchaseRequestRead)
def submit(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PurchaseRequestRead:
    return submit_purchase_request(db, request_id, current_user)


@router.post("/{request_id}/approve", response_model=PurchaseRequestRead)
def approve(
    request_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER)),
    db: Session = Depends(get_db),
) -> PurchaseRequestRead:
    return approve_purchase_request(db, request_id, current_user)


@router.post("/{request_id}/reject", response_model=PurchaseRequestRead)
def reject(
    request_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER)),
    db: Session = Depends(get_db),
) -> PurchaseRequestRead:
    return reject_purchase_request(db, request_id, current_user)
