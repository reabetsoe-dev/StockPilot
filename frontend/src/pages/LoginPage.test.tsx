import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { LoginPage } from "./LoginPage";

vi.mock("../hooks/useAuth", () => ({
  useAuth: () => ({
    login: vi.fn(),
  }),
}));

describe("LoginPage", () => {
  it("shows StockPilot demo credentials", () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: /Access StockPilot/i })).toBeInTheDocument();
    expect(screen.getByText("admin@stockpilot.local")).toBeInTheDocument();
    expect(screen.getByText("warehouse@stockpilot.local")).toBeInTheDocument();
  });
});
