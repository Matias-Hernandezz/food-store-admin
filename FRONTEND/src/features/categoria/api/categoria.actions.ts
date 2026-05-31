import { apiFetch } from "../../../shared/api/client";
import type {
  Categoria,
  CategoriaCreate,
  CategoriaUpdate,
  CategoriaList,
} from "../../../shared/types";

const BASE = "/categorias";

export const categoriaApi = {
  getAll: (offset = 0, limit = 100) =>
    apiFetch<CategoriaList>(`${BASE}/?offset=${offset}&limit=${limit}`),

  getById: (id: number) =>
    apiFetch<Categoria>(`${BASE}/${id}`),

  create: (data: CategoriaCreate) =>
    apiFetch<Categoria>(BASE + "/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: number, data: CategoriaUpdate) =>
    apiFetch<Categoria>(`${BASE}/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  delete: (id: number) =>
    apiFetch<void>(`${BASE}/${id}`, { method: "DELETE" }),
};
