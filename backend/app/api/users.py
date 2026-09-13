from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import require_admin
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.services.audit_service import record_audit_log

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserRead])
def list_users(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[User]:
    return list(
        db.scalars(
            select(User)
            .options(selectinload(User.department))
            .order_by(User.role, User.full_name)
        )
    )


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> User:
    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists.")

    user = User(
        full_name=payload.full_name,
        email=payload.email.lower(),
        password_hash=get_password_hash(payload.password),
        role=payload.role,
        department_id=payload.department_id,
        active=payload.active,
    )
    db.add(user)
    db.flush()
    record_audit_log(
        db,
        current_user,
        "USER_CREATED",
        "User",
        user.id,
        f"{current_user.full_name} created user {user.email}.",
    )
    db.commit()
    db.refresh(user)
    return user
