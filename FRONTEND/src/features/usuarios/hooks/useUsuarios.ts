// features/usuarios/api/usuariosApi.ts
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
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
export function useSoftDeleteUsuario() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (id: number) => usuariosApi.softDelete(id),
        onSuccess: () => qc.invalidateQueries({ queryKey: ["usuarios"] }),
    });
}
export function useQuitarRol() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: ({ id, rol }: { id: number; rol: string }) =>
            usuariosApi.quitarRol(id, rol),
        onSuccess: () => qc.invalidateQueries({ queryKey: ["usuarios"] }),
    });
}

export function useAsignarRol() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: ({ id, rol }: { id: number; rol: string }) =>
            usuariosApi.asignarRol(id, rol),
        onSuccess: () => qc.invalidateQueries({ queryKey: ["usuarios"] }),
    });
}

export function useUsuarios() {
    return useQuery({ queryKey: ["usuarios"], queryFn: usuariosApi.getAll });
}