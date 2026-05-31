import { useState } from "react";
import { usePedidos, useAvanzarEstado, ESTADO_LABEL } from "../hooks/usePedidos";
import { PedidoCard } from "../components/pedidoCard";

const FILTROS = ["TODOS", "PENDIENTE", "CONFIRMADO", "PREPARACION", "ENVIADO", "ENTREGADO", "CANCELADO"];

export function CajeroPedidosPage() {
    const [filtro, setFiltro] = useState("TODOS");
    const { data, isLoading, error } = usePedidos();
    const { mutate: avanzar, isPending } = useAvanzarEstado();

    const pedidos = data?.data ?? [];
    const filtrados = filtro === "TODOS" ? pedidos : pedidos.filter((p) => p.estado_codigo === filtro);

    if (isLoading) return (
        <div className="flex items-center justify-center h-64">
            <div className="w-8 h-8 border-2 border-t-transparent rounded-full animate-spin" style={{ borderColor: "#c8722a", borderTopColor: "transparent" }} />
        </div>
    );

    if (error) return (
        <div className="rounded-xl p-4" style={{ backgroundColor: "#fee2e2", border: "1px solid #fecaca", color: "#991b1b" }}>
            ⚠️ Error al cargar pedidos
        </div>
    );

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold" style={{ color: "#2d1e0f" }}>Gestión de Pedidos</h1>
                <p className="text-sm mt-1" style={{ color: "#9a8070" }}>{data?.total ?? 0} pedidos en total • se actualiza cada 30s</p>
            </div>

            <div className="flex gap-2 flex-wrap mb-6">
                {FILTROS.map((f) => (
                    <button key={f} onClick={() => setFiltro(f)}
                        className="text-xs font-bold px-4 py-2 rounded-full transition-all"
                        style={filtro === f
                            ? { backgroundColor: "#c8722a", color: "#fff" }
                            : { backgroundColor: "#fff", border: "1px solid #d6c9be", color: "#6b5a4e" }}>
                        {f === "TODOS" ? "Todos" : ESTADO_LABEL[f]}
                        {f !== "TODOS" && <span className="ml-1 opacity-70">({pedidos.filter((p) => p.estado_codigo === f).length})</span>}
                    </button>
                ))}
            </div>

            {filtrados.length === 0 ? (
                <div className="text-center py-16" style={{ color: "#9a8070" }}>
                    <p className="text-4xl mb-3">📋</p>
                    <p>No hay pedidos en este estado</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                    {filtrados.map((pedido) => (
                        <PedidoCard key={pedido.id} pedido={pedido} loading={isPending} onAvanzar={(id, estado) => avanzar({ id, estado })} />
                    ))}
                </div>
            )}
        </div>
    );
}