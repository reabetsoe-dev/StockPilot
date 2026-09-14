# Database

Phase 3 models:

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

    DEPARTMENT {
        int id
        string name
        string description
        bool active
    }

    USER {
        int id
        string full_name
        string email
        string role
        int department_id
        bool active
    }

    AUDIT_LOG {
        int id
        int user_id
        string action
        string entity_type
        string entity_id
        string description
    }

    CATEGORY {
        int id
        string name
        string description
        bool active
    }

    SUPPLIER {
        int id
        string supplier_code
        string name
        string contact_person
        string email
        string payment_terms
        bool active
    }

    WAREHOUSE {
        int id
        string code
        string name
        string location
        string description
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
```

Later phases will add purchase requests, purchase orders, goods receipts, stock requests, and transfers.
