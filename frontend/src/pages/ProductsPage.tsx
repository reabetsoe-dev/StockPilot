import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Boxes, PackagePlus, Search, Tags, Truck } from "lucide-react";
import { FormEvent, useMemo, useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { FormInput, FormSelect, FormTextarea } from "../components/FormInput";
import { PageHeader } from "../components/PageHeader";
import { StatCard } from "../components/StatCard";
import { StatusBadge } from "../components/StatusBadge";
import { useAuth } from "../hooks/useAuth";
import { api } from "../services/api";
import type { Category, Product, Supplier } from "../types/catalog";
import { getApiErrorMessage } from "../utils/errors";
import { formatMoney } from "../utils/format";

interface ProductFormState {
  sku: string;
  barcode: string;
  name: string;
  description: string;
  category_id: string;
  unit_of_measure: string;
  cost_price: string;
  selling_price: string;
  reorder_level: string;
  preferred_supplier_id: string;
}

const emptyProductForm: ProductFormState = {
  sku: "",
  barcode: "",
  name: "",
  description: "",
  category_id: "",
  unit_of_measure: "Each",
  cost_price: "",
  selling_price: "",
  reorder_level: "0",
  preferred_supplier_id: "",
};

export function ProductsPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [categoryId, setCategoryId] = useState("all");
  const [supplierId, setSupplierId] = useState("all");
  const [activeFilter, setActiveFilter] = useState("true");
  const [form, setForm] = useState<ProductFormState>(emptyProductForm);
  const [successMessage, setSuccessMessage] = useState("");
  const canManage = user?.role === "ADMINISTRATOR" || user?.role === "INVENTORY_MANAGER";

  const { data: categories = [] } = useQuery({
    queryKey: ["categories"],
    queryFn: async () => (await api.get<Category[]>("/categories")).data,
  });
  const { data: suppliers = [] } = useQuery({
    queryKey: ["suppliers"],
    queryFn: async () => (await api.get<Supplier[]>("/suppliers")).data,
  });
  const { data: products = [], isLoading } = useQuery({
    queryKey: ["products", search, categoryId, supplierId, activeFilter],
    queryFn: async () =>
      (
        await api.get<Product[]>("/products", {
          params: {
            search: search || undefined,
            category_id: categoryId === "all" ? undefined : Number(categoryId),
            supplier_id: supplierId === "all" ? undefined : Number(supplierId),
            active: activeFilter === "all" ? undefined : activeFilter === "true",
          },
        })
      ).data,
  });

  const catalogStats = useMemo(() => {
    const activeProducts = products.filter((product) => product.active).length;
    const avgReorder =
      products.length === 0
        ? 0
        : Math.round(products.reduce((total, product) => total + product.reorder_level, 0) / products.length);
    return {
      products: products.length,
      activeProducts,
      categories: categories.length,
      suppliers: suppliers.length,
      avgReorder,
    };
  }, [categories.length, products, suppliers.length]);

  const createMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        sku: form.sku,
        barcode: form.barcode || null,
        name: form.name,
        description: form.description || null,
        category_id: Number(form.category_id),
        unit_of_measure: form.unit_of_measure,
        cost_price: form.cost_price,
        selling_price: form.selling_price,
        reorder_level: Number(form.reorder_level),
        preferred_supplier_id: form.preferred_supplier_id ? Number(form.preferred_supplier_id) : null,
        active: true,
      };
      return (await api.post<Product>("/products", payload)).data;
    },
    onSuccess: (product) => {
      setSuccessMessage(`${product.sku} was added to the catalog.`);
      setForm(emptyProductForm);
      queryClient.invalidateQueries({ queryKey: ["products"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });

  function updateForm(field: keyof ProductFormState, value: string) {
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
        eyebrow="Catalog control"
        title="Products"
        description="Central SKU records, pricing, categories, reorder controls, and supplier ownership for the operating catalog."
        icon={PackagePlus}
        meta={`${catalogStats.products} products`}
      />

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Products" value={isLoading ? "..." : catalogStats.products} tone="emerald" icon={Boxes} />
        <StatCard label="Active products" value={isLoading ? "..." : catalogStats.activeProducts} tone="blue" icon={PackagePlus} />
        <StatCard label="Categories" value={catalogStats.categories} tone="amber" icon={Tags} />
        <StatCard label="Preferred suppliers" value={catalogStats.suppliers} tone="slate" icon={Truck} />
      </section>

      <section className="grid gap-5 xl:grid-cols-[1fr_360px]">
        <div className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="grid gap-3 border-b border-slate-200 p-5 dark:border-slate-800 lg:grid-cols-[1fr_220px_220px_160px]">
            <label className="relative block">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                className="h-11 w-full rounded-lg border border-slate-200 bg-slate-50 pl-10 pr-3 text-sm outline-none transition focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:focus:ring-emerald-950"
                placeholder="Search name, SKU, or barcode"
              />
            </label>
            <FormSelect label="Category" value={categoryId} onChange={(event) => setCategoryId(event.target.value)}>
              <option value="all">All categories</option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </FormSelect>
            <FormSelect label="Supplier" value={supplierId} onChange={(event) => setSupplierId(event.target.value)}>
              <option value="all">All suppliers</option>
              {suppliers.map((supplier) => (
                <option key={supplier.id} value={supplier.id}>
                  {supplier.name}
                </option>
              ))}
            </FormSelect>
            <FormSelect label="Status" value={activeFilter} onChange={(event) => setActiveFilter(event.target.value)}>
              <option value="true">Active</option>
              <option value="false">Inactive</option>
              <option value="all">All statuses</option>
            </FormSelect>
          </div>

          {!isLoading && products.length === 0 ? (
            <div className="p-5">
              <EmptyState icon={Boxes} title="No products found" message="No catalog records match the selected filters." />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
                <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500 dark:bg-slate-950 dark:text-slate-400">
                  <tr>
                    <th className="px-5 py-3">SKU</th>
                    <th className="px-5 py-3">Product</th>
                    <th className="px-5 py-3">Category</th>
                    <th className="px-5 py-3">Supplier</th>
                    <th className="px-5 py-3">Cost</th>
                    <th className="px-5 py-3">Selling</th>
                    <th className="px-5 py-3">Reorder</th>
                    <th className="px-5 py-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                  {products.map((product) => (
                    <tr key={product.id} className="align-top">
                      <td className="px-5 py-4 font-mono text-sm font-semibold text-slate-900 dark:text-white">{product.sku}</td>
                      <td className="px-5 py-4">
                        <p className="font-semibold text-slate-950 dark:text-white">{product.name}</p>
                        <p className="mt-1 max-w-md text-sm leading-5 text-slate-500 dark:text-slate-400">{product.description}</p>
                      </td>
                      <td className="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{product.category.name}</td>
                      <td className="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">
                        {product.preferred_supplier?.name ?? "Unassigned"}
                      </td>
                      <td className="px-5 py-4 text-sm font-semibold">{formatMoney(product.cost_price)}</td>
                      <td className="px-5 py-4 text-sm font-semibold">{formatMoney(product.selling_price)}</td>
                      <td className="px-5 py-4 text-sm">{product.reorder_level} {product.unit_of_measure}</td>
                      <td className="px-5 py-4">
                        <StatusBadge label={product.active ? "Active" : "Inactive"} tone={product.active ? "emerald" : "slate"} />
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
              <p className="text-sm font-bold uppercase text-emerald-600 dark:text-emerald-300">Product record</p>
              <h2 className="mt-1 text-xl font-bold">New product</h2>
            </div>
            <PackagePlus className="h-6 w-6 text-emerald-600" />
          </div>

          {canManage ? (
            <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
              <FormInput label="SKU" value={form.sku} onChange={(event) => updateForm("sku", event.target.value)} required />
              <FormInput label="Name" value={form.name} onChange={(event) => updateForm("name", event.target.value)} required />
              <FormInput label="Barcode" value={form.barcode} onChange={(event) => updateForm("barcode", event.target.value)} />
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-1">
                <FormSelect label="Category" value={form.category_id} onChange={(event) => updateForm("category_id", event.target.value)} required>
                  <option value="">Select category</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </FormSelect>
                <FormSelect
                  label="Supplier"
                  value={form.preferred_supplier_id}
                  onChange={(event) => updateForm("preferred_supplier_id", event.target.value)}
                >
                  <option value="">No preferred supplier</option>
                  {suppliers.map((supplier) => (
                    <option key={supplier.id} value={supplier.id}>
                      {supplier.name}
                    </option>
                  ))}
                </FormSelect>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <FormInput label="Unit" value={form.unit_of_measure} onChange={(event) => updateForm("unit_of_measure", event.target.value)} required />
                <FormInput
                  label="Reorder"
                  type="number"
                  min="0"
                  value={form.reorder_level}
                  onChange={(event) => updateForm("reorder_level", event.target.value)}
                  required
                />
                <FormInput
                  label="Cost price"
                  type="number"
                  min="0"
                  step="0.01"
                  value={form.cost_price}
                  onChange={(event) => updateForm("cost_price", event.target.value)}
                  required
                />
                <FormInput
                  label="Selling price"
                  type="number"
                  min="0"
                  step="0.01"
                  value={form.selling_price}
                  onChange={(event) => updateForm("selling_price", event.target.value)}
                  required
                />
              </div>
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
                <PackagePlus className="h-4 w-4" />
                {createMutation.isPending ? "Saving" : "Create product"}
              </button>
            </form>
          ) : (
            <div className="mt-5 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300">
              Your role has read-only catalog access.
            </div>
          )}
        </aside>
      </section>
    </div>
  );
}
