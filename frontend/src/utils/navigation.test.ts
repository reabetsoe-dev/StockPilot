import { describe, expect, it } from "vitest";

import { navigationForRole } from "./navigation";

describe("navigationForRole", () => {
  it("shows administration pages to administrators", () => {
    const labels = navigationForRole("ADMINISTRATOR").map((item) => item.label);

    expect(labels).toContain("Users");
    expect(labels).toContain("Departments");
  });

  it("keeps auditors read-oriented", () => {
    const labels = navigationForRole("AUDITOR").map((item) => item.label);

    expect(labels).toContain("Audit Logs");
    expect(labels).not.toContain("Users");
    expect(labels).not.toContain("Departments");
  });
});
