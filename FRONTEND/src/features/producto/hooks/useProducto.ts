import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { productoApi } from "../api/producto.actions";
import type { ProductoCreate, ProductoUpdate } from "../../../shared/types";

export const PRODUCTO_KEY = ["productos"] as const;

export function useProductos(page = 1, size = 100, categoria?: number) {
  return useQuery({
    queryKey: [...PRODUCTO_KEY, page, size, categoria],
    queryFn: () => productoApi.getAll(page, size, categoria),
  });
}

export function useProducto(id: number) {
  return useQuery({
    queryKey: [...PRODUCTO_KEY, id],
    queryFn: () => productoApi.getById(id),
    enabled: !!id,
  });
}

export function useCreateProducto() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ProductoCreate) => productoApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: PRODUCTO_KEY }),
  });
}

export function useUpdateProducto() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ProductoUpdate }) =>
      productoApi.update(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: PRODUCTO_KEY }),
  });
}

export function useDeleteProducto() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => productoApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: PRODUCTO_KEY }),
  });
}
