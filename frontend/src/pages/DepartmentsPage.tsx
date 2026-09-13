import { useQuery } from "@tanstack/react-query";
import { Building2 } from "lucide-react";

import { EmptyState } from "../components/EmptyState";
import { api } from "../services/api";
import type { Department } from "../types/auth";

export function DepartmentsPage() {
  const { data = [], isLoading } = useQuery({
    queryKey: ["departments"],
    queryFn: async () => (await api.get<Department[]>("/departments")).data,
  });

  if (!isLoading && data.length === 0) {
    return <EmptyState icon={Building2} title="No departments found" message="Seeded departments will appear here after setup." />;
  }

  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm font-bold uppercase text-emerald-600">Organization</p>
        <h1 className="mt-2 text-3xl font-bold">Departments</h1>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {data.map((department) => (
          <article key={department.id} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <div className="flex items-start gap-3">
              <div className="rounded-lg bg-emerald-50 p-3 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-200">
                <Building2 className="h-5 w-5" />
              </div>
              <div>
                <h2 className="font-bold">{department.name}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">{department.description}</p>
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
