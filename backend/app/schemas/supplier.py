from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SupplierBase(BaseModel):
    supplier_code: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=2, max_length=180)
    contact_person: str = Field(min_length=2, max_length=140)
    email: str | None = Field(default=None, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    phone: str | None = Field(default=None, max_length=60)
    address: str | None = None
    tax_reference: str | None = Field(default=None, max_length=80)
    payment_terms: str | None = Field(default=None, max_length=120)
    active: bool = True


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    supplier_code: str | None = Field(default=None, min_length=2, max_length=40)
    name: str | None = Field(default=None, min_length=2, max_length=180)
    contact_person: str | None = Field(default=None, min_length=2, max_length=140)
    email: str | None = Field(default=None, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    phone: str | None = Field(default=None, max_length=60)
    address: str | None = None
    tax_reference: str | None = Field(default=None, max_length=80)
    payment_terms: str | None = Field(default=None, max_length=120)
    active: bool | None = None


class SupplierRead(SupplierBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
