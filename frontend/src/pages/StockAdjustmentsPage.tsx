import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, SlidersHorizontal } from "lucide-react";
import { FormEvent, useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { FormInput, FormSelect, FormTextarea } from "../components/FormInput";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { useAuth } from "../hooks/useAuth";
import { api } from "../services/api";
import type { Product, Warehouse } from "../types/catalog";
import type { StockAdjustment, StockAdjustmentType } from "../types/operations";
import { getApiErrorMessage } from "../utils/errors";
import { formatDateTime } from "../utils/format";
import { statusLabel, statusTone } from "../utils/status";

export function StockAdjustmentsPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [productId, setProductId] = useState("");
  const [warehouseId, setWarehouseId] = useState("");
  const [adjustmentType, setAdjustmentType] = useState<StockAdjustmentType>("INCREASE");
  const [quantity, setQuantity] = useState("1");
  const [reason, setReason] = useState("");
  const [message, setMessage] = useState("");
  const canManage = user?.role === "ADMINISTRATOR" || user?.role === "INVENTORY_MANAGER";

  const { data: products = [] } = useQuery({ queryKey: ["products"], queryFn: async () => (await api.get<Product[]>("/products")).data });
  const { data: warehouses = [] } = useQuery({ queryKey: ["warehouses"], queryFn: async () => (await api.get<Warehouse[]>("/warehouses")).data });
  const { data = [], isLoading } = useQuery({ queryKey: ["stock-adjustments"], queryFn: async () => (await api.get<StockAdjustment[]>("/stock-adjustments")).data });

  const createMutation = useMutation({
    mutationFn: async () =>
      (
        await api.post<StockAdjustment>("/stock-adjustments", {
          product_id: Number(productId),
          warehouse_id: Number(warehouseId),
          adjustment_type: adjustmentType,
          quantity: Number(quantity),
          reason,
        })
      ).data,
    onSuccess: (adjustment) => {
      setMessage(`${adjustment.adjustment_number} was recorded.`);
      setProductId("");
      setWarehouseId("");
      setQuantity("1");
      setReason("");
      queryClient.invalidateQueries({ queryKey: ["stock-adjustments"] });
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
      queryClient.invalidateQueries({ queryKey: ["stock-movements"] });
    },
  });

  function submitForm(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    createMutation.mutate();
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Inventory control"
        title="Stock Adjustments"
        description="Authorized inventory corrections for count variance, damage, loss, returns, and operational corrections."
        icon={SlidersHorizontal}
        meta={`${data.length} adjustments`}
      />

      <section className="grid gap-5 xl:grid-cols-[1fr_360px]">
        <div className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
          {!isLoading && data.length === 0 ? (
            <div className="p-5">
              <EmptyState icon={SlidersHorizontal} title="No adjustments found" message="Stock adjustments will appear when inventory managers record corrections." />
            </div>
          ) : (
            <div className="divide-y divide-slate-200 dark:divide-slate-800">
              {data.map((adjustment) => (
                <article key={adjustment.id} className="p-5">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="font-mono text-sm font-bold">{adjustment.adjustment_number}</p>
                    <StatusBadge label={statusLabel(adjustment.adjustment_type)} tone={statusTone(adjustment.adjustment_type)} />
                  </div>
                  <h2 className="mt-3 text-lg font-bold">{adjustment.product_name}</h2>
                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    {adjustment.quantity} units at {adjustment.warehouse_name} by {adjustment.performed_by_name} on {formatDateTime(adjustment.created_at)}
                  </p>
                  <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{adjustment.reason}</p>
                </article>
              ))}
            </div>
          )}
        </div>

        <aside className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-bold uppercase text-emerald-600 dark:text-emerald-300">Adjustment form</p>
              <h2 className="mt-1 text-xl font-bold">Record adjustment</h2>
            </div>
            <Plus className="h-6 w-6 text-emerald-600" />
          </div>

          {canManage ? (
            <form className="mt-5 space-y-4" onSubmit={submitForm}>
              <FormSelect label="Product" value={productId} onChange={(event) => setProductId(event.target.value)} required>
                <option value="">Select product</option>
                {products.map((product) => <option key={product.id} value={product.id}>{product.sku} - {product.name}</option>)}
              </FormSelect>
              <FormSelect label="Warehouse" value={warehouseId} onChange={(event) => setWarehouseId(event.target.value)} required>
                <option value="">Select warehouse</option>
                {warehouses.map((warehouse) => <option key={warehouse.id} value={warehouse.id}>{warehouse.name}</option>)}
              </FormSelect>
              <FormSelect label="Type" value={adjustmentType} onChange={(event) => setAdjustmentType(event.target.value as StockAdjustmentType)}>
                <option value="INCREASE">Increase</option>
                <option value="DECREASE">Decrease</option>
              </FormSelect>
              <FormInput label="Quantity" type="number" min="1" value={quantity} onChange={(event) => setQuantity(event.target.value)} required />
              <FormTextarea label="Reason" value={reason} onChange={(event) => setReason(event.target.value)} required />
              {createMutation.isError && (
                <p className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200">
                  {getApiErrorMessage(createMutation.error)}
                </p>
              )}
              {message && (
                <p className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-200">
                  {message}
                </p>
              )}
              <button type="submit" disabled={createMutation.isPending} className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 text-sm font-bold text-white shadow-sm transition hover:bg-emerald-700 disabled:bg-slate-400">
                <Plus className="h-4 w-4" />
                Record adjustment
              </button>
            </form>
          ) : (
            <div className="mt-5 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300">
              Your role can review adjustment history.
            </div>
          )}
        </aside>
      </section>
    </div>
  );
}
