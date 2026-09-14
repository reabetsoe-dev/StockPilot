type BadgeTone = "emerald" | "amber" | "blue" | "slate" | "rose";

interface StatusBadgeProps {
  label: string;
  tone?: BadgeTone;
}

const toneClasses: Record<BadgeTone, string> = {
  emerald: "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-200",
  amber: "border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-200",
  blue: "border-blue-200 bg-blue-50 text-blue-700 dark:border-blue-800 dark:bg-blue-950 dark:text-blue-200",
  slate: "border-slate-200 bg-slate-100 text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200",
  rose: "border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-800 dark:bg-rose-950 dark:text-rose-200",
};

export function StatusBadge({ label, tone = "slate" }: StatusBadgeProps) {
  return (
    <span className={`inline-flex rounded-md border px-2.5 py-1 text-xs font-bold uppercase ${toneClasses[tone]}`}>
      {label}
    </span>
  );
}
