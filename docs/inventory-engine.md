# Inventory Engine

StockPilot treats stock as a ledger-driven system. Quantities are stored in `InventoryBalance`, and every change is explained by a `StockMovement`.

## Core Rules

- Stock is tracked per product and warehouse.
- Available quantity is calculated as `quantity_on_hand - quantity_reserved`.
- Inventory value is calculated as `quantity_on_hand * cost_price`.
- Stock status is calculated as `NORMAL`, `LOW_STOCK`, or `OUT_OF_STOCK`.
- Low stock is true when available quantity is less than or equal to reorder level.
- Suggested reorder quantity uses deterministic logic: `max(reorder_level * 3, reorder_level + 1) - available_quantity`.
- Quantities should never be changed silently.

## Movement Types

- `OPENING_BALANCE`
- `GOODS_RECEIPT`
- `STOCK_ISSUE`
- `TRANSFER_OUT`
- `TRANSFER_IN`
- `ADJUSTMENT_INCREASE`
- `ADJUSTMENT_DECREASE`
- `RETURN`

## Goods Receipt Flow

```text
Validate purchase order
Validate receiving quantities
Create GoodsReceipt and GoodsReceiptItem records
Increase InventoryBalance
Create GOODS_RECEIPT movements
Update PurchaseOrderItem quantity_received
Recalculate PurchaseOrder status
Create audit log and notifications
Commit transaction
```

## Stock Issue Flow

```text
Validate stock request is approved
Validate available source stock for every line
Create STOCK_ISSUE movements
Decrease source InventoryBalance
Mark quantities issued
Set request status to ISSUED
Create audit log and notifications
Commit transaction
```

## Transfer Flow

Dispatch:

```text
Validate source and destination warehouses
Validate available source stock
Decrease source InventoryBalance
Create TRANSFER_OUT movements
Set transfer status to IN_TRANSIT
```

Receipt:

```text
Increase destination InventoryBalance
Create TRANSFER_IN movements
Set transfer status to COMPLETED
Record completing user and timestamp
```

## Adjustment Flow

Inventory managers can increase or decrease stock with a required reason. Each adjustment creates a `StockAdjustment`, a matching stock movement, and an audit record. Negative stock is rejected.
