# Deployment

StockPilot is designed for local SQLite development and Vercel deployment.

## Local

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m app.seed.seed_data
uvicorn app.main:app --reload
```

```bash
cd frontend
npm install
npm run dev
```

## Vercel

The root `vercel.json` uses Vercel Services:

- `frontend`: Vite app in `frontend/`
- `backend`: FastAPI app in `backend/`

Production should set:

```text
TURSO_DATABASE_URL=
TURSO_AUTH_TOKEN=
JWT_SECRET_KEY=
FRONTEND_URL=
```

SQLite remains the default for local development.
