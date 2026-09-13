import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string | number;
  tone: "emerald" | "blue" | "amber" | "slate";
  icon: LucideIcon;
}

const toneClasses = {
  emerald: "bg-emerald-50 text-emerald-700 ring-emerald-100 dark:bg-emerald-950 dark:text-emerald-200 dark:ring-emerald-900",
  blue: "bg-blue-50 text-blue-700 ring-blue-100 dark:bg-blue-950 dark:text-blue-200 dark:ring-blue-900",
  amber: "bg-amber-50 text-amber-700 ring-amber-100 dark:bg-amber-950 dark:text-amber-200 dark:ring-amber-900",
  slate: "bg-slate-100 text-slate-700 ring-slate-200 dark:bg-slate-800 dark:text-slate-200 dark:ring-slate-700",
};

export function StatCard({ label, value, tone, icon: Icon }: StatCardProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</p>
          <p className="mt-2 text-3xl font-bold text-slate-950 dark:text-white">{value}</p>
        </div>
        <div className={`inline-flex h-12 w-12 items-center justify-center rounded-lg ring-1 ${toneClasses[tone]}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </div>
  );
}
