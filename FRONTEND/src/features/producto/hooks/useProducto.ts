import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { productoApi } from "../api/producto.actions";
import { useUIStore } from "../../../store/uiStore";
import type { ProductoCreate, ProductoUpdate } from "../../../shared/types";

export const PRODUCTO_KEY = ["productos"] as const;

export function useProductos(page = 1, size = 100, categoria?: number, incluirEliminados = false) {
  return useQuery({
    queryKey: [...PRODUCTO_KEY, page, size, categoria, incluirEliminados],
    queryFn: () => productoApi.getAll(page, size, categoria, incluirEliminados),
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
  const addToast = useUIStore((s) => s.addToast);
  return useMutation({
    mutationFn: (data: ProductoCreate) => productoApi.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: PRODUCTO_KEY });
      addToast({ type: "success", message: "Producto creado" });
    },
    onError: (err: any) => {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail || err?.message || "";
      const msg =
        status === 409 ? (detail || "El nombre ya está en uso") :
        status === 422 ? (detail || "Datos inválidos") :
        status === 403 ? "No tenés permisos para esta acción" :
        status === 400 ? (detail || "Datos inválidos") :
        !navigator.onLine ? "Sin conexión a internet" :
        (detail || "Error al crear el producto");
      addToast({ type: "error", message: msg });
    },
  });
}

export function useUpdateProducto() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ProductoUpdate }) =>
      productoApi.update(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: PRODUCTO_KEY });
      addToast({ type: "success", message: "Producto actualizado" });
    },
    onError: (err: any) => {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail || err?.message || "";
      const msg =
        status === 409 ? (detail || "El nombre ya está en uso") :
        status === 404 ? "Producto no encontrado" :
        status === 422 ? (detail || "Datos inválidos") :
        status === 403 ? "No tenés permisos para esta acción" :
        status === 400 ? (detail || "Datos inválidos") :
        !navigator.onLine ? "Sin conexión a internet" :
        (detail || "Error al actualizar el producto");
      addToast({ type: "error", message: msg });
    },
  });
}

export function useDeleteProducto() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);
  return useMutation({
    mutationFn: (id: number) => productoApi.delete(id),
    onMutate: async (id) => {
      await qc.cancelQueries({ queryKey: PRODUCTO_KEY });
      const previous = qc.getQueriesData({ queryKey: PRODUCTO_KEY })
        .filter(([, d]) => d != null) as [unknown, any][];
      previous.forEach(([key, data]) => {
        qc.setQueryData(key, {
          ...data,
          data: data.data.map((p: any) =>
            p.id === id ? { ...p, deleted_at: new Date().toISOString() } : p
          ),
        });
      });
      return { previous };
    },
    onSuccess: () => {
      addToast({ type: "success", message: "Producto eliminado" });
    },
    onError: (err: any, _id, context) => {
      if (context?.previous) {
        context.previous.forEach(([key, data]: any) => qc.setQueryData(key, data));
      }
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail || err?.message || "";
      const msg =
        status === 404 ? "Producto no encontrado" :
        status === 403 ? "No tenés permisos para esta acción" :
        !navigator.onLine ? "Sin conexión a internet" :
        (detail || "Error al eliminar el producto");
      addToast({ type: "error", message: msg });
    },
    onSettled: () => qc.invalidateQueries({ queryKey: PRODUCTO_KEY }),
  });
}

export function useRestoreProducto() {
  const qc = useQueryClient();
  const addToast = useUIStore((s) => s.addToast);
  return useMutation({
    mutationFn: (id: number) => productoApi.restore(id),
    onMutate: async (id) => {
      await qc.cancelQueries({ queryKey: PRODUCTO_KEY });
      const previous = qc.getQueriesData({ queryKey: PRODUCTO_KEY })
        .filter(([, d]) => d != null) as [unknown, any][];
      previous.forEach(([key, data]) => {
        qc.setQueryData(key, {
          ...data,
          data: data.data.map((p: any) =>
            p.id === id ? { ...p, deleted_at: null } : p
          ),
        });
      });
      return { previous };
    },
    onSuccess: () => {
      addToast({ type: "success", message: "Producto restaurado" });
    },
    onError: (err: any, _id, context) => {
      if (context?.previous) {
        context.previous.forEach(([key, data]: any) => qc.setQueryData(key, data));
      }
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail || err?.message || "";
      const msg =
        status === 409 ? (detail || "Conflicto al restaurar") :
        status === 404 ? "Producto no encontrado" :
        status === 403 ? "No tenés permisos para esta acción" :
        !navigator.onLine ? "Sin conexión a internet" :
        (detail || "Error al restaurar el producto");
      addToast({ type: "error", message: msg });
    },
    onSettled: () => qc.invalidateQueries({ queryKey: PRODUCTO_KEY }),
  });
}

export function useUnidadesMedida() {
  return useQuery({
    queryKey: ["unidades-medida"],
    queryFn: () => productoApi.getUnidadesMedida(),
    staleTime: 10 * 60 * 1000,
  });
}
