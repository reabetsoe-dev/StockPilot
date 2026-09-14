import { Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "./hooks/useAuth";
import { AppLayout } from "./layouts/AppLayout";
import { CategoriesPage } from "./pages/CategoriesPage";
import { DashboardPage } from "./pages/DashboardPage";
import { DepartmentsPage } from "./pages/DepartmentsPage";
import { InventoryPage } from "./pages/InventoryPage";
import { LoginPage } from "./pages/LoginPage";
import { PlaceholderPage } from "./pages/PlaceholderPage";
import { ProductsPage } from "./pages/ProductsPage";
import { ProductStockDetailsPage } from "./pages/ProductStockDetailsPage";
import { StockMovementsPage } from "./pages/StockMovementsPage";
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
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
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
        <Route path="/stock-requests" element={<PlaceholderPage title="Stock requests" />} />
        <Route path="/purchase-orders" element={<PlaceholderPage title="Purchase orders" />} />
        <Route path="/goods-receiving" element={<PlaceholderPage title="Goods receiving" />} />
        <Route path="/analytics" element={<PlaceholderPage title="Analytics" />} />
        <Route path="/audit-logs" element={<PlaceholderPage title="Audit logs" />} />
        <Route path="/settings" element={<PlaceholderPage title="Settings" />} />
        <Route path="/controls" element={<PlaceholderPage title="Controls" />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
