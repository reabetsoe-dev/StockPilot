import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FileCheck2, Plus, Search, Send, ShoppingCart } from "lucide-react";
import { FormEvent, useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { FormInput, FormSelect, FormTextarea } from "../components/FormInput";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { useAuth } from "../hooks/useAuth";
import { api } from "../services/api";
import type { Product, Supplier } from "../types/catalog";
import type { PurchaseOrder, PurchaseOrderStatus, PurchaseRequest } from "../types/operations";
import { getApiErrorMessage } from "../utils/errors";
import { formatMoney } from "../utils/format";
import { statusLabel, statusTone } from "../utils/status";

const orderStatuses: Array<PurchaseOrderStatus | "all"> = ["all", "DRAFT", "ISSUED", "PARTIALLY_RECEIVED", "RECEIVED", "CANCELLED"];

export function PurchaseOrdersPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<PurchaseOrderStatus | "all">("all");
  const [supplierId, setSupplierId] = useState("");
  const [requestId, setRequestId] = useState("");
  const [productId, setProductId] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [unitPrice, setUnitPrice] = useState("");
  const [notes, setNotes] = useState("");
  const [message, setMessage] = useState("");
  const canManage = user?.role === "ADMINISTRATOR" || user?.role === "PROCUREMENT_OFFICER";

  const { data: suppliers = [] } = useQuery({
    queryKey: ["suppliers"],
    queryFn: async () => (await api.get<Supplier[]>("/suppliers")).data,
  });
  const { data: products = [] } = useQuery({
    queryKey: ["products"],
    queryFn: async () => (await api.get<Product[]>("/products")).data,
  });
  const { data: approvedRequests = [] } = useQuery({
    queryKey: ["purchase-requests", "APPROVED"],
    queryFn: async () => (await api.get<PurchaseRequest[]>("/purchase-requests", { params: { status: "APPROVED" } })).data,
    enabled: canManage,
  });
  const { data = [], isLoading } = useQuery({
    queryKey: ["purchase-orders", status, search],
    queryFn: async () =>
      (
        await api.get<PurchaseOrder[]>("/purchase-orders", {
          params: { status: status === "all" ? undefined : status, search: search || undefined },
        })
      ).data,
  });

  const createMutation = useMutation({
    mutationFn: async () => {
      const product = products.find((item) => item.id === Number(productId));
      return (
        await api.post<PurchaseOrder>("/purchase-orders", {
          supplier_id: Number(supplierId),
          purchase_request_id: requestId ? Number(requestId) : null,
          notes: notes || null,
          items: [
            {
              product_id: Number(productId),
              description: product?.name,
              quantity_ordered: Number(quantity),
              unit_price: unitPrice,
            },
          ],
        })
      ).data;
    },
    onSuccess: (order) => {
      setMessage(`${order.po_number} was created.`);
      setSupplierId("");
      setRequestId("");
      setProductId("");
      setQuantity("1");
      setUnitPrice("");
      setNotes("");
      queryClient.invalidateQueries({ queryKey: ["purchase-orders"] });
      queryClient.invalidateQueries({ queryKey: ["purchase-requests"] });
    },
  });

  const issueMutation = useMutation({
    mutationFn: async (id: number) => (await api.post<PurchaseOrder>(`/purchase-orders/${id}/issue`)).data,
    onSuccess: (order) => {
      setMessage(`${order.po_number} was issued.`);
      queryClient.invalidateQueries({ queryKey: ["purchase-orders"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
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
        eyebrow="Procurement control"
        title="Purchase Orders"
        description="Supplier orders with backend-calculated totals, issue workflow, and receiving progress."
        icon={ShoppingCart}
        meta={`${data.length} orders`}
      />

      <section className="grid gap-5 xl:grid-cols-[1fr_360px]">
        <div className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="grid gap-3 border-b border-slate-200 p-5 dark:border-slate-800 lg:grid-cols-[1fr_220px]">
            <label className="relative block">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                className="h-11 w-full rounded-lg border border-slate-200 bg-slate-50 pl-10 pr-3 text-sm outline-none transition focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:focus:ring-emerald-950"
                placeholder="Search PO or supplier"
              />
            </label>
            <FormSelect label="Status" value={status} onChange={(event) => setStatus(event.target.value as PurchaseOrderStatus | "all")}>
              {orderStatuses.map((item) => (
                <option key={item} value={item}>
                  {item === "all" ? "All statuses" : statusLabel(item)}
                </option>
              ))}
            </FormSelect>
          </div>

          {!isLoading && data.length === 0 ? (
            <div className="p-5">
              <EmptyState icon={ShoppingCart} title="No purchase orders found" message="No orders match the selected filter." />
            </div>
          ) : (
            <div className="divide-y divide-slate-200 dark:divide-slate-800">
              {data.map((order) => (
                <article key={order.id} className="p-5">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="font-mono text-sm font-bold">{order.po_number}</p>
                        <StatusBadge label={statusLabel(order.status)} tone={statusTone(order.status)} />
                      </div>
                      <h2 className="mt-3 text-lg font-bold">{order.supplier_name}</h2>
                      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                        Total {formatMoney(order.total)} - {order.items.length} line item(s)
                      </p>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {order.items.map((item) => (
                          <span key={item.id} className="rounded-lg border border-slate-200 px-3 py-2 text-sm dark:border-slate-800">
                            {item.quantity_received}/{item.quantity_ordered} {item.product_name}
                          </span>
                        ))}
                      </div>
                    </div>
                    {canManage && order.status === "DRAFT" && (
                      <button
                        type="button"
                        onClick={() => issueMutation.mutate(order.id)}
                        className="inline-flex h-10 items-center gap-2 rounded-lg border border-emerald-200 px-3 text-sm font-bold text-emerald-700 hover:bg-emerald-50 dark:border-emerald-800 dark:text-emerald-200 dark:hover:bg-emerald-950"
                      >
                        <Send className="h-4 w-4" />
                        Issue
                      </button>
                    )}
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>

        <aside className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-bold uppercase text-emerald-600 dark:text-emerald-300">Order form</p>
              <h2 className="mt-1 text-xl font-bold">New purchase order</h2>
            </div>
            <FileCheck2 className="h-6 w-6 text-emerald-600" />
          </div>

          {canManage ? (
            <form className="mt-5 space-y-4" onSubmit={submitForm}>
              <FormSelect label="Supplier" value={supplierId} onChange={(event) => setSupplierId(event.target.value)} required>
                <option value="">Select supplier</option>
                {suppliers.map((supplier) => (
                  <option key={supplier.id} value={supplier.id}>
                    {supplier.name}
                  </option>
                ))}
              </FormSelect>
              <FormSelect label="Approved request" value={requestId} onChange={(event) => setRequestId(event.target.value)}>
                <option value="">No linked request</option>
                {approvedRequests.map((request) => (
                  <option key={request.id} value={request.id}>
                    {request.reference_number}
                  </option>
                ))}
              </FormSelect>
              <FormSelect label="Product" value={productId} onChange={(event) => setProductId(event.target.value)} required>
                <option value="">Select product</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.sku} - {product.name}
                  </option>
                ))}
              </FormSelect>
              <div className="grid gap-4 sm:grid-cols-2">
                <FormInput label="Quantity" type="number" min="1" value={quantity} onChange={(event) => setQuantity(event.target.value)} required />
                <FormInput label="Unit price" type="number" min="0" step="0.01" value={unitPrice} onChange={(event) => setUnitPrice(event.target.value)} required />
              </div>
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
                disabled={createMutation.isPending}
                className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 text-sm font-bold text-white shadow-sm transition hover:bg-emerald-700 disabled:bg-slate-400"
              >
                <Plus className="h-4 w-4" />
                Create order
              </button>
            </form>
          ) : (
            <div className="mt-5 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300">
              Your role can review purchase order history.
            </div>
          )}
        </aside>
      </section>
    </div>
  );
}
