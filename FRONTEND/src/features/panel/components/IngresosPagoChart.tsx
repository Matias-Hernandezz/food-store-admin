import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { IngresosItem } from "../hooks/useEstadisticas";

const LABELS: Record<string, string> = {
  EFECTIVO: "Efectivo",
  MERCADOPAGO: "MercadoPago",
  TRANSFERENCIA: "Transferencia",
  MERCADO_PAGO: "MercadoPago",
};

interface Props {
  data: IngresosItem[];
  loading: boolean;
  error: boolean;
  onRetry?: () => void;
}

export function IngresosPagoChart({ data, loading, error, onRetry }: Props) {
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
        Sin datos para el período
      </div>
    );
  }

  const chartData = data.map((item) => ({
    nombre: LABELS[item.forma_pago_codigo] ?? item.forma_pago_codigo,
    total: item.total,
    cantidad: item.cantidad,
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
        <YAxis type="category" dataKey="nombre" tick={{ fontSize: 10, fill: "#9a8070" }} width={100} />
        <Tooltip
          contentStyle={{
            backgroundColor: "#fff",
            border: "1px solid #d6c9be",
            borderRadius: 8,
            fontSize: 12,
          }}
          formatter={(value: number | string, name: string) => [
            name === "total" ? `$${Number(value).toFixed(2)}` : `${Number(value)} pedidos`,
            name === "total" ? "Total" : "Cantidad",
          ]}
        />
        <Bar dataKey="total" fill="#c2652a" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
