from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DepartmentBase(BaseModel):
    name: str
    description: str | None = None
    active: bool = True


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentRead(DepartmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
