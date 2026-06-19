import { useQuery } from "@tanstack/react-query";
import api from "../../../shared/api/axiosClient";

// ─── Tipos ────────────────────────────────────────────────────────────────

export interface ResumenResponse {
  ventas_hoy: number;
  ticket_promedio: number;
  pedidos_activos: number;
  mes_actual: number;
}

export interface VentasPeriodoItem {
  periodo: string;
  total_ventas: number;
  cantidad_pedidos: number;
}

export interface ProductoTopItem {
  producto_id: number;
  nombre: string;
  ingresos: number;
  cantidad_vendida: number;
}

export interface PedidosEstadoItem {
  estado_codigo: string;
  cantidad: number;
}

export interface IngresosItem {
  forma_pago_codigo: string;
  total: number;
  cantidad: number;
}

// ─── Hooks ─────────────────────────────────────────────────────────────────

const BASE = "/api/v1/estadisticas";

export function useResumen() {
  return useQuery({
    queryKey: ["estadisticas", "resumen"],
    queryFn: () => api.get<ResumenResponse>(`${BASE}/resumen`).then((r) => r.data),
    refetchInterval: 30000,
  });
}

export function useVentas(desde: string, hasta: string, agrupacion: "day" | "week" | "month" = "day") {
  return useQuery({
    queryKey: ["estadisticas", "ventas", desde, hasta, agrupacion],
    queryFn: () =>
      api.get<VentasPeriodoItem[]>(`${BASE}/ventas`, {
        params: { desde, hasta, agrupacion },
      }).then((r) => r.data),
    enabled: !!desde && !!hasta,
  });
}

export function useProductosTop(limit: number = 8) {
  return useQuery({
    queryKey: ["estadisticas", "productos-top", limit],
    queryFn: () =>
      api.get<ProductoTopItem[]>(`${BASE}/productos-top`, {
        params: { limit },
      }).then((r) => r.data),
    refetchInterval: 60000,
  });
}

export function usePedidosPorEstado() {
  return useQuery({
    queryKey: ["estadisticas", "pedidos-por-estado"],
    queryFn: () => api.get<PedidosEstadoItem[]>(`${BASE}/pedidos-por-estado`).then((r) => r.data),
    refetchInterval: 30000,
  });
}

export function useIngresos(desde: string, hasta: string) {
  return useQuery({
    queryKey: ["estadisticas", "ingresos", desde, hasta],
    queryFn: () =>
      api.get<IngresosItem[]>(`${BASE}/ingresos`, {
        params: { desde, hasta },
      }).then((r) => r.data),
    enabled: !!desde && !!hasta,
  });
}
