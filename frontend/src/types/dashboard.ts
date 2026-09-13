export interface RoleCount {
  role: string;
  count: number;
}

export interface DashboardSummary {
  organization: string;
  active_users: number;
  departments: number;
  demo_accounts: number;
  role_counts: RoleCount[];
  implementation_phase: string;
  readiness_score: number;
  enabled_modules: string[];
}
