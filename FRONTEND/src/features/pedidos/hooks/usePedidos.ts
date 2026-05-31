// features/pedidos/hooks/usePedidos.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { pedidosApi } from "../api/pedidosApi";

// Estados en orden FSM
export const ESTADOS_FSM: Record<string, string[]> = {
    PENDIENTE: ["CONFIRMADO", "CANCELADO"],
    CONFIRMADO: ["PREPARACION", "CANCELADO"],
    PREPARACION: ["ENVIADO"],
    ENVIADO: ["ENTREGADO"],
    ENTREGADO: [],
    CANCELADO: [],
};

export const ESTADO_LABEL: Record<string, string> = {
    PENDIENTE: "Pendiente",
    CONFIRMADO: "Confirmado",
    PREPARACION: "En Preparación",
    ENVIADO: "Enviado",
    ENTREGADO: "Entregado",
    CANCELADO: "Cancelado",
};

export const ESTADO_COLOR: Record<string, string> = {
    PENDIENTE: "bg-yellow-100 text-yellow-800",
    CONFIRMADO: "bg-blue-100 text-blue-800",
    PREPARACION: "bg-orange-100 text-orange-800",
    ENVIADO: "bg-purple-100 text-purple-800",
    ENTREGADO: "bg-green-100 text-green-800",
    CANCELADO: "bg-red-100 text-red-800",
};

export function usePedidos() {
    return useQuery({
        queryKey: ["pedidos"],
        queryFn: () => pedidosApi.getAll(),
        refetchInterval: 30000,
    });
}

export function useAvanzarEstado() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: ({ id, estado, motivo }: { id: number; estado: string; motivo?: string }) =>
            pedidosApi.avanzarEstado(id, estado, motivo),
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["pedidos"] });
        },
    });
}