import { apiFetch } from "../../../shared/api/client";
import type {
  Producto,
  ProductoCreate,
  ProductoUpdate,
  ProductoList,
} from "../../../shared/types";

const BASE = "/productos";

export const productoApi = {
  getAll: (offset = 0, limit = 100) =>
    apiFetch<ProductoList>(`${BASE}/?offset=${offset}&limit=${limit}`),

  getById: (id: number) =>
    apiFetch<Producto>(`${BASE}/${id}`),

  create: (data: ProductoCreate) =>
    apiFetch<Producto>(BASE + "/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: number, data: ProductoUpdate) =>
    apiFetch<Producto>(`${BASE}/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  delete: (id: number) =>
    apiFetch<void>(`${BASE}/${id}`, { method: "DELETE" }),
};
