from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import UserRole
from app.schemas.department import DepartmentRead


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=128)
    role: UserRole
    department_id: int | None = None
    active: bool = True


class UserRead(BaseModel):
    id: int
    full_name: str
    email: str
    role: UserRole
    department_id: int | None
    active: bool
    department: DepartmentRead | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
