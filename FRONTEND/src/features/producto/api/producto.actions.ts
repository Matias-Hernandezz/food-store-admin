import api from "../../../shared/api/axiosClient";
import type {
  Producto,
  ProductoCreate,
  ProductoUpdate,
  ProductoList,
  UnidadMedida,
} from "../../../shared/types";

const BASE = "/api/v1/productos";

export const productoApi = {
  getAll: (page = 1, size = 100, categoria?: number, incluirEliminados = false) => {
    const params = new URLSearchParams({
      page: String(page),
      size: String(size),
    });
    if (categoria) params.set("categoria", String(categoria));
    if (incluirEliminados) params.set("incluir_eliminados", "true");
    return api.get<ProductoList>(`${BASE}/?${params}`).then((r) => r.data);
  },

  getById: (id: number) =>
    api.get<Producto>(`${BASE}/${id}`).then((r) => r.data),

  create: (data: ProductoCreate) =>
    api.post<Producto>(BASE + "/", data).then((r) => r.data),

  update: (id: number, data: ProductoUpdate) =>
    api.put<Producto>(`${BASE}/${id}`, data).then((r) => r.data),

  restore: (id: number) =>
    api.patch<Producto>(`${BASE}/${id}/restaurar`).then((r) => r.data),

  delete: (id: number) =>
    api.delete(`${BASE}/${id}`),

  getUnidadesMedida: () =>
    api.get<UnidadMedida[]>("/api/v1/unidades-medida/").then((r) => r.data),
};
