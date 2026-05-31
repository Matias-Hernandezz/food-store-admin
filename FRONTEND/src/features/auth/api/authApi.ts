import { apiFetch } from "../../../shared/api/client";
import type { LoginInput, UsuarioRead, UsuarioCreate } from "../types";

const BASE = "/api/v1/auth";

export const authApi = {
    register: (data: UsuarioCreate) =>
        apiFetch<UsuarioRead>(`${BASE}/register`, {
            method: "POST",
            body: JSON.stringify(data),
        }),

    login: (data: LoginInput) =>
        apiFetch<UsuarioRead>(`${BASE}/login`, {
            method: "POST",
            body: JSON.stringify(data),
        }),

    logout: () =>
        apiFetch<void>(`${BASE}/logout`, { method: "POST" }),

    me: () =>
        apiFetch<UsuarioRead>(`${BASE}/me`),

    refresh: () =>
        apiFetch<void>(`${BASE}/refresh`, { method: "POST" }),
};