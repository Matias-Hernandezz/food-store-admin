import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { VentasPeriodoItem } from "../hooks/useEstadisticas";

interface Props {
  data: VentasPeriodoItem[];
  loading: boolean;
  error: boolean;
  onRetry?: () => void;
}

const C = { primary: "#059669", secondary: "#0f766e", accent: "#d97706", text: "#1e293b", muted: "#94a3b8", grid: "#e2e8f0", card: "#fff", bg: "#f8fafc" };

export function VentasChart({ data, loading, error, onRetry }: Props) {
  if (error) return (
    <div className="h-[300px] flex flex-col items-center justify-center gap-3" style={{ color: "#dc2626" }}>
      <p>Error al cargar datos</p>
      {onRetry && <button onClick={onRetry} className="text-sm underline cursor-pointer">Reintentar</button>}
    </div>
  );
  if (loading) return <div className="h-[300px] flex items-center justify-center" style={{ color: C.muted }}>Cargando gráfico...</div>;
  if (data.length === 0) return <div className="h-[300px] flex items-center justify-center" style={{ color: C.muted }}>Sin datos para este período</div>;

  const chartData = data.map((d) => ({ ...d, total_ventas: Number(d.total_ventas), cantidad_pedidos: Number(d.cantidad_pedidos) }));

  return (
    <div style={{ width: "100%", height: 300 }}>
      <ResponsiveContainer>
        <AreaChart data={chartData} margin={{ top: 10, right: 40, left: 10, bottom: 10 }}>
          <defs>
            <linearGradient id="colorVentas" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={C.primary} stopOpacity={0.3} />
              <stop offset="95%" stopColor={C.primary} stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorPedidos" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={C.accent} stopOpacity={0.2} />
              <stop offset="95%" stopColor={C.accent} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke={C.grid} />
          <XAxis dataKey="periodo" tick={{ fontSize: 11, fill: C.muted }} />
          <YAxis yAxisId="left" tick={{ fontSize: 11, fill: C.muted }} tickFormatter={(v) => Number(v) >= 1000 ? `$${(Number(v)/1000).toFixed(1)}k` : `$${Number(v).toFixed(0)}`} />
          <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11, fill: C.muted }} tickFormatter={(v) => Number(v).toFixed(0)} allowDecimals={false} />
          <Tooltip contentStyle={{ backgroundColor: C.card, border: `1px solid ${C.grid}`, borderRadius: 8, fontSize: 12, color: C.text }} />
          <Legend wrapperStyle={{ fontSize: 12, color: C.text }} />
          <Area yAxisId="left" type="monotone" dataKey="total_ventas" stroke={C.primary} fill="url(#colorVentas)" strokeWidth={2} dot={{ fill: C.primary, r: 3 }} activeDot={{ r: 5 }} name="Total ($)" connectNulls />
          <Area yAxisId="right" type="monotone" dataKey="cantidad_pedidos" stroke={C.accent} fill="url(#colorPedidos)" strokeWidth={2} dot={{ fill: C.accent, r: 3 }} activeDot={{ r: 5 }} name="Pedidos" connectNulls />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
