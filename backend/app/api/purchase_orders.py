from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.procurement import PurchaseOrderStatus
from app.models.user import User, UserRole
from app.schemas.procurement import PurchaseOrderCreate, PurchaseOrderRead
from app.services.procurement_service import create_purchase_order, issue_purchase_order, list_purchase_orders, load_purchase_order, purchase_order_to_read

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])


@router.get("", response_model=list[PurchaseOrderRead])
def index(
    status: PurchaseOrderStatus | None = None,
    search: str | None = None,
    _: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.PROCUREMENT_OFFICER, UserRole.WAREHOUSE_OFFICER, UserRole.AUDITOR)),
    db: Session = Depends(get_db),
) -> list[PurchaseOrderRead]:
    return list_purchase_orders(db, status, search)


@router.post("", response_model=PurchaseOrderRead, status_code=201)
def create(
    payload: PurchaseOrderCreate,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.PROCUREMENT_OFFICER)),
    db: Session = Depends(get_db),
) -> PurchaseOrderRead:
    return create_purchase_order(db, payload, current_user)


@router.get("/{order_id}", response_model=PurchaseOrderRead)
def detail(
    order_id: int,
    _: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.PROCUREMENT_OFFICER, UserRole.WAREHOUSE_OFFICER, UserRole.AUDITOR)),
    db: Session = Depends(get_db),
) -> PurchaseOrderRead:
    return purchase_order_to_read(load_purchase_order(db, order_id))


@router.post("/{order_id}/issue", response_model=PurchaseOrderRead)
def issue(
    order_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.PROCUREMENT_OFFICER)),
    db: Session = Depends(get_db),
) -> PurchaseOrderRead:
    return issue_purchase_order(db, order_id, current_user)
