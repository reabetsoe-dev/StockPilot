import {
  Activity,
  AlertTriangle,
  Building2,
  CheckCircle2,
  PackagePlus,
  PackageX,
  ShieldCheck,
  Tags,
  Truck,
  Users,
  Warehouse,
} from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useQuery } from "@tanstack/react-query";

import { StatCard } from "../components/StatCard";
import { api } from "../services/api";
import type { DashboardSummary } from "../types/dashboard";
import { formatMoney, roleLabel } from "../utils/format";

export function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: async () => (await api.get<DashboardSummary>("/dashboard/summary")).data,
  });

  const roleData =
    data?.role_counts.map((item) => ({
      role: roleLabel(item.role).replace(" Officer", ""),
      users: item.count,
    })) ?? [];

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <p className="text-sm font-bold uppercase text-emerald-600 dark:text-emerald-300">Operations overview</p>
        <div className="mt-3 flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
          <div>
            <h1 className="text-4xl font-bold tracking-tight text-slate-950 dark:text-white">
              {data?.organization ?? "StockPilot Distribution Ltd"}
            </h1>
            <p className="mt-3 max-w-3xl text-base leading-7 text-slate-600 dark:text-slate-300">
              Secure access, role-aware navigation, user administration, and catalog master data now anchor the
              backend stock ledger, opening balances, valuation, and procurement lifecycle.
            </p>
          </div>
          <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-5 py-4 text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-100">
            <p className="text-sm font-semibold">Readiness</p>
            <p className="text-3xl font-bold">{data?.readiness_score ?? 0}%</p>
          </div>
        </div>
      </section>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Inventory value" value={isLoading ? "..." : formatMoney(data?.inventory_value ?? 0)} tone="emerald" icon={Activity} />
        <StatCard label="Products" value={isLoading ? "..." : data?.products ?? 0} tone="blue" icon={PackagePlus} />
        <StatCard label="Low stock" value={isLoading ? "..." : data?.low_stock_items ?? 0} tone="amber" icon={AlertTriangle} />
        <StatCard label="Out of stock" value={isLoading ? "..." : data?.out_of_stock_items ?? 0} tone="slate" icon={PackageX} />
      </section>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Warehouses" value={isLoading ? "..." : data?.warehouses ?? 0} tone="emerald" icon={Warehouse} />
        <StatCard label="Stock movements" value={isLoading ? "..." : data?.stock_movements ?? 0} tone="blue" icon={Activity} />
        <StatCard label="Suppliers" value={isLoading ? "..." : data?.suppliers ?? 0} tone="amber" icon={Truck} />
        <StatCard label="Categories" value={isLoading ? "..." : data?.categories ?? 0} tone="slate" icon={Tags} />
      </section>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Active users" value={isLoading ? "..." : data?.active_users ?? 0} tone="emerald" icon={Users} />
        <StatCard label="Departments" value={isLoading ? "..." : data?.departments ?? 0} tone="blue" icon={Building2} />
        <StatCard label="Demo accounts" value={isLoading ? "..." : data?.demo_accounts ?? 0} tone="amber" icon={ShieldCheck} />
        <StatCard label="Enabled modules" value={isLoading ? "..." : data?.enabled_modules.length ?? 0} tone="slate" icon={CheckCircle2} />
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h2 className="text-lg font-bold text-slate-950 dark:text-white">Role coverage</h2>
          <div className="mt-5 h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={roleData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="role" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="users" fill="#059669" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h2 className="text-lg font-bold text-slate-950 dark:text-white">Enabled foundation</h2>
          <div className="mt-4 space-y-3">
            {(data?.enabled_modules ?? []).map((module) => (
              <div key={module} className="flex items-center gap-3 rounded-lg border border-slate-200 px-4 py-3 dark:border-slate-800">
                <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                <span className="text-sm font-medium text-slate-700 dark:text-slate-200">{module}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
