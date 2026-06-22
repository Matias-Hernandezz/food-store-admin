import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "../../../shared/api/axiosClient";
import { usePedidos, useAvanzarEstado, ESTADO_LABEL } from "../hooks/usePedidos";
import { PedidoCard } from "../components/pedidoCard";

interface IngredienteSimple { id: number; nombre: string };

const COLUMNAS: { codigo: string; titulo: string }[] = [
    { codigo: "PENDIENTE", titulo: "Pendientes" },
    { codigo: "CONFIRMADO", titulo: "Confirmados" },
    { codigo: "EN_PREP", titulo: "En Preparación" },
    { codigo: "ENTREGADO", titulo: "Entregados" },
];

function hoyISO(): string {
    // Fecha local del navegador (Argentina), NO UTC
    const now = new Date();
    const y = now.getFullYear();
    const m = String(now.getMonth() + 1).padStart(2, "0");
    const d = String(now.getDate()).padStart(2, "0");
    return `${y}-${m}-${d}`;
}

/* ── Iconos inline ─────────────────────────────────────────────────────── */

const CalendarIcon = ({ size = 14 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
        <path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zm0-12H5V6h14v2z" />
    </svg>
);

const SearchIcon = ({ size = 14 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
        <path d="M15.5 14h-.79l-.28-.27A6.47 6.47 0 0016 9.5 6.5 6.5 0 109.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" />
    </svg>
);

/* ═════════════════════════════════════════════════════════════════════════ */

export function PedidosKanbanPage() {
    const [fechaFiltro, setFechaFiltro] = useState<"TODOS" | "HOY" | "PERSONALIZADO">("TODOS");
    const [fechaCustom, setFechaCustom] = useState(hoyISO());
    const [search, setSearch] = useState("");

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

    const searchTerm = search.trim() || undefined;

    const { data, isLoading } = usePedidos(desde, hasta, searchTerm);
    const avanzar = useAvanzarEstado();

    const { data: ingredientesData } = useQuery({
        queryKey: ["ingredientes"],
        queryFn: () => api.get<{ data: IngredienteSimple[] }>("/api/v1/ingredientes/?limit=100").then(r => r.data),
        staleTime: 5 * 60 * 1000,
    });
    const ingredientesMap = useMemo(() => new Map(
        (ingredientesData?.data ?? []).map((i) => [i.id, i.nombre])
    ), [ingredientesData]);

    const pedidos = (data?.data ?? []).filter((p) => p.estado_codigo !== "CANCELADO");

    const pedidosPorEstado = (codigo: string) =>
        pedidos.filter((p) => p.estado_codigo === codigo);

    const handleAvanzar = (id: number, estado: string, motivo?: string) => {
        avanzar.mutate({ id, estado, motivo });
    };

    const fechaLabel =
        fechaFiltro === "HOY" ? "hoy" :
        fechaFiltro === "PERSONALIZADO" ? fechaCustom :
        "todos";

    return (
        <div>
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h1 className="text-2xl font-bold" style={{ color: "#2d1e0f" }}>Gestión de Pedidos</h1>
                    <p className="text-sm mt-1" style={{ color: "#9a8070" }}>
                        {data?.total ?? 0} pedidos · {fechaLabel}{searchTerm ? ` · "${searchTerm}"` : ""} · en vivo
                    </p>
                </div>
            </div>

            {/* Barra de filtros: fecha + búsqueda */}
            <div className="flex items-center gap-2 mb-5">
                {(["TODOS", "HOY", "PERSONALIZADO"] as const).map((f) => (
                    <button
                        key={f}
                        onClick={() => setFechaFiltro(f)}
                        className="inline-flex items-center gap-1.5 text-xs font-bold px-4 py-2 rounded-full transition-all whitespace-nowrap"
                        style={fechaFiltro === f
                            ? { backgroundColor: "#2d1e0f", color: "#fff" }
                            : { backgroundColor: "#fff", border: "1px solid #E5E2DA", color: "#6b5a4e" }}
                    >
                        <CalendarIcon size={14} />
                        {f === "TODOS" ? "Todos" : f === "HOY" ? "Hoy" : "Día"}
                    </button>
                ))}
                {fechaFiltro === "PERSONALIZADO" && (
                    <input
                        type="date"
                        value={fechaCustom}
                        onChange={(e) => setFechaCustom(e.target.value)}
                        className="text-xs px-3 py-2 rounded-full border"
                        style={{ borderColor: "#E5E2DA", color: "#6b5a4e" }}
                    />
                )}

                <div className="flex-1 relative ml-1">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: "#8b6b4a" }}>
                        <SearchIcon size={16} />
                    </span>
                    <input
                        type="text"
                        placeholder="Buscar por cliente..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full text-sm pl-9 pr-4 py-2 rounded-full border outline-none transition-colors"
                        style={{
                            borderColor: "#8b6b4a",
                            color: "#2d1e0f",
                            backgroundColor: "#fdfaf7",
                        }}
                    />
                </div>
            </div>

            {isLoading ? (
                <div className="flex justify-center py-20">
                    <div className="w-8 h-8 border-2 border-[#C87A2E] border-t-transparent rounded-full animate-spin" />
                </div>
            ) : (
                <div className="overflow-x-auto pb-2">
                    <div className="grid grid-cols-4 gap-4" style={{ minWidth: "800px" }}>
                    {COLUMNAS.map((col) => {
                        const peds = pedidosPorEstado(col.codigo);
                        return (
                            <div key={col.codigo} className="flex flex-col">
                                <div className="flex items-center gap-2 mb-3 px-1">
                                    <span className="text-xs font-black uppercase tracking-wider" style={{ color: "#9a8070" }}>
                                        {col.titulo}: {peds.length}
                                    </span>
                                </div>

                                <div className="flex flex-col gap-3">
                                    {peds.length === 0 ? (
                                        <div
                                            className="rounded-xl border border-dashed flex items-center justify-center"
                                            style={{ borderColor: "#E5E2DA", minHeight: 100 }}
                                        >
                                            <p className="text-xs" style={{ color: "#9a8070" }}>Sin pedidos</p>
                                        </div>
                                    ) : (
                                        peds.map((p) => (
                                            <PedidoCard key={p.id} pedido={p} onAvanzar={handleAvanzar} loading={avanzar.isPending} ingredientesMap={ingredientesMap} />
                                        ))
                                    )}
                                </div>
                            </div>
                        );
                    })}
                    </div>
                </div>
            )}
        </div>
    );
}
