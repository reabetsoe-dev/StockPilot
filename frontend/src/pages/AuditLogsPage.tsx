import { useQuery } from "@tanstack/react-query";
import { FileClock, Search } from "lucide-react";
import { FormEvent, useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { api } from "../services/api";
import type { AuditLog } from "../types/operations";
import { formatDateTime } from "../utils/format";

export function AuditLogsPage() {
  const [searchDraft, setSearchDraft] = useState("");
  const [search, setSearch] = useState("");
  const { data = [], isLoading } = useQuery({
    queryKey: ["audit-logs", search],
    queryFn: async () => (await api.get<AuditLog[]>("/audit-logs", { params: { search: search || undefined } })).data,
  });

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSearch(searchDraft.trim());
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Accountability"
        title="Audit Logs"
        description="Immutable operational history for authentication, master data, procurement actions, receiving, stock issues, transfers, and adjustments."
        icon={FileClock}
        meta={`${data.length} recent logs`}
      />

      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <form className="flex flex-col gap-3 md:flex-row" onSubmit={submitSearch}>
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
            <input
              value={searchDraft}
              onChange={(event) => setSearchDraft(event.target.value)}
              className="h-11 w-full rounded-lg border border-slate-200 bg-white pl-12 pr-4 text-sm outline-none transition placeholder:text-slate-400 focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:focus:ring-emerald-950"
              placeholder="Search actions, entities, descriptions"
            />
          </div>
          <button type="submit" className="inline-flex h-11 items-center justify-center rounded-lg bg-emerald-600 px-4 text-sm font-bold text-white hover:bg-emerald-700">
            Search
          </button>
        </form>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        {!isLoading && data.length === 0 ? (
          <div className="p-5">
            <EmptyState icon={FileClock} title="No audit logs found" message="Try another search term or seed the demo data." />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
              <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500 dark:bg-slate-950 dark:text-slate-400">
                <tr>
                  <th className="px-5 py-3">Time</th>
                  <th className="px-5 py-3">Action</th>
                  <th className="px-5 py-3">Entity</th>
                  <th className="px-5 py-3">User</th>
                  <th className="px-5 py-3">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                {data.map((log) => (
                  <tr key={log.id}>
                    <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{formatDateTime(log.created_at)}</td>
                    <td className="px-5 py-4">
                      <StatusBadge label={log.action} tone="blue" />
                    </td>
                    <td className="px-5 py-4 text-sm">
                      <span className="font-semibold">{log.entity_type}</span>
                      {log.entity_id && <span className="ml-2 font-mono text-xs text-slate-500 dark:text-slate-400">{log.entity_id}</span>}
                    </td>
                    <td className="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{log.user_name ?? "System"}</td>
                    <td className="max-w-xl px-5 py-4 text-sm leading-6 text-slate-600 dark:text-slate-300">{log.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
