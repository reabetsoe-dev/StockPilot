import type { InputHTMLAttributes, SelectHTMLAttributes, TextareaHTMLAttributes } from "react";

interface FieldProps {
  label: string;
}

export function FormInput({ label, className = "", ...props }: FieldProps & InputHTMLAttributes<HTMLInputElement>) {
  return (
    <label className="block">
      <span className="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">{label}</span>
      <input
        {...props}
        className={`mt-2 h-11 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-950 outline-none transition placeholder:text-slate-400 focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:focus:ring-emerald-950 ${className}`}
      />
    </label>
  );
}

export function FormSelect({ label, className = "", ...props }: FieldProps & SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <label className="block">
      <span className="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">{label}</span>
      <select
        {...props}
        className={`mt-2 h-11 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-950 outline-none transition focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:focus:ring-emerald-950 ${className}`}
      />
    </label>
  );
}

export function FormTextarea({ label, className = "", ...props }: FieldProps & TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <label className="block">
      <span className="text-xs font-bold uppercase text-slate-500 dark:text-slate-400">{label}</span>
      <textarea
        {...props}
        className={`mt-2 min-h-24 w-full rounded-lg border border-slate-200 bg-white px-3 py-3 text-sm text-slate-950 outline-none transition placeholder:text-slate-400 focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:focus:ring-emerald-950 ${className}`}
      />
    </label>
  );
}
