import { Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "./hooks/useAuth";
import { AppLayout } from "./layouts/AppLayout";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { AuditLogsPage } from "./pages/AuditLogsPage";
import { CategoriesPage } from "./pages/CategoriesPage";
import { DashboardPage } from "./pages/DashboardPage";
import { DepartmentsPage } from "./pages/DepartmentsPage";
import { GoodsReceivingPage } from "./pages/GoodsReceivingPage";
import { InventoryPage } from "./pages/InventoryPage";
import { LandingPage } from "./pages/LandingPage";
import { LoginPage } from "./pages/LoginPage";
import { LowStockPage } from "./pages/LowStockPage";
import { NotificationsPage } from "./pages/NotificationsPage";
import { ProductsPage } from "./pages/ProductsPage";
import { ProductStockDetailsPage } from "./pages/ProductStockDetailsPage";
import { PurchaseOrdersPage } from "./pages/PurchaseOrdersPage";
import { PurchaseRequestsPage } from "./pages/PurchaseRequestsPage";
import { SettingsPage } from "./pages/SettingsPage";
import { StockAdjustmentsPage } from "./pages/StockAdjustmentsPage";
import { StockMovementsPage } from "./pages/StockMovementsPage";
import { StockRequestsPage } from "./pages/StockRequestsPage";
import { StockTransfersPage } from "./pages/StockTransfersPage";
import { SuppliersPage } from "./pages/SuppliersPage";
import { UsersPage } from "./pages/UsersPage";
import { WarehousesPage } from "./pages/WarehousesPage";

function ProtectedRoute({ children }: { children: JSX.Element }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <div className="rounded-lg border border-white/10 bg-white/10 px-5 py-4 text-sm font-semibold">
          Loading StockPilot
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/users" element={<UsersPage />} />
        <Route path="/departments" element={<DepartmentsPage />} />
        <Route path="/products" element={<ProductsPage />} />
        <Route path="/categories" element={<CategoriesPage />} />
        <Route path="/suppliers" element={<SuppliersPage />} />
        <Route path="/warehouses" element={<WarehousesPage />} />
        <Route path="/inventory" element={<InventoryPage />} />
        <Route path="/inventory/:productId" element={<ProductStockDetailsPage />} />
        <Route path="/stock-movements" element={<StockMovementsPage />} />
        <Route path="/purchase-requests" element={<PurchaseRequestsPage />} />
        <Route path="/purchase-orders" element={<PurchaseOrdersPage />} />
        <Route path="/goods-receiving" element={<GoodsReceivingPage />} />
        <Route path="/stock-requests" element={<StockRequestsPage />} />
        <Route path="/stock-transfers" element={<StockTransfersPage />} />
        <Route path="/stock-adjustments" element={<StockAdjustmentsPage />} />
        <Route path="/low-stock" element={<LowStockPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/audit-logs" element={<AuditLogsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
