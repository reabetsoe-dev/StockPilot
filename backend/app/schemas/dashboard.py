from pydantic import BaseModel


class RoleCount(BaseModel):
    role: str
    count: int


class DashboardSummary(BaseModel):
    organization: str
    active_users: int
    departments: int
    demo_accounts: int
    categories: int
    products: int
    suppliers: int
    warehouses: int
    inventory_value: float
    low_stock_items: int
    out_of_stock_items: int
    stock_movements: int
    role_counts: list[RoleCount]
    implementation_phase: str
    readiness_score: int
    enabled_modules: list[str]
