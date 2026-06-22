import api from "../../../shared/api/axiosClient";
import type {
  Ingrediente,
  IngredienteCreate,
  IngredienteUpdate,
  IngredienteList,
} from "../../../shared/types";

const BASE = "/api/v1/ingredientes";

export const ingredienteApi = {
  getAll: (offset = 0, limit = 100, incluirEliminados = false) =>
    api.get<IngredienteList>(`${BASE}/?offset=${offset}&limit=${limit}&incluir_eliminados=${incluirEliminados}`).then((r) => r.data),

  getById: (id: number) =>
    api.get<Ingrediente>(`${BASE}/${id}`).then((r) => r.data),

  create: (data: IngredienteCreate) =>
    api.post<Ingrediente>(BASE + "/", data).then((r) => r.data),

  update: (id: number, data: IngredienteUpdate) =>
    api.put<Ingrediente>(`${BASE}/${id}`, data).then((r) => r.data),

  restore: (id: number) =>
    api.patch<Ingrediente>(`${BASE}/${id}/restaurar`).then((r) => r.data),

  delete: (id: number) =>
    api.delete(`${BASE}/${id}`),
};
