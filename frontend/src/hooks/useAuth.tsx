import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { api } from "../services/api";
import type { AuthResponse, User } from "../types/auth";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("stockpilot_token"));
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem("stockpilot_user");
    return stored ? (JSON.parse(stored) as User) : null;
  });
  const [loading, setLoading] = useState(Boolean(token));

  const logout = useCallback(() => {
    localStorage.removeItem("stockpilot_token");
    localStorage.removeItem("stockpilot_user");
    setToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }

    let active = true;
    api
      .get<User>("/auth/me")
      .then((response) => {
        if (!active) return;
        setUser(response.data);
        localStorage.setItem("stockpilot_user", JSON.stringify(response.data));
      })
      .catch(logout)
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [logout, token]);

  const login = useCallback(async (email: string, password: string) => {
    const response = await api.post<AuthResponse>("/auth/login", { email, password });
    localStorage.setItem("stockpilot_token", response.data.access_token);
    localStorage.setItem("stockpilot_user", JSON.stringify(response.data.user));
    setToken(response.data.access_token);
    setUser(response.data.user);
  }, []);

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      isAuthenticated: Boolean(token && user),
      login,
      logout,
    }),
    [loading, login, logout, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return value;
}
