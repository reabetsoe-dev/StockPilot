import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Boxes, ClipboardList, PackageCheck, PackageX, ShieldCheck, Warehouse } from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { StatCard } from "../components/StatCard";
import { StatusBadge } from "../components/StatusBadge";
import { api } from "../services/api";
import type { ProductInventoryDetail } from "../types/inventory";
import { formatDateTime, formatMoney } from "../utils/format";
import { movementLabel, stockStatusLabel, stockStatusTone } from "../utils/inventory";

export function ProductStockDetailsPage() {
  const { productId } = useParams();
  const { data, isLoading } = useQuery({
    queryKey: ["inventory-detail", productId],
    queryFn: async () => (await api.get<ProductInventoryDetail>(`/inventory/${productId}`)).data,
    enabled: Boolean(productId),
  });

  if (!data && !isLoading) {
    return <EmptyState icon={PackageX} title="Product not found" message="The selected inventory record could not be loaded." />;
  }

  if (!data) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-6 text-sm font-semibold text-slate-600 shadow-sm dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300">
        Loading product stock details
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Link
        to="/inventory"
        className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 transition hover:text-emerald-700 dark:text-slate-300 dark:hover:text-emerald-200"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to inventory
      </Link>

      <PageHeader
        eyebrow={data.product.sku}
        title={data.product.name}
        description={data.product.description ?? "Product stock detail, warehouse balances, valuation, and ledger history."}
        icon={PackageCheck}
        meta={stockStatusLabel(data.stock_status)}
      />

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="On hand" value={data.total_on_hand} tone="emerald" icon={Boxes} />
        <StatCard label="Available" value={data.available_quantity} tone="blue" icon={PackageCheck} />
        <StatCard label="Reserved" value={data.total_reserved} tone="amber" icon={ShieldCheck} />
        <StatCard label="Inventory value" value={formatMoney(data.inventory_value)} tone="slate" icon={Warehouse} />
      </section>

      <section className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-bold uppercase text-emerald-600 dark:text-emerald-300">Warehouse balances</p>
              <h2 className="mt-1 text-xl font-bold">Stock by location</h2>
            </div>
            <StatusBadge label={stockStatusLabel(data.stock_status)} tone={stockStatusTone(data.stock_status)} />
          </div>

          <div className="mt-5 overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
              <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500 dark:bg-slate-950 dark:text-slate-400">
                <tr>
                  <th className="px-4 py-3">Warehouse</th>
                  <th className="px-4 py-3">On hand</th>
                  <th className="px-4 py-3">Reserved</th>
                  <th className="px-4 py-3">Available</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                {data.balances.map((balance) => (
                  <tr key={balance.id}>
                    <td className="px-4 py-4">
                      <p className="font-semibold">{balance.warehouse.name}</p>
                      <p className="mt-1 font-mono text-xs text-slate-500 dark:text-slate-400">{balance.warehouse.code}</p>
                    </td>
                    <td className="px-4 py-4 text-sm font-semibold">{balance.quantity_on_hand}</td>
                    <td className="px-4 py-4 text-sm">{balance.quantity_reserved}</td>
                    <td className="px-4 py-4 text-sm font-semibold">{balance.available_quantity}</td>
                    <td className="px-4 py-4">
                      <StatusBadge label={stockStatusLabel(balance.stock_status)} tone={stockStatusTone(balance.stock_status)} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <p className="text-sm font-bold uppercase text-emerald-600 dark:text-emerald-300">Product information</p>
          <dl className="mt-5 grid gap-4 sm:grid-cols-2">
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950">
              <dt className="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">Category</dt>
              <dd className="mt-2 font-semibold">{data.product.category.name}</dd>
            </div>
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950">
              <dt className="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">Preferred supplier</dt>
              <dd className="mt-2 font-semibold">{data.product.preferred_supplier?.name ?? "Unassigned"}</dd>
            </div>
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950">
              <dt className="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">Cost price</dt>
              <dd className="mt-2 font-semibold">{formatMoney(data.product.cost_price)}</dd>
            </div>
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950">
              <dt className="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">Reorder level</dt>
              <dd className="mt-2 font-semibold">{data.product.reorder_level} {data.product.unit_of_measure}</dd>
            </div>
          </dl>
        </div>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="border-b border-slate-200 p-5 dark:border-slate-800">
          <div className="flex items-center gap-3">
            <ClipboardList className="h-5 w-5 text-emerald-600" />
            <div>
              <p className="text-sm font-bold uppercase text-emerald-600 dark:text-emerald-300">Stock ledger</p>
              <h2 className="mt-1 text-xl font-bold">Recent movements</h2>
            </div>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
            <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500 dark:bg-slate-950 dark:text-slate-400">
              <tr>
                <th className="px-5 py-3">Date</th>
                <th className="px-5 py-3">Movement</th>
                <th className="px-5 py-3">Warehouse</th>
                <th className="px-5 py-3">Quantity</th>
                <th className="px-5 py-3">Reference</th>
                <th className="px-5 py-3">Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
              {data.recent_movements.map((movement) => (
                <tr key={movement.id}>
                  <td className="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{formatDateTime(movement.created_at)}</td>
                  <td className="px-5 py-4 text-sm font-semibold">{movementLabel(movement.movement_type)}</td>
                  <td className="px-5 py-4 text-sm">{movement.warehouse_name}</td>
                  <td className={`px-5 py-4 text-sm font-bold ${movement.quantity < 0 ? "text-rose-600" : "text-emerald-600"}`}>
                    {movement.quantity > 0 ? "+" : ""}
                    {movement.quantity}
                  </td>
                  <td className="px-5 py-4 font-mono text-xs text-slate-500 dark:text-slate-400">{movement.reference_id ?? "-"}</td>
                  <td className="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{movement.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
