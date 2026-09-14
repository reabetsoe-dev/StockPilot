import { useQuery } from "@tanstack/react-query";
import { Bell, LogOut, PackageCheck, Search } from "lucide-react";
import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { RoleBadge } from "../components/RoleBadge";
import { ThemeToggle } from "../components/ThemeToggle";
import { useAuth } from "../hooks/useAuth";
import { api } from "../services/api";
import type { Notification, SearchResult } from "../types/operations";
import { navigationForRole } from "../utils/navigation";

export function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const navItems = user ? navigationForRole(user.role) : [];
  const [searchTerm, setSearchTerm] = useState("");
  const trimmedSearch = searchTerm.trim();

  const { data: searchResults = [] } = useQuery({
    queryKey: ["global-search", trimmedSearch],
    queryFn: async () => (await api.get<SearchResult[]>("/search", { params: { q: trimmedSearch } })).data,
    enabled: trimmedSearch.length >= 2,
  });

  const { data: notifications = [] } = useQuery({
    queryKey: ["notifications"],
    queryFn: async () => (await api.get<Notification[]>("/notifications")).data,
    enabled: Boolean(user),
  });

  const unreadCount = notifications.filter((notification) => !notification.read).length;

  function handleLogout() {
    logout();
    navigate("/login");
  }

  function goToResult(result: SearchResult) {
    setSearchTerm("");
    navigate(result.url);
  }

  return (
    <div className="min-h-screen bg-slate-100 text-slate-950 dark:bg-slate-950 dark:text-white">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-72 border-r border-slate-200 bg-white px-6 py-6 dark:border-slate-800 dark:bg-slate-950 lg:block">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-emerald-600 text-white shadow-soft">
            <PackageCheck className="h-7 w-7" />
          </div>
          <div>
            <p className="text-xl font-bold tracking-tight">StockPilot</p>
            <p className="text-xs font-semibold uppercase text-emerald-600 dark:text-emerald-300">Distribution Ltd</p>
          </div>
        </div>

        <nav className="mt-9 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-semibold transition ${
                    isActive
                      ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-200"
                      : "text-slate-600 hover:bg-slate-100 hover:text-slate-950 dark:text-slate-300 dark:hover:bg-slate-900 dark:hover:text-white"
                  }`
                }
              >
                <Icon className="h-5 w-5" />
                {item.label}
              </NavLink>
            );
          })}
        </nav>

        {user && (
          <div className="absolute bottom-6 left-6 right-6 rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-900">
            <p className="font-semibold">{user.full_name}</p>
            <p className="mt-1 truncate text-sm text-slate-500 dark:text-slate-400">{user.email}</p>
            <div className="mt-3">
              <RoleBadge role={user.role} />
            </div>
          </div>
        )}
      </aside>

      <div className="lg:pl-72">
        <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/90 px-5 py-4 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90">
          <div className="flex items-center gap-3">
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
              <input
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
                className="h-11 w-full rounded-lg border border-slate-200 bg-slate-50 pl-12 pr-4 text-sm outline-none transition placeholder:text-slate-400 focus:border-emerald-300 focus:ring-4 focus:ring-emerald-100 dark:border-slate-800 dark:bg-slate-900 dark:focus:ring-emerald-950"
                placeholder="Search products, SKUs, suppliers, POs, requests"
              />
              {trimmedSearch.length >= 2 && (
                <div className="absolute left-0 right-0 top-14 z-30 rounded-lg border border-slate-200 bg-white p-2 shadow-xl dark:border-slate-800 dark:bg-slate-900">
                  {searchResults.length === 0 ? (
                    <p className="px-3 py-4 text-sm text-slate-500 dark:text-slate-400">No matches found.</p>
                  ) : (
                    <div className="max-h-80 overflow-y-auto">
                      {searchResults.map((result) => (
                        <button
                          key={`${result.type}-${result.label}`}
                          type="button"
                          onClick={() => goToResult(result)}
                          className="block w-full rounded-md px-3 py-3 text-left transition hover:bg-slate-100 dark:hover:bg-slate-800"
                        >
                          <span className="text-xs font-bold uppercase text-emerald-600 dark:text-emerald-300">{result.type}</span>
                          <span className="mt-1 block truncate text-sm font-semibold text-slate-950 dark:text-white">{result.label}</span>
                          <span className="mt-1 block truncate text-xs text-slate-500 dark:text-slate-400">{result.description}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
            <button
              type="button"
              onClick={() => navigate("/notifications")}
              className="relative hidden h-11 w-11 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-700 shadow-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 sm:inline-flex"
              aria-label="Notifications"
            >
              <Bell className="h-5 w-5" />
              {unreadCount > 0 && (
                <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-emerald-600 px-1 text-[10px] font-bold text-white">
                  {unreadCount}
                </span>
              )}
            </button>
            <ThemeToggle />
            <button
              type="button"
              onClick={handleLogout}
              className="inline-flex h-11 w-11 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-700 shadow-sm transition hover:border-rose-300 hover:text-rose-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200"
              aria-label="Logout"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
          <nav className="mt-4 flex gap-2 overflow-x-auto pb-1 lg:hidden">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `inline-flex h-10 shrink-0 items-center gap-2 rounded-lg border px-3 text-sm font-semibold ${
                      isActive
                        ? "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-200"
                        : "border-slate-200 bg-white text-slate-600 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300"
                    }`
                  }
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </NavLink>
              );
            })}
          </nav>
        </header>

        <main className="mx-auto max-w-7xl px-5 py-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
