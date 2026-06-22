import { create } from "zustand";
import { persist } from "zustand/middleware";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface UsuarioRead {
    id: number;
    nombre: string;
    apellido: string;
    email: string;
    celular: string | null;
    roles: string[];
    deleted_at: string | null;
}

interface AuthState {
    accessToken: string | null;
    user: UsuarioRead | null;
    isAuthenticated: boolean;
    isLoading: boolean;

    login: (email: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
    fetchUser: () => Promise<void>;
    refreshToken: () => Promise<string>;
}

async function fetchJSON<T>(path: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, {
        credentials: "include",
        headers: { "Content-Type": "application/json", ...options?.headers },
        ...options,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Error" }));
        throw new Error(err.detail ?? `HTTP ${res.status}`);
    }
    if (res.status === 204) return undefined as T;
    return res.json();
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            accessToken: null,
            user: null,
            isAuthenticated: false,
            isLoading: true,

            login: async (email, password) => {
                // 1. Login → backend setea httpOnly cookies
                await fetchJSON<UsuarioRead>(`/api/v1/auth/login`, {
                    method: "POST",
                    body: JSON.stringify({ email, password }),
                });

                // 2. Obtener access token para Zustand
                const tokenRes = await fetchJSON<{ access_token: string }>(`/api/v1/auth/token`);

                // 3. Obtener datos del usuario
                const user = await fetchJSON<UsuarioRead>(`/api/v1/auth/me`);

                set({
                    accessToken: tokenRes.access_token,
                    user,
                    isAuthenticated: true,
                    isLoading: false,
                });
            },

            logout: async () => {
                try {
                    await fetchJSON(`/api/v1/auth/logout`, { method: "POST" });
                } catch {
                    // Si falla el logout, igual limpiamos estado local
                }
                set({
                    accessToken: null,
                    user: null,
                    isAuthenticated: false,
                    isLoading: false,
                });
            },

            fetchUser: async () => {
                try {
                    const user = await fetchJSON<UsuarioRead>(`/api/v1/auth/me`);
                    // También refrescar el token por si expiró
                    const tokenRes = await fetchJSON<{ access_token: string }>(`/api/v1/auth/token`);
                    set({
                        user,
                        accessToken: tokenRes.access_token,
                        isAuthenticated: true,
                        isLoading: false,
                    });
                } catch {
                    set({
                        accessToken: null,
                        user: null,
                        isAuthenticated: false,
                        isLoading: false,
                    });
                }
            },

            refreshToken: async () => {
                await fetchJSON(`/api/v1/auth/refresh`, { method: "POST" });
                const tokenRes = await fetchJSON<{ access_token: string }>(`/api/v1/auth/token`);
                set({ accessToken: tokenRes.access_token });
                return tokenRes.access_token;
            },
        }),
        {
            name: "admin-auth",
            partialize: (state) => ({ accessToken: state.accessToken }),
        }
    )
);
