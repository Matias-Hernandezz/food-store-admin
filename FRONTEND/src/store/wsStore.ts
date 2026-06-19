import { create } from "zustand";

export type ConnectionStatus = "disconnected" | "connecting" | "connected" | "error";

export interface WSEvent {
    event: string;
    pedido_id: number;
    estado_anterior: string | null;
    estado_nuevo: string;
    usuario_id: number | null;
    motivo: string | null;
    timestamp: string;
    data?: Record<string, unknown>;
}

interface WSState {
    status: ConnectionStatus;
    lastEvent: WSEvent | null;
    reconnectAttempt: number;

    setStatus: (status: ConnectionStatus) => void;
    setLastEvent: (event: WSEvent) => void;
    incrementReconnect: () => void;
    resetReconnect: () => void;
    reset: () => void;
}

export const useWSStore = create<WSState>()((set) => ({
    status: "disconnected",
    lastEvent: null,
    reconnectAttempt: 0,

    setStatus: (status) => set({ status }),

    setLastEvent: (event) => set({ lastEvent: event }),

    incrementReconnect: () =>
        set((s) => ({ reconnectAttempt: s.reconnectAttempt + 1 })),

    resetReconnect: () => set({ reconnectAttempt: 0 }),

    reset: () =>
        set({
            status: "disconnected",
            lastEvent: null,
            reconnectAttempt: 0,
        }),
}));
