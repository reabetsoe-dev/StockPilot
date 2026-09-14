import {
  BarChart3,
  Building2,
  ClipboardList,
  FileClock,
  LayoutDashboard,
  Layers3,
  PackageSearch,
  PackagePlus,
  Settings,
  ShieldCheck,
  ShoppingCart,
  Truck,
  Users,
  Warehouse,
} from "lucide-react";

import type { UserRole } from "../types/auth";

export interface NavigationItem {
  label: string;
  path: string;
  roles: UserRole[];
  icon: typeof LayoutDashboard;
}

const allRoles: UserRole[] = [
  "ADMINISTRATOR",
  "INVENTORY_MANAGER",
  "PROCUREMENT_OFFICER",
  "WAREHOUSE_OFFICER",
  "DEPARTMENT_REQUESTER",
  "AUDITOR",
];

export const navigationItems: NavigationItem[] = [
  { label: "Dashboard", path: "/dashboard", roles: allRoles, icon: LayoutDashboard },
  {
    label: "Products",
    path: "/products",
    roles: ["ADMINISTRATOR", "INVENTORY_MANAGER", "PROCUREMENT_OFFICER", "WAREHOUSE_OFFICER", "DEPARTMENT_REQUESTER", "AUDITOR"],
    icon: PackagePlus,
  },
  {
    label: "Categories",
    path: "/categories",
    roles: ["ADMINISTRATOR", "INVENTORY_MANAGER", "AUDITOR"],
    icon: Layers3,
  },
  {
    label: "Suppliers",
    path: "/suppliers",
    roles: ["ADMINISTRATOR", "PROCUREMENT_OFFICER", "INVENTORY_MANAGER", "AUDITOR"],
    icon: Truck,
  },
  {
    label: "Inventory",
    path: "/inventory",
    roles: ["ADMINISTRATOR", "INVENTORY_MANAGER", "WAREHOUSE_OFFICER", "AUDITOR"],
    icon: PackageSearch,
  },
  {
    label: "Stock Requests",
    path: "/stock-requests",
    roles: ["ADMINISTRATOR", "WAREHOUSE_OFFICER", "DEPARTMENT_REQUESTER"],
    icon: ClipboardList,
  },
  {
    label: "Purchase Orders",
    path: "/purchase-orders",
    roles: ["ADMINISTRATOR", "PROCUREMENT_OFFICER", "AUDITOR"],
    icon: ShoppingCart,
  },
  {
    label: "Goods Receiving",
    path: "/goods-receiving",
    roles: ["ADMINISTRATOR", "WAREHOUSE_OFFICER", "AUDITOR"],
    icon: ClipboardList,
  },
  {
    label: "Warehouses",
    path: "/warehouses",
    roles: ["ADMINISTRATOR", "INVENTORY_MANAGER", "WAREHOUSE_OFFICER", "AUDITOR"],
    icon: Warehouse,
  },
  {
    label: "Analytics",
    path: "/analytics",
    roles: ["ADMINISTRATOR", "INVENTORY_MANAGER", "PROCUREMENT_OFFICER", "AUDITOR"],
    icon: BarChart3,
  },
  {
    label: "Audit Logs",
    path: "/audit-logs",
    roles: ["ADMINISTRATOR", "AUDITOR"],
    icon: FileClock,
  },
  { label: "Users", path: "/users", roles: ["ADMINISTRATOR"], icon: Users },
  { label: "Departments", path: "/departments", roles: ["ADMINISTRATOR"], icon: Building2 },
  { label: "Settings", path: "/settings", roles: ["ADMINISTRATOR"], icon: Settings },
  { label: "Controls", path: "/controls", roles: ["ADMINISTRATOR", "AUDITOR"], icon: ShieldCheck },
];

export function navigationForRole(role: UserRole): NavigationItem[] {
  return navigationItems.filter((item) => item.roles.includes(role));
}
