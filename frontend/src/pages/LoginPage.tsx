import { ArrowLeft, ArrowRight, Lock, Mail, PackageCheck, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

const demoAccounts = [
  ["Administrator", "admin@stockpilot.local"],
  ["Inventory Manager", "inventory@stockpilot.local"],
  ["Procurement Officer", "procurement@stockpilot.local"],
  ["Warehouse Officer", "warehouse@stockpilot.local"],
  ["Department Requester", "requester@stockpilot.local"],
  ["Auditor", "auditor@stockpilot.local"],
] as const;

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("admin@stockpilot.local");
  const [password, setPassword] = useState("Demo123!");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch {
      setError("Invalid email or password.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="relative grid h-dvh overflow-hidden bg-slate-100 px-4 py-5 text-slate-950 dark:bg-slate-950 dark:text-white">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_18%,rgba(16,185,129,0.18),transparent_30%),radial-gradient(circle_at_84%_12%,rgba(59,130,246,0.16),transparent_28%)]" />

      <Link
        to="/"
        className="relative z-10 inline-flex h-10 w-fit items-center gap-2 rounded-lg border border-slate-200 bg-white/90 px-3 text-sm font-bold text-slate-700 shadow-sm backdrop-blur transition hover:border-emerald-300 hover:text-emerald-700 dark:border-slate-800 dark:bg-slate-900/90 dark:text-slate-200"
      >
        <ArrowLeft className="h-4 w-4" />
        Home
      </Link>

      <section className="relative z-10 mx-auto flex w-full max-w-md items-center">
        <div className="w-full rounded-lg border border-slate-200 bg-white/95 p-6 shadow-soft backdrop-blur dark:border-slate-800 dark:bg-slate-900/95">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-emerald-600 text-white">
                <PackageCheck className="h-6 w-6" />
              </div>
              <div>
                <p className="text-xl font-bold tracking-tight">StockPilot</p>
                <p className="text-xs font-bold uppercase text-emerald-600 dark:text-emerald-300">Distribution Ltd</p>
              </div>
            </div>
            <div className="rounded-lg bg-emerald-50 p-3 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-200">
              <ShieldCheck className="h-5 w-5" />
            </div>
          </div>

          <div className="mt-6">
            <p className="text-sm font-bold uppercase text-emerald-700 dark:text-emerald-300">Welcome back</p>
            <h1 className="mt-2 text-3xl font-bold tracking-tight">Access StockPilot</h1>
            <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">
              Select a demo role or enter credentials. All demo accounts use Demo123!.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <label className="block">
              <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">Demo account</span>
              <select
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="mt-2 h-11 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm outline-none transition focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:focus:ring-emerald-950"
              >
                {demoAccounts.map(([role, account]) => (
                  <option key={account} value={account}>
                    {role} - {account}
                  </option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">Email</span>
              <span className="mt-2 flex h-11 items-center gap-3 rounded-lg border border-slate-200 bg-white px-3 focus-within:border-emerald-300 focus-within:ring-4 focus-within:ring-emerald-100 dark:border-slate-700 dark:bg-slate-950 dark:focus-within:ring-emerald-950">
                <Mail className="h-5 w-5 text-slate-400" />
                <input
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  className="w-full bg-transparent text-sm outline-none"
                  type="email"
                  autoComplete="email"
                />
              </span>
            </label>

            <label className="block">
              <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">Password</span>
              <span className="mt-2 flex h-11 items-center gap-3 rounded-lg border border-slate-200 bg-white px-3 focus-within:border-emerald-300 focus-within:ring-4 focus-within:ring-emerald-100 dark:border-slate-700 dark:bg-slate-950 dark:focus-within:ring-emerald-950">
                <Lock className="h-5 w-5 text-slate-400" />
                <input
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  className="w-full bg-transparent text-sm outline-none"
                  type="password"
                  autoComplete="current-password"
                />
              </span>
            </label>

            {error && <p className="rounded-lg bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700 dark:bg-rose-950 dark:text-rose-200">{error}</p>}

            <button
              type="submit"
              disabled={submitting}
              className="inline-flex h-11 w-full items-center justify-center gap-3 rounded-lg bg-emerald-600 px-5 text-sm font-bold text-white shadow-sm transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {submitting ? "Signing in" : "Sign in"}
              <ArrowRight className="h-5 w-5" />
            </button>
          </form>
        </div>
      </section>
    </main>
  );
}
