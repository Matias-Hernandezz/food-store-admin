import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { categoriaApi } from "../api/categoria.actions";
import type { CategoriaCreate, CategoriaUpdate } from "../../../shared/types";

export const CATEGORIA_KEY = ["categorias"] as const;

export function useCategorias(offset = 0, limit = 100) {
  return useQuery({
    queryKey: [...CATEGORIA_KEY, offset, limit],
    queryFn: () => categoriaApi.getAll(offset, limit),
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
  return useMutation({
    mutationFn: (data: CategoriaCreate) => categoriaApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CATEGORIA_KEY }),
  });
}

export function useUpdateCategoria() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: CategoriaUpdate }) =>
      categoriaApi.update(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: CATEGORIA_KEY }),
  });
}

export function useDeleteCategoria() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => categoriaApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: CATEGORIA_KEY }),
  });
}
