import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ingredienteApi } from "../api/ingrediente.actions";
import type { IngredienteCreate, IngredienteUpdate } from "../../../shared/types";

export const INGREDIENTE_KEY = ["ingredientes"] as const;

export function useIngredientes(offset = 0, limit = 100) {
  return useQuery({
    queryKey: [...INGREDIENTE_KEY, offset, limit],
    queryFn: () => ingredienteApi.getAll(offset, limit),
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
  return useMutation({
    mutationFn: (data: IngredienteCreate) => ingredienteApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: INGREDIENTE_KEY }),
  });
}

export function useUpdateIngrediente() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: IngredienteUpdate }) =>
      ingredienteApi.update(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: INGREDIENTE_KEY }),
  });
}

export function useDeleteIngrediente() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => ingredienteApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: INGREDIENTE_KEY }),
  });
}
