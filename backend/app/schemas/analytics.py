from decimal import Decimal

from pydantic import BaseModel


class NamedMetric(BaseModel):
    name: str
    value: Decimal | int


class AnalyticsSummary(BaseModel):
    inventory_value: Decimal
    low_stock_items: int
    out_of_stock_items: int
    pending_purchase_requests: int
    open_purchase_orders: int
    goods_received: int
    warehouse_transfers: int
    inventory_value_by_category: list[NamedMetric]
    stock_by_warehouse: list[NamedMetric]
    purchase_order_status: list[NamedMetric]
    purchases_by_supplier: list[NamedMetric]
    top_purchased_products: list[NamedMetric]
