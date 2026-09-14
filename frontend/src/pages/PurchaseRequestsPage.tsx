import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, ClipboardList, Plus, Search, Send, X } from "lucide-react";
import { FormEvent, useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { FormInput, FormSelect, FormTextarea } from "../components/FormInput";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { useAuth } from "../hooks/useAuth";
import { api } from "../services/api";
import type { Product } from "../types/catalog";
import type { PurchaseRequest, PurchaseRequestPriority, PurchaseRequestStatus } from "../types/operations";
import { getApiErrorMessage } from "../utils/errors";
import { formatMoney } from "../utils/format";
import { statusLabel, statusTone } from "../utils/status";

const priorities: PurchaseRequestPriority[] = ["LOW", "NORMAL", "HIGH", "URGENT"];
const statusOptions: Array<PurchaseRequestStatus | "all"> = ["all", "DRAFT", "SUBMITTED", "APPROVED", "REJECTED", "CONVERTED_TO_PO"];

export function PurchaseRequestsPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<PurchaseRequestStatus | "all">("all");
  const [purpose, setPurpose] = useState("");
  const [priority, setPriority] = useState<PurchaseRequestPriority>("NORMAL");
  const [productId, setProductId] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [message, setMessage] = useState("");
  const canCreate = user?.role === "ADMINISTRATOR" || user?.role === "DEPARTMENT_REQUESTER";
  const canReview = user?.role === "ADMINISTRATOR" || user?.role === "INVENTORY_MANAGER";

  const { data: products = [] } = useQuery({
    queryKey: ["products"],
    queryFn: async () => (await api.get<Product[]>("/products")).data,
  });
  const { data = [], isLoading } = useQuery({
    queryKey: ["purchase-requests", status, search],
    queryFn: async () =>
      (
        await api.get<PurchaseRequest[]>("/purchase-requests", {
          params: { status: status === "all" ? undefined : status, search: search || undefined },
        })
      ).data,
  });

  const createMutation = useMutation({
    mutationFn: async () => {
      const product = products.find((item) => item.id === Number(productId));
      return (
        await api.post<PurchaseRequest>("/purchase-requests", {
          purpose,
          priority,
          items: [
            {
              product_id: Number(productId),
              description: product?.name ?? "Requested item",
              quantity: Number(quantity),
              estimated_unit_price: product?.cost_price ?? "0.00",
            },
          ],
        })
      ).data;
    },
    onSuccess: (request) => {
      setMessage(`${request.reference_number} was created as a draft.`);
      setPurpose("");
      setProductId("");
      setQuantity("1");
      queryClient.invalidateQueries({ queryKey: ["purchase-requests"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const actionMutation = useMutation({
    mutationFn: async ({ id, action }: { id: number; action: "submit" | "approve" | "reject" }) =>
      (await api.post<PurchaseRequest>(`/purchase-requests/${id}/${action}`)).data,
    onSuccess: (request) => {
      setMessage(`${request.reference_number} is now ${statusLabel(request.status)}.`);
      queryClient.invalidateQueries({ queryKey: ["purchase-requests"] });
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
        eyebrow="Procurement intake"
        title="Purchase Requests"
        description="Department purchase needs move from draft to submitted, approval, rejection, or conversion into purchase orders."
        icon={ClipboardList}
        meta={`${data.length} requests`}
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
                placeholder="Search reference or purpose"
              />
            </label>
            <FormSelect label="Status" value={status} onChange={(event) => setStatus(event.target.value as PurchaseRequestStatus | "all")}>
              {statusOptions.map((item) => (
                <option key={item} value={item}>
                  {item === "all" ? "All statuses" : statusLabel(item)}
                </option>
              ))}
            </FormSelect>
          </div>

          {!isLoading && data.length === 0 ? (
            <div className="p-5">
              <EmptyState icon={ClipboardList} title="No purchase requests found" message="No requests match the selected filter." />
            </div>
          ) : (
            <div className="divide-y divide-slate-200 dark:divide-slate-800">
              {data.map((request) => (
                <article key={request.id} className="p-5">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="font-mono text-sm font-bold text-slate-950 dark:text-white">{request.reference_number}</p>
                        <StatusBadge label={statusLabel(request.status)} tone={statusTone(request.status)} />
                        <StatusBadge label={request.priority} tone={request.priority === "URGENT" ? "rose" : "slate"} />
                      </div>
                      <h2 className="mt-3 text-lg font-bold">{request.purpose}</h2>
                      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                        {request.department_name} - requested by {request.requested_by_name}
                      </p>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {request.items.map((item) => (
                          <span key={item.id} className="rounded-lg border border-slate-200 px-3 py-2 text-sm dark:border-slate-800">
                            {item.quantity} x {item.description} ({formatMoney(item.estimated_unit_price)})
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {request.status === "DRAFT" && (
                        <button
                          type="button"
                          onClick={() => actionMutation.mutate({ id: request.id, action: "submit" })}
                          className="inline-flex h-10 items-center gap-2 rounded-lg border border-blue-200 px-3 text-sm font-bold text-blue-700 hover:bg-blue-50 dark:border-blue-800 dark:text-blue-200 dark:hover:bg-blue-950"
                        >
                          <Send className="h-4 w-4" />
                          Submit
                        </button>
                      )}
                      {canReview && request.status === "SUBMITTED" && (
                        <>
                          <button
                            type="button"
                            onClick={() => actionMutation.mutate({ id: request.id, action: "approve" })}
                            className="inline-flex h-10 items-center gap-2 rounded-lg border border-emerald-200 px-3 text-sm font-bold text-emerald-700 hover:bg-emerald-50 dark:border-emerald-800 dark:text-emerald-200 dark:hover:bg-emerald-950"
                          >
                            <Check className="h-4 w-4" />
                            Approve
                          </button>
                          <button
                            type="button"
                            onClick={() => actionMutation.mutate({ id: request.id, action: "reject" })}
                            className="inline-flex h-10 items-center gap-2 rounded-lg border border-rose-200 px-3 text-sm font-bold text-rose-700 hover:bg-rose-50 dark:border-rose-800 dark:text-rose-200 dark:hover:bg-rose-950"
                          >
                            <X className="h-4 w-4" />
                            Reject
                          </button>
                        </>
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
              <h2 className="mt-1 text-xl font-bold">New purchase request</h2>
            </div>
            <Plus className="h-6 w-6 text-emerald-600" />
          </div>

          {canCreate ? (
            <form className="mt-5 space-y-4" onSubmit={submitForm}>
              <FormTextarea label="Purpose" value={purpose} onChange={(event) => setPurpose(event.target.value)} required />
              <FormSelect label="Priority" value={priority} onChange={(event) => setPriority(event.target.value as PurchaseRequestPriority)}>
                {priorities.map((item) => (
                  <option key={item} value={item}>
                    {statusLabel(item)}
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
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 text-sm font-bold text-white shadow-sm transition hover:bg-emerald-700 disabled:bg-slate-400"
              >
                <Plus className="h-4 w-4" />
                Create draft
              </button>
            </form>
          ) : (
            <div className="mt-5 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300">
              Your role can review purchase request history.
            </div>
          )}
        </aside>
      </section>
    </div>
  );
}
