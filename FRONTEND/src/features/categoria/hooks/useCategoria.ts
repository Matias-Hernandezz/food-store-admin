import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { categoriaApi } from "../api/categoria.actions";
import { useUIStore } from "../../../store/uiStore";
import type { CategoriaCreate, CategoriaUpdate } from "../../../shared/types";

export const CATEGORIA_KEY = ["categorias"] as const;

export function useCategorias(offset = 0, limit = 100, incluirEliminados = false) {
  return useQuery({
    queryKey: [...CATEGORIA_KEY, offset, limit, incluirEliminados],
    queryFn: () => categoriaApi.getAll(offset, limit, incluirEliminados),
  });
}

export function useCategoria(id: number) {
  return useQuery({
    queryKey: [...CATEGORIA_KEY, id],
    queryFn: () => categoriaApi.getById(id),
    enabled: !!id,
  });
}

export function useCreateCategoria() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);
  return useMutation({
    mutationFn: (data: CategoriaCreate) => categoriaApi.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: CATEGORIA_KEY });
      addToast({ type: "success", message: "Categoría creada" });
    },
    onError: (err: any) => {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail || err?.message || "";
      const msg =
        status === 409 ? (detail || "El nombre ya está en uso") :
        status === 422 ? (detail || "Datos inválidos") :
        status === 403 ? "No tenés permisos para esta acción" :
        !navigator.onLine ? "Sin conexión a internet" :
        (detail || "Error al crear la categoría");
      addToast({ type: "error", message: msg });
    },
  });
}

export function useUpdateCategoria() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: CategoriaUpdate }) =>
      categoriaApi.update(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: CATEGORIA_KEY });
      addToast({ type: "success", message: "Categoría actualizada" });
    },
    onError: (err: any) => {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail || err?.message || "";
      const msg =
        status === 409 ? (detail || "El nombre ya está en uso") :
        status === 404 ? "Categoría no encontrada" :
        status === 422 ? (detail || "Datos inválidos") :
        status === 403 ? "No tenés permisos para esta acción" :
        status === 400 ? (detail || "Datos inválidos") :
        !navigator.onLine ? "Sin conexión a internet" :
        (detail || "Error al actualizar la categoría");
      addToast({ type: "error", message: msg });
    },
  });
}

export function useDeleteCategoria() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);
  return useMutation({
    mutationFn: (id: number) => categoriaApi.delete(id),
    onMutate: async (id) => {
      await qc.cancelQueries({ queryKey: CATEGORIA_KEY });
      const previous = qc.getQueriesData({ queryKey: CATEGORIA_KEY })
        .filter(([, d]) => d != null) as [unknown, any][];
      previous.forEach(([key, data]) => {
        qc.setQueryData(key, {
          ...data,
          data: data.data.map((c: any) =>
            c.id === id ? { ...c, deleted_at: new Date().toISOString() } : c
          ),
        });
      });
      return { previous };
    },
    onSuccess: () => {
      addToast({ type: "success", message: "Categoría eliminada" });
    },
    onError: (err: any, _id, context) => {
      if (context?.previous) {
        context.previous.forEach(([key, data]: any) => qc.setQueryData(key, data));
      }
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail || err?.message || "";
      const msg =
        status === 404 ? "Categoría no encontrada" :
        status === 403 ? "No tenés permisos para esta acción" :
        !navigator.onLine ? "Sin conexión a internet" :
        (detail || "Error al eliminar la categoría");
      addToast({ type: "error", message: msg });
    },
    onSettled: () => qc.invalidateQueries({ queryKey: CATEGORIA_KEY }),
  });
}

export function useRestoreCategoria() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);
  return useMutation({
    mutationFn: (id: number) => categoriaApi.restore(id),
    onMutate: async (id) => {
      await qc.cancelQueries({ queryKey: CATEGORIA_KEY });
      const previous = qc.getQueriesData({ queryKey: CATEGORIA_KEY })
        .filter(([, d]) => d != null) as [unknown, any][];
      previous.forEach(([key, data]) => {
        qc.setQueryData(key, {
          ...data,
          data: data.data.map((c: any) =>
            c.id === id ? { ...c, deleted_at: null } : c
          ),
        });
      });
      return { previous };
    },
    onSuccess: () => {
      addToast({ type: "success", message: "Categoría restaurada" });
    },
    onError: (err: any, _id, context) => {
      if (context?.previous) {
        context.previous.forEach(([key, data]: any) => qc.setQueryData(key, data));
      }
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail || err?.message || "";
      const msg =
        status === 409 ? (detail || "Conflicto al restaurar") :
        status === 404 ? "Categoría no encontrada" :
        status === 403 ? "No tenés permisos para esta acción" :
        !navigator.onLine ? "Sin conexión a internet" :
        (detail || "Error al restaurar la categoría");
      addToast({ type: "error", message: msg });
    },
    onSettled: () => qc.invalidateQueries({ queryKey: CATEGORIA_KEY }),
  });
}
