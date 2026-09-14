import type { StockMovementType, StockStatus } from "../types/inventory";

export function stockStatusLabel(status: StockStatus): string {
  if (status === "LOW_STOCK") return "Low stock";
  if (status === "OUT_OF_STOCK") return "Out of stock";
  return "Normal";
}

export function stockStatusTone(status: StockStatus): "emerald" | "amber" | "rose" {
  if (status === "LOW_STOCK") return "amber";
  if (status === "OUT_OF_STOCK") return "rose";
  return "emerald";
}

export function movementLabel(type: StockMovementType): string {
  return type
    .toLowerCase()
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}
