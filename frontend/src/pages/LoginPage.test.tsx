import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { LoginPage } from "./LoginPage";
import { LandingPage } from "./LandingPage";

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
    expect(screen.getByRole("option", { name: /admin@stockpilot.local/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Home/i })).toHaveAttribute("href", "/");
  });

  it("keeps the landing page separate from login", () => {
    render(
      <MemoryRouter>
        <LandingPage />
      </MemoryRouter>,
    );

    expect(screen.getByRole("link", { name: /Get Started/i })).toHaveAttribute("href", "/login");
    expect(screen.queryByRole("heading", { name: /Access StockPilot/i })).not.toBeInTheDocument();
  });
});
