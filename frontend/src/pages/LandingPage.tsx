import { ArrowRight, PackageCheck } from "lucide-react";
import { Link } from "react-router-dom";

export function LandingPage() {
  return (
    <main
      className="relative h-dvh overflow-hidden bg-slate-950 bg-cover bg-center text-white"
      style={{
        backgroundImage:
          "linear-gradient(135deg, rgba(2, 6, 23, 0.84), rgba(5, 46, 35, 0.7)), url('https://images.unsplash.com/photo-1553413077-190dd305871c?auto=format&fit=crop&w=2400&q=80')",
      }}
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_15%,rgba(16,185,129,0.35),transparent_28%),radial-gradient(circle_at_80%_20%,rgba(59,130,246,0.22),transparent_26%)]" />

      <section className="relative mx-auto flex h-dvh max-w-5xl flex-col items-center justify-center px-6 text-center">
        <div className="inline-flex items-center gap-3 rounded-lg border border-white/20 bg-white/10 px-4 py-3 shadow-soft backdrop-blur">
          <PackageCheck className="h-6 w-6 text-emerald-300" />
          <span className="text-sm font-bold uppercase tracking-[0.18em] text-emerald-100">StockPilot</span>
        </div>

        <h1 className="mt-8 max-w-4xl text-5xl font-bold leading-tight tracking-tight md:text-7xl">
          Inventory, procurement, and warehouse control in one operating view.
        </h1>
        <p className="mt-6 max-w-2xl text-base leading-8 text-slate-200 md:text-lg">
          A lightweight ERP-style portfolio platform for stock ledgers, purchase workflows, receiving, transfers,
          reorder alerts, analytics, and audit visibility.
        </p>

        <Link
          to="/login"
          className="mt-9 inline-flex h-12 items-center justify-center gap-3 rounded-lg bg-emerald-500 px-7 text-sm font-bold text-slate-950 shadow-soft transition hover:bg-emerald-300 focus:outline-none focus:ring-4 focus:ring-emerald-200/50"
        >
          Get Started
          <ArrowRight className="h-5 w-5" />
        </Link>
      </section>
    </main>
  );
}
