import type { Pedido } from "../api/pedidosApi";
import { ESTADO_LABEL, ESTADO_COLOR, ESTADOS_FSM } from "../hooks/usePedidos";

interface Props {
    pedido: Pedido;
    onAvanzar: (id: number, estado: string) => void;
    loading: boolean;
}

export function PedidoCard({ pedido, onAvanzar, loading }: Props) {
    const siguientes = ESTADOS_FSM[pedido.estado_codigo] ?? [];

    return (
        <div className="rounded-2xl p-5 shadow-sm" style={{ backgroundColor: "#fff", border: "1px solid #d6c9be" }}>
            <div className="flex items-center justify-between mb-3">
                <div>
                    <span className="text-xs font-mono" style={{ color: "#9a8070" }}>#{pedido.id}</span>
                    <p className="text-sm font-semibold" style={{ color: "#2d1e0f" }}>Usuario #{pedido.usuario_id}</p>
                    <p className="text-xs" style={{ color: "#9a8070" }}>{new Date(pedido.created_at).toLocaleString("es-AR")}</p>
                </div>
                <span className={`text-xs font-bold px-3 py-1 rounded-full ${ESTADO_COLOR[pedido.estado_codigo]}`}>
                    {ESTADO_LABEL[pedido.estado_codigo]}
                </span>
            </div>

            <div className="pt-3 mb-3 space-y-1" style={{ borderTop: "1px solid #f0e8e0" }}>
                {pedido.detalles.map((d) => (
                    <div key={d.producto_id} className="flex justify-between text-sm">
                        <span style={{ color: "#6b5a4e" }}>{d.cantidad}x {d.nombre_snapshot}</span>
                        <span className="font-medium" style={{ color: "#2d1e0f" }}>${Number(d.subtotal).toFixed(2)}</span>
                    </div>
                ))}
            </div>

            <div className="flex justify-between text-sm font-bold pt-2 mb-4" style={{ borderTop: "1px solid #f0e8e0" }}>
                <span style={{ color: "#2d1e0f" }}>Total</span>
                <span style={{ color: "#c8722a" }}>${Number(pedido.total).toFixed(2)}</span>
            </div>

            {siguientes.length > 0 && (
                <div className="flex gap-2 flex-wrap">
                    {siguientes.map((estado) => (
                        <button key={estado} disabled={loading} onClick={() => onAvanzar(pedido.id, estado)}
                            className="flex-1 text-xs font-bold py-2 px-3 rounded-xl transition-all disabled:opacity-50"
                            style={estado === "CANCELADO"
                                ? { backgroundColor: "#fee2e2", color: "#991b1b", border: "1px solid #fecaca" }
                                : { backgroundColor: "#c8722a", color: "#fff" }}>
                            → {ESTADO_LABEL[estado]}
                        </button>
                    ))}
                </div>
            )}
            {siguientes.length === 0 && <p className="text-xs text-center italic" style={{ color: "#9a8070" }}>Estado terminal</p>}
        </div>
    );
}