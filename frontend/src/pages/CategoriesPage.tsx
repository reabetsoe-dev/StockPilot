import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Layers3, Plus, Tags } from "lucide-react";
import { FormEvent, useState } from "react";

import { EmptyState } from "../components/EmptyState";
import { FormInput, FormTextarea } from "../components/FormInput";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { useAuth } from "../hooks/useAuth";
import { api } from "../services/api";
import type { Category } from "../types/catalog";
import { getApiErrorMessage } from "../utils/errors";

export function CategoriesPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const canManage = user?.role === "ADMINISTRATOR" || user?.role === "INVENTORY_MANAGER";

  const { data = [], isLoading } = useQuery({
    queryKey: ["categories"],
    queryFn: async () => (await api.get<Category[]>("/categories")).data,
  });

  const createMutation = useMutation({
    mutationFn: async () =>
      (
        await api.post<Category>("/categories", {
          name,
          description: description || null,
          active: true,
        })
      ).data,
    onSuccess: (category) => {
      setSuccessMessage(`${category.name} was added.`);
      setName("");
      setDescription("");
      queryClient.invalidateQueries({ queryKey: ["categories"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSuccessMessage("");
    createMutation.mutate();
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Catalog setup"
        title="Categories"
        description="Product classification for procurement, reporting, reorder review, and warehouse planning."
        icon={Tags}
        meta={`${data.length} categories`}
      />

      <section className="grid gap-5 xl:grid-cols-[1fr_340px]">
        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          {!isLoading && data.length === 0 ? (
            <EmptyState icon={Tags} title="No categories found" message="Seeded catalog categories will appear after setup." />
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {data.map((category) => (
                <article key={category.id} className="rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3">
                      <div className="rounded-lg bg-emerald-50 p-3 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-200">
                        <Layers3 className="h-5 w-5" />
                      </div>
                      <div>
                        <h2 className="font-bold text-slate-950 dark:text-white">{category.name}</h2>
                        <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">{category.description}</p>
                      </div>
                    </div>
                    <StatusBadge label={category.active ? "Active" : "Inactive"} tone={category.active ? "emerald" : "slate"} />
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>

        <aside className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-bold uppercase text-emerald-600 dark:text-emerald-300">Category record</p>
              <h2 className="mt-1 text-xl font-bold">New category</h2>
            </div>
            <Plus className="h-6 w-6 text-emerald-600" />
          </div>

          {canManage ? (
            <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
              <FormInput
                label="Name"
                value={name}
                onChange={(event) => {
                  setSuccessMessage("");
                  createMutation.reset();
                  setName(event.target.value);
                }}
                required
              />
              <FormTextarea
                label="Description"
                value={description}
                onChange={(event) => {
                  setSuccessMessage("");
                  createMutation.reset();
                  setDescription(event.target.value);
                }}
              />
              {createMutation.isError && (
                <p className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200">
                  {getApiErrorMessage(createMutation.error)}
                </p>
              )}
              {successMessage && (
                <p className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-200">
                  {successMessage}
                </p>
              )}
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 text-sm font-bold text-white shadow-sm transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-400"
              >
                <Plus className="h-4 w-4" />
                {createMutation.isPending ? "Saving" : "Create category"}
              </button>
            </form>
          ) : (
            <div className="mt-5 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300">
              Your role has read-only category access.
            </div>
          )}
        </aside>
      </section>
    </div>
  );
}
