# Procurement Flow

The procurement lifecycle will be introduced in later phases.

```mermaid
flowchart LR
    PR[Purchase Request] --> Review[Approval Review]
    Review --> PO[Purchase Order]
    PO --> GRN[Goods Receipt]
    GRN --> Inventory[Warehouse Inventory]
```

The first implementation does not include the procurement tables yet. It prepares roles, authentication, departments, and the layout that later procurement screens will use.
