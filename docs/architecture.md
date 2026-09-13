# Architecture

StockPilot uses a React frontend and FastAPI backend with a local SQLite database for development.

```mermaid
flowchart TD
    User[User] --> Vercel[Vercel]
    Vercel --> Frontend[React Vite Frontend]
    Vercel --> Backend[FastAPI Backend]
    Backend --> DB[(SQLite locally / Turso in production)]
```

Phase 1 focuses on authentication, role-aware navigation, seeded users, departments, and a backend-driven dashboard. Business logic will continue moving into service modules as inventory and procurement features are added.
