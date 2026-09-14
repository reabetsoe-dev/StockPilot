# Architecture

StockPilot uses a React frontend and FastAPI backend with a local SQLite database for development.

```mermaid
flowchart TD
    User[User] --> Vercel[Vercel]
    Vercel --> Frontend[React Vite Frontend]
    Vercel --> Backend[FastAPI Backend]
    Backend --> DB[(SQLite locally / Turso in production)]
```

Phase 2 adds the catalog master data used by later inventory and procurement flows: categories, products, suppliers, and warehouses. Business logic will continue moving into service modules as stock balances, purchase requests, purchase orders, receiving, and transfers are added.
