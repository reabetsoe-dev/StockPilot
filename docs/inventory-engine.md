# Inventory Engine

Phase 3 introduces the first real inventory ledger slice.

Implemented principles:

- Quantities are stored per product and warehouse in `InventoryBalance`.
- Available quantity is calculated as `quantity_on_hand - quantity_reserved`.
- Every seeded opening stock quantity creates an `OPENING_BALANCE` `StockMovement`.
- Inventory value is calculated by the backend as `quantity_on_hand * cost_price`.
- Stock status is calculated by the backend as `NORMAL`, `LOW_STOCK`, or `OUT_OF_STOCK`.
- Stock quantities should not be changed directly without a matching movement record.

Current opening stock flow:

```text
Seed product and warehouse records
Find or create InventoryBalance
Create OPENING_BALANCE StockMovement
Increase quantity_on_hand
Set seeded reserved quantity
Commit seeded demo ledger
```

Future transaction flow:

```text
Goods receipt created
InventoryBalance increased
StockMovement GOODS_RECEIPT inserted
PurchaseOrderItem received quantity updated
PurchaseOrder status recalculated
AuditLog inserted
Transaction committed
```
