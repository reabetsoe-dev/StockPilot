import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { Category, Product, Supplier, Warehouse } from "../types/catalog";
import type { InventoryItem } from "../types/inventory";
import { GoodsReceivingPage } from "./GoodsReceivingPage";
import { InventoryPage } from "./InventoryPage";
import { ProductsPage } from "./ProductsPage";
import { PurchaseOrdersPage } from "./PurchaseOrdersPage";
import { StockTransfersPage } from "./StockTransfersPage";

const mocks = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}));

vi.mock("../services/api", () => ({
  api: mocks,
}));

vi.mock("../hooks/useAuth", () => ({
  useAuth: () => ({
    user: {
      id: 1,
      full_name: "Admin User",
      email: "admin@stockpilot.local",
      role: "ADMINISTRATOR",
      department_id: 1,
      department_name: "Administration",
      active: true,
    },
  }),
}));

const category: Category = {
  id: 1,
  name: "Computers",
  description: "Computer equipment",
  active: true,
  created_at: "2026-09-14T08:00:00Z",
  updated_at: "2026-09-14T08:00:00Z",
};

const supplier: Supplier = {
  id: 1,
  supplier_code: "SUP-001",
  name: "Apex Office Supply",
  contact_person: "Lerato Mokoena",
  email: "supply@example.test",
  phone: "555-0100",
  address: "Demo address",
  tax_reference: "TX-001",
  payment_terms: "30 days",
  active: true,
  created_at: "2026-09-14T08:00:00Z",
  updated_at: "2026-09-14T08:00:00Z",
};

const warehouseA: Warehouse = {
  id: 1,
  code: "CENTRAL",
  name: "Central Warehouse",
  location: "Maseru",
  description: "Main site",
  active: true,
  created_at: "2026-09-14T08:00:00Z",
  updated_at: "2026-09-14T08:00:00Z",
};

const warehouseB: Warehouse = {
  ...warehouseA,
  id: 2,
  code: "NORTH",
  name: "North Warehouse",
};

const product: Product = {
  id: 1,
  sku: "LAP-HP-840",
  barcode: "BAR-LAP-HP-840",
  name: "HP EliteBook 840",
  description: "Business laptop",
  category_id: 1,
  unit_of_measure: "Each",
  cost_price: "14500.00",
  selling_price: "17200.00",
  reorder_level: 5,
  preferred_supplier_id: 1,
  active: true,
  category,
  preferred_supplier: supplier,
  created_at: "2026-09-14T08:00:00Z",
  updated_at: "2026-09-14T08:00:00Z",
};

const inventoryItem: InventoryItem = {
  product_id: 1,
  sku: "LAP-HP-840",
  product_name: "HP EliteBook 840",
  category_name: "Computers",
  preferred_supplier_name: "Apex Office Supply",
  unit_of_measure: "Each",
  reorder_level: 5,
  total_on_hand: 5,
  total_reserved: 1,
  available_quantity: 4,
  inventory_value: "72500.00",
  stock_status: "LOW_STOCK",
  warehouse_count: 1,
};

function renderWithClient(children: ReactNode) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  mocks.get.mockReset();
  mocks.post.mockReset();
  mocks.get.mockImplementation((url: string) => {
    const dataByUrl: Record<string, unknown> = {
      "/categories": [category],
      "/suppliers": [supplier],
      "/warehouses": [warehouseA, warehouseB],
      "/products": [product],
      "/inventory": [inventoryItem],
      "/purchase-requests": [],
      "/purchase-orders": [
        {
          id: 1,
          po_number: "PO-2026-9999",
          supplier_id: 1,
          supplier_name: "Apex Office Supply",
          purchase_request_id: null,
          purchase_request_reference: null,
          order_date: "2026-09-14",
          expected_delivery_date: null,
          status: "ISSUED",
          subtotal: "14500.00",
          tax: "2175.00",
          total: "16675.00",
          notes: null,
          created_by_name: "Admin User",
          created_at: "2026-09-14T08:00:00Z",
          updated_at: "2026-09-14T08:00:00Z",
          items: [
            {
              id: 1,
              product_id: 1,
              product_sku: "LAP-HP-840",
              product_name: "HP EliteBook 840",
              description: "Business laptop",
              quantity_ordered: 10,
              quantity_received: 0,
              unit_price: "14500.00",
              line_total: "145000.00",
              remaining_quantity: 10,
            },
          ],
        },
      ],
      "/goods-receipts": [],
      "/transfers": [],
    };

    return Promise.resolve({ data: dataByUrl[url] ?? [] });
  });
});

describe("operations pages", () => {
  it("shows the product form", async () => {
    renderWithClient(<ProductsPage />);

    expect(await screen.findByRole("heading", { name: /New product/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Search name, SKU, or barcode/i)).toBeInTheDocument();
  });

  it("shows low-stock status in the inventory table", async () => {
    renderWithClient(<InventoryPage />);

    expect(await screen.findByText("LAP-HP-840")).toBeInTheDocument();
    expect(screen.getAllByText("Low stock").length).toBeGreaterThan(0);
  });

  it("shows the purchase order form", async () => {
    renderWithClient(<PurchaseOrdersPage />);

    expect(await screen.findByRole("heading", { name: /New purchase order/i })).toBeInTheDocument();
    expect(screen.getByText("Create order")).toBeInTheDocument();
  });

  it("shows goods receipt inputs for issued purchase orders", async () => {
    renderWithClient(<GoodsReceivingPage />);

    expect(await screen.findByText(/PO-2026-9999/i)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Record goods/i })).toBeInTheDocument();
  });

  it("shows warehouse transfer controls", async () => {
    renderWithClient(<StockTransfersPage />);

    expect(await screen.findByRole("heading", { name: /New transfer/i })).toBeInTheDocument();
    expect(screen.getByText("Create transfer")).toBeInTheDocument();
  });
});
