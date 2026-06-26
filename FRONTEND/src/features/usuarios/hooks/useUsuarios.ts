// features/usuarios/hooks/useUsuarios.ts
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { usuariosApi } from "../api/usuariosApi";
import { authApi } from "../../auth/api/authApi";
import { useUIStore } from "../../../store/uiStore";
import { useAuthStore } from "../../../store/authStore";
import type { UsuarioCreate } from "../../auth/types";
import type { AxiosError } from "axios";

interface Props {
  id?: number;
  page?: number;
  pageSize?: number;
  search?: string;
  enabled?: boolean;
}

export function useUsuarios({
  id,
  page = 0,
  pageSize = 100,
  search,
  enabled = true,
}: Props = {}) {
  const queryClient = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);
  const user = useAuthStore((s) => s.user);

  // --- QUERIES (GET) ---
  const usuariosList = useQuery({
    queryKey: ["usuarios", search],
    queryFn: () => usuariosApi.getAll(search),
    enabled: enabled && !id,
  });

  // --- MUTATIONS ---
  const softDeleteUsuario = useMutation({
    mutationFn: (id: number) => usuariosApi.softDelete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["usuarios"] });
      addToast({ type: "success", message: "Usuario eliminado" });
    },
    onError: (err: AxiosError<{ detail: string }>) => {
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

  const quitarRol = useMutation({
    mutationFn: ({ id, rol }: { id: number; rol: string }) =>
      usuariosApi.quitarRol(id, rol),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["usuarios"] });
      addToast({ type: "success", message: "Rol removido" });
    },
    onError: (err: AxiosError<{ detail: string }>) => {
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

  const asignarRol = useMutation({
    mutationFn: ({ id, rol }: { id: number; rol: string }) =>
      usuariosApi.asignarRol(id, rol),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["usuarios"] });
      addToast({ type: "success", message: "Rol asignado" });
    },
    onError: (err: AxiosError<{ detail: string }>) => {
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

  const crearUsuario = useMutation({
    mutationFn: (data: UsuarioCreate) => authApi.register(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["usuarios"] });
      addToast({ type: "success", message: "Usuario creado" });
    },
    onError: (err: AxiosError<{ detail: string }>) => {
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

  // --- ROLE HELPERS (absorbidos de useRole.ts) ---
  const hasRole = (...roles: string[]) =>
    roles.some((r) => user?.roles?.includes(r)) ?? false;

  const isAdmin = user?.roles?.includes("ADMIN") ?? false;

  return {
    data: usuariosList.data,
    isLoading: usuariosList.isLoading,
    isFetching: usuariosList.isFetching,
    isError: usuariosList.isError,
    refetch: usuariosList.refetch,
    softDeleteUser: softDeleteUsuario.mutateAsync,
    softDeleteUserPending: softDeleteUsuario.isPending,
    quitarRol: quitarRol.mutateAsync,
    quitarRolPending: quitarRol.isPending,
    asignarRol: asignarRol.mutateAsync,
    asignarRolPending: asignarRol.isPending,
    createUser: crearUsuario.mutateAsync,
    createUserPending: crearUsuario.isPending,
    hasRole,
    isAdmin,
  };
}
