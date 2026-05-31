// features/usuarios/api/usuariosApi.ts
import { apiFetch } from "../../../shared/api/client";

const BASE = "/api/v1/auth";

export interface UsuarioAdmin {
    id: number;
    nombre: string;
    apellido: string;
    email: string;
    celular: string | null;
    roles: string[];
    deleted_at: string | null;
}

export const usuariosApi = {
    getAll: () =>
        apiFetch<UsuarioAdmin[]>(`${BASE}/usuarios`),

    asignarRol: (id: number, rol_codigo: string) =>
        apiFetch<UsuarioAdmin>(`${BASE}/usuarios/${id}/roles`, {
            method: "POST",
            body: JSON.stringify({ rol_codigo }),
        }),

    quitarRol: (id: number, rol_codigo: string) =>
        apiFetch<void>(`${BASE}/usuarios/${id}/roles/${rol_codigo}`, {
            method: "DELETE",
        }),

    softDelete: (id: number) =>
        apiFetch<void>(`${BASE}/usuarios/${id}`, { method: "DELETE" }),
};