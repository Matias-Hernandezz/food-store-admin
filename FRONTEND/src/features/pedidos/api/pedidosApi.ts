import api from "../../../shared/api/axiosClient";
import { Pedido, PedidoList, PedidoCreate, DireccionCreate, DireccionRead, FormaPago } from "../types";

const BASE = "/api/v1/pedidos";

export const pedidosApi = {
  getAll: (offset = 0, limit = 50, desde?: string, hasta?: string, search?: string) => {
    const params = new URLSearchParams({ offset: String(offset), limit: String(limit) });
    if (desde) params.set("desde", desde);
    if (hasta) params.set("hasta", hasta);
    if (search) params.set("search", search);
    return api.get<PedidoList>(`${BASE}/?${params}`).then((r) => r.data);
  },

  getById: (id: number) =>
    api.get<Pedido>(`${BASE}/${id}`).then((r) => r.data),

  avanzarEstado: (id: number, nuevoEstado: string, motivo?: string) =>
    api.patch<Pedido>(`${BASE}/${id}/estado`, {
      nuevo_estado: nuevoEstado,
      motivo: motivo ?? null,
    }).then((r) => r.data),

  crear: (data: PedidoCreate) =>
    api.post<Pedido>(`${BASE}/`, data).then((r) => r.data),

  getMisPedidos: () =>
    api.get<PedidoList>(`${BASE}/?limit=50`).then((r) => r.data),

  getFormasPago: () =>
    api.get<FormaPago[]>(`${BASE}/formas-pago`).then((r) => r.data),

  getDirecciones: () =>
    api.get<DireccionRead[]>("/api/v1/direcciones").then((r) => r.data),

  getCocinaPedidos: (desde?: string, hasta?: string) => {
    const params = new URLSearchParams();
    if (desde) params.set("desde", desde);
    if (hasta) params.set("hasta", hasta);
    const qs = params.toString();
    return api.get<PedidoList>(`${BASE}/cocina${qs ? "?" + qs : ""}`).then((r) => r.data);
  },

  crearDireccion: (data: DireccionCreate) =>
    api.post<DireccionRead>("/api/v1/direcciones", data).then((r) => r.data),
};
