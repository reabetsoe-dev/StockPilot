from datetime import datetime

from pydantic import BaseModel, Field

from app.models.warehouse_ops import StockAdjustmentType, StockRequestStatus, StockTransferStatus


class StockRequestItemCreate(BaseModel):
    product_id: int
    quantity_requested: int = Field(gt=0)


class StockRequestCreate(BaseModel):
    department_id: int | None = None
    source_warehouse_id: int
    purpose: str = Field(min_length=5)
    items: list[StockRequestItemCreate] = Field(min_length=1)


class StockRequestItemRead(BaseModel):
    id: int
    product_id: int
    product_sku: str
    product_name: str
    quantity_requested: int
    quantity_issued: int


class StockRequestRead(BaseModel):
    id: int
    reference_number: str
    department_id: int
    department_name: str
    requested_by: int
    requested_by_name: str
    source_warehouse_id: int
    source_warehouse_name: str
    purpose: str
    status: StockRequestStatus
    issued_by_name: str | None
    issued_at: datetime | None
    created_at: datetime
    updated_at: datetime
    items: list[StockRequestItemRead]


class StockTransferItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class StockTransferCreate(BaseModel):
    source_warehouse_id: int
    destination_warehouse_id: int
    items: list[StockTransferItemCreate] = Field(min_length=1)


class StockTransferItemRead(BaseModel):
    id: int
    product_id: int
    product_sku: str
    product_name: str
    quantity: int


class StockTransferRead(BaseModel):
    id: int
    transfer_number: str
    source_warehouse_id: int
    source_warehouse_name: str
    destination_warehouse_id: int
    destination_warehouse_name: str
    status: StockTransferStatus
    requested_by: int
    requested_by_name: str
    completed_by_name: str | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    items: list[StockTransferItemRead]


class StockAdjustmentCreate(BaseModel):
    product_id: int
    warehouse_id: int
    adjustment_type: StockAdjustmentType
    quantity: int = Field(gt=0)
    reason: str = Field(min_length=5)
    notes: str | None = None


class StockAdjustmentRead(BaseModel):
    id: int
    adjustment_number: str
    product_id: int
    product_sku: str
    product_name: str
    warehouse_id: int
    warehouse_name: str
    adjustment_type: StockAdjustmentType
    quantity: int
    reason: str
    notes: str | None
    performed_by_name: str
    created_at: datetime
