import { useState } from "react";
import { useAdminOrdersFeed } from "../../../shared/hooks/useAdminOrdersFeed";
import {
  useResumen,
  useVentas,
  useProductosTop,
  usePedidosPorEstado,
  useIngresos,
} from "../hooks/useEstadisticas";
import { KPICard } from "../components/KPICard";
import { VentasChart } from "../components/VentasChart";
import { ProductosTopChart } from "../components/ProductosTopChart";
import { EstadosPieChart } from "../components/EstadosPieChart";
import { IngresosPagoChart } from "../components/IngresosPagoChart";
import { Icons } from "../../../shared/components/ui/Icons";

function daysAgoStr(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d.toISOString().slice(0, 10);
}

function todayStr(): string {
  return new Date().toISOString().slice(0, 10);
}

export function DashboardPage() {
  useAdminOrdersFeed();

  const [desde, setDesde] = useState(() => daysAgoStr(14));
  const [hasta, setHasta] = useState(() => todayStr());

  const { data: resumen } = useResumen();
  const { data: ventas, isLoading: loadingVentas } = useVentas(desde, hasta);
  const { data: productosTop, isLoading: loadingTop } = useProductosTop(8);
  const { data: pedidosEstado, isLoading: loadingEstados } = usePedidosPorEstado();
  const { data: ingresos, isLoading: loadingIngresos } = useIngresos(desde, hasta);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6" style={{ color: "#2d1e0f" }}>
        Panel
      </h1>

      {/* ─── Filtro de fechas ────────────────────────────────────────── */}
      <div className="flex items-center gap-3 mb-8">
        <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-lg border border-[#d6c9be]">
          <span className="text-xs font-bold uppercase tracking-wider" style={{ color: "#9a8070" }}>
            Desde
          </span>
          <input
            type="date"
            value={desde}
            onChange={(e) => setDesde(e.target.value)}
            className="border-none p-0 text-sm focus:ring-0 bg-transparent"
            style={{ color: "#2d1e0f" }}
          />
        </div>
        <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-lg border border-[#d6c9be]">
          <span className="text-xs font-bold uppercase tracking-wider" style={{ color: "#9a8070" }}>
            Hasta
          </span>
          <input
            type="date"
            value={hasta}
            onChange={(e) => setHasta(e.target.value)}
            className="border-none p-0 text-sm focus:ring-0 bg-transparent"
            style={{ color: "#2d1e0f" }}
          />
        </div>
      </div>

      {/* ─── KPIs ────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <KPICard
          label="Ventas de Hoy"
          value={resumen ? `$${Number(resumen.ventas_hoy).toFixed(2)}` : "—"}
          icon={<Icons.TrendingUp width={20} height={20} />}
          accentColor="#c2652a"
          accentBg="rgba(194,101,42,0.1)"
        />
        <KPICard
          label="Ticket Promedio"
          value={resumen ? `$${Number(resumen.ticket_promedio).toFixed(2)}` : "—"}
          icon={<Icons.ShoppingBag width={20} height={20} />}
          accentColor="#8c3c3c"
          accentBg="rgba(140,60,60,0.1)"
        />
        <KPICard
          label="Pedidos Activos"
          value={resumen ? String(resumen.pedidos_activos) : "—"}
          icon={<Icons.RestaurantMenu width={20} height={20} />}
          accentColor="#504840"
          accentBg="rgba(80,72,64,0.1)"
        />
        <KPICard
          label="Ingresos del Mes"
          value={resumen ? `$${Number(resumen.mes_actual).toFixed(2)}` : "—"}
          icon={<Icons.Payments width={20} height={20} />}
          accentColor="#c2652a"
          accentBg="rgba(194,101,42,0.08)"
        />
      </div>

      {/* ─── Ventas por Período ──────────────────────────────────────── */}
      <div
        className="p-7 rounded-xl border mb-8"
        style={{
          backgroundColor: "#fff",
          borderColor: "rgba(214, 201, 190, 0.2)",
          boxShadow: "0 2px 16px rgba(58, 48, 42, 0.04)",
        }}
      >
        <h3 className="text-xl font-bold mb-1" style={{ color: "#2d1e0f" }}>
          Ventas por Período
        </h3>
        <p className="text-sm mb-6" style={{ color: "#9a8070" }}>
          Total de ventas y cantidad de pedidos en el intervalo seleccionado.
        </p>
        <VentasChart data={ventas ?? []} loading={loadingVentas} />
      </div>

      {/* ─── Gráficos inferiores ─────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div
          className="p-7 rounded-xl border"
          style={{
            backgroundColor: "#fff",
            borderColor: "rgba(214, 201, 190, 0.2)",
            boxShadow: "0 2px 16px rgba(58, 48, 42, 0.04)",
          }}
        >
          <h4 className="text-lg font-bold mb-4" style={{ color: "#2d1e0f" }}>
            Top Productos
          </h4>
          <ProductosTopChart data={productosTop ?? []} loading={loadingTop} />
        </div>

        <div
          className="p-7 rounded-xl border flex flex-col items-center"
          style={{
            backgroundColor: "#fff",
            borderColor: "rgba(214, 201, 190, 0.2)",
            boxShadow: "0 2px 16px rgba(58, 48, 42, 0.04)",
          }}
        >
          <h4 className="text-lg font-bold mb-4 self-start" style={{ color: "#2d1e0f" }}>
            Distribución por Estado
          </h4>
          <EstadosPieChart data={pedidosEstado ?? []} loading={loadingEstados} />
        </div>

        <div
          className="p-7 rounded-xl border"
          style={{
            backgroundColor: "#fff",
            borderColor: "rgba(214, 201, 190, 0.2)",
            boxShadow: "0 2px 16px rgba(58, 48, 42, 0.04)",
          }}
        >
          <h4 className="text-lg font-bold mb-4" style={{ color: "#2d1e0f" }}>
            Ingresos por Pago
          </h4>
          <IngresosPagoChart data={ingresos ?? []} loading={loadingIngresos} />
        </div>
      </div>
    </div>
  );
}
