import type { UserRole } from "../types/auth";
import { roleLabel } from "../utils/format";

const roleClasses: Record<UserRole, string> = {
  ADMINISTRATOR: "border-slate-300 bg-slate-100 text-slate-700 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200",
  INVENTORY_MANAGER: "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-200",
  PROCUREMENT_OFFICER: "border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-200",
  WAREHOUSE_OFFICER: "border-blue-200 bg-blue-50 text-blue-700 dark:border-blue-800 dark:bg-blue-950 dark:text-blue-200",
  DEPARTMENT_REQUESTER: "border-violet-200 bg-violet-50 text-violet-700 dark:border-violet-800 dark:bg-violet-950 dark:text-violet-200",
  AUDITOR: "border-cyan-200 bg-cyan-50 text-cyan-700 dark:border-cyan-800 dark:bg-cyan-950 dark:text-cyan-200",
};

export function RoleBadge({ role }: { role: UserRole }) {
  return (
    <span className={`inline-flex rounded-md border px-2.5 py-1 text-xs font-semibold ${roleClasses[role]}`}>
      {roleLabel(role)}
    </span>
  );
}
