// features/pedidos/hooks/usePedidos.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { pedidosApi } from "../api/pedidosApi";
import { useUIStore } from "../../../store/uiStore";
import type { PedidoCreate, DireccionCreate, DireccionRead } from "../types/index";
// Estados en orden FSM
export const ESTADOS_FSM: Record<string, string[]> = {
    PENDIENTE: ["CONFIRMADO", "CANCELADO"],
    CONFIRMADO: ["EN_PREP", "CANCELADO"],
    EN_PREP: ["ENTREGADO", "CANCELADO"],
    ENTREGADO: [],
    CANCELADO: [],
};

export const ESTADO_LABEL: Record<string, string> = {
    PENDIENTE: "Pendiente",
    CONFIRMADO: "Confirmado",
    EN_PREP: "En preparacion",
    ENTREGADO: "Entregado",
    CANCELADO: "Cancelado",
};

export const ESTADO_COLOR: Record<string, string> = {
    PENDIENTE: "bg-yellow-100 text-yellow-800",
    CONFIRMADO: "bg-blue-100 text-blue-800",
    EN_PREP: "bg-orange-100 text-orange-800",
    ENTREGADO: "bg-green-100 text-green-800",
    CANCELADO: "bg-red-100 text-red-800",
};

export function usePedidos(desde?: string, hasta?: string, search?: string) {
    return useQuery({
        queryKey: ["pedidos", { desde, hasta, search }],
        queryFn: () => pedidosApi.getAll(0, 50, desde, hasta, search),
        refetchInterval: 30000,
    });
}

export function useAvanzarEstado() {
    const qc = useQueryClient();
    const addToast = useUIStore((s) => s.addToast);
    return useMutation({
        mutationFn: ({ id, estado, motivo }: { id: number; estado: string; motivo?: string }) =>
            pedidosApi.avanzarEstado(id, estado, motivo),
        onSuccess: (_, { estado }) => {
            qc.invalidateQueries({ queryKey: ["pedidos"] });
            addToast({ type: "success", message: `Pedido → ${ESTADO_LABEL[estado] ?? estado}` });
        },
        onError: (err: any) => {
            const status = err?.response?.status;
            const detail = err?.response?.data?.detail || err?.message || "";
            const msg =
                status === 429 ? "Demasiadas peticiones, esperá unos segundos" :
                status === 403 ? "No tenés permisos para esta acción" :
                status === 422 ? (detail || "Datos inválidos") :
                status === 404 ? "Pedido no encontrado" :
                !navigator.onLine ? "Sin conexión a internet" :
                (detail || "Error al cambiar el estado del pedido");
            addToast({ type: "error", message: msg });
        },
    });
}
export function useMisPedidos() {
    return useQuery({
        queryKey: ["mis-pedidos"],
        queryFn: () => pedidosApi.getMisPedidos(),
    });
}

export function useFormasPago() {
    return useQuery({
        queryKey: ["formas-pago"],
        queryFn: () => pedidosApi.getFormasPago(),
    });
}
export function useDirecciones() {
    return useQuery({
        queryKey: ["direcciones"],
        queryFn: () => pedidosApi.getDirecciones(),
    });
}

export function useCrearDireccion() {
    const queryClient = useQueryClient();
    const addToast = useUIStore((s) => s.addToast);
    return useMutation({
        mutationFn: (data: DireccionCreate) => pedidosApi.crearDireccion(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["direcciones"] });
            addToast({ type: "success", message: "Dirección creada" });
        },
        onError: (err: any) => {
            const status = err?.response?.status;
            const detail = err?.response?.data?.detail || err?.message || "";
            const msg =
                status === 422 ? (detail || "Datos inválidos") :
                status === 403 ? "No tenés permisos para esta acción" :
                !navigator.onLine ? "Sin conexión a internet" :
                (detail || "Error al crear la dirección");
            addToast({ type: "error", message: msg });
        },
    });
}
export function useCrearPedido() {
    const qc = useQueryClient();
    const addToast = useUIStore((s) => s.addToast);
    return useMutation({
        mutationFn: (data: PedidoCreate) => pedidosApi.crear(data),
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["mis-pedidos"] });
            addToast({ type: "success", message: "Pedido creado" });
        },
        onError: (err: any) => {
            const status = err?.response?.status;
            const detail = err?.response?.data?.detail || err?.message || "";
            const msg =
                status === 422 ? (detail || "Datos inválidos") :
                status === 403 ? "No tenés permisos para esta acción" :
                status === 409 ? (detail || "Conflicto al crear el pedido") :
                !navigator.onLine ? "Sin conexión a internet" :
                (detail || "Error al crear el pedido");
            addToast({ type: "error", message: msg });
        },
    });
}



