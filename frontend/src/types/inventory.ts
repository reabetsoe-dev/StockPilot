import type { Product, Warehouse } from "./catalog";

export type StockStatus = "NORMAL" | "LOW_STOCK" | "OUT_OF_STOCK";

export type StockMovementType =
  | "OPENING_BALANCE"
  | "GOODS_RECEIPT"
  | "STOCK_ISSUE"
  | "TRANSFER_OUT"
  | "TRANSFER_IN"
  | "ADJUSTMENT_INCREASE"
  | "ADJUSTMENT_DECREASE"
  | "RETURN";

export interface InventoryItem {
  product_id: number;
  sku: string;
  product_name: string;
  category_name: string;
  preferred_supplier_name: string | null;
  unit_of_measure: string;
  reorder_level: number;
  total_on_hand: number;
  total_reserved: number;
  available_quantity: number;
  inventory_value: string;
  stock_status: StockStatus;
  warehouse_count: number;
}

export interface LowStockItem extends InventoryItem {
  suggested_reorder_quantity: number;
}

export interface InventoryBalance {
  id: number;
  warehouse: Warehouse;
  product_id: number;
  quantity_on_hand: number;
  quantity_reserved: number;
  available_quantity: number;
  inventory_value: string;
  stock_status: StockStatus;
  updated_at: string;
}

export interface StockMovement {
  id: number;
  product_id: number;
  product_sku: string;
  product_name: string;
  warehouse_id: number;
  warehouse_code: string;
  warehouse_name: string;
  movement_type: StockMovementType;
  quantity: number;
  reference_type: string | null;
  reference_id: string | null;
  reason: string;
  performed_by: number | null;
  performed_by_name: string | null;
  created_at: string;
}

export interface ProductInventoryDetail {
  product: Product;
  total_on_hand: number;
  total_reserved: number;
  available_quantity: number;
  inventory_value: string;
  stock_status: StockStatus;
  balances: InventoryBalance[];
  recent_movements: StockMovement[];
}
