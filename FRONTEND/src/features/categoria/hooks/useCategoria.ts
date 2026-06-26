import { useQuery, QueryKey, useMutation, useQueryClient } from "@tanstack/react-query";
import { categoriaApi } from "../api/categoria.actions";
import { useUIStore } from "../../../store/uiStore";
import type { CategoriaCreate, CategoriaUpdate } from "../../../shared/types";
import type { AxiosError } from "axios";

const CATEGORIA_KEY = ["categorias"] as const;

interface Props {
  id?: number;
  page?: number;
  pageSize?: number;
  incluirEliminados?: boolean;
  enabled?: boolean;
}

export function useCategorias({
  id,
  page = 0,
  pageSize = 100,
  incluirEliminados = false,
  enabled = true,
}: Props = {}) {
  const queryClient = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);

  // --- QUERIES (GET) ---
  const categoriasList = useQuery({
    queryKey: [...CATEGORIA_KEY, page, pageSize, incluirEliminados],
    queryFn: () => categoriaApi.getAll(page, pageSize, incluirEliminados),
    enabled: enabled && !id,
  });

  const categoriaById = useQuery({
    queryKey: [...CATEGORIA_KEY, id],
    queryFn: () => id ? categoriaApi.getById(id) : Promise.reject("No ID provided"),
    enabled: enabled && !!id,
  });

  // --- MUTATIONS (POST/PUT/DELETE) ---
  const createCategory = useMutation({
    mutationFn: (data: CategoriaCreate) => categoriaApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CATEGORIA_KEY });
      addToast({ type: "success", message: "Categoría creada" });
    },
    onError: (err: AxiosError<{ detail: string }>) => {
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

  const updateCategory = useMutation({
    mutationFn: ({ id, data }: { id: number; data: CategoriaUpdate }) =>
      categoriaApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CATEGORIA_KEY });
      addToast({ type: "success", message: "Categoría actualizada" });
    },
    onError: (err: AxiosError<{ detail: string }>) => {
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

  const deleteCategory = useMutation({
    mutationFn: (id: number) => categoriaApi.delete(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: CATEGORIA_KEY });
      const previous = queryClient.getQueriesData({ queryKey: CATEGORIA_KEY })
        .filter(([, d]) => d != null) as [QueryKey, any][];
      previous.forEach(([key, data]) => {
        queryClient.setQueryData(key, {
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
    onError: (err: AxiosError<{ detail: string }>, _id, context) => {
      if (context?.previous) {
        context.previous.forEach(([key, data]: any) => queryClient.setQueryData(key, data));
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
    onSettled: () => queryClient.invalidateQueries({ queryKey: CATEGORIA_KEY }),
  });

  const restoreCategory = useMutation({
    mutationFn: (id: number) => categoriaApi.restore(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: CATEGORIA_KEY });
      const previous = queryClient.getQueriesData({ queryKey: CATEGORIA_KEY })
        .filter(([, d]) => d != null) as [QueryKey, any][];
      previous.forEach(([key, data]) => {
        queryClient.setQueryData(key, {
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
    onError: (err: AxiosError<{ detail: string }>, _id, context) => {
      if (context?.previous) {
        context.previous.forEach(([key, data]: any) => queryClient.setQueryData(key, data));
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
    onSettled: () => queryClient.invalidateQueries({ queryKey: CATEGORIA_KEY }),
  });

  return {
    data: categoriasList.data,
    singleData: categoriaById.data,
    isLoading: categoriasList.isLoading || categoriaById.isLoading,
    isFetching: categoriasList.isFetching || categoriaById.isFetching,
    isError: categoriasList.isError || categoriaById.isError,
    refetch: categoriasList.refetch,
    refetchById: categoriaById.refetch,
    createCategory: createCategory.mutateAsync,
    createCategoryPending: createCategory.isPending,
    updateCategory: updateCategory.mutateAsync,
    updateCategoryPending: updateCategory.isPending,
    deleteCategory: deleteCategory.mutateAsync,
    deleteCategoryPending: deleteCategory.isPending,
    restoreCategory: restoreCategory.mutateAsync,
    restoreCategoryPending: restoreCategory.isPending,
  };
}
