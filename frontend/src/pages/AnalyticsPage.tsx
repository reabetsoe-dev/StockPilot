import { useQuery } from "@tanstack/react-query";
import { Activity, AlertTriangle, BarChart3, Boxes, PackageCheck, ShoppingCart, Truck } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { StatCard } from "../components/StatCard";
import { api } from "../services/api";
import type { AnalyticsSummary, NamedMetric } from "../types/operations";
import { formatMoney } from "../utils/format";

const palette = ["#059669", "#2563eb", "#d97706", "#7c3aed", "#db2777", "#475569"];

function toNumber(value: string | number): number {
  return typeof value === "string" ? Number(value) : value;
}

function metricData(metrics: NamedMetric[], label: string) {
  return metrics.map((metric) => ({
    name: metric.name,
    [label]: toNumber(metric.value),
  }));
}

interface ChartPanelProps {
  title: string;
  children: JSX.Element;
}

function ChartPanel({ title, children }: ChartPanelProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <h2 className="text-lg font-bold text-slate-950 dark:text-white">{title}</h2>
      <div className="mt-5 h-80">{children}</div>
    </section>
  );
}

export function AnalyticsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["analytics-dashboard"],
    queryFn: async () => (await api.get<AnalyticsSummary>("/analytics/dashboard")).data,
  });

  if (!isLoading && !data) {
    return <EmptyState icon={BarChart3} title="Analytics unavailable" message="Refresh the page to reload operational metrics." />;
  }

  const categoryData = metricData(data?.inventory_value_by_category ?? [], "value");
  const warehouseData = metricData(data?.stock_by_warehouse ?? [], "units");
  const supplierData = metricData(data?.purchases_by_supplier ?? [], "value");
  const productData = metricData(data?.top_purchased_products ?? [], "units");
  const statusData = metricData(data?.purchase_order_status ?? [], "orders");

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Operations intelligence"
        title="Analytics"
        description="Backend-calculated inventory valuation, procurement activity, receiving throughput, transfer volume, and reorder risk."
        icon={BarChart3}
        meta={isLoading ? "Loading metrics" : "Live from ledger"}
      />

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Inventory value" value={isLoading ? "..." : formatMoney(data?.inventory_value ?? 0)} tone="emerald" icon={Activity} />
        <StatCard label="Low stock items" value={isLoading ? "..." : data?.low_stock_items ?? 0} tone="amber" icon={AlertTriangle} />
        <StatCard label="Open purchase orders" value={isLoading ? "..." : data?.open_purchase_orders ?? 0} tone="blue" icon={ShoppingCart} />
        <StatCard label="Warehouse transfers" value={isLoading ? "..." : data?.warehouse_transfers ?? 0} tone="slate" icon={Truck} />
      </section>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Pending requests" value={isLoading ? "..." : data?.pending_purchase_requests ?? 0} tone="amber" icon={Boxes} />
        <StatCard label="Goods receipts" value={isLoading ? "..." : data?.goods_received ?? 0} tone="emerald" icon={PackageCheck} />
        <StatCard label="Out of stock" value={isLoading ? "..." : data?.out_of_stock_items ?? 0} tone="rose" icon={AlertTriangle} />
        <StatCard label="Chart groups" value={isLoading ? "..." : categoryData.length + warehouseData.length} tone="blue" icon={BarChart3} />
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <ChartPanel title="Inventory Value by Category">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={categoryData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tickFormatter={(value) => `M${Number(value).toLocaleString("en-US")}`} />
              <Tooltip formatter={(value) => formatMoney(Number(value))} />
              <Bar dataKey="value" fill="#059669" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartPanel>

        <ChartPanel title="Stock Units by Warehouse">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={warehouseData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="units" fill="#2563eb" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartPanel>

        <ChartPanel title="Purchase Value by Supplier">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={supplierData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tickFormatter={(value) => `M${Number(value).toLocaleString("en-US")}`} />
              <Tooltip formatter={(value) => formatMoney(Number(value))} />
              <Bar dataKey="value" fill="#d97706" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartPanel>

        <ChartPanel title="Purchase Order Status">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={statusData} dataKey="orders" nameKey="name" innerRadius={58} outerRadius={108} paddingAngle={3}>
                {statusData.map((entry, index) => (
                  <Cell key={entry.name} fill={palette[index % palette.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </ChartPanel>

        <ChartPanel title="Top Purchased Products">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={productData} layout="vertical" margin={{ left: 24 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis type="number" allowDecimals={false} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 12 }} width={130} />
              <Tooltip />
              <Bar dataKey="units" fill="#7c3aed" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartPanel>
      </section>
    </div>
  );
}
