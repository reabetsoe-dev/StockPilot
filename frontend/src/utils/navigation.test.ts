import { describe, expect, it } from "vitest";

import { navigationForRole } from "./navigation";

describe("navigationForRole", () => {
  it("shows administration pages to administrators", () => {
    const labels = navigationForRole("ADMINISTRATOR").map((item) => item.label);

    expect(labels).toContain("Users");
    expect(labels).toContain("Departments");
    expect(labels).toContain("Products");
    expect(labels).toContain("Suppliers");
    expect(labels).toContain("Warehouses");
  });

  it("keeps auditors read-oriented", () => {
    const labels = navigationForRole("AUDITOR").map((item) => item.label);

    expect(labels).toContain("Audit Logs");
    expect(labels).toContain("Products");
    expect(labels).not.toContain("Users");
    expect(labels).not.toContain("Departments");
  });

  it("shows catalog ownership to inventory and procurement roles", () => {
    const inventoryLabels = navigationForRole("INVENTORY_MANAGER").map((item) => item.label);
    const procurementLabels = navigationForRole("PROCUREMENT_OFFICER").map((item) => item.label);

    expect(inventoryLabels).toContain("Products");
    expect(inventoryLabels).toContain("Categories");
    expect(inventoryLabels).toContain("Warehouses");
    expect(procurementLabels).toContain("Suppliers");
    expect(procurementLabels).toContain("Products");
  });
});
