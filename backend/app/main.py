from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    adjustments,
    analytics,
    audit,
    auth,
    categories,
    dashboard,
    departments,
    goods_receipts,
    inventory,
    low_stock,
    notifications,
    products,
    purchase_orders,
    purchase_requests,
    search,
    stock_requests,
    suppliers,
    transfers,
    users,
    warehouses,
)
from app.core.config import get_settings
from app.core.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.environment != "test":
        init_db()
    yield


app = FastAPI(
    title="StockPilot API",
    description="Backend API for the StockPilot inventory, procurement, and warehouse demo.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(adjustments.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(departments.router, prefix="/api")
app.include_router(goods_receipts.router, prefix="/api")
app.include_router(inventory.router, prefix="/api")
app.include_router(low_stock.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(purchase_orders.router, prefix="/api")
app.include_router(purchase_requests.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(stock_requests.router, prefix="/api")
app.include_router(suppliers.router, prefix="/api")
app.include_router(transfers.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(warehouses.router, prefix="/api")


@app.get("/api/health", tags=["System"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "stockpilot-api"}
