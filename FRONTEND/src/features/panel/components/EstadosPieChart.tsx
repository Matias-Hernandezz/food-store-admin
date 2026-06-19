import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { PedidosEstadoItem } from "../hooks/useEstadisticas";

const COLORS: Record<string, string> = {
  PENDIENTE: "#eab308",
  CONFIRMADO: "#3b82f6",
  EN_PREP: "#f97316",
  ENTREGADO: "#22c55e",
  CANCELADO: "#ef4444",
};

const LABELS: Record<string, string> = {
  PENDIENTE: "Pendiente",
  CONFIRMADO: "Confirmado",
  EN_PREP: "En Prep.",
  ENTREGADO: "Entregado",
  CANCELADO: "Cancelado",
};

interface Props {
  data: PedidosEstadoItem[];
  loading: boolean;
}

export function EstadosPieChart({ data, loading }: Props) {
  if (loading) {
    return (
      <div className="h-[220px] flex items-center justify-center" style={{ color: "#9a8070" }}>
        Cargando...
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="h-[220px] flex items-center justify-center" style={{ color: "#9a8070" }}>
        Sin datos aún
      </div>
    );
  }

  const chartData = data.map((item) => ({
    name: LABELS[item.estado_codigo] ?? item.estado_codigo,
    value: item.cantidad,
    color: COLORS[item.estado_codigo] ?? "#9a8070",
  }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius={45}
          outerRadius={80}
          paddingAngle={2}
          dataKey="value"
        >
          {chartData.map((entry, i) => (
            <Cell key={i} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: "#fff",
            border: "1px solid #d6c9be",
            borderRadius: 8,
            fontSize: 12,
          }}
        />
        <Legend
          wrapperStyle={{ fontSize: 10, color: "#2d1e0f" }}
          iconSize={8}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
