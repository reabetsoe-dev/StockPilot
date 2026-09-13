from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.models.department import Department
from app.models.user import User
from app.schemas.department import DepartmentCreate, DepartmentRead
from app.services.audit_service import record_audit_log

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("", response_model=list[DepartmentRead])
def list_departments(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Department]:
    return list(db.scalars(select(Department).order_by(Department.name)))


@router.post("", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED)
def create_department(
    payload: DepartmentCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Department:
    existing = db.scalar(select(Department).where(Department.name == payload.name))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Department already exists.")

    department = Department(
        name=payload.name,
        description=payload.description,
        active=payload.active,
    )
    db.add(department)
    db.flush()
    record_audit_log(
        db,
        current_user,
        "DEPARTMENT_CREATED",
        "Department",
        department.id,
        f"{current_user.full_name} created department {department.name}.",
    )
    db.commit()
    db.refresh(department)
    return department
