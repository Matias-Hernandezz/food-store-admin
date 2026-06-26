import { useQuery, QueryKey, useMutation, useQueryClient } from "@tanstack/react-query";
import { ingredienteApi } from "../api/ingrediente.actions";
import { useUIStore } from "../../../store/uiStore";
import type { IngredienteCreate, IngredienteUpdate } from "../../../shared/types";
import type { AxiosError } from "axios";

const INGREDIENTE_KEY = ["ingredientes"] as const;

interface Props {
  id?: number;
  page?: number;
  pageSize?: number;
  incluirEliminados?: boolean;
  enabled?: boolean;
}

export function useIngredientes({
  id,
  page = 0,
  pageSize = 100,
  incluirEliminados = false,
  enabled = true,
}: Props = {}) {
  const queryClient = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);

  // --- QUERIES (GET) ---
  const ingredientesList = useQuery({
    queryKey: [...INGREDIENTE_KEY, page, pageSize, incluirEliminados],
    queryFn: () => ingredienteApi.getAll(page, pageSize, incluirEliminados),
    enabled: enabled && !id,
  });

  const ingredienteById = useQuery({
    queryKey: [...INGREDIENTE_KEY, id],
    queryFn: () => id ? ingredienteApi.getById(id) : Promise.reject("No ID provided"),
    enabled: enabled && !!id,
  });

  // --- MUTATIONS (POST/PUT/DELETE) ---
  const createIngredient = useMutation({
    mutationFn: (data: IngredienteCreate) => ingredienteApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: INGREDIENTE_KEY });
      addToast({ type: "success", message: "Ingrediente creado" });
    },
    onError: (err: AxiosError<{ detail: string }>) => {
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

  const updateIngredient = useMutation({
    mutationFn: ({ id, data }: { id: number; data: IngredienteUpdate }) =>
      ingredienteApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: INGREDIENTE_KEY });
      addToast({ type: "success", message: "Ingrediente actualizado" });
    },
    onError: (err: AxiosError<{ detail: string }>) => {
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

  const deleteIngredient = useMutation({
    mutationFn: (id: number) => ingredienteApi.delete(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: INGREDIENTE_KEY });
      const previous = queryClient.getQueriesData({ queryKey: INGREDIENTE_KEY })
        .filter(([, d]) => d != null) as [QueryKey, any][];
      previous.forEach(([key, data]) => {
        queryClient.setQueryData(key, {
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
    onError: (err: AxiosError<{ detail: string }>, _id, context) => {
      if (context?.previous) {
        context.previous.forEach(([key, data]: any) => queryClient.setQueryData(key, data));
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
    onSettled: () => queryClient.invalidateQueries({ queryKey: INGREDIENTE_KEY }),
  });

  const restoreIngredient = useMutation({
    mutationFn: (id: number) => ingredienteApi.restore(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: INGREDIENTE_KEY });
      const previous = queryClient.getQueriesData({ queryKey: INGREDIENTE_KEY })
        .filter(([, d]) => d != null) as [QueryKey, any][];
      previous.forEach(([key, data]) => {
        queryClient.setQueryData(key, {
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
    onError: (err: AxiosError<{ detail: string }>, _id, context) => {
      if (context?.previous) {
        context.previous.forEach(([key, data]: any) => queryClient.setQueryData(key, data));
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
    onSettled: () => queryClient.invalidateQueries({ queryKey: INGREDIENTE_KEY }),
  });

  return {
    data: ingredientesList.data,
    singleData: ingredienteById.data,
    isLoading: ingredientesList.isLoading || ingredienteById.isLoading,
    isFetching: ingredientesList.isFetching || ingredienteById.isFetching,
    isError: ingredientesList.isError || ingredienteById.isError,
    refetch: ingredientesList.refetch,
    refetchById: ingredienteById.refetch,
    createIngredient: createIngredient.mutateAsync,
    createIngredientPending: createIngredient.isPending,
    updateIngredient: updateIngredient.mutateAsync,
    updateIngredientPending: updateIngredient.isPending,
    deleteIngredient: deleteIngredient.mutateAsync,
    deleteIngredientPending: deleteIngredient.isPending,
    restoreIngredient: restoreIngredient.mutateAsync,
    restoreIngredientPending: restoreIngredient.isPending,
  };
}
