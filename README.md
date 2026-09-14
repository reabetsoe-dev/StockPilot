# StockPilot

**Inventory, Procurement & Warehouse Management Platform**

StockPilot is a full-stack business operations platform designed to demonstrate how organizations can manage inventory, procurement, suppliers, warehouses, and stock movement from a centralized system.

This repository is being built incrementally. Phase 3 now establishes the platform foundation, catalog layer, and inventory ledger: FastAPI, React, SQLite, SQLAlchemy, authentication, JWT sessions, role-aware navigation, seeded demo accounts, protected frontend routes, dashboard metrics, product categories, products, suppliers, warehouses, inventory balances, stock movements, opening stock, and product stock detail screens.

## Business Problem

Many small and medium-sized organizations still manage stock with spreadsheets, paper stock cards, chat messages, and disconnected supplier records. StockPilot is designed to centralize the operational lifecycle from request to procurement, receiving, warehouse inventory, issuing, movement history, and reporting.

## Demo Credentials

All demo users use the password `Demo123!`.

| Role | Email |
| --- | --- |
| Administrator | `admin@stockpilot.local` |
| Inventory Manager | `inventory@stockpilot.local` |
| Procurement Officer | `procurement@stockpilot.local` |
| Warehouse Officer | `warehouse@stockpilot.local` |
| Department Requester | `requester@stockpilot.local` |
| Auditor | `auditor@stockpilot.local` |

## Implemented Features

- FastAPI backend with SQLAlchemy models for users, departments, and audit logs.
- SQLite local database with Turso/libSQL-ready configuration for later Vercel deployment.
- JWT authentication with bcrypt password hashing.
- Backend role authorization for administrator-only user and department management.
- Seeded fictional organization: StockPilot Distribution Ltd.
- Catalog models and APIs for categories, products, suppliers, and warehouses.
- Seeded catalog data: 8 categories, 12 suppliers, 3 warehouses, and 50 realistic products.
- Backend uniqueness validation for SKU, barcode, supplier code, warehouse code, and category names.
- InventoryBalance and StockMovement models for per-warehouse stock tracking.
- Seeded opening balances across Central, North, and Retail warehouses with traceable OPENING_BALANCE movements.
- Backend-calculated available quantity, stock status, and inventory valuation.
- Inventory index, product stock detail, and stock movement history screens.
- React, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, Recharts, and Lucide React.
- Professional login screen, protected routes, app layout, theme toggle, role-aware sidebar foundation, dashboard, user list, department view, product table, category cards, supplier register, warehouse directory, inventory table, and ledger view.
- Backend pytest coverage for authentication, RBAC, catalog permissions, inventory calculations, movement filtering, and inventory authorization.
- Frontend Vitest coverage for login rendering and role-based navigation.

## Technology Stack

Frontend: React, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, Recharts, Lucide React.

Backend: Python, FastAPI, SQLAlchemy, Pydantic, JWT, bcrypt.

Database: SQLite locally. Turso/libSQL support is prepared through environment variables.

## Local Development

Backend:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m app.seed.seed_data
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Testing

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm run lint
npm test
npm run build
```

## API Documentation

When the backend is running locally:

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Vercel Deployment

The repository includes a Vercel Services configuration for one project with a Vite frontend service and FastAPI backend service. Production persistence should use Turso/libSQL through:

```text
TURSO_DATABASE_URL=
TURSO_AUTH_TOKEN=
JWT_SECRET_KEY=
```

## Documentation

- [Architecture](docs/architecture.md)
- [Database](docs/database.md)
- [Inventory Engine](docs/inventory-engine.md)
- [Procurement Flow](docs/procurement-flow.md)
- [Deployment](docs/deployment.md)

## Screenshots

Screenshot placeholders are prepared in `docs/screenshots/`. Real screenshots should be added after each feature phase is visually complete.

## Limitations

Phase 3 does not yet implement purchase requests, purchase orders, goods receipts, stock issues, transfers, stock adjustments, a dedicated low-stock/reorder page, or procurement analytics. Those are planned in later phases.

## Future Improvements

Future phases will add the procurement lifecycle, receiving, stock issue, transfer logic, low-stock/reorder suggestions, analytics, audit views, and production database verification.
