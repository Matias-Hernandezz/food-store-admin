// features/usuarios/hooks/useUsuarios.ts
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { usuariosApi } from "../api/usuariosApi";
import { authApi } from "../../auth/api/authApi";
import { useUIStore } from "../../../store/uiStore";
import type { UsuarioCreate } from "../../auth/types";

export function useSoftDeleteUsuario() {
    const qc = useQueryClient();
    const addToast = useUIStore((s) => s.addToast);
    return useMutation({
        mutationFn: (id: number) => usuariosApi.softDelete(id),
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["usuarios"] });
            addToast({ type: "success", message: "Usuario eliminado" });
        },
        onError: (err: any) => {
            const status = err?.response?.status;
            const detail = err?.response?.data?.detail || err?.message || "";
            const msg =
                status === 404 ? "Usuario no encontrado" :
                status === 403 ? "No tenés permisos para esta acción" :
                !navigator.onLine ? "Sin conexión a internet" :
                (detail || "Error al eliminar el usuario");
            addToast({ type: "error", message: msg });
        },
    });
}

export function useQuitarRol() {
    const qc = useQueryClient();
    const addToast = useUIStore((s) => s.addToast);
    return useMutation({
        mutationFn: ({ id, rol }: { id: number; rol: string }) =>
            usuariosApi.quitarRol(id, rol),
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["usuarios"] });
            addToast({ type: "success", message: "Rol removido" });
        },
        onError: (err: any) => {
            const status = err?.response?.status;
            const detail = err?.response?.data?.detail || err?.message || "";
            const msg =
                status === 404 ? "Usuario o rol no encontrado" :
                status === 409 ? (detail || "No se puede quitar el rol") :
                status === 403 ? "No tenés permisos para esta acción" :
                !navigator.onLine ? "Sin conexión a internet" :
                (detail || "Error al quitar el rol");
            addToast({ type: "error", message: msg });
        },
    });
}

export function useAsignarRol() {
    const qc = useQueryClient();
    const addToast = useUIStore((s) => s.addToast);
    return useMutation({
        mutationFn: ({ id, rol }: { id: number; rol: string }) =>
            usuariosApi.asignarRol(id, rol),
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["usuarios"] });
            addToast({ type: "success", message: "Rol asignado" });
        },
        onError: (err: any) => {
            const status = err?.response?.status;
            const detail = err?.response?.data?.detail || err?.message || "";
            const msg =
                status === 404 ? "Usuario no encontrado" :
                status === 409 ? (detail || "El rol ya está asignado") :
                status === 403 ? "No tenés permisos para esta acción" :
                !navigator.onLine ? "Sin conexión a internet" :
                (detail || "Error al asignar el rol");
            addToast({ type: "error", message: msg });
        },
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
    const addToast = useUIStore((s) => s.addToast);
    return useMutation({
        mutationFn: (data: UsuarioCreate) => authApi.register(data),
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["usuarios"] });
            addToast({ type: "success", message: "Usuario creado" });
        },
        onError: (err: any) => {
            const status = err?.response?.status;
            const detail = err?.response?.data?.detail || err?.message || "";
            const msg =
                status === 409 ? (detail || "El email ya está registrado") :
                status === 422 ? (detail || "Datos inválidos") :
                status === 403 ? "No tenés permisos para esta acción" :
                !navigator.onLine ? "Sin conexión a internet" :
                (detail || "Error al crear el usuario");
            addToast({ type: "error", message: msg });
        },
    });
}
