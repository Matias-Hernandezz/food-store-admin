import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ingredienteApi } from "../api/ingrediente.actions";
import { useUIStore } from "../../../store/uiStore";
import type { IngredienteCreate, IngredienteUpdate } from "../../../shared/types";

export const INGREDIENTE_KEY = ["ingredientes"] as const;

export function useIngredientes(offset = 0, limit = 100, incluirEliminados = false) {
  return useQuery({
    queryKey: [...INGREDIENTE_KEY, offset, limit, incluirEliminados],
    queryFn: () => ingredienteApi.getAll(offset, limit, incluirEliminados),
  });
}

export function useIngrediente(id: number) {
  return useQuery({
    queryKey: [...INGREDIENTE_KEY, id],
    queryFn: () => ingredienteApi.getById(id),
    enabled: !!id,
  });
}

export function useCreateIngrediente() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);
  return useMutation({
    mutationFn: (data: IngredienteCreate) => ingredienteApi.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: INGREDIENTE_KEY });
      addToast({ type: "success", message: "Ingrediente creado" });
    },
    onError: (err: any) => {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail || err?.message || "";
      const msg =
        status === 409 ? (detail || "El nombre ya está en uso") :
        status === 422 ? (detail || "Datos inválidos") :
        status === 403 ? "No tenés permisos para esta acción" :
        !navigator.onLine ? "Sin conexión a internet" :
        (detail || "Error al crear el ingrediente");
      addToast({ type: "error", message: msg });
    },
  });
}

export function useUpdateIngrediente() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: IngredienteUpdate }) =>
      ingredienteApi.update(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: INGREDIENTE_KEY });
      addToast({ type: "success", message: "Ingrediente actualizado" });
    },
    onError: (err: any) => {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail || err?.message || "";
      const msg =
        status === 409 ? (detail || "El nombre ya está en uso") :
        status === 404 ? "Ingrediente no encontrado" :
        status === 422 ? (detail || "Datos inválidos") :
        status === 403 ? "No tenés permisos para esta acción" :
        !navigator.onLine ? "Sin conexión a internet" :
        (detail || "Error al actualizar el ingrediente");
      addToast({ type: "error", message: msg });
    },
  });
}

export function useDeleteIngrediente() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);
  return useMutation({
    mutationFn: (id: number) => ingredienteApi.delete(id),
    onMutate: async (id) => {
      await qc.cancelQueries({ queryKey: INGREDIENTE_KEY });
      const previous = qc.getQueriesData({ queryKey: INGREDIENTE_KEY })
        .filter(([, d]) => d != null) as [unknown, any][];
      previous.forEach(([key, data]) => {
        qc.setQueryData(key, {
          ...data,
          data: data.data.map((i: any) =>
            i.id === id ? { ...i, deleted_at: new Date().toISOString() } : i
          ),
        });
      });
      return { previous };
    },
    onSuccess: () => {
      addToast({ type: "success", message: "Ingrediente eliminado" });
    },
    onError: (err: any, _id, context) => {
      if (context?.previous) {
        context.previous.forEach(([key, data]: any) => qc.setQueryData(key, data));
      }
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail || err?.message || "";
      const msg =
        status === 404 ? "Ingrediente no encontrado" :
        status === 403 ? "No tenés permisos para esta acción" :
        !navigator.onLine ? "Sin conexión a internet" :
        (detail || "Error al eliminar el ingrediente");
      addToast({ type: "error", message: msg });
    },
    onSettled: () => qc.invalidateQueries({ queryKey: INGREDIENTE_KEY }),
  });
}

export function useRestoreIngrediente() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);
  return useMutation({
    mutationFn: (id: number) => ingredienteApi.restore(id),
    onMutate: async (id) => {
      await qc.cancelQueries({ queryKey: INGREDIENTE_KEY });
      const previous = qc.getQueriesData({ queryKey: INGREDIENTE_KEY })
        .filter(([, d]) => d != null) as [unknown, any][];
      previous.forEach(([key, data]) => {
        qc.setQueryData(key, {
          ...data,
          data: data.data.map((i: any) =>
            i.id === id ? { ...i, deleted_at: null } : i
          ),
        });
      });
      return { previous };
    },
    onSuccess: () => {
      addToast({ type: "success", message: "Ingrediente restaurado" });
    },
    onError: (err: any, _id, context) => {
      if (context?.previous) {
        context.previous.forEach(([key, data]: any) => qc.setQueryData(key, data));
      }
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail || err?.message || "";
      const msg =
        status === 409 ? (detail || "Conflicto al restaurar") :
        status === 404 ? "Ingrediente no encontrado" :
        status === 403 ? "No tenés permisos para esta acción" :
        !navigator.onLine ? "Sin conexión a internet" :
        (detail || "Error al restaurar el ingrediente");
      addToast({ type: "error", message: msg });
    },
    onSettled: () => qc.invalidateQueries({ queryKey: INGREDIENTE_KEY }),
  });
}
