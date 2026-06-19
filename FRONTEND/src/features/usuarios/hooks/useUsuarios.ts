// features/usuarios/hooks/useUsuarios.ts
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { usuariosApi } from "../api/usuariosApi";
import { authApi } from "../../auth/api/authApi";
import type { UsuarioCreate } from "../../auth/types";

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

export function useUsuarios(search?: string) {
    return useQuery({
        queryKey: ["usuarios", search],
        queryFn: () => usuariosApi.getAll(search),
    });
}

export function useCrearUsuario() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (data: UsuarioCreate) => authApi.register(data),
        onSuccess: () => qc.invalidateQueries({ queryKey: ["usuarios"] }),
    });
}
