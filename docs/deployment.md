# Deployment

StockPilot is designed for local SQLite development and Vercel deployment.

## Local

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

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`.

## Vercel

The repository provides:

- `vercel.json` with Vercel Services: `frontend` rooted at `frontend/` and `backend` rooted at `backend/`.
- `backend/app/main.py` as the FastAPI service entry point through `app.main:app`.
- `api/index.py` as a classic Python runtime shim if deploying without Services.
- `requirements.txt` at the repository root and `backend/requirements.txt` for Python dependency installation.
- `frontend/package.json` and Vite build scripts for the React app.

Production should set:

```text
ENVIRONMENT=production
TURSO_DATABASE_URL=
TURSO_AUTH_TOKEN=
JWT_SECRET_KEY=
FRONTEND_URL=
CORS_ORIGINS=
```

SQLite remains the default for local development. Production persistence should use Turso/libSQL because a local SQLite file inside a serverless function is not durable.

## GitHub Actions

`.github/workflows/ci.yml` runs on push and pull request:

- install backend dependencies
- run pytest
- install frontend dependencies
- run TypeScript lint
- run Vitest
- run the production build
