import api from "../../../shared/api/axiosClient";
import type {
  Categoria,
  CategoriaCreate,
  CategoriaUpdate,
  CategoriaList,
} from "../../../shared/types";

const BASE = "/api/v1/categorias";

export const categoriaApi = {
  getAll: (offset = 0, limit = 100) =>
    api.get<CategoriaList>(`${BASE}/?offset=${offset}&limit=${limit}`).then((r) => r.data),

  getById: (id: number) =>
    api.get<Categoria>(`${BASE}/${id}`).then((r) => r.data),

  create: (data: CategoriaCreate) =>
    api.post<Categoria>(BASE + "/", data).then((r) => r.data),

  update: (id: number, data: CategoriaUpdate) =>
    api.patch<Categoria>(`${BASE}/${id}`, data).then((r) => r.data),

  delete: (id: number) =>
    api.delete(`${BASE}/${id}`),
};
