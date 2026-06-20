import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { ProductoTopItem } from "../hooks/useEstadisticas";

interface Props {
  data: ProductoTopItem[];
  loading: boolean;
  error: boolean;
  onRetry?: () => void;
}

export function ProductosTopChart({ data, loading, error, onRetry }: Props) {
  if (error) {
    return (
      <div className="h-[300px] flex flex-col items-center justify-center gap-3" style={{ color: "#dc2626" }}>
        <p>Error al cargar datos del servidor</p>
        {onRetry && (
          <button onClick={onRetry} className="text-sm underline cursor-pointer hover:opacity-80">
            Reintentar
          </button>
        )}
      </div>
    );
  }

  if (loading) {
    return (
      <div className="h-[300px] flex items-center justify-center" style={{ color: "#9a8070" }}>
        Cargando...
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="h-[250px] flex items-center justify-center" style={{ color: "#9a8070" }}>
        Sin datos aún
      </div>
    );
  }

  const chartData = data.map((item) => ({
    nombre:
      item.nombre.length > 18 ? item.nombre.slice(0, 16) + "…" : item.nombre,
    ingresos: item.ingresos,
    cantidad: item.cantidad_vendida,
  }));

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e8ddd5" horizontal={false} />
        <XAxis type="number" tick={{ fontSize: 10, fill: "#9a8070" }} tickFormatter={(v) => `$${v}`} />
        <YAxis type="category" dataKey="nombre" tick={{ fontSize: 10, fill: "#9a8070" }} width={120} />
        <Tooltip
          contentStyle={{
            backgroundColor: "#fff",
            border: "1px solid #d6c9be",
            borderRadius: 8,
            fontSize: 12,
          }}
          formatter={(value: number | string, name: string) => [
            name === "ingresos" ? `$${Number(value).toFixed(2)}` : `${Number(value)} vend.`,
            name === "ingresos" ? "Ingresos" : "Cantidad",
          ]}
        />
        <Bar dataKey="ingresos" fill="#c2652a" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
