import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Boxes, Eye, PackageCheck, PackageX, Search, Warehouse } from "lucide-react";
import { Link } from "react-router-dom";
import { useMemo, useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { FormSelect } from "../components/FormInput";
import { PageHeader } from "../components/PageHeader";
import { StatCard } from "../components/StatCard";
import { StatusBadge } from "../components/StatusBadge";
import { api } from "../services/api";
import type { Category, Supplier, Warehouse as WarehouseRecord } from "../types/catalog";
import type { InventoryItem, StockStatus } from "../types/inventory";
import { formatMoney } from "../utils/format";
import { stockStatusLabel, stockStatusTone } from "../utils/inventory";

export function InventoryPage() {
  const [search, setSearch] = useState("");
  const [warehouseId, setWarehouseId] = useState("all");
  const [categoryId, setCategoryId] = useState("all");
  const [supplierId, setSupplierId] = useState("all");
  const [stockStatus, setStockStatus] = useState("all");

  const { data: warehouses = [] } = useQuery({
    queryKey: ["warehouses"],
    queryFn: async () => (await api.get<WarehouseRecord[]>("/warehouses")).data,
  });
  const { data: categories = [] } = useQuery({
    queryKey: ["categories"],
    queryFn: async () => (await api.get<Category[]>("/categories")).data,
  });
  const { data: suppliers = [] } = useQuery({
    queryKey: ["suppliers"],
    queryFn: async () => (await api.get<Supplier[]>("/suppliers")).data,
  });
  const { data: inventory = [], isLoading } = useQuery({
    queryKey: ["inventory", search, warehouseId, categoryId, supplierId, stockStatus],
    queryFn: async () =>
      (
        await api.get<InventoryItem[]>("/inventory", {
          params: {
            search: search || undefined,
            warehouse_id: warehouseId === "all" ? undefined : Number(warehouseId),
            category_id: categoryId === "all" ? undefined : Number(categoryId),
            supplier_id: supplierId === "all" ? undefined : Number(supplierId),
            stock_status: stockStatus === "all" ? undefined : stockStatus,
          },
        })
      ).data,
  });

  const stats = useMemo(() => {
    return {
      items: inventory.length,
      value: inventory.reduce((total, item) => total + Number(item.inventory_value), 0),
      low: inventory.filter((item) => item.stock_status === "LOW_STOCK").length,
      out: inventory.filter((item) => item.stock_status === "OUT_OF_STOCK").length,
    };
  }, [inventory]);

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Inventory control"
        title="Inventory"
        description="Backend-calculated stock positions, reserved quantities, valuation, and reorder status across operating warehouses."
        icon={PackageCheck}
        meta={`${stats.items} stock records`}
      />

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Products tracked" value={isLoading ? "..." : stats.items} tone="emerald" icon={Boxes} />
        <StatCard label="Inventory value" value={isLoading ? "..." : formatMoney(stats.value)} tone="blue" icon={PackageCheck} />
        <StatCard label="Low stock" value={isLoading ? "..." : stats.low} tone="amber" icon={AlertTriangle} />
        <StatCard label="Out of stock" value={isLoading ? "..." : stats.out} tone="slate" icon={PackageX} />
      </section>

      <section className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="grid gap-3 border-b border-slate-200 p-5 dark:border-slate-800 lg:grid-cols-[1fr_180px_190px_210px_180px]">
          <label className="relative block">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              className="h-11 w-full rounded-lg border border-slate-200 bg-slate-50 pl-10 pr-3 text-sm outline-none transition focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:focus:ring-emerald-950"
              placeholder="Search product, SKU, or barcode"
            />
          </label>
          <FormSelect label="Warehouse" value={warehouseId} onChange={(event) => setWarehouseId(event.target.value)}>
            <option value="all">All warehouses</option>
            {warehouses.map((warehouse) => (
              <option key={warehouse.id} value={warehouse.id}>
                {warehouse.name}
              </option>
            ))}
          </FormSelect>
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
          <FormSelect label="Stock status" value={stockStatus} onChange={(event) => setStockStatus(event.target.value)}>
            <option value="all">All statuses</option>
            <option value="NORMAL">Normal</option>
            <option value="LOW_STOCK">Low stock</option>
            <option value="OUT_OF_STOCK">Out of stock</option>
          </FormSelect>
        </div>

        {!isLoading && inventory.length === 0 ? (
          <div className="p-5">
            <EmptyState icon={Warehouse} title="No inventory found" message="No stock records match the selected filters." />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
              <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500 dark:bg-slate-950 dark:text-slate-400">
                <tr>
                  <th className="px-5 py-3">SKU</th>
                  <th className="px-5 py-3">Product</th>
                  <th className="px-5 py-3">Category</th>
                  <th className="px-5 py-3">On hand</th>
                  <th className="px-5 py-3">Available</th>
                  <th className="px-5 py-3">Reorder</th>
                  <th className="px-5 py-3">Value</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                {inventory.map((item) => (
                  <tr key={item.product_id} className="align-top">
                    <td className="px-5 py-4 font-mono text-sm font-semibold text-slate-900 dark:text-white">{item.sku}</td>
                    <td className="px-5 py-4">
                      <p className="font-semibold text-slate-950 dark:text-white">{item.product_name}</p>
                      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                        {item.preferred_supplier_name ?? "No preferred supplier"} - {item.warehouse_count} stocked locations
                      </p>
                    </td>
                    <td className="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{item.category_name}</td>
                    <td className="px-5 py-4 text-sm font-semibold">{item.total_on_hand} {item.unit_of_measure}</td>
                    <td className="px-5 py-4 text-sm font-semibold">{item.available_quantity} {item.unit_of_measure}</td>
                    <td className="px-5 py-4 text-sm">{item.reorder_level}</td>
                    <td className="px-5 py-4 text-sm font-semibold">{formatMoney(item.inventory_value)}</td>
                    <td className="px-5 py-4">
                      <StatusBadge label={stockStatusLabel(item.stock_status)} tone={stockStatusTone(item.stock_status as StockStatus)} />
                    </td>
                    <td className="px-5 py-4">
                      <Link
                        to={`/inventory/${item.product_id}`}
                        className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-700 transition hover:border-emerald-300 hover:text-emerald-700 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-200"
                        aria-label={`View stock details for ${item.product_name}`}
                      >
                        <Eye className="h-5 w-5" />
                      </Link>
                    </td>
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
