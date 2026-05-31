import { apiFetch } from "../../../shared/api/client";
import type {
  Ingrediente,
  IngredienteCreate,
  IngredienteUpdate,
  IngredienteList,
} from "../../../shared/types";

const BASE = "/ingredientes";

export const ingredienteApi = {
  getAll: (offset = 0, limit = 100) =>
    apiFetch<IngredienteList>(`${BASE}/?offset=${offset}&limit=${limit}`),

  getById: (id: number) =>
    apiFetch<Ingrediente>(`${BASE}/${id}`),

  create: (data: IngredienteCreate) =>
    apiFetch<Ingrediente>(BASE + "/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: number, data: IngredienteUpdate) =>
    apiFetch<Ingrediente>(`${BASE}/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  delete: (id: number) =>
    apiFetch<void>(`${BASE}/${id}`, { method: "DELETE" }),
};
