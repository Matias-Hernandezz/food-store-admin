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

// ─── Hook Unificado ─────────────────────────────────────────────────────

const BASE = "/api/v1/estadisticas";

interface Props {
  desde?: string;
  hasta?: string;
  agrupacion?: "day" | "week" | "month";
  limit?: number;
  enabled?: boolean;
}

export function useEstadisticas({
  desde,
  hasta,
  agrupacion = "day",
  limit = 8,
  enabled = true,
}: Props = {}) {
  const resumen = useQuery({
    queryKey: ["estadisticas", "resumen"],
    queryFn: () => api.get<ResumenResponse>(`${BASE}/resumen`).then((r) => r.data),
    refetchInterval: 30000,
    enabled,
  });

  const ventas = useQuery({
    queryKey: ["estadisticas", "ventas", desde, hasta, agrupacion],
    queryFn: () =>
      api.get<VentasPeriodoItem[]>(`${BASE}/ventas`, {
        params: { desde, hasta, agrupacion },
      }).then((r) => r.data),
    enabled: enabled && !!desde && !!hasta,
  });

  const productosTop = useQuery({
    queryKey: ["estadisticas", "productos-top", limit],
    queryFn: () =>
      api.get<ProductoTopItem[]>(`${BASE}/productos-top`, {
        params: { limit },
      }).then((r) => r.data),
    refetchInterval: 60000,
    enabled,
  });

  const pedidosPorEstado = useQuery({
    queryKey: ["estadisticas", "pedidos-por-estado"],
    queryFn: () => api.get<PedidosEstadoItem[]>(`${BASE}/pedidos-por-estado`).then((r) => r.data),
    refetchInterval: 30000,
    enabled,
  });

  const ingresos = useQuery({
    queryKey: ["estadisticas", "ingresos", desde, hasta],
    queryFn: () =>
      api.get<IngresosItem[]>(`${BASE}/ingresos`, {
        params: { desde, hasta },
      }).then((r) => r.data),
    enabled: enabled && !!desde && !!hasta,
  });

  return {
    resumen: resumen.data,
    resumenLoading: resumen.isLoading,
    resumenError: resumen.isError,
    ventas: ventas.data,
    ventasLoading: ventas.isLoading,
    ventasError: ventas.isError,
    ventasRefetch: ventas.refetch,
    productosTop: productosTop.data,
    productosTopLoading: productosTop.isLoading,
    productosTopError: productosTop.isError,
    productosTopRefetch: productosTop.refetch,
    pedidosPorEstado: pedidosPorEstado.data,
    pedidosPorEstadoLoading: pedidosPorEstado.isLoading,
    pedidosPorEstadoError: pedidosPorEstado.isError,
    pedidosPorEstadoRefetch: pedidosPorEstado.refetch,
    ingresos: ingresos.data,
    ingresosLoading: ingresos.isLoading,
    ingresosError: ingresos.isError,
    ingresosRefetch: ingresos.refetch,
  };
}
