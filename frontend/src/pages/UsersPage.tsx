import { useQuery } from "@tanstack/react-query";
import { Users } from "lucide-react";

import { EmptyState } from "../components/EmptyState";
import { RoleBadge } from "../components/RoleBadge";
import { api } from "../services/api";
import type { User } from "../types/auth";

export function UsersPage() {
  const { data = [], isLoading } = useQuery({
    queryKey: ["users"],
    queryFn: async () => (await api.get<User[]>("/users")).data,
  });

  if (!isLoading && data.length === 0) {
    return <EmptyState icon={Users} title="No users found" message="Seeded users will appear here after the backend is initialized." />;
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="border-b border-slate-200 p-5 dark:border-slate-800">
        <p className="text-sm font-bold uppercase text-emerald-600">Administration</p>
        <h1 className="mt-2 text-2xl font-bold">Users</h1>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
          <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500 dark:bg-slate-950 dark:text-slate-400">
            <tr>
              <th className="px-5 py-3">Name</th>
              <th className="px-5 py-3">Email</th>
              <th className="px-5 py-3">Role</th>
              <th className="px-5 py-3">Department</th>
              <th className="px-5 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
            {data.map((user) => (
              <tr key={user.id}>
                <td className="px-5 py-4 font-semibold">{user.full_name}</td>
                <td className="px-5 py-4 text-slate-600 dark:text-slate-300">{user.email}</td>
                <td className="px-5 py-4"><RoleBadge role={user.role} /></td>
                <td className="px-5 py-4 text-slate-600 dark:text-slate-300">{user.department?.name ?? "-"}</td>
                <td className="px-5 py-4 text-sm font-semibold text-emerald-700">{user.active ? "Active" : "Inactive"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
