import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, ShoppingCart } from "lucide-react";
import { Link } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { api } from "../services/api";
import type { LowStockItem } from "../types/inventory";
import { formatMoney } from "../utils/format";
import { stockStatusLabel, stockStatusTone } from "../utils/inventory";

export function LowStockPage() {
  const { data = [], isLoading } = useQuery({
    queryKey: ["low-stock"],
    queryFn: async () => (await api.get<LowStockItem[]>("/low-stock")).data,
  });

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Reorder control"
        title="Low Stock"
        description="Deterministic reorder suggestions based on backend-calculated available quantity and each product's reorder level."
        icon={AlertTriangle}
        meta={`${data.length} watch items`}
      />

      <section className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        {!isLoading && data.length === 0 ? (
          <div className="p-5">
            <EmptyState icon={AlertTriangle} title="No low-stock items" message="All products are above their reorder thresholds." />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
              <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500 dark:bg-slate-950 dark:text-slate-400">
                <tr>
                  <th className="px-5 py-3">Product</th>
                  <th className="px-5 py-3">Available</th>
                  <th className="px-5 py-3">Reorder</th>
                  <th className="px-5 py-3">Suggested reorder</th>
                  <th className="px-5 py-3">Supplier</th>
                  <th className="px-5 py-3">Value</th>
                  <th className="px-5 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                {data.map((item) => (
                  <tr key={item.product_id}>
                    <td className="px-5 py-4">
                      <Link to={`/inventory/${item.product_id}`} className="font-semibold text-slate-950 hover:text-emerald-700 dark:text-white dark:hover:text-emerald-200">
                        {item.product_name}
                      </Link>
                      <p className="mt-1 font-mono text-xs text-slate-500 dark:text-slate-400">{item.sku}</p>
                    </td>
                    <td className="px-5 py-4 text-sm font-semibold">{item.available_quantity}</td>
                    <td className="px-5 py-4 text-sm">{item.reorder_level}</td>
                    <td className="px-5 py-4 text-sm font-bold text-emerald-700 dark:text-emerald-200">
                      {item.suggested_reorder_quantity}
                    </td>
                    <td className="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{item.preferred_supplier_name ?? "Unassigned"}</td>
                    <td className="px-5 py-4 text-sm font-semibold">{formatMoney(item.inventory_value)}</td>
                    <td className="px-5 py-4">
                      <StatusBadge label={stockStatusLabel(item.stock_status)} tone={stockStatusTone(item.stock_status)} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <Link to="/purchase-orders" className="inline-flex h-11 items-center gap-2 rounded-lg bg-emerald-600 px-4 text-sm font-bold text-white shadow-sm hover:bg-emerald-700">
        <ShoppingCart className="h-4 w-4" />
        Review procurement
      </Link>
    </div>
  );
}
