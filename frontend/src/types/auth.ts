export type UserRole =
  | "ADMINISTRATOR"
  | "INVENTORY_MANAGER"
  | "PROCUREMENT_OFFICER"
  | "WAREHOUSE_OFFICER"
  | "DEPARTMENT_REQUESTER"
  | "AUDITOR";

export interface Department {
  id: number;
  name: string;
  description: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: number;
  full_name: string;
  email: string;
  role: UserRole;
  department_id: number | null;
  active: boolean;
  department?: Department | null;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: "bearer";
  user: User;
}
