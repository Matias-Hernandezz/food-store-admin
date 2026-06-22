import { useEffect, useRef, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useWSStore } from "../../store/wsStore";
import { useAuthStore } from "../../store/authStore";

const MAX_RETRIES = 10;
const BASE_DELAY = 1000;

const WS_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000")
    .replace("http://", "ws://")
    .replace("https://", "wss://") + "/api/v1/pedidos/ws/pedidos";

/**
 * Hook de WebSocket para administradores.
 * Recibe todos los eventos de pedidos a través del canal por rol.
 * Invalida queries de TanStack Query automáticamente.
 */
export function useAdminOrdersFeed({ enabled = true }: { enabled?: boolean } = {}) {
    const queryClient = useQueryClient();
    const setStatus = useWSStore((s) => s.setStatus);
    const setLastEvent = useWSStore((s) => s.setLastEvent);
    const incrementReconnect = useWSStore((s) => s.incrementReconnect);
    const resetReconnect = useWSStore((s) => s.resetReconnect);

    const wsRef = useRef<WebSocket | null>(null);
    const retryRef = useRef(0);
    const mountedRef = useRef(true);

    const connect = useCallback(() => {
        if (!mountedRef.current || !enabled) return;

        let token = useAuthStore.getState().accessToken;

        // Si no hay token en el store, intentar obtenerlo del backend (cookie httpOnly)
        if (!token) {
            setStatus("connecting");
            fetch(`${(import.meta.env.VITE_API_URL || "http://localhost:8000")}/api/v1/auth/token`, {
                credentials: "include",
            })
                .then((r) => r.json())
                .then((data) => {
                    token = data.access_token;
                    if (!token || !mountedRef.current) return;
                    doConnect(token);
                })
                .catch(() => {
                    if (mountedRef.current) setStatus("error");
                });
            return;
        }

        doConnect(token);
    }, [enabled, queryClient, setStatus, setLastEvent, incrementReconnect, resetReconnect]);

    const doConnect = useCallback((token: string) => {
        if (!mountedRef.current || !enabled) return;

        setStatus("connecting");

        const url = `${WS_URL}?token=${token}`;
        let ws: WebSocket;
        try {
            ws = new WebSocket(url);
            wsRef.current = ws;
        } catch {
            setStatus("error");
            scheduleReconnect();
            return;
        }

        ws.onopen = () => {
            if (!mountedRef.current) return;
            setStatus("connected");
            resetReconnect();
            retryRef.current = 0;

            // Invalidar queries para tener datos frescos
            queryClient.invalidateQueries({ queryKey: ["pedidos"] });
            queryClient.invalidateQueries({ queryKey: ["pedidos", "cocina"] });
            queryClient.invalidateQueries({ queryKey: ["estadisticas"] });
        };

        ws.onmessage = (msg) => {
            if (!mountedRef.current) return;
            try {
                const event = JSON.parse(msg.data);
                if (event.event === "SUBSCRIBED" || event.event === "ERROR") return;
                if (event.event === "ping") return;  // heartbeat del servidor

                setLastEvent(event);

                // Invalidar queries relevantes
                queryClient.invalidateQueries({ queryKey: ["pedidos"] });
                queryClient.invalidateQueries({ queryKey: ["pedidos", "cocina"] });
                queryClient.invalidateQueries({ queryKey: ["estadisticas"] });
            } catch {
                // mensaje no JSON, ignorar
            }
        };

        ws.onclose = (ev) => {
            if (!mountedRef.current) return;
            // 4001 = token inválido/expirado → intentar refresh y reconectar
            if (ev.code === 4001) {
                useAuthStore.getState().refreshToken().then(() => {
                    if (mountedRef.current) connect();
                }).catch(() => {
                    setStatus("error");
                });
                return;
            }
            if (ev.code === 1000) {
                setStatus("disconnected");
                return;
            }
            scheduleReconnect();
        };

        ws.onerror = () => {
            // onclose se dispara después de onerror
        };
    }, [enabled, queryClient, setStatus, setLastEvent, incrementReconnect, resetReconnect]);

    const scheduleReconnect = useCallback(() => {
        if (!mountedRef.current) return;

        const attempt = retryRef.current + 1;
        if (attempt > MAX_RETRIES) {
            setStatus("error");
            return;
        }

        retryRef.current = attempt;
        incrementReconnect();

        const delay = Math.min(BASE_DELAY * 2 ** (attempt - 1), 30000);
        window.setTimeout(() => {
            if (mountedRef.current) connect();
        }, delay);
    }, [connect, setStatus, incrementReconnect]);

    useEffect(() => {
        mountedRef.current = true;
        if (!enabled) return;

        connect();

        return () => {
            mountedRef.current = false;
            const ws = wsRef.current;
            if (ws) {
                ws.onclose = null;
                ws.close(1000, "Component unmounted");
                wsRef.current = null;
            }
            setStatus("disconnected");
        };
    }, [enabled]); // eslint-disable-line react-hooks/exhaustive-deps

    // Re-conectar solo cuando cambia el token (evita race condition de [connect])
    const token = useAuthStore((s) => s.accessToken);
    useEffect(() => {
        const ws = wsRef.current;
        if (ws && ws.readyState !== WebSocket.OPEN && token) {
            connect();
        }
    }, [token]); // eslint-disable-line react-hooks/exhaustive-deps
}
