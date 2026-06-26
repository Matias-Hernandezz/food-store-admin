import { useState } from "react";
import {
  useEstadisticas,
} from "../hooks/useEstadisticas";
import { KPICard } from "../components/KPICard";
import { VentasChart } from "../components/VentasChart";
import { ProductosTopChart } from "../components/ProductosTopChart";
import { EstadosPieChart } from "../components/EstadosPieChart";
import { IngresosPagoChart } from "../components/IngresosPagoChart";
import { ConnectionBadge } from "../../../shared/components/ConnectionBadge";
import { Icons } from "../../../shared/components/ui/Icons";

const C = { bg: "#f8fafc", card: "#fff", border: "#e2e8f0", text: "#1e293b", muted: "#64748b", shadow: "0 1px 3px rgba(0,0,0,0.04)" };

function toLocalISO(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}
function daysAgoStr(days: number): string {
  const d = new Date(); d.setDate(d.getDate() - days);
  return toLocalISO(d);
}
function todayStr(): string { return toLocalISO(new Date()); }

export function DashboardPage() {
  const [desde, setDesde] = useState(() => daysAgoStr(14));
  const [hasta, setHasta] = useState(() => todayStr());

  const { resumen, ventas, ventasLoading: lV, ventasError: eV, ventasRefetch: rV, productosTop, productosTopLoading: lT, productosTopError: eT, productosTopRefetch: rT, pedidosPorEstado: pedidosEstado, pedidosPorEstadoLoading: lE, pedidosPorEstadoError: eE, pedidosPorEstadoRefetch: rE, ingresos, ingresosLoading: lI, ingresosError: eI, ingresosRefetch: rI } = useEstadisticas({ desde, hasta });

  return (
    <div style={{ backgroundColor: C.bg, minHeight: "100vh" }}>
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-6 flex items-center gap-4" style={{ color: "#0f172a" }}>
          Dashboard
          <ConnectionBadge />
        </h1>

        {/* Filtro de fechas */}
        <div className="flex items-center gap-3 mb-8">
          <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-lg border" style={{ borderColor: C.border }}>
            <span className="text-xs font-bold uppercase tracking-wider" style={{ color: C.muted }}>Desde</span>
            <input type="date" value={desde} onChange={(e) => setDesde(e.target.value)} className="border-none p-0 text-sm focus:ring-0 bg-transparent" style={{ color: C.text }} />
          </div>
          <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-lg border" style={{ borderColor: C.border }}>
            <span className="text-xs font-bold uppercase tracking-wider" style={{ color: C.muted }}>Hasta</span>
            <input type="date" value={hasta} onChange={(e) => setHasta(e.target.value)} className="border-none p-0 text-sm focus:ring-0 bg-transparent" style={{ color: C.text }} />
          </div>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <KPICard label="Ventas de Hoy" value={resumen ? `$${Number(resumen.ventas_hoy).toFixed(2)}` : "—"} icon={<Icons.TrendingUp width={20} height={20} />} accentColor="#059669" accentBg="#ecfdf5" />
          <KPICard label="Ticket Promedio" value={resumen ? `$${Number(resumen.ticket_promedio).toFixed(2)}` : "—"} icon={<Icons.ShoppingBag width={20} height={20} />} accentColor="#0f766e" accentBg="#f0fdfa" />
          <KPICard label="Pedidos Activos" value={resumen ? String(resumen.pedidos_activos) : "—"} icon={<Icons.RestaurantMenu width={20} height={20} />} accentColor="#d97706" accentBg="#fffbeb" />
          <KPICard label="Ingresos del Mes" value={resumen ? `$${Number(resumen.mes_actual).toFixed(2)}` : "—"} icon={<Icons.Payments width={20} height={20} />} accentColor="#7c3aed" accentBg="#f5f3ff" />
        </div>

        {/* Ventas */}
        <div className="p-7 rounded-xl border mb-8" style={{ backgroundColor: C.card, borderColor: C.border, boxShadow: C.shadow }}>
          <h3 className="text-xl font-bold mb-1" style={{ color: "#0f172a" }}>Ventas por Período</h3>
          <p className="text-sm mb-6" style={{ color: C.muted }}>Total de ventas y cantidad de pedidos en el intervalo seleccionado.</p>
          <VentasChart data={ventas ?? []} loading={lV} error={eV} onRetry={rV} />
        </div>

        {/* Gráficos inferiores */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="p-7 rounded-xl border" style={{ backgroundColor: C.card, borderColor: C.border, boxShadow: C.shadow }}>
            <h4 className="text-lg font-bold mb-4" style={{ color: "#0f172a" }}>Top Productos</h4>
            <ProductosTopChart data={productosTop ?? []} loading={lT} error={eT} onRetry={rT} />
          </div>
          <div className="p-7 rounded-xl border flex flex-col items-center" style={{ backgroundColor: C.card, borderColor: C.border, boxShadow: C.shadow }}>
            <h4 className="text-lg font-bold mb-4 self-start" style={{ color: "#0f172a" }}>Distribución por Estado</h4>
            <EstadosPieChart data={pedidosEstado ?? []} loading={lE} error={eE} onRetry={rE} />
          </div>
          <div className="p-7 rounded-xl border" style={{ backgroundColor: C.card, borderColor: C.border, boxShadow: C.shadow }}>
            <h4 className="text-lg font-bold mb-4" style={{ color: "#0f172a" }}>Ingresos por Pago</h4>
            <IngresosPagoChart data={ingresos ?? []} loading={lI} error={eI} onRetry={rI} />
          </div>
        </div>
      </div>
    </div>
  );
}
