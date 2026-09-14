from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.inventory import StockMovementType
from app.schemas.product import ProductRead
from app.schemas.warehouse import WarehouseRead


class InventoryBalanceRead(BaseModel):
    id: int
    warehouse: WarehouseRead
    product_id: int
    quantity_on_hand: int
    quantity_reserved: int
    available_quantity: int
    inventory_value: Decimal
    stock_status: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InventoryItem(BaseModel):
    product_id: int
    sku: str
    product_name: str
    category_name: str
    preferred_supplier_name: str | None
    unit_of_measure: str
    reorder_level: int
    total_on_hand: int
    total_reserved: int
    available_quantity: int
    inventory_value: Decimal
    stock_status: str
    warehouse_count: int


class LowStockItem(InventoryItem):
    suggested_reorder_quantity: int
    suggested_target_quantity: int


class StockMovementRead(BaseModel):
    id: int
    product_id: int
    product_sku: str
    product_name: str
    warehouse_id: int
    warehouse_code: str
    warehouse_name: str
    movement_type: StockMovementType
    quantity: int
    reference_type: str | None
    reference_id: str | None
    reason: str
    performed_by: int | None
    performed_by_name: str | None
    created_at: datetime


class ProductInventoryDetail(BaseModel):
    product: ProductRead
    total_on_hand: int
    total_reserved: int
    available_quantity: int
    inventory_value: Decimal
    stock_status: str
    balances: list[InventoryBalanceRead]
    recent_movements: list[StockMovementRead]
