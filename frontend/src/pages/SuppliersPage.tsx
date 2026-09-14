import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Building2, Mail, Phone, Plus, Search, Truck } from "lucide-react";
import { FormEvent, useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { FormInput, FormTextarea } from "../components/FormInput";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { useAuth } from "../hooks/useAuth";
import { api } from "../services/api";
import type { Supplier } from "../types/catalog";
import { getApiErrorMessage } from "../utils/errors";

interface SupplierFormState {
  supplier_code: string;
  name: string;
  contact_person: string;
  email: string;
  phone: string;
  address: string;
  tax_reference: string;
  payment_terms: string;
}

const emptySupplierForm: SupplierFormState = {
  supplier_code: "",
  name: "",
  contact_person: "",
  email: "",
  phone: "",
  address: "",
  tax_reference: "",
  payment_terms: "Net 30",
};

export function SuppliersPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [form, setForm] = useState<SupplierFormState>(emptySupplierForm);
  const [successMessage, setSuccessMessage] = useState("");
  const canManage = user?.role === "ADMINISTRATOR" || user?.role === "PROCUREMENT_OFFICER";

  const { data = [], isLoading } = useQuery({
    queryKey: ["suppliers", search],
    queryFn: async () => (await api.get<Supplier[]>("/suppliers", { params: { search: search || undefined } })).data,
  });

  const createMutation = useMutation({
    mutationFn: async () =>
      (
        await api.post<Supplier>("/suppliers", {
          supplier_code: form.supplier_code,
          name: form.name,
          contact_person: form.contact_person,
          email: form.email || null,
          phone: form.phone || null,
          address: form.address || null,
          tax_reference: form.tax_reference || null,
          payment_terms: form.payment_terms || null,
          active: true,
        })
      ).data,
    onSuccess: (supplier) => {
      setSuccessMessage(`${supplier.supplier_code} was added.`);
      setForm(emptySupplierForm);
      queryClient.invalidateQueries({ queryKey: ["suppliers"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });

  function updateForm(field: keyof SupplierFormState, value: string) {
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
        eyebrow="Procurement setup"
        title="Suppliers"
        description="Supplier records for preferred sourcing, payment terms, purchasing accountability, and product ownership."
        icon={Truck}
        meta={`${data.length} suppliers`}
      />

      <section className="grid gap-5 xl:grid-cols-[1fr_360px]">
        <div className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="border-b border-slate-200 p-5 dark:border-slate-800">
            <label className="relative block max-w-xl">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                className="h-11 w-full rounded-lg border border-slate-200 bg-slate-50 pl-10 pr-3 text-sm outline-none transition focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:focus:ring-emerald-950"
                placeholder="Search supplier, code, or contact"
              />
            </label>
          </div>

          {!isLoading && data.length === 0 ? (
            <div className="p-5">
              <EmptyState icon={Truck} title="No suppliers found" message="No supplier records match the current search." />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
                <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500 dark:bg-slate-950 dark:text-slate-400">
                  <tr>
                    <th className="px-5 py-3">Supplier</th>
                    <th className="px-5 py-3">Code</th>
                    <th className="px-5 py-3">Contact</th>
                    <th className="px-5 py-3">Payment</th>
                    <th className="px-5 py-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                  {data.map((supplier) => (
                    <tr key={supplier.id} className="align-top">
                      <td className="px-5 py-4">
                        <p className="font-semibold text-slate-950 dark:text-white">{supplier.name}</p>
                        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{supplier.address}</p>
                      </td>
                      <td className="px-5 py-4 font-mono text-sm font-semibold">{supplier.supplier_code}</td>
                      <td className="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">
                        <p className="font-semibold text-slate-800 dark:text-slate-100">{supplier.contact_person}</p>
                        <p className="mt-1 inline-flex items-center gap-2">
                          <Mail className="h-4 w-4" />
                          {supplier.email ?? "No email"}
                        </p>
                        <p className="mt-1 inline-flex items-center gap-2">
                          <Phone className="h-4 w-4" />
                          {supplier.phone ?? "No phone"}
                        </p>
                      </td>
                      <td className="px-5 py-4 text-sm font-semibold">{supplier.payment_terms ?? "-"}</td>
                      <td className="px-5 py-4">
                        <StatusBadge label={supplier.active ? "Active" : "Inactive"} tone={supplier.active ? "emerald" : "slate"} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <aside className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-bold uppercase text-emerald-600 dark:text-emerald-300">Supplier record</p>
              <h2 className="mt-1 text-xl font-bold">New supplier</h2>
            </div>
            <Building2 className="h-6 w-6 text-emerald-600" />
          </div>

          {canManage ? (
            <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-1">
                <FormInput label="Code" value={form.supplier_code} onChange={(event) => updateForm("supplier_code", event.target.value)} required />
                <FormInput label="Name" value={form.name} onChange={(event) => updateForm("name", event.target.value)} required />
              </div>
              <FormInput label="Contact person" value={form.contact_person} onChange={(event) => updateForm("contact_person", event.target.value)} required />
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-1">
                <FormInput label="Email" type="email" value={form.email} onChange={(event) => updateForm("email", event.target.value)} />
                <FormInput label="Phone" value={form.phone} onChange={(event) => updateForm("phone", event.target.value)} />
                <FormInput label="Tax reference" value={form.tax_reference} onChange={(event) => updateForm("tax_reference", event.target.value)} />
                <FormInput label="Payment terms" value={form.payment_terms} onChange={(event) => updateForm("payment_terms", event.target.value)} />
              </div>
              <FormTextarea label="Address" value={form.address} onChange={(event) => updateForm("address", event.target.value)} />
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
                {createMutation.isPending ? "Saving" : "Create supplier"}
              </button>
            </form>
          ) : (
            <div className="mt-5 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300">
              Your role has read-only supplier access.
            </div>
          )}
        </aside>
      </section>
    </div>
  );
}
