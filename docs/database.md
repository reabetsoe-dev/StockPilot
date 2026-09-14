# Database

StockPilot persists business state through SQLAlchemy models. SQLite is the local default, and the same ORM layer can target Turso/libSQL in production.

```mermaid
erDiagram
    DEPARTMENT ||--o{ USER : contains
    USER ||--o{ AUDIT_LOG : performs
    CATEGORY ||--o{ PRODUCT : classifies
    SUPPLIER ||--o{ PRODUCT : supplies
    PRODUCT ||--o{ INVENTORY_BALANCE : stocked_as
    WAREHOUSE ||--o{ INVENTORY_BALANCE : stores
    PRODUCT ||--o{ STOCK_MOVEMENT : changes
    WAREHOUSE ||--o{ STOCK_MOVEMENT : records
    USER ||--o{ STOCK_MOVEMENT : performs
    USER ||--o{ NOTIFICATION : receives
    DEPARTMENT ||--o{ PURCHASE_REQUEST : requests
    USER ||--o{ PURCHASE_REQUEST : creates
    PURCHASE_REQUEST ||--o{ PURCHASE_REQUEST_ITEM : contains
    PURCHASE_REQUEST ||--o{ PURCHASE_ORDER : converts_to
    SUPPLIER ||--o{ PURCHASE_ORDER : receives
    PURCHASE_ORDER ||--o{ PURCHASE_ORDER_ITEM : contains
    PURCHASE_ORDER ||--o{ GOODS_RECEIPT : received_by
    GOODS_RECEIPT ||--o{ GOODS_RECEIPT_ITEM : contains
    PURCHASE_ORDER_ITEM ||--o{ GOODS_RECEIPT_ITEM : fulfills
    DEPARTMENT ||--o{ STOCK_REQUEST : requests
    STOCK_REQUEST ||--o{ STOCK_REQUEST_ITEM : contains
    WAREHOUSE ||--o{ STOCK_TRANSFER : source
    WAREHOUSE ||--o{ STOCK_TRANSFER : destination
    STOCK_TRANSFER ||--o{ STOCK_TRANSFER_ITEM : contains
    PRODUCT ||--o{ STOCK_ADJUSTMENT : adjusted
    WAREHOUSE ||--o{ STOCK_ADJUSTMENT : adjusted_at

    USER {
        int id
        string full_name
        string email
        string role
        int department_id
        bool active
    }

    PRODUCT {
        int id
        string sku
        string barcode
        string name
        int category_id
        decimal cost_price
        decimal selling_price
        int reorder_level
        int preferred_supplier_id
        bool active
    }

    INVENTORY_BALANCE {
        int id
        int warehouse_id
        int product_id
        int quantity_on_hand
        int quantity_reserved
    }

    STOCK_MOVEMENT {
        int id
        int product_id
        int warehouse_id
        string movement_type
        int quantity
        string reference_type
        string reference_id
        string reason
        int performed_by
    }

    PURCHASE_REQUEST {
        int id
        string reference_number
        int requested_by
        int department_id
        string priority
        string status
    }

    PURCHASE_ORDER {
        int id
        string po_number
        int supplier_id
        int purchase_request_id
        string status
        decimal subtotal
        decimal tax
        decimal total
    }

    GOODS_RECEIPT {
        int id
        string receipt_number
        int purchase_order_id
        int warehouse_id
        int received_by
    }

    STOCK_REQUEST {
        int id
        string reference_number
        int department_id
        int requested_by
        int source_warehouse_id
        string status
    }

    STOCK_TRANSFER {
        int id
        string transfer_number
        int source_warehouse_id
        int destination_warehouse_id
        string status
    }

    STOCK_ADJUSTMENT {
        int id
        string adjustment_number
        int product_id
        int warehouse_id
        string adjustment_type
        int quantity
        string reason
    }
```

## Integrity Rules

- SKU, supplier code, category name, and warehouse code are unique.
- Available stock is calculated as `quantity_on_hand - quantity_reserved`.
- Purchase order totals are calculated in the backend.
- Goods receipts cannot exceed remaining ordered quantities.
- Stock issues and transfers reject operations that would create negative stock.
- Completed transfer and receipt records are not silently modified.
- Stock quantity changes create `StockMovement` records.
- Important workflow actions create `AuditLog` records.
