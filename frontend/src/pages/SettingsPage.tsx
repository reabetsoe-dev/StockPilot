import { useQuery } from "@tanstack/react-query";
import { Building2, Database, KeyRound, Settings, ShieldCheck } from "lucide-react";

import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { api } from "../services/api";
import type { DashboardSummary } from "../types/dashboard";

const settings = [
  { label: "Authentication", value: "JWT access tokens", icon: KeyRound },
  { label: "Authorization", value: "Backend role checks", icon: ShieldCheck },
  { label: "Local database", value: "SQLite", icon: Database },
  { label: "Production database", value: "Turso/libSQL-ready", icon: Database },
];

export function SettingsPage() {
  const { data } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: async () => (await api.get<DashboardSummary>("/dashboard/summary")).data,
  });

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Administration"
        title="Settings"
        description="System configuration overview for the demo organization, security model, local development database, and production deployment readiness."
        icon={Settings}
        meta="Administrator"
      />

      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-start gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-200">
            <Building2 className="h-6 w-6" />
          </div>
          <div>
            <p className="text-sm font-bold uppercase text-emerald-600 dark:text-emerald-300">Organization</p>
            <h2 className="mt-1 text-2xl font-bold text-slate-950 dark:text-white">{data?.organization ?? "StockPilot Distribution Ltd"}</h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600 dark:text-slate-300">
              The demo environment is seeded from backend fixtures so portfolio reviewers can reset the same fictional organization, roles, catalog, stock ledger, procurement flows, and audit history.
            </p>
          </div>
        </div>
      </section>

      <section className="grid gap-5 md:grid-cols-2">
        {settings.map((item) => {
          const Icon = item.icon;
          return (
            <article key={item.label} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-bold text-slate-500 dark:text-slate-400">{item.label}</p>
                  <h3 className="mt-2 text-xl font-bold text-slate-950 dark:text-white">{item.value}</h3>
                </div>
                <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200">
                  <Icon className="h-5 w-5" />
                </div>
              </div>
              <div className="mt-4">
                <StatusBadge label="Configured" tone="emerald" />
              </div>
            </article>
          );
        })}
      </section>
    </div>
  );
}
