# StockPilot

**Inventory, Procurement & Warehouse Management Platform**

StockPilot is a full-stack business operations platform for managing inventory, suppliers, purchasing, warehouses, stock movements, receiving, internal stock requests, reorder risk, analytics, audit logs, and role-based access from one system.

It is designed as a professional portfolio project: realistic business workflows, clean FastAPI service architecture, a React enterprise interface, seeded demonstration data, automated tests, and Vercel deployment readiness without paid APIs or paid infrastructure.

## Live Demo

The project is Vercel-ready. Add the production URL here after connecting the repository and configuring the environment variables:

```text
https://your-stockpilot-vercel-url.vercel.app
```

## Business Problem

Many small and medium-sized organizations still manage inventory with spreadsheets, paper stock cards, chat messages, and disconnected supplier records. That makes it hard to prevent stock-outs, trace stock changes, understand supplier activity, or know which purchase orders and requests are still active.

StockPilot centralizes the lifecycle:

```text
Supplier -> Purchase Request -> Approval -> Purchase Order -> Goods Receipt -> Warehouse Inventory -> Stock Issue / Transfer -> Analytics
```

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

The seed creates 20 fictional users across the same roles for a populated demo.

## Features

- JWT authentication with bcrypt password hashing.
- Backend role authorization for administrators, inventory managers, procurement officers, warehouse officers, department requesters, and auditors.
- User, department, category, product, supplier, and warehouse management.
- Per-warehouse `InventoryBalance` records with backend-calculated available stock and valuation.
- Traceable `StockMovement` ledger for opening balances, goods receipts, stock issues, transfers, adjustments, and returns.
- Product stock detail pages with warehouse balances and recent movement history.
- Purchase requests with draft, submit, approve, and reject actions.
- Purchase orders with backend-calculated line totals, subtotal, tax, and total.
- Goods receiving with partial receipt support, PO quantity updates, inventory increases, and movement records.
- Internal stock requests with approval and stock issuing.
- Warehouse transfers with dispatch, receipt, source stock validation, and transfer movement history.
- Stock adjustments with required reasons and audit logging.
- Low-stock page with deterministic suggested reorder quantity.
- Analytics dashboards for inventory value, low stock, open purchase orders, goods receipts, transfers, supplier purchase value, and top purchased products.
- Internal notifications and notification inbox.
- Audit log viewer with search.
- Global search across products, SKUs, suppliers, warehouses, purchase requests, and purchase orders.
- Light and dark mode.
- Seed/reset commands for fictional demonstration data.
- GitHub Actions for backend tests, frontend lint, frontend tests, and production build.
- Vercel FastAPI entry point and SPA routing support.

## Technology Stack

Frontend: React, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, Recharts, Lucide React.

Backend: Python, FastAPI, SQLAlchemy, Pydantic, JWT, bcrypt.

Database: SQLite locally. Turso/libSQL is supported for production through environment variables.

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

Default local URLs:

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Demo Reset

To rebuild the local SQLite demo database from fictional seed data:

```bash
cd backend
python -m app.seed.reset_demo
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

## Deployment

The repository includes:

- `vercel.json` using Vercel Services for a Vite frontend service and FastAPI backend service.
- `backend/app/main.py` as the FastAPI backend service entry point.
- `api/index.py` as a classic Python runtime shim if deploying outside the Services setup.
- `backend/requirements.txt` and root `requirements.txt` for Python dependencies.
- `frontend/package.json` for the Vite build.

Production should use Turso/libSQL or another SQLite-compatible serverless database. Do not rely on a local SQLite file inside a Vercel function for production persistence.

If Turso variables are omitted on Vercel, the backend falls back to an ephemeral `/tmp/stockpilot.db` and auto-seeds demo data so reviewers can open the live portfolio. Use Turso/libSQL for durable production persistence.

Required production environment variables:

```text
ENVIRONMENT=production
TURSO_DATABASE_URL=
TURSO_AUTH_TOKEN=
JWT_SECRET_KEY=
FRONTEND_URL=
CORS_ORIGINS=
```

## Documentation

- [Architecture](docs/architecture.md)
- [Database](docs/database.md)
- [Inventory Engine](docs/inventory-engine.md)
- [Procurement Flow](docs/procurement-flow.md)
- [Deployment](docs/deployment.md)
- [Screenshots](docs/screenshots/README.md)

## Project Structure

```text
StockPilot/
  api/
  backend/
    app/
      api/
      core/
      models/
      schemas/
      seed/
      services/
    tests/
  docs/
  frontend/
    src/
      components/
      hooks/
      layouts/
      pages/
      services/
      types/
      utils/
```

## Security

StockPilot uses JWT sessions, hashed passwords, backend authorization checks, Pydantic validation, SQLAlchemy ORM queries, environment-based secrets, and configurable CORS. No database secret is exposed to browser code.

## Limitations

Version 1 intentionally avoids AI, paid APIs, background workers, email delivery, accounting integrations, barcode hardware integrations, and complex workflow engines. The project focuses on deterministic inventory and procurement business logic.

## Future Improvements

Demand forecasting, barcode scanner integration, supplier portal, email notifications, invoice matching, purchase budgets, a mobile warehouse app, multi-company support, accounting integration, and predictive inventory planning are documented future directions.

## License

MIT
