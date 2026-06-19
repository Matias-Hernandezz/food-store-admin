import { useWSStore } from "../../store/wsStore";

const STATUS_CONFIG: Record<string, { color: string; label: string }> = {
    connected: { color: "#22c55e", label: "En vivo" },
    connecting: { color: "#eab308", label: "Conectando..." },
    disconnected: { color: "#9ca3af", label: "Sin conexión" },
    error: { color: "#ef4444", label: "Error" },
};

export function ConnectionBadge() {
    const status = useWSStore((s) => s.status);
    const reconnectAttempt = useWSStore((s) => s.reconnectAttempt);

    const config = STATUS_CONFIG[status];
    const showRetry = status === "connecting" && reconnectAttempt > 0;

    return (
        <div className="flex items-center gap-1.5">
            <span
                className="inline-block w-2 h-2 rounded-full animate-pulse"
                style={{ backgroundColor: config.color }}
            />
            <span className="text-xs" style={{ color: "#9a8070" }}>
                {config.label}
                {showRetry && ` (${reconnectAttempt})`}
            </span>
        </div>
    );
}
