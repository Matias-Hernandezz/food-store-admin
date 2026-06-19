import api from "../../../shared/api/axiosClient";
import type {
  Ingrediente,
  IngredienteCreate,
  IngredienteUpdate,
  IngredienteList,
} from "../../../shared/types";

const BASE = "/api/v1/ingredientes";

export const ingredienteApi = {
  getAll: (offset = 0, limit = 100) =>
    api.get<IngredienteList>(`${BASE}/?offset=${offset}&limit=${limit}`).then((r) => r.data),

  getById: (id: number) =>
    api.get<Ingrediente>(`${BASE}/${id}`).then((r) => r.data),

  create: (data: IngredienteCreate) =>
    api.post<Ingrediente>(BASE + "/", data).then((r) => r.data),

  update: (id: number, data: IngredienteUpdate) =>
    api.patch<Ingrediente>(`${BASE}/${id}`, data).then((r) => r.data),

  delete: (id: number) =>
    api.delete(`${BASE}/${id}`),
};
