import { ArrowRight, Lock, Mail, PackageCheck, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

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
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(16,185,129,0.28),transparent_32%),radial-gradient(circle_at_85%_15%,rgba(59,130,246,0.20),transparent_26%),linear-gradient(135deg,#06111f_0%,#101827_48%,#06251f_100%)]" />
      <div className="relative mx-auto grid min-h-screen max-w-6xl items-center gap-10 px-6 py-10 lg:grid-cols-[1.05fr_0.95fr]">
        <section>
          <div className="inline-flex items-center gap-3 rounded-lg border border-white/15 bg-white/10 px-4 py-3 backdrop-blur">
            <PackageCheck className="h-6 w-6 text-emerald-300" />
            <span className="text-sm font-semibold uppercase tracking-[0.18em] text-emerald-100">StockPilot</span>
          </div>
          <h1 className="mt-7 max-w-2xl text-5xl font-bold leading-tight tracking-tight">
            Inventory, procurement, and warehouse control in one operating view.
          </h1>
          <p className="mt-5 max-w-xl text-lg leading-8 text-slate-300">
            A Phase 1 platform foundation for StockPilot Distribution Ltd with secure access,
            role-aware navigation, seeded users, and a backend-driven dashboard.
          </p>
          <div className="mt-8 grid max-w-xl gap-3 sm:grid-cols-3">
            {["JWT auth", "SQLite local", "RBAC ready"].map((item) => (
              <div key={item} className="rounded-lg border border-white/10 bg-white/10 p-4 text-sm font-semibold backdrop-blur">
                {item}
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-lg border border-white/15 bg-white/95 p-7 text-slate-950 shadow-soft backdrop-blur">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm font-bold uppercase text-emerald-700">Welcome back</p>
              <h2 className="mt-2 text-3xl font-bold">Access StockPilot</h2>
              <p className="mt-2 text-sm text-slate-500">All demo accounts use Demo123!.</p>
            </div>
            <div className="rounded-lg bg-emerald-50 p-3 text-emerald-700">
              <ShieldCheck className="h-6 w-6" />
            </div>
          </div>

          <form onSubmit={handleSubmit} className="mt-7 space-y-5">
            <label className="block">
              <span className="text-sm font-semibold text-slate-700">Email</span>
              <span className="mt-2 flex h-12 items-center gap-3 rounded-lg border border-slate-200 bg-white px-4 focus-within:border-emerald-300 focus-within:ring-4 focus-within:ring-emerald-100">
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
              <span className="text-sm font-semibold text-slate-700">Password</span>
              <span className="mt-2 flex h-12 items-center gap-3 rounded-lg border border-slate-200 bg-white px-4 focus-within:border-emerald-300 focus-within:ring-4 focus-within:ring-emerald-100">
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

            {error && <p className="rounded-lg bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">{error}</p>}

            <button
              type="submit"
              disabled={submitting}
              className="inline-flex h-12 w-full items-center justify-center gap-3 rounded-lg bg-emerald-600 px-5 text-sm font-bold text-white shadow-sm transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {submitting ? "Signing in" : "Sign in"}
              <ArrowRight className="h-5 w-5" />
            </button>
          </form>

          <div className="mt-7">
            <p className="text-sm font-bold text-slate-700">Demo credentials</p>
            <div className="mt-3 grid gap-2">
              {demoAccounts.map(([role, account]) => (
                <button
                  type="button"
                  key={account}
                  onClick={() => setEmail(account)}
                  className="flex items-center justify-between rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-left text-sm transition hover:border-emerald-300 hover:bg-emerald-50"
                >
                  <span className="font-semibold">{role}</span>
                  <span className="text-slate-500">{account}</span>
                </button>
              ))}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
