import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import type { IngresosItem } from "../hooks/useEstadisticas";

interface Props { data: IngresosItem[]; loading: boolean; error: boolean; onRetry?: () => void; }

const LABELS: Record<string, string> = { EFECTIVO: "Efectivo", MERCADOPAGO: "MercadoPago", MERCADO_PAGO: "MercadoPago", TRANSFERENCIA: "Transferencia" };
const C = { primary: "#0f766e", text: "#1e293b", muted: "#94a3b8", grid: "#e2e8f0", card: "#fff" };

export function IngresosPagoChart({ data, loading, error, onRetry }: Props) {
  if (error) return <div className="h-[250px] flex flex-col items-center justify-center gap-3" style={{ color: "#dc2626" }}><p>Error al cargar</p>{onRetry && <button onClick={onRetry} className="text-sm underline cursor-pointer">Reintentar</button>}</div>;
  if (loading) return <div className="h-[250px] flex items-center justify-center" style={{ color: C.muted }}>Cargando...</div>;
  if (data.length === 0) return <div className="h-[250px] flex items-center justify-center" style={{ color: C.muted }}>Sin datos aún</div>;

  const chartData = data.map((d) => ({ ...d, label: LABELS[d.forma_pago_codigo] ?? d.forma_pago_codigo, total: Number(d.total), cantidad: Number(d.cantidad) }));

  return (
    <div style={{ width: "100%", height: 250 }}>
      <ResponsiveContainer>
        <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={C.grid} horizontal={false} />
          <XAxis type="number" tick={{ fontSize: 11, fill: C.muted }} tickFormatter={(v) => `$${Number(v).toFixed(0)}`} />
          <YAxis type="category" dataKey="label" tick={{ fontSize: 11, fill: C.text }} width={100} />
          <Tooltip contentStyle={{ backgroundColor: C.card, border: `1px solid ${C.grid}`, borderRadius: 8, fontSize: 12, color: C.text }}
            formatter={(value: number, name: string) => [name === "total" ? `$${value.toFixed(2)}` : `${value} pedidos`, name === "total" ? "Total" : "Cantidad"]} />
          <Bar dataKey="total" fill={C.primary} radius={[0, 4, 4, 0]} barSize={24} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
