from collections import defaultdict
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.category import Category
from app.models.inventory import InventoryBalance
from app.models.procurement import GoodsReceipt, PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus, PurchaseRequest, PurchaseRequestStatus
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.warehouse import Warehouse
from app.models.warehouse_ops import StockTransfer
from app.schemas.analytics import AnalyticsSummary, NamedMetric
from app.services.inventory_service import inventory_snapshot_metrics, inventory_value


def analytics_summary(db: Session) -> AnalyticsSummary:
    inventory_metrics = inventory_snapshot_metrics(db)
    pending_purchase_requests = db.scalar(
        select(func.count(PurchaseRequest.id)).where(PurchaseRequest.status == PurchaseRequestStatus.SUBMITTED)
    ) or 0
    open_purchase_orders = db.scalar(
        select(func.count(PurchaseOrder.id)).where(PurchaseOrder.status.in_([PurchaseOrderStatus.DRAFT, PurchaseOrderStatus.ISSUED, PurchaseOrderStatus.PARTIALLY_RECEIVED]))
    ) or 0
    goods_received = db.scalar(select(func.count(GoodsReceipt.id))) or 0
    warehouse_transfers = db.scalar(select(func.count(StockTransfer.id))) or 0

    category_values: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    products = db.scalars(select(Product).options(selectinload(Product.category), selectinload(Product.inventory_balances)))
    for product in products:
        quantity_on_hand = sum(balance.quantity_on_hand for balance in product.inventory_balances)
        category_values[product.category.name] += inventory_value(quantity_on_hand, product.cost_price)

    warehouse_stock = [
        NamedMetric(name=name, value=value)
        for name, value in db.execute(
            select(Warehouse.name, func.coalesce(func.sum(InventoryBalance.quantity_on_hand), 0))
            .join(InventoryBalance, InventoryBalance.warehouse_id == Warehouse.id, isouter=True)
            .group_by(Warehouse.id)
            .order_by(Warehouse.name)
        ).all()
    ]

    po_status = [
        NamedMetric(name=status, value=count)
        for status, count in db.execute(
            select(PurchaseOrder.status, func.count(PurchaseOrder.id))
            .group_by(PurchaseOrder.status)
            .order_by(PurchaseOrder.status)
        ).all()
    ]

    supplier_values = [
        NamedMetric(name=name, value=value or Decimal("0.00"))
        for name, value in db.execute(
            select(Supplier.name, func.coalesce(func.sum(PurchaseOrder.total), 0))
            .join(PurchaseOrder, PurchaseOrder.supplier_id == Supplier.id, isouter=True)
            .group_by(Supplier.id)
            .order_by(func.coalesce(func.sum(PurchaseOrder.total), 0).desc())
            .limit(8)
        ).all()
    ]

    top_products = [
        NamedMetric(name=name, value=value or Decimal("0.00"))
        for name, value in db.execute(
            select(Product.name, func.coalesce(func.sum(PurchaseOrderItem.line_total), 0))
            .join(PurchaseOrderItem, PurchaseOrderItem.product_id == Product.id, isouter=True)
            .group_by(Product.id)
            .order_by(func.coalesce(func.sum(PurchaseOrderItem.line_total), 0).desc())
            .limit(8)
        ).all()
    ]

    return AnalyticsSummary(
        inventory_value=inventory_metrics["inventory_value"],
        low_stock_items=inventory_metrics["low_stock_items"],
        out_of_stock_items=inventory_metrics["out_of_stock_items"],
        pending_purchase_requests=pending_purchase_requests,
        open_purchase_orders=open_purchase_orders,
        goods_received=goods_received,
        warehouse_transfers=warehouse_transfers,
        inventory_value_by_category=[
            NamedMetric(name=name, value=value)
            for name, value in sorted(category_values.items(), key=lambda row: row[1], reverse=True)
        ],
        stock_by_warehouse=warehouse_stock,
        purchase_order_status=po_status,
        purchases_by_supplier=supplier_values,
        top_purchased_products=top_products,
    )
