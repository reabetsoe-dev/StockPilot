import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowRightLeft, CheckCircle2, Plus, Send } from "lucide-react";
import { FormEvent, useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { FormInput, FormSelect } from "../components/FormInput";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { useAuth } from "../hooks/useAuth";
import { api } from "../services/api";
import type { Product, Warehouse } from "../types/catalog";
import type { StockTransfer } from "../types/operations";
import { getApiErrorMessage } from "../utils/errors";
import { statusLabel, statusTone } from "../utils/status";

export function StockTransfersPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [sourceId, setSourceId] = useState("");
  const [destinationId, setDestinationId] = useState("");
  const [productId, setProductId] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [message, setMessage] = useState("");
  const canManage = user?.role === "ADMINISTRATOR" || user?.role === "INVENTORY_MANAGER" || user?.role === "WAREHOUSE_OFFICER";
  const canOperate = user?.role === "ADMINISTRATOR" || user?.role === "WAREHOUSE_OFFICER";

  const { data: warehouses = [] } = useQuery({
    queryKey: ["warehouses"],
    queryFn: async () => (await api.get<Warehouse[]>("/warehouses")).data,
  });
  const { data: products = [] } = useQuery({
    queryKey: ["products"],
    queryFn: async () => (await api.get<Product[]>("/products")).data,
  });
  const { data = [], isLoading } = useQuery({
    queryKey: ["transfers"],
    queryFn: async () => (await api.get<StockTransfer[]>("/transfers")).data,
  });

  const createMutation = useMutation({
    mutationFn: async () =>
      (
        await api.post<StockTransfer>("/transfers", {
          source_warehouse_id: Number(sourceId),
          destination_warehouse_id: Number(destinationId),
          items: [{ product_id: Number(productId), quantity: Number(quantity) }],
        })
      ).data,
    onSuccess: (transfer) => {
      setMessage(`${transfer.transfer_number} was created.`);
      setSourceId("");
      setDestinationId("");
      setProductId("");
      setQuantity("1");
      queryClient.invalidateQueries({ queryKey: ["transfers"] });
    },
  });

  const actionMutation = useMutation({
    mutationFn: async ({ id, action }: { id: number; action: "dispatch" | "receive" }) =>
      (await api.post<StockTransfer>(`/transfers/${id}/${action}`)).data,
    onSuccess: (transfer) => {
      setMessage(`${transfer.transfer_number} is now ${statusLabel(transfer.status)}.`);
      queryClient.invalidateQueries({ queryKey: ["transfers"] });
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
        eyebrow="Warehouse movement"
        title="Stock Transfers"
        description="Move inventory between warehouses through dispatch and receipt movements, with completed transfers locked by status."
        icon={ArrowRightLeft}
        meta={`${data.length} transfers`}
      />

      <section className="grid gap-5 xl:grid-cols-[1fr_360px]">
        <div className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
          {!isLoading && data.length === 0 ? (
            <div className="p-5">
              <EmptyState icon={ArrowRightLeft} title="No transfers found" message="Warehouse transfers will appear once stock starts moving between locations." />
            </div>
          ) : (
            <div className="divide-y divide-slate-200 dark:divide-slate-800">
              {data.map((transfer) => (
                <article key={transfer.id} className="p-5">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="font-mono text-sm font-bold">{transfer.transfer_number}</p>
                        <StatusBadge label={statusLabel(transfer.status)} tone={statusTone(transfer.status)} />
                      </div>
                      <h2 className="mt-3 text-lg font-bold">
                        {transfer.source_warehouse_name} to {transfer.destination_warehouse_name}
                      </h2>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {transfer.items.map((item) => (
                          <span key={item.id} className="rounded-lg border border-slate-200 px-3 py-2 text-sm dark:border-slate-800">
                            {item.quantity} x {item.product_name}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {canOperate && transfer.status === "DRAFT" && (
                        <button type="button" onClick={() => actionMutation.mutate({ id: transfer.id, action: "dispatch" })} className="inline-flex h-10 items-center gap-2 rounded-lg border border-blue-200 px-3 text-sm font-bold text-blue-700 hover:bg-blue-50 dark:border-blue-800 dark:text-blue-200">
                          <Send className="h-4 w-4" />
                          Dispatch
                        </button>
                      )}
                      {canOperate && transfer.status === "IN_TRANSIT" && (
                        <button type="button" onClick={() => actionMutation.mutate({ id: transfer.id, action: "receive" })} className="inline-flex h-10 items-center gap-2 rounded-lg border border-emerald-200 px-3 text-sm font-bold text-emerald-700 hover:bg-emerald-50 dark:border-emerald-800 dark:text-emerald-200">
                          <CheckCircle2 className="h-4 w-4" />
                          Receive
                        </button>
                      )}
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>

        <aside className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-bold uppercase text-emerald-600 dark:text-emerald-300">Transfer form</p>
              <h2 className="mt-1 text-xl font-bold">New transfer</h2>
            </div>
            <Plus className="h-6 w-6 text-emerald-600" />
          </div>

          {canManage ? (
            <form className="mt-5 space-y-4" onSubmit={submitForm}>
              <FormSelect label="Source" value={sourceId} onChange={(event) => setSourceId(event.target.value)} required>
                <option value="">Select source</option>
                {warehouses.map((warehouse) => <option key={warehouse.id} value={warehouse.id}>{warehouse.name}</option>)}
              </FormSelect>
              <FormSelect label="Destination" value={destinationId} onChange={(event) => setDestinationId(event.target.value)} required>
                <option value="">Select destination</option>
                {warehouses.map((warehouse) => <option key={warehouse.id} value={warehouse.id}>{warehouse.name}</option>)}
              </FormSelect>
              <FormSelect label="Product" value={productId} onChange={(event) => setProductId(event.target.value)} required>
                <option value="">Select product</option>
                {products.map((product) => <option key={product.id} value={product.id}>{product.sku} - {product.name}</option>)}
              </FormSelect>
              <FormInput label="Quantity" type="number" min="1" value={quantity} onChange={(event) => setQuantity(event.target.value)} required />
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
                Create transfer
              </button>
            </form>
          ) : (
            <div className="mt-5 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300">
              Your role can review transfer history.
            </div>
          )}
        </aside>
      </section>
    </div>
  );
}
