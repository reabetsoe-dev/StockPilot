import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bell, CheckCircle2, MailOpen } from "lucide-react";
import { Link } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { api } from "../services/api";
import type { Notification } from "../types/operations";
import { formatDateTime } from "../utils/format";

export function NotificationsPage() {
  const queryClient = useQueryClient();
  const { data = [], isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: async () => (await api.get<Notification[]>("/notifications")).data,
  });

  const markReadMutation = useMutation({
    mutationFn: async (notificationId: number) => (await api.post<Notification>(`/notifications/${notificationId}/read`)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const unreadCount = data.filter((notification) => !notification.read).length;

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Internal alerts"
        title="Notifications"
        description="Operational notices for approvals, purchase orders, low-stock events, warehouse movements, and completed workflow actions."
        icon={Bell}
        meta={`${unreadCount} unread`}
      />

      <section className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        {!isLoading && data.length === 0 ? (
          <div className="p-5">
            <EmptyState icon={MailOpen} title="No notifications" message="Workflow and inventory alerts will appear here." />
          </div>
        ) : (
          <div className="divide-y divide-slate-200 dark:divide-slate-800">
            {data.map((notification) => (
              <article key={notification.id} className="flex flex-col gap-4 p-5 lg:flex-row lg:items-start lg:justify-between">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <StatusBadge label={notification.read ? "Read" : "Unread"} tone={notification.read ? "slate" : "emerald"} />
                    {notification.entity_type && <span className="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">{notification.entity_type}</span>}
                    <span className="text-xs text-slate-500 dark:text-slate-400">{formatDateTime(notification.created_at)}</span>
                  </div>
                  <h2 className="mt-3 text-lg font-bold text-slate-950 dark:text-white">{notification.title}</h2>
                  <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600 dark:text-slate-300">{notification.message}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {notification.action_url && (
                    <Link to={notification.action_url} className="inline-flex h-10 items-center rounded-lg border border-slate-200 px-3 text-sm font-bold text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800">
                      Open
                    </Link>
                  )}
                  {!notification.read && (
                    <button
                      type="button"
                      onClick={() => markReadMutation.mutate(notification.id)}
                      className="inline-flex h-10 items-center gap-2 rounded-lg bg-emerald-600 px-3 text-sm font-bold text-white hover:bg-emerald-700 disabled:bg-slate-400"
                      disabled={markReadMutation.isPending}
                    >
                      <CheckCircle2 className="h-4 w-4" />
                      Mark read
                    </button>
                  )}
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
