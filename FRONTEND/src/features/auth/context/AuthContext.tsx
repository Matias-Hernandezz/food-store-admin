
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { authApi } from "../api/authApi";
import type { UsuarioRead } from "../types";

interface AuthContextValue {
  user: UsuarioRead | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  hasRole: (...roles: string[]) => boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UsuarioRead | null>(null);
  const [loading, setLoading] = useState(true);


  useEffect(() => {
    authApi.me()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  const login = async (email: string, password: string) => {
    const userData = await authApi.login({ email, password });
    setUser(userData);
  };

  const logout = async () => {
    await authApi.logout();
    setUser(null);
  };

  const hasRole = (...roles: string[]) =>
    roles.some((r) => user?.roles.includes(r)) ?? false;

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, hasRole }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  return ctx;
}