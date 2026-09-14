import { useQuery } from "@tanstack/react-query";
import { ClipboardList, Search } from "lucide-react";
import { useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { FormSelect } from "../components/FormInput";
import { PageHeader } from "../components/PageHeader";
import { api } from "../services/api";
import type { Warehouse } from "../types/catalog";
import type { StockMovement, StockMovementType } from "../types/inventory";
import { formatDateTime } from "../utils/format";
import { movementLabel } from "../utils/inventory";

const movementTypes: StockMovementType[] = [
  "OPENING_BALANCE",
  "GOODS_RECEIPT",
  "STOCK_ISSUE",
  "TRANSFER_OUT",
  "TRANSFER_IN",
  "ADJUSTMENT_INCREASE",
  "ADJUSTMENT_DECREASE",
  "RETURN",
];

export function StockMovementsPage() {
  const [search, setSearch] = useState("");
  const [warehouseId, setWarehouseId] = useState("all");
  const [movementType, setMovementType] = useState("all");

  const { data: warehouses = [] } = useQuery({
    queryKey: ["warehouses"],
    queryFn: async () => (await api.get<Warehouse[]>("/warehouses")).data,
  });
  const { data = [], isLoading } = useQuery({
    queryKey: ["stock-movements", search, warehouseId, movementType],
    queryFn: async () =>
      (
        await api.get<StockMovement[]>("/stock-movements", {
          params: {
            search: search || undefined,
            warehouse_id: warehouseId === "all" ? undefined : Number(warehouseId),
            movement_type: movementType === "all" ? undefined : movementType,
            limit: 100,
          },
        })
      ).data,
  });

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Stock ledger"
        title="Stock Movements"
        description="Traceable stock history for opening balances and every future goods receipt, issue, transfer, return, or adjustment."
        icon={ClipboardList}
        meta={`${data.length} movements`}
      />

      <section className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="grid gap-3 border-b border-slate-200 p-5 dark:border-slate-800 lg:grid-cols-[1fr_220px_220px]">
          <label className="relative block">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              className="h-11 w-full rounded-lg border border-slate-200 bg-slate-50 pl-10 pr-3 text-sm outline-none transition focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:focus:ring-emerald-950"
              placeholder="Search product, SKU, warehouse, reference"
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
          <FormSelect label="Movement" value={movementType} onChange={(event) => setMovementType(event.target.value)}>
            <option value="all">All movements</option>
            {movementTypes.map((type) => (
              <option key={type} value={type}>
                {movementLabel(type)}
              </option>
            ))}
          </FormSelect>
        </div>

        {!isLoading && data.length === 0 ? (
          <div className="p-5">
            <EmptyState icon={ClipboardList} title="No movements found" message="No ledger entries match the selected filters." />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
              <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500 dark:bg-slate-950 dark:text-slate-400">
                <tr>
                  <th className="px-5 py-3">Date</th>
                  <th className="px-5 py-3">Product</th>
                  <th className="px-5 py-3">Warehouse</th>
                  <th className="px-5 py-3">Movement</th>
                  <th className="px-5 py-3">Quantity</th>
                  <th className="px-5 py-3">Reference</th>
                  <th className="px-5 py-3">Actor</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                {data.map((movement) => (
                  <tr key={movement.id} className="align-top">
                    <td className="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{formatDateTime(movement.created_at)}</td>
                    <td className="px-5 py-4">
                      <p className="font-semibold">{movement.product_name}</p>
                      <p className="mt-1 font-mono text-xs text-slate-500 dark:text-slate-400">{movement.product_sku}</p>
                    </td>
                    <td className="px-5 py-4">
                      <p className="text-sm font-semibold">{movement.warehouse_name}</p>
                      <p className="mt-1 font-mono text-xs text-slate-500 dark:text-slate-400">{movement.warehouse_code}</p>
                    </td>
                    <td className="px-5 py-4 text-sm font-semibold">{movementLabel(movement.movement_type)}</td>
                    <td className={`px-5 py-4 text-sm font-bold ${movement.quantity < 0 ? "text-rose-600" : "text-emerald-600"}`}>
                      {movement.quantity > 0 ? "+" : ""}
                      {movement.quantity}
                    </td>
                    <td className="px-5 py-4">
                      <p className="font-mono text-xs text-slate-500 dark:text-slate-400">{movement.reference_id ?? "-"}</p>
                      <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{movement.reference_type ?? "-"}</p>
                    </td>
                    <td className="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{movement.performed_by_name ?? "System"}</td>
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
