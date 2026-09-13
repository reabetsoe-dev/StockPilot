from pydantic import BaseModel


class RoleCount(BaseModel):
    role: str
    count: int


class DashboardSummary(BaseModel):
    organization: str
    active_users: int
    departments: int
    demo_accounts: int
    role_counts: list[RoleCount]
    implementation_phase: str
    readiness_score: int
    enabled_modules: list[str]
