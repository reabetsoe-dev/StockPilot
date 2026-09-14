from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.analytics import AnalyticsSummary
from app.services.analytics_service import analytics_summary

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=AnalyticsSummary)
def dashboard(
    _: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER, UserRole.PROCUREMENT_OFFICER, UserRole.WAREHOUSE_OFFICER, UserRole.AUDITOR)),
    db: Session = Depends(get_db),
) -> AnalyticsSummary:
    return analytics_summary(db)


@router.get("/inventory", response_model=AnalyticsSummary)
def inventory(
    _: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.INVENTORY_MANAGER, UserRole.AUDITOR)),
    db: Session = Depends(get_db),
) -> AnalyticsSummary:
    return analytics_summary(db)


@router.get("/procurement", response_model=AnalyticsSummary)
def procurement(
    _: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.PROCUREMENT_OFFICER, UserRole.AUDITOR)),
    db: Session = Depends(get_db),
) -> AnalyticsSummary:
    return analytics_summary(db)
