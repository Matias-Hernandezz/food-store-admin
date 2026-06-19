import type { Pedido } from "../types/index";
import { ESTADO_LABEL, ESTADO_COLOR, ESTADOS_FSM } from "../hooks/usePedidos";

interface Props {
    pedido: Pedido;
    onAvanzar: (id: number, estado: string) => void;
    loading: boolean;
    ingredientesMap?: Map<number, string>;
}

export function PedidoCard({ pedido, onAvanzar, loading, ingredientesMap }: Props) {
    const siguientes = ESTADOS_FSM[pedido.estado_codigo] ?? [];

    return (
        <div className="rounded-2xl p-5 shadow-sm flex flex-col h-full" style={{ backgroundColor: "#fff", border: "1px solid #d6c9be" }}>
            <div className="flex items-center justify-between mb-3">
                <div>
                    <div className="flex items-center gap-2">
                        <span className="text-xs font-mono" style={{ color: "#9a8070" }}>#{pedido.id}</span>
                        {pedido.usuario_nombre && (
                            <span className="text-sm font-semibold" style={{ color: "#2d1e0f" }}>
                                {pedido.usuario_nombre}
                            </span>
                        )}
                    </div>
                    <p className="text-xs mt-0.5" style={{ color: "#9a8070" }}>
                        {new Date(pedido.created_at).toLocaleDateString("es-AR")}{" "}
                        {new Date(pedido.created_at).toLocaleTimeString("es-AR", { hour: "2-digit", minute: "2-digit" })}
                        {pedido.forma_pago_codigo === "EFECTIVO" && " · Efectivo"}
                        {pedido.forma_pago_codigo === "MERCADOPAGO" && " · MP"}
                        {pedido.forma_pago_codigo === "TRANSFERENCIA" && " · Transf."}
                    </p>
                </div>
                <span className={`text-xs font-bold px-3 py-1 rounded-full ${ESTADO_COLOR[pedido.estado_codigo]}`}>
                    {ESTADO_LABEL[pedido.estado_codigo]}
                </span>
            </div>

            {pedido.direccion && (
                <div className="mb-3 p-3 rounded-xl bg-orange-50 border border-orange-100">
                    <p className="text-[10px] font-bold text-[#c8722a] uppercase tracking-widest mb-1">
                        📍 Dirección de entrega
                    </p>
                    <p className="text-sm font-medium text-[#2d1e0f]">
                        {pedido.direccion.linea1} {pedido.direccion.linea2 ?? ""}
                    </p>
                </div>
            )}

            <div className="pt-3 mb-3 space-y-1 mt-auto" style={{ borderTop: "1px solid #f0e8e0" }}>
                {pedido.detalles.map((d) => (
                    <div key={d.producto_id}>
                        <div className="flex justify-between text-sm">
                            <span style={{ color: "#6b5a4e" }}>{d.cantidad}x {d.nombre_snapshot}</span>
                            <span className="font-medium" style={{ color: "#2d1e0f" }}>${Number(d.subtotal).toFixed(2)}</span>
                        </div>
                        {Array.isArray(d.personalizacion) && d.personalizacion.length > 0 && ingredientesMap && (
                            <p className="text-[10px] text-red-500 italic ml-1 -mt-0.5 mb-1">
                                Sin: {ingredientesMap.size > 0
                                    ? d.personalizacion.map((id) => ingredientesMap.get(Number(id)) ?? `#${id}`).join(", ")
                                    : `${d.personalizacion.length} ingrediente(s)`}
                            </p>
                        )}
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
            {siguientes.length === 0 && (
                <p className="text-xs text-center italic" style={{ color: "#9a8070" }}>Estado terminal</p>
            )}
        </div>
    );
}
