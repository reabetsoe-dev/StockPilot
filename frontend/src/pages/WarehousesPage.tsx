import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { MapPin, Plus, Search, Warehouse } from "lucide-react";
import { FormEvent, useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { FormInput, FormTextarea } from "../components/FormInput";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { useAuth } from "../hooks/useAuth";
import { api } from "../services/api";
import type { Warehouse as WarehouseRecord } from "../types/catalog";
import { getApiErrorMessage } from "../utils/errors";

interface WarehouseFormState {
  code: string;
  name: string;
  location: string;
  description: string;
}

const emptyWarehouseForm: WarehouseFormState = {
  code: "",
  name: "",
  location: "",
  description: "",
};

export function WarehousesPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [form, setForm] = useState<WarehouseFormState>(emptyWarehouseForm);
  const [successMessage, setSuccessMessage] = useState("");
  const canManage = user?.role === "ADMINISTRATOR" || user?.role === "INVENTORY_MANAGER";

  const { data = [], isLoading } = useQuery({
    queryKey: ["warehouses", search],
    queryFn: async () => (await api.get<WarehouseRecord[]>("/warehouses", { params: { search: search || undefined } })).data,
  });

  const createMutation = useMutation({
    mutationFn: async () =>
      (
        await api.post<WarehouseRecord>("/warehouses", {
          code: form.code,
          name: form.name,
          location: form.location,
          description: form.description || null,
          active: true,
        })
      ).data,
    onSuccess: (warehouse) => {
      setSuccessMessage(`${warehouse.code} was added.`);
      setForm(emptyWarehouseForm);
      queryClient.invalidateQueries({ queryKey: ["warehouses"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });

  function updateForm(field: keyof WarehouseFormState, value: string) {
    setSuccessMessage("");
    createMutation.reset();
    setForm((current) => ({ ...current, [field]: value }));
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    createMutation.mutate();
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Warehouse setup"
        title="Warehouses"
        description="Operating locations for receiving, storage, retail fulfillment, transfers, and future stock balances."
        icon={Warehouse}
        meta={`${data.length} warehouses`}
      />

      <section className="grid gap-5 xl:grid-cols-[1fr_340px]">
        <div className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="border-b border-slate-200 p-5 dark:border-slate-800">
            <label className="relative block max-w-xl">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                className="h-11 w-full rounded-lg border border-slate-200 bg-slate-50 pl-10 pr-3 text-sm outline-none transition focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:focus:ring-emerald-950"
                placeholder="Search warehouse, code, or location"
              />
            </label>
          </div>

          {!isLoading && data.length === 0 ? (
            <div className="p-5">
              <EmptyState icon={Warehouse} title="No warehouses found" message="No warehouse records match the current search." />
            </div>
          ) : (
            <div className="grid gap-4 p-5 md:grid-cols-2">
              {data.map((warehouse) => (
                <article key={warehouse.id} className="rounded-lg border border-slate-200 bg-slate-50 p-5 dark:border-slate-800 dark:bg-slate-950">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3">
                      <div className="rounded-lg bg-emerald-50 p-3 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-200">
                        <Warehouse className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="font-mono text-xs font-bold uppercase text-emerald-700 dark:text-emerald-300">{warehouse.code}</p>
                        <h2 className="mt-1 font-bold text-slate-950 dark:text-white">{warehouse.name}</h2>
                        <p className="mt-2 inline-flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
                          <MapPin className="h-4 w-4" />
                          {warehouse.location}
                        </p>
                        <p className="mt-3 text-sm leading-6 text-slate-500 dark:text-slate-400">{warehouse.description}</p>
                      </div>
                    </div>
                    <StatusBadge label={warehouse.active ? "Active" : "Inactive"} tone={warehouse.active ? "emerald" : "slate"} />
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>

        <aside className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-bold uppercase text-emerald-600 dark:text-emerald-300">Warehouse record</p>
              <h2 className="mt-1 text-xl font-bold">New warehouse</h2>
            </div>
            <Plus className="h-6 w-6 text-emerald-600" />
          </div>

          {canManage ? (
            <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
              <FormInput label="Code" value={form.code} onChange={(event) => updateForm("code", event.target.value)} required />
              <FormInput label="Name" value={form.name} onChange={(event) => updateForm("name", event.target.value)} required />
              <FormInput label="Location" value={form.location} onChange={(event) => updateForm("location", event.target.value)} required />
              <FormTextarea label="Description" value={form.description} onChange={(event) => updateForm("description", event.target.value)} />
              {createMutation.isError && (
                <p className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200">
                  {getApiErrorMessage(createMutation.error)}
                </p>
              )}
              {successMessage && (
                <p className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-200">
                  {successMessage}
                </p>
              )}
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 text-sm font-bold text-white shadow-sm transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-400"
              >
                <Plus className="h-4 w-4" />
                {createMutation.isPending ? "Saving" : "Create warehouse"}
              </button>
            </form>
          ) : (
            <div className="mt-5 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300">
              Your role has read-only warehouse access.
            </div>
          )}
        </aside>
      </section>
    </div>
  );
}
