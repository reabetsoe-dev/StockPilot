import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, ClipboardCheck, ClipboardList, Plus, X } from "lucide-react";
import { FormEvent, useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { FormInput, FormSelect, FormTextarea } from "../components/FormInput";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { useAuth } from "../hooks/useAuth";
import { api } from "../services/api";
import type { Product, Warehouse } from "../types/catalog";
import type { StockRequest } from "../types/operations";
import { getApiErrorMessage } from "../utils/errors";
import { statusLabel, statusTone } from "../utils/status";

export function StockRequestsPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [warehouseId, setWarehouseId] = useState("");
  const [productId, setProductId] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [purpose, setPurpose] = useState("");
  const [message, setMessage] = useState("");
  const canCreate = user?.role === "ADMINISTRATOR" || user?.role === "DEPARTMENT_REQUESTER";
  const canApprove = user?.role === "ADMINISTRATOR" || user?.role === "INVENTORY_MANAGER";
  const canIssue = user?.role === "ADMINISTRATOR" || user?.role === "WAREHOUSE_OFFICER";

  const { data: products = [] } = useQuery({
    queryKey: ["products"],
    queryFn: async () => (await api.get<Product[]>("/products")).data,
  });
  const { data: warehouses = [] } = useQuery({
    queryKey: ["warehouses"],
    queryFn: async () => (await api.get<Warehouse[]>("/warehouses")).data,
  });
  const { data = [], isLoading } = useQuery({
    queryKey: ["stock-requests"],
    queryFn: async () => (await api.get<StockRequest[]>("/stock-requests")).data,
  });

  const createMutation = useMutation({
    mutationFn: async () =>
      (
        await api.post<StockRequest>("/stock-requests", {
          source_warehouse_id: Number(warehouseId),
          purpose,
          items: [{ product_id: Number(productId), quantity_requested: Number(quantity) }],
        })
      ).data,
    onSuccess: (request) => {
      setMessage(`${request.reference_number} was submitted.`);
      setWarehouseId("");
      setProductId("");
      setQuantity("1");
      setPurpose("");
      queryClient.invalidateQueries({ queryKey: ["stock-requests"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const actionMutation = useMutation({
    mutationFn: async ({ id, action }: { id: number; action: "approve" | "reject" | "issue" }) =>
      (await api.post<StockRequest>(`/stock-requests/${id}/${action}`)).data,
    onSuccess: (request) => {
      setMessage(`${request.reference_number} is now ${statusLabel(request.status)}.`);
      queryClient.invalidateQueries({ queryKey: ["stock-requests"] });
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
        eyebrow="Internal fulfillment"
        title="Stock Requests"
        description="Departments request existing inventory, managers approve it, and warehouse teams issue stock without allowing negative balances."
        icon={ClipboardList}
        meta={`${data.length} requests`}
      />

      <section className="grid gap-5 xl:grid-cols-[1fr_360px]">
        <div className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
          {!isLoading && data.length === 0 ? (
            <div className="p-5">
              <EmptyState icon={ClipboardList} title="No stock requests found" message="Internal stock requests will appear here after departments submit them." />
            </div>
          ) : (
            <div className="divide-y divide-slate-200 dark:divide-slate-800">
              {data.map((request) => (
                <article key={request.id} className="p-5">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="font-mono text-sm font-bold">{request.reference_number}</p>
                        <StatusBadge label={statusLabel(request.status)} tone={statusTone(request.status)} />
                      </div>
                      <h2 className="mt-3 text-lg font-bold">{request.purpose}</h2>
                      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                        {request.department_name} - {request.source_warehouse_name}
                      </p>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {request.items.map((item) => (
                          <span key={item.id} className="rounded-lg border border-slate-200 px-3 py-2 text-sm dark:border-slate-800">
                            {item.quantity_issued}/{item.quantity_requested} {item.product_name}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {canApprove && request.status === "SUBMITTED" && (
                        <>
                          <button type="button" onClick={() => actionMutation.mutate({ id: request.id, action: "approve" })} className="inline-flex h-10 items-center gap-2 rounded-lg border border-emerald-200 px-3 text-sm font-bold text-emerald-700 hover:bg-emerald-50 dark:border-emerald-800 dark:text-emerald-200">
                            <Check className="h-4 w-4" />
                            Approve
                          </button>
                          <button type="button" onClick={() => actionMutation.mutate({ id: request.id, action: "reject" })} className="inline-flex h-10 items-center gap-2 rounded-lg border border-rose-200 px-3 text-sm font-bold text-rose-700 hover:bg-rose-50 dark:border-rose-800 dark:text-rose-200">
                            <X className="h-4 w-4" />
                            Reject
                          </button>
                        </>
                      )}
                      {canIssue && request.status === "APPROVED" && (
                        <button type="button" onClick={() => actionMutation.mutate({ id: request.id, action: "issue" })} className="inline-flex h-10 items-center gap-2 rounded-lg border border-blue-200 px-3 text-sm font-bold text-blue-700 hover:bg-blue-50 dark:border-blue-800 dark:text-blue-200">
                          <ClipboardCheck className="h-4 w-4" />
                          Issue
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
              <p className="text-sm font-bold uppercase text-emerald-600 dark:text-emerald-300">Request form</p>
              <h2 className="mt-1 text-xl font-bold">New stock request</h2>
            </div>
            <Plus className="h-6 w-6 text-emerald-600" />
          </div>

          {canCreate ? (
            <form className="mt-5 space-y-4" onSubmit={submitForm}>
              <FormSelect label="Source warehouse" value={warehouseId} onChange={(event) => setWarehouseId(event.target.value)} required>
                <option value="">Select warehouse</option>
                {warehouses.map((warehouse) => (
                  <option key={warehouse.id} value={warehouse.id}>{warehouse.name}</option>
                ))}
              </FormSelect>
              <FormSelect label="Product" value={productId} onChange={(event) => setProductId(event.target.value)} required>
                <option value="">Select product</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>{product.sku} - {product.name}</option>
                ))}
              </FormSelect>
              <FormInput label="Quantity" type="number" min="1" value={quantity} onChange={(event) => setQuantity(event.target.value)} required />
              <FormTextarea label="Purpose" value={purpose} onChange={(event) => setPurpose(event.target.value)} required />
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
                Submit request
              </button>
            </form>
          ) : (
            <div className="mt-5 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300">
              Your role can review stock request history.
            </div>
          )}
        </aside>
      </section>
    </div>
  );
}
