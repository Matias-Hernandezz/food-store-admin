import {
  LineChart,
  Line,
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
}

export function VentasChart({ data, loading }: Props) {
  if (loading) {
    return (
      <div className="h-[300px] flex items-center justify-center" style={{ color: "#9a8070" }}>
        Cargando gráfico...
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="h-[300px] flex items-center justify-center" style={{ color: "#9a8070" }}>
        Sin datos para el período seleccionado
      </div>
    );
  }

  const chartData = data.map((d) => ({
    ...d,
    total_ventas: Number(d.total_ventas),
    cantidad_pedidos: Number(d.cantidad_pedidos),
  }));

  return (
    <div style={{ width: "100%", height: 300 }}>
      <ResponsiveContainer>
        <LineChart data={chartData} margin={{ top: 10, right: 40, left: 10, bottom: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e8ddd5" />
        <XAxis dataKey="periodo" tick={{ fontSize: 11, fill: "#9a8070" }} />
        <YAxis
          yAxisId="left"
          tick={{ fontSize: 11, fill: "#9a8070" }}
          tickFormatter={(v) => {
            const n = Number(v);
            if (n >= 1000) return `$${(n / 1000).toFixed(1)}k`;
            return `$${n.toFixed(0)}`;
          }}
        />
        <YAxis
          yAxisId="right"
          orientation="right"
          tick={{ fontSize: 11, fill: "#9a8070" }}
          tickFormatter={(v) => Number(v).toFixed(0)}
          allowDecimals={false}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#fff",
            border: "1px solid #d6c9be",
            borderRadius: 8,
            fontSize: 12,
          }}
        />
        <Legend wrapperStyle={{ fontSize: 12, color: "#2d1e0f" }} />
        <Line
          yAxisId="left"
          type="monotone"
          dataKey="total_ventas"
          stroke="#c2652a"
          strokeWidth={2}
          dot={{ fill: "#c2652a", r: 4 }}
          activeDot={{ r: 6 }}
          name="Total ($)"
          connectNulls
        />
        <Line
          yAxisId="right"
          type="monotone"
          dataKey="cantidad_pedidos"
          stroke="#8c3c3c"
          strokeWidth={2}
          dot={{ fill: "#8c3c3c", r: 4 }}
          activeDot={{ r: 6 }}
          name="Cant. Pedidos"
          connectNulls
        />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
