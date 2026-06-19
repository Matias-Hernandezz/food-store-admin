import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "../../../shared/api/axiosClient";
import { usePedidos, useAvanzarEstado, ESTADO_LABEL } from "../hooks/usePedidos";
import { PedidoCard } from "../components/pedidoCard";
import { useAdminOrdersFeed } from "../../../shared/hooks/useAdminOrdersFeed";

interface IngredienteSimple { id: number; nombre: string }

function hoyISO(): string {
    return new Date().toISOString().slice(0, 10);
}

export function CajeroPedidosPage() {
    const [filtro, setFiltro] = useState("TODOS");
    const [fechaFiltro, setFechaFiltro] = useState<"TODOS" | "HOY" | "PERSONALIZADO">("TODOS");
    const [fechaCustom, setFechaCustom] = useState(hoyISO());

    // Calcular desde/hasta según el filtro de fecha
    const { desde, hasta } = useMemo(() => {
        if (fechaFiltro === "HOY") {
            const hoy = hoyISO();
            return { desde: hoy, hasta: hoy };
        }
        if (fechaFiltro === "PERSONALIZADO") {
            return { desde: fechaCustom, hasta: fechaCustom };
        }
        return { desde: undefined, hasta: undefined };
    }, [fechaFiltro, fechaCustom]);

    const { data, isLoading, error } = usePedidos(desde, hasta);
    const { mutate: avanzar, isPending } = useAvanzarEstado();
    useAdminOrdersFeed();

    const { data: ingredientesData } = useQuery({
        queryKey: ["ingredientes"],
        queryFn: () => api.get<{ data: IngredienteSimple[] }>("/api/v1/ingredientes/?limit=100").then(r => r.data),
        staleTime: 5 * 60 * 1000,
    });
    const ingredientesMap = useMemo(() => new Map(
        (ingredientesData?.data ?? []).map((i) => [i.id, i.nombre])
    ), [ingredientesData]);

    const pedidos = data?.data ?? [];
    const filtrados = filtro === "TODOS" ? pedidos : pedidos.filter((p) => p.estado_codigo === filtro);
    const FILTROS = ["TODOS", "PENDIENTE", "CONFIRMADO", "EN_PREP", "ENTREGADO", "CANCELADO"];

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
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold" style={{ color: "#2d1e0f" }}>Gestión de Pedidos</h1>
                    <p className="text-sm mt-1" style={{ color: "#9a8070" }}>
                        {data?.total ?? 0} pedidos · {fechaFiltro === "HOY" ? "hoy" : fechaFiltro === "PERSONALIZADO" ? fechaCustom : "todos"} · en vivo
                    </p>
                </div>
            </div>

            {/* Filtro de fecha */}
            <div className="flex gap-2 flex-wrap mb-4">
                {(["TODOS", "HOY", "PERSONALIZADO"] as const).map((f) => (
                    <button key={f} onClick={() => setFechaFiltro(f)}
                        className="text-xs font-bold px-4 py-2 rounded-full transition-all"
                        style={fechaFiltro === f
                            ? { backgroundColor: "#2d1e0f", color: "#fff" }
                            : { backgroundColor: "#fff", border: "1px solid #d6c9be", color: "#6b5a4e" }}>
                        {f === "TODOS" ? "Todos" : f === "HOY" ? "Hoy" : "Día"}
                    </button>
                ))}
                {fechaFiltro === "PERSONALIZADO" && (
                    <input
                        type="date"
                        value={fechaCustom}
                        onChange={(e) => setFechaCustom(e.target.value)}
                        className="text-xs px-3 py-2 rounded-full border"
                        style={{ borderColor: "#d6c9be", color: "#6b5a4e" }}
                    />
                )}
            </div>

            {/* Filtro de estado */}
            <div className="flex gap-2 flex-wrap mb-6">
                {FILTROS.map((f) => (
                    <button key={f} onClick={() => setFiltro(f)}
                        className="text-xs font-bold px-4 py-2 rounded-full transition-all"
                        style={filtro === f
                            ? { backgroundColor: "#c8722a", color: "#fff" }
                            : { backgroundColor: "#fff", border: "1px solid #d6c9be", color: "#6b5a4e" }}>
                        {f === "TODOS" ? `Todos (${pedidos.length})` : `${ESTADO_LABEL[f]}: ${pedidos.filter((p) => p.estado_codigo === f).length}`}
                    </button>
                ))}
            </div>

            {filtrados.length === 0 ? (
                <div className="text-center py-16" style={{ color: "#9a8070" }}>
                    <p className="text-4xl mb-3">📋</p>
                    <p>No hay pedidos{ fechaFiltro !== "TODOS" ? " en esta fecha" : "" }</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                    {filtrados.map((pedido) => (
                        <PedidoCard key={pedido.id} pedido={pedido} loading={isPending} onAvanzar={(id, estado) => avanzar({ id, estado })} ingredientesMap={ingredientesMap} />
                    ))}
                </div>
            )}
        </div>
    );
}
