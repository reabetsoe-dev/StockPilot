from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.category import CategoryRead
from app.schemas.supplier import SupplierRead


class ProductBase(BaseModel):
    sku: str = Field(min_length=2, max_length=80)
    barcode: str | None = Field(default=None, max_length=80)
    name: str = Field(min_length=2, max_length=180)
    description: str | None = None
    category_id: int
    unit_of_measure: str = Field(default="Each", min_length=1, max_length=40)
    cost_price: Decimal = Field(default=Decimal("0.00"), ge=0)
    selling_price: Decimal = Field(default=Decimal("0.00"), ge=0)
    reorder_level: int = Field(default=0, ge=0)
    preferred_supplier_id: int | None = None
    active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=2, max_length=80)
    barcode: str | None = Field(default=None, max_length=80)
    name: str | None = Field(default=None, min_length=2, max_length=180)
    description: str | None = None
    category_id: int | None = None
    unit_of_measure: str | None = Field(default=None, min_length=1, max_length=40)
    cost_price: Decimal | None = Field(default=None, ge=0)
    selling_price: Decimal | None = Field(default=None, ge=0)
    reorder_level: int | None = Field(default=None, ge=0)
    preferred_supplier_id: int | None = None
    active: bool | None = None


class ProductRead(ProductBase):
    id: int
    category: CategoryRead
    preferred_supplier: SupplierRead | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
