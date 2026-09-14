export interface Category {
  id: number;
  name: string;
  description: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Supplier {
  id: number;
  supplier_code: string;
  name: string;
  contact_person: string;
  email: string | null;
  phone: string | null;
  address: string | null;
  tax_reference: string | null;
  payment_terms: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Warehouse {
  id: number;
  code: string;
  name: string;
  location: string;
  description: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: number;
  sku: string;
  barcode: string | null;
  name: string;
  description: string | null;
  category_id: number;
  unit_of_measure: string;
  cost_price: string;
  selling_price: string;
  reorder_level: number;
  preferred_supplier_id: number | null;
  active: boolean;
  category: Category;
  preferred_supplier: Supplier | null;
  created_at: string;
  updated_at: string;
}
