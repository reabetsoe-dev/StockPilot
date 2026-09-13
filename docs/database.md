# Database

Phase 1 models:

```mermaid
erDiagram
    DEPARTMENT ||--o{ USER : contains
    USER ||--o{ AUDIT_LOG : performs

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
```

Later phases will add products, categories, suppliers, warehouses, inventory balances, stock movements, purchase requests, purchase orders, goods receipts, stock requests, and transfers.
