export function statusLabel(status: string): string {
  return status
    .toLowerCase()
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function statusTone(status: string): "emerald" | "amber" | "blue" | "slate" | "rose" {
  if (["APPROVED", "ISSUED", "RECEIVED", "COMPLETED", "NORMAL", "INCREASE"].includes(status)) return "emerald";
  if (["SUBMITTED", "DRAFT", "PARTIALLY_RECEIVED", "IN_TRANSIT", "LOW_STOCK"].includes(status)) return "amber";
  if (["REJECTED", "CANCELLED", "OUT_OF_STOCK", "DECREASE"].includes(status)) return "rose";
  if (["CONVERTED_TO_PO"].includes(status)) return "blue";
  return "slate";
}
