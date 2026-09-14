import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { PackageCheck, Plus, Search, Truck } from "lucide-react";
import { FormEvent, useMemo, useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { FormInput, FormSelect, FormTextarea } from "../components/FormInput";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { useAuth } from "../hooks/useAuth";
import { api } from "../services/api";
import type { Warehouse } from "../types/catalog";
import type { GoodsReceipt, PurchaseOrder } from "../types/operations";
import { getApiErrorMessage } from "../utils/errors";
import { formatDateTime } from "../utils/format";
import { statusLabel, statusTone } from "../utils/status";

export function GoodsReceivingPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [orderId, setOrderId] = useState("");
  const [warehouseId, setWarehouseId] = useState("");
  const [quantities, setQuantities] = useState<Record<number, string>>({});
  const [notes, setNotes] = useState("");
  const [message, setMessage] = useState("");
  const canReceive = user?.role === "ADMINISTRATOR" || user?.role === "WAREHOUSE_OFFICER";

  const { data: warehouses = [] } = useQuery({
    queryKey: ["warehouses"],
    queryFn: async () => (await api.get<Warehouse[]>("/warehouses")).data,
  });
  const { data: orders = [] } = useQuery({
    queryKey: ["purchase-orders", "receiving"],
    queryFn: async () => (await api.get<PurchaseOrder[]>("/purchase-orders")).data,
  });
  const { data: receipts = [], isLoading } = useQuery({
    queryKey: ["goods-receipts", search],
    queryFn: async () => (await api.get<GoodsReceipt[]>("/goods-receipts", { params: { search: search || undefined } })).data,
  });

  const receivableOrders = useMemo(
    () => orders.filter((order) => order.status === "ISSUED" || order.status === "PARTIALLY_RECEIVED"),
    [orders],
  );
  const selectedOrder = receivableOrders.find((order) => order.id === Number(orderId));

  const createMutation = useMutation({
    mutationFn: async () =>
      (
        await api.post<GoodsReceipt>("/goods-receipts", {
          purchase_order_id: Number(orderId),
          warehouse_id: Number(warehouseId),
          notes: notes || null,
          items:
            selectedOrder?.items
              .map((item) => ({
                purchase_order_item_id: item.id,
                quantity_received: Number(quantities[item.id] ?? 0),
                quantity_rejected: 0,
              }))
              .filter((item) => item.quantity_received > 0) ?? [],
        })
      ).data,
    onSuccess: (receipt) => {
      setMessage(`${receipt.receipt_number} was recorded.`);
      setOrderId("");
      setQuantities({});
      setNotes("");
      queryClient.invalidateQueries({ queryKey: ["goods-receipts"] });
      queryClient.invalidateQueries({ queryKey: ["purchase-orders"] });
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
        eyebrow="Warehouse receiving"
        title="Goods Receiving"
        description="Receive issued purchase orders, update purchase order quantities, and increase warehouse inventory through stock movements."
        icon={Truck}
        meta={`${receivableOrders.length} awaiting receipt`}
      />

      <section className="grid gap-5 xl:grid-cols-[1fr_380px]">
        <div className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="border-b border-slate-200 p-5 dark:border-slate-800">
            <label className="relative block max-w-xl">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                className="h-11 w-full rounded-lg border border-slate-200 bg-slate-50 pl-10 pr-3 text-sm outline-none transition focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:focus:ring-emerald-950"
                placeholder="Search receipt or PO"
              />
            </label>
          </div>
          {!isLoading && receipts.length === 0 ? (
            <div className="p-5">
              <EmptyState icon={PackageCheck} title="No receipts found" message="Goods receipts will appear here as warehouse teams receive issued purchase orders." />
            </div>
          ) : (
            <div className="divide-y divide-slate-200 dark:divide-slate-800">
              {receipts.map((receipt) => (
                <article key={receipt.id} className="p-5">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="font-mono text-sm font-bold">{receipt.receipt_number}</p>
                    <StatusBadge label={receipt.purchase_order_number} tone="blue" />
                  </div>
                  <p className="mt-2 font-semibold">{receipt.warehouse_name}</p>
                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    Received by {receipt.received_by_name} on {formatDateTime(receipt.created_at)}
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {receipt.items.map((item) => (
                      <span key={item.id} className="rounded-lg border border-slate-200 px-3 py-2 text-sm dark:border-slate-800">
                        +{item.quantity_received} {item.product_name}
                      </span>
                    ))}
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>

        <aside className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-bold uppercase text-emerald-600 dark:text-emerald-300">Receipt form</p>
              <h2 className="mt-1 text-xl font-bold">Record goods</h2>
            </div>
            <PackageCheck className="h-6 w-6 text-emerald-600" />
          </div>

          {canReceive ? (
            <form className="mt-5 space-y-4" onSubmit={submitForm}>
              <FormSelect label="Purchase order" value={orderId} onChange={(event) => setOrderId(event.target.value)} required>
                <option value="">Select issued PO</option>
                {receivableOrders.map((order) => (
                  <option key={order.id} value={order.id}>
                    {order.po_number} - {order.supplier_name}
                  </option>
                ))}
              </FormSelect>
              <FormSelect label="Warehouse" value={warehouseId} onChange={(event) => setWarehouseId(event.target.value)} required>
                <option value="">Select warehouse</option>
                {warehouses.map((warehouse) => (
                  <option key={warehouse.id} value={warehouse.id}>
                    {warehouse.name}
                  </option>
                ))}
              </FormSelect>
              {selectedOrder?.items.map((item) => (
                <FormInput
                  key={item.id}
                  label={`${item.product_sku} remaining ${item.remaining_quantity}`}
                  type="number"
                  min="0"
                  max={item.remaining_quantity}
                  value={quantities[item.id] ?? ""}
                  onChange={(event) => setQuantities((current) => ({ ...current, [item.id]: event.target.value }))}
                />
              ))}
              <FormTextarea label="Notes" value={notes} onChange={(event) => setNotes(event.target.value)} />
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
              <button
                type="submit"
                disabled={createMutation.isPending || !selectedOrder}
                className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 text-sm font-bold text-white shadow-sm transition hover:bg-emerald-700 disabled:bg-slate-400"
              >
                <Plus className="h-4 w-4" />
                Record receipt
              </button>
            </form>
          ) : (
            <div className="mt-5 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300">
              Your role can review receiving history.
            </div>
          )}
        </aside>
      </section>
    </div>
  );
}
