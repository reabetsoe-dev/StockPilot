export type PurchaseRequestStatus = "DRAFT" | "SUBMITTED" | "APPROVED" | "REJECTED" | "CONVERTED_TO_PO" | "CANCELLED";
export type PurchaseRequestPriority = "LOW" | "NORMAL" | "HIGH" | "URGENT";
export type PurchaseOrderStatus = "DRAFT" | "ISSUED" | "PARTIALLY_RECEIVED" | "RECEIVED" | "CANCELLED";
export type StockRequestStatus = "SUBMITTED" | "APPROVED" | "REJECTED" | "ISSUED" | "CANCELLED";
export type StockTransferStatus = "DRAFT" | "IN_TRANSIT" | "COMPLETED" | "CANCELLED";
export type StockAdjustmentType = "INCREASE" | "DECREASE";

export interface PurchaseRequestItem {
  id: number;
  product_id: number | null;
  product_sku: string | null;
  product_name: string | null;
  description: string;
  quantity: number;
  estimated_unit_price: string;
}

export interface PurchaseRequest {
  id: number;
  reference_number: string;
  requested_by: number;
  requested_by_name: string;
  department_id: number;
  department_name: string;
  purpose: string;
  priority: PurchaseRequestPriority;
  status: PurchaseRequestStatus;
  created_at: string;
  updated_at: string;
  items: PurchaseRequestItem[];
}

export interface PurchaseOrderItem {
  id: number;
  product_id: number;
  product_sku: string;
  product_name: string;
  description: string;
  quantity_ordered: number;
  quantity_received: number;
  unit_price: string;
  line_total: string;
  remaining_quantity: number;
}

export interface PurchaseOrder {
  id: number;
  po_number: string;
  supplier_id: number;
  supplier_name: string;
  purchase_request_id: number | null;
  purchase_request_reference: string | null;
  order_date: string;
  expected_delivery_date: string | null;
  status: PurchaseOrderStatus;
  subtotal: string;
  tax: string;
  total: string;
  notes: string | null;
  created_by_name: string;
  created_at: string;
  updated_at: string;
  items: PurchaseOrderItem[];
}

export interface GoodsReceipt {
  id: number;
  receipt_number: string;
  purchase_order_id: number;
  purchase_order_number: string;
  warehouse_id: number;
  warehouse_name: string;
  received_by_name: string;
  received_date: string;
  notes: string | null;
  created_at: string;
  items: Array<{
    id: number;
    product_sku: string;
    product_name: string;
    quantity_received: number;
    quantity_rejected: number;
  }>;
}

export interface StockRequest {
  id: number;
  reference_number: string;
  department_name: string;
  requested_by_name: string;
  source_warehouse_id: number;
  source_warehouse_name: string;
  purpose: string;
  status: StockRequestStatus;
  issued_by_name: string | null;
  issued_at: string | null;
  created_at: string;
  items: Array<{
    id: number;
    product_id: number;
    product_sku: string;
    product_name: string;
    quantity_requested: number;
    quantity_issued: number;
  }>;
}

export interface StockTransfer {
  id: number;
  transfer_number: string;
  source_warehouse_id: number;
  source_warehouse_name: string;
  destination_warehouse_id: number;
  destination_warehouse_name: string;
  status: StockTransferStatus;
  requested_by_name: string;
  completed_by_name: string | null;
  completed_at: string | null;
  created_at: string;
  items: Array<{
    id: number;
    product_id: number;
    product_sku: string;
    product_name: string;
    quantity: number;
  }>;
}

export interface StockAdjustment {
  id: number;
  adjustment_number: string;
  product_id: number;
  product_sku: string;
  product_name: string;
  warehouse_id: number;
  warehouse_name: string;
  adjustment_type: StockAdjustmentType;
  quantity: number;
  reason: string;
  notes: string | null;
  performed_by_name: string;
  created_at: string;
}

export interface Notification {
  id: number;
  title: string;
  message: string;
  entity_type: string | null;
  entity_id: string | null;
  action_url: string | null;
  read: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuditLog {
  id: number;
  user_id: number | null;
  user_name: string | null;
  action: string;
  entity_type: string;
  entity_id: string | null;
  description: string;
  created_at: string;
}

export interface NamedMetric {
  name: string;
  value: string | number;
}

export interface AnalyticsSummary {
  inventory_value: string;
  low_stock_items: number;
  out_of_stock_items: number;
  pending_purchase_requests: number;
  open_purchase_orders: number;
  goods_received: number;
  warehouse_transfers: number;
  inventory_value_by_category: NamedMetric[];
  stock_by_warehouse: NamedMetric[];
  purchase_order_status: NamedMetric[];
  purchases_by_supplier: NamedMetric[];
  top_purchased_products: NamedMetric[];
}

export interface SearchResult {
  type: string;
  label: string;
  description: string;
  url: string;
}
