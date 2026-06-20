import { useMemo } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { pedidosApi } from "../../pedidos/api/pedidosApi";
import { PedidoCard } from "../../pedidos/components/pedidoCard";
import { useAdminOrdersFeed } from "../../../shared/hooks/useAdminOrdersFeed";
import api from "../../../shared/api/axiosClient";

interface IngredienteSimple { id: number; nombre: string }

export function CocinaPage() {
    useAdminOrdersFeed();

    const queryClient = useQueryClient();

    const { data, isLoading, error } = useQuery({
        queryKey: ["pedidos", "cocina"],
        queryFn: () => pedidosApi.getCocinaPedidos(),
    });

    const { data: ingredientesData } = useQuery({
        queryKey: ["ingredientes"],
        queryFn: () => api.get<{ data: IngredienteSimple[] }>("/api/v1/ingredientes/?limit=100").then(r => r.data),
        staleTime: 5 * 60 * 1000,
    });
    const ingredientesMap = useMemo(() => new Map(
        (ingredientesData?.data ?? []).map((i) => [i.id, i.nombre])
    ), [ingredientesData]);

    const avanzar = useMutation({
        mutationFn: ({ id, estado }: { id: number; estado: string }) =>
            pedidosApi.avanzarEstado(id, estado),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["pedidos", "cocina"] });
            queryClient.invalidateQueries({ queryKey: ["pedidos"] });
        },
    });

    const pedidos = data?.data ?? [];

    if (isLoading) return (
        <div className="flex items-center justify-center h-64">
            <div className="w-8 h-8 border-2 border-t-transparent rounded-full animate-spin" style={{ borderColor: "#c8722a", borderTopColor: "transparent" }} />
        </div>
    );

    if (error) return (
        <div className="rounded-xl p-4" style={{ backgroundColor: "#fee2e2", border: "1px solid #fecaca", color: "#991b1b" }}>
            ⚠️ Error al cargar pedidos de cocina
        </div>
    );

    return (
        <div>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold" style={{ color: "#2d1e0f" }}>
                        Cocina
                    </h1>
                    <p className="text-sm mt-1" style={{ color: "#9a8070" }}>
                        {pedidos.length} pedidos en preparacion · en vivo
                    </p>
                </div>
            </div>

            {pedidos.length === 0 ? (
                <div className="text-center py-16" style={{ color: "#9a8070" }}>
                    <p>No hay pedidos en preparacion</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                    {pedidos.map((pedido) => (
                        <PedidoCard
                            key={pedido.id}
                            pedido={pedido}
                            loading={avanzar.isPending}
                            onAvanzar={(id, proximoEstado) => avanzar.mutate({ id, estado: proximoEstado })}
                            ingredientesMap={ingredientesMap}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}