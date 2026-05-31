// features/pedidos/api/pedidosApi.ts
import { apiFetch } from "../../../shared/api/client";

const BASE = "/api/v1/pedidos";

export interface DetallePedido {
  producto_id: number;
  cantidad: number;
  nombre_snapshot: string;
  precio_snapshot: number;
  subtotal: number;
}

export interface Pedido {
  id: number;
  usuario_id: number;
  estado_codigo: string;
  forma_pago_codigo: string;
  subtotal: number;
  descuento: number;
  costo_envio: number;
  total: number;
  notas: string | null;
  created_at: string;
  detalles: DetallePedido[];
}

export interface PedidoList {
  data: Pedido[];
  total: number;
}

export const pedidosApi = {
  getAll: (offset = 0, limit = 50) =>
    apiFetch<PedidoList>(`${BASE}/?offset=${offset}&limit=${limit}`),

  getById: (id: number) =>
    apiFetch<Pedido>(`${BASE}/${id}`),

  avanzarEstado: (id: number, nuevoEstado: string, motivo?: string) =>
    apiFetch<Pedido>(`${BASE}/${id}/estado/${nuevoEstado}`, {
      method: "PATCH",
      body: JSON.stringify({ motivo: motivo ?? null }),
    }),
};