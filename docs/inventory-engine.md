# Inventory Engine

The inventory engine will be implemented after the platform foundation.

Design principles:

- Quantities will be stored per product and warehouse in `InventoryBalance`.
- Every quantity change will create a `StockMovement`.
- Goods receipts, stock issues, transfers, and adjustments will be transaction-safe.
- Stock must never become negative.
- Totals and available quantity will be calculated by the backend.

Example future transaction flow:

```text
Goods receipt created
InventoryBalance increased
StockMovement GOODS_RECEIPT inserted
PurchaseOrderItem received quantity updated
PurchaseOrder status recalculated
AuditLog inserted
Transaction committed
```
