from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.department import Department
from app.models.user import User
from app.schemas.dashboard import DashboardSummary, RoleCount

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

ORGANIZATION_NAME = "StockPilot Distribution Ltd"
ENABLED_MODULES = [
    "Authentication",
    "Role-aware navigation",
    "User administration",
    "Department directory",
    "Seeded demo organization",
    "Audit foundation",
]


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardSummary:
    active_users = db.scalar(select(func.count(User.id)).where(User.active.is_(True))) or 0
    department_count = db.scalar(select(func.count(Department.id))) or 0
    demo_accounts = db.scalar(
        select(func.count(User.id)).where(User.email.like("%@stockpilot.local"))
    ) or 0
    role_counts = [
        RoleCount(role=role, count=count)
        for role, count in db.execute(
            select(User.role, func.count(User.id)).group_by(User.role).order_by(User.role)
        ).all()
    ]
    readiness_score = min(100, int((active_users / 10) * 45 + (department_count / 7) * 35 + 20))
    return DashboardSummary(
        organization=ORGANIZATION_NAME,
        active_users=active_users,
        departments=department_count,
        demo_accounts=demo_accounts,
        role_counts=role_counts,
        implementation_phase="Phase 1 - Platform foundation",
        readiness_score=readiness_score,
        enabled_modules=ENABLED_MODULES,
    )
