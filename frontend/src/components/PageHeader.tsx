import type { LucideIcon } from "lucide-react";

interface PageHeaderProps {
  eyebrow: string;
  title: string;
  description: string;
  icon: LucideIcon;
  meta?: string;
}

export function PageHeader({ eyebrow, title, description, icon: Icon, meta }: PageHeaderProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
        <div className="max-w-3xl">
          <p className="text-sm font-bold uppercase text-emerald-600 dark:text-emerald-300">{eyebrow}</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950 dark:text-white">{title}</h1>
          <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{description}</p>
        </div>
        <div className="inline-flex items-center gap-3 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-100">
          <Icon className="h-5 w-5" />
          <span className="text-sm font-semibold">{meta ?? "Catalog ready"}</span>
        </div>
      </div>
    </section>
  );
}
