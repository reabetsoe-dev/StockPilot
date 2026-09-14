from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.procurement import PurchaseOrderStatus, PurchaseRequestPriority, PurchaseRequestStatus


class PurchaseRequestItemCreate(BaseModel):
    product_id: int | None = None
    description: str = Field(min_length=2)
    quantity: int = Field(gt=0)
    estimated_unit_price: Decimal = Field(default=Decimal("0.00"), ge=0)


class PurchaseRequestCreate(BaseModel):
    department_id: int | None = None
    purpose: str = Field(min_length=5)
    priority: PurchaseRequestPriority = PurchaseRequestPriority.NORMAL
    items: list[PurchaseRequestItemCreate] = Field(min_length=1)


class PurchaseRequestItemRead(BaseModel):
    id: int
    product_id: int | None
    product_sku: str | None
    product_name: str | None
    description: str
    quantity: int
    estimated_unit_price: Decimal


class PurchaseRequestRead(BaseModel):
    id: int
    reference_number: str
    requested_by: int
    requested_by_name: str
    department_id: int
    department_name: str
    purpose: str
    priority: PurchaseRequestPriority
    status: PurchaseRequestStatus
    created_at: datetime
    updated_at: datetime
    items: list[PurchaseRequestItemRead]


class PurchaseOrderItemCreate(BaseModel):
    product_id: int
    description: str | None = None
    quantity_ordered: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0)


class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    purchase_request_id: int | None = None
    expected_delivery_date: date | None = None
    notes: str | None = None
    items: list[PurchaseOrderItemCreate] = Field(min_length=1)


class PurchaseOrderItemRead(BaseModel):
    id: int
    product_id: int
    product_sku: str
    product_name: str
    description: str
    quantity_ordered: int
    quantity_received: int
    unit_price: Decimal
    line_total: Decimal
    remaining_quantity: int


class PurchaseOrderRead(BaseModel):
    id: int
    po_number: str
    supplier_id: int
    supplier_name: str
    purchase_request_id: int | None
    purchase_request_reference: str | None
    order_date: date
    expected_delivery_date: date | None
    status: PurchaseOrderStatus
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    notes: str | None
    created_by: int
    created_by_name: str
    created_at: datetime
    updated_at: datetime
    items: list[PurchaseOrderItemRead]


class GoodsReceiptItemCreate(BaseModel):
    purchase_order_item_id: int
    quantity_received: int = Field(ge=0)
    quantity_rejected: int = Field(default=0, ge=0)
    notes: str | None = None


class GoodsReceiptCreate(BaseModel):
    purchase_order_id: int
    warehouse_id: int
    received_date: date | None = None
    notes: str | None = None
    items: list[GoodsReceiptItemCreate] = Field(min_length=1)


class GoodsReceiptItemRead(BaseModel):
    id: int
    purchase_order_item_id: int
    product_id: int
    product_sku: str
    product_name: str
    quantity_received: int
    quantity_rejected: int
    notes: str | None


class GoodsReceiptRead(BaseModel):
    id: int
    receipt_number: str
    purchase_order_id: int
    purchase_order_number: str
    warehouse_id: int
    warehouse_name: str
    received_by: int
    received_by_name: str
    received_date: date
    notes: str | None
    created_at: datetime
    items: list[GoodsReceiptItemRead]
