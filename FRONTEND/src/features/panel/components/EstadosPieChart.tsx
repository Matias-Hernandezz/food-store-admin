import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import type { PedidosEstadoItem } from "../hooks/useEstadisticas";

interface Props { data: PedidosEstadoItem[]; loading: boolean; error: boolean; onRetry?: () => void; }

const COLORS: Record<string, string> = { PENDIENTE: "#eab308", CONFIRMADO: "#3b82f6", EN_PREP: "#f59e0b", ENTREGADO: "#059669", CANCELADO: "#dc2626" };
const LABELS: Record<string, string> = { PENDIENTE: "Pendiente", CONFIRMADO: "Confirmado", EN_PREP: "En Prep.", ENTREGADO: "Entregado", CANCELADO: "Cancelado" };
const C = { text: "#1e293b", muted: "#94a3b8", card: "#fff", grid: "#e2e8f0" };

export function EstadosPieChart({ data, loading, error, onRetry }: Props) {
  if (error) return <div className="h-[220px] flex flex-col items-center justify-center gap-3" style={{ color: "#dc2626" }}><p>Error al cargar</p>{onRetry && <button onClick={onRetry} className="text-sm underline cursor-pointer">Reintentar</button>}</div>;
  if (loading) return <div className="h-[220px] flex items-center justify-center" style={{ color: C.muted }}>Cargando...</div>;
  if (data.length === 0) return <div className="h-[220px] flex items-center justify-center" style={{ color: C.muted }}>Sin datos aún</div>;

  const chartData = data.map((d) => ({ ...d, cantidad: Number(d.cantidad), name: LABELS[d.estado_codigo] ?? d.estado_codigo }));

  return (
    <div style={{ width: "100%", height: 220 }}>
      <ResponsiveContainer>
        <PieChart>
          <Pie data={chartData} cx="50%" cy="50%" innerRadius={45} outerRadius={75} paddingAngle={3} dataKey="cantidad">
            {chartData.map((entry) => <Cell key={entry.estado_codigo} fill={COLORS[entry.estado_codigo] ?? C.muted} />)}
          </Pie>
          <Tooltip contentStyle={{ backgroundColor: C.card, border: `1px solid ${C.grid}`, borderRadius: 8, fontSize: 12, color: C.text }} />
          <Legend wrapperStyle={{ fontSize: 11, color: C.text }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
