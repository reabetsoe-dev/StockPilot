from fastapi import APIRouter, Depends
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.audit import AuditLog
from app.models.user import User, UserRole
from app.schemas.audit import AuditLogRead

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=list[AuditLogRead])
def index(
    search: str | None = None,
    _: User = Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.AUDITOR)),
    db: Session = Depends(get_db),
) -> list[AuditLogRead]:
    stmt = select(AuditLog).options(selectinload(AuditLog.user))
    if search:
        needle = f"%{search.strip()}%"
        stmt = stmt.where(or_(AuditLog.action.ilike(needle), AuditLog.entity_type.ilike(needle), AuditLog.description.ilike(needle)))
    logs = db.scalars(stmt.order_by(desc(AuditLog.created_at), desc(AuditLog.id)).limit(200))
    return [
        AuditLogRead(
            id=log.id,
            user_id=log.user_id,
            user_name=log.user.full_name if log.user else None,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            description=log.description,
            created_at=log.created_at,
        )
        for log in logs
    ]
