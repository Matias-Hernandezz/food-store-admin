import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { usePedidos } from "../../pedidos/hooks/usePedidos";

export function EstadisticasPage() {
    const { data, isLoading, error } = usePedidos();
    const pedidos = data?.data ?? [];

    const porEstado = Object.entries(
        pedidos.reduce<Record<string, number>>((acc, pedido) => {
            acc[pedido.estado_codigo] = (acc[pedido.estado_codigo] ?? 0) + 1;
            return acc;
        }, {})
    ).map(([estado, cantidad]) => ({ estado, cantidad }));

    const totalFacturado = pedidos.reduce((acc, pedido) => acc + Number(pedido.total), 0);

    if (isLoading) return <p>Cargando estadisticas...</p>;
    if (error) return <p>Error al cargar estadisticas</p>;

    return (
        <div>
            <h1 className="text-2xl font-bold mb-6" style={{ color: "#2d1e0f" }}>
                Estadisticas
            </h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-white border border-[#E5E2DA] rounded-lg p-4">
                    <p className="text-sm" style={{ color: "#9a8070" }}>Pedidos</p>
                    <p className="text-2xl font-bold" style={{ color: "#2d1e0f" }}>{pedidos.length}</p>
                </div>

                <div className="bg-white border border-[#E5E2DA] rounded-lg p-4">
                    <p className="text-sm" style={{ color: "#9a8070" }}>Facturacion</p>
                    <p className="text-2xl font-bold" style={{ color: "#2d1e0f" }}>
                        ${totalFacturado.toFixed(2)}
                    </p>
                </div>

                <div className="bg-white border border-[#E5E2DA] rounded-lg p-4">
                    <p className="text-sm" style={{ color: "#9a8070" }}>En preparacion</p>
                    <p className="text-2xl font-bold" style={{ color: "#2d1e0f" }}>
                        {pedidos.filter((p) => p.estado_codigo === "EN_PREP").length}
                    </p>
                </div>
            </div>

            <div className="h-80 bg-white border border-[#E5E2DA] rounded-lg p-4">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={porEstado}>
                        <XAxis dataKey="estado" />
                        <YAxis allowDecimals={false} />
                        <Tooltip />
                        <Bar dataKey="cantidad" fill="#C87A2E" radius={[4, 4, 0, 0]} />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}