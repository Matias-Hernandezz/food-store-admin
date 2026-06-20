import { useState, useMemo, useEffect } from "react";
import { useProductos } from "../../producto/hooks/useProducto";
import { useUsuarios } from "../../usuarios/hooks/useUsuarios";
import { useFormasPago } from "../hooks/usePedidos";
import type { Producto } from "../../../shared/types/index";
import type { UsuarioRead, FormaPago, PedidoCreate } from "../types/index";

interface CrearPedidoModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (data: PedidoCreate) => void;
    isPending: boolean;
}

export function CrearPedidoModal({ isOpen, onClose, onSubmit, isPending }: CrearPedidoModalProps) {
    if (!isOpen) return null;

    // 1. LLAMADAS A HOOKS (Estructurados según tus nuevas definiciones)
    const { data: productosData, isLoading: loadingProds } = useProductos(1, 100);
    const { data: usuariosData, isLoading: loadingUsers } = useUsuarios();
    const { data: formasPagoData, isLoading: loadingPagos } = useFormasPago();

    // 2. ESTADOS DEL FORMULARIO
    const [usuarioId, setUsuarioId] = useState<string>("");
    const [direccionId, setDireccionId] = useState<string>("");
    const [formaPago, setFormaPago] = useState<string>("");
    const [notas, setNotas] = useState<string>("");
    const [carrito, setCarrito] = useState<Record<number, number>>({});

    // 3. PROCESAMIENTO Y TIPADO DE DATA
    const usuarios = usuariosData ?? [];
    const formasPago = formasPagoData ?? [];

    const productos = useMemo<Producto[]>(() => {
        if (!productosData) return [];
        return productosData.data ?? [];
    }, [productosData]);

    // Setea la primera forma de pago disponible por defecto cuando carguen de la API
    useEffect(() => {
        if (formasPago.length > 0 && !formaPago) {
            const primeraHabilitada = formasPago.find(f => f.habilitado);
            if (primeraHabilitada) setFormaPago(primeraHabilitada.codigo);
        }
    }, [formasPago, formaPago]);

    // OBTENER DIRECCIONES COMPATIBLES CON LA INTERFAZ DireccionEntrega
    const direccionesDelUsuario = useMemo(() => {
        if (!usuarioId) return [];
        const usuarioSeleccionado = usuarios.find((u) => Number(u.id) === Number(usuarioId));
        return usuarioSeleccionado?.direcciones ?? [];
    }, [usuarioId, usuarios]);

    const handleCambiarCantidad = (productoId: number, cambio: number) => {
        setCarrito((prev) => {
            const nuevaCantidad = (prev[productoId] || 0) + cambio;
            const nuevoCarrito = { ...prev };
            if (nuevaCantidad <= 0) {
                delete nuevoCarrito[productoId];
            } else {
                nuevoCarrito[productoId] = nuevaCantidad;
            }
            return nuevoCarrito;
        });
    };

    const totalCalculado = useMemo(() => {
        return Object.entries(carrito).reduce((acc, [idStr, cant]) => {
            const id = Number(idStr);
            const prod = productos.find((p) => p.id === id);
            const precio = prod ? prod.precio_base : 0;
            return acc + (precio * cant);
        }, 0);
    }, [carrito, productos]);

    // 4. SUBMIT DEL FORMULARIO EN BASE A PedidoCreate
    const handleGuardar = (e: React.FormEvent) => {
        e.preventDefault();
        if (!usuarioId) {
            alert("Por favor, seleccioná un cliente.");
            return;
        }
        if (Object.keys(carrito).length === 0) {
            alert("El carrito no puede estar vacío.");
            return;
        }

        // Mapeo exacto al esquema requerido por tu backend en PedidoCreate
        const listaProductos = Object.entries(carrito).map(([idStr, cantidad]) => ({
            producto_id: Number(idStr),
            cantidad: cantidad,
        }));

        onSubmit({
            // Se envía el usuario_id para que el componente padre sepa a quién asociarlo/armar la URL
            usuario_id: Number(usuarioId),

            // Estructura exacta de PedidoCreate
            direccion_id: direccionId ? Number(direccionId) : null,
            forma_pago_codigo: formaPago,
            notas: notas.trim() || null,
            productos: listaProductos
        });
    };

    const isLoadingCatalogo = loadingProds || loadingUsers || loadingPagos;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="relative w-full max-w-4xl rounded-2xl bg-white p-6 shadow-2xl transition-all">

                {/* HEADER */}
                <div className="flex items-center justify-between border-b pb-4">
                    <h2 className="flex items-center gap-2 text-xl font-bold text-amber-900">
                        Nuevo Pedido Comercial
                    </h2>
                    <button type="button" onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl font-semibold">
                        ✕
                    </button>
                </div>

                <form onSubmit={handleGuardar} className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">

                    {/* COLUMNA 1: DATOS DE VENTA */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-bold uppercase tracking-wider text-amber-700">
                            1. Datos de Venta
                        </h3>

                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Usuario / Cliente *</label>
                            <select
                                value={usuarioId}
                                onChange={(e) => {
                                    setUsuarioId(e.target.value);
                                    setDireccionId("");
                                }}
                                className="w-full rounded-lg border border-gray-300 p-2.5 bg-gray-50 text-sm"
                                required
                            >
                                <option value="">-- Seleccionar Cliente --</option>
                                {usuarios.map((user) => (
                                    <option key={user.id} value={user.id}>
                                        {user.nombre} {user.apellido} ({user.email})
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Dirección de Entrega</label>
                            <select
                                value={direccionId}
                                onChange={(e) => setDireccionId(e.target.value)}
                                disabled={!usuarioId}
                                className="w-full rounded-lg border border-gray-300 p-2.5 bg-gray-50 text-sm disabled:bg-gray-100 disabled:text-gray-400"
                            >
                                <option value="">🏠 Retiro en Local (Sin envío)</option>
                                {direccionesDelUsuario.map((dir) => (
                                    <option key={dir.id} value={dir.id}>
                                        📍 {dir.linea1} {dir.linea2 ? `(${dir.linea2})` : ""} - {dir.ciudad}
                                    </option>
                                ))}
                            </select>
                            {usuarioId && direccionesDelUsuario.length === 0 && (
                                <p className="text-[11px] text-amber-600 mt-1 italic">
                                    ⚠️ El usuario no tiene direcciones cargadas. Se usará Retiro en Local.
                                </p>
                            )}
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Método de Pago</label>
                            <select
                                value={formaPago}
                                onChange={(e) => setFormaPago(e.target.value)}
                                className="w-full rounded-lg border border-gray-300 p-2.5 bg-gray-50 text-sm"
                                required
                            >
                                {formasPago.length === 0 ? (
                                    <option value="">Cargando métodos...</option>
                                ) : (
                                    formasPago
                                        .filter((fp) => fp.habilitado)
                                        .map((fp) => (
                                            <option key={fp.codigo} value={fp.codigo}>
                                                {fp.descripcion}
                                            </option>
                                        ))
                                )}
                            </select>
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Notas o Aclaraciones</label>
                            <textarea
                                value={notas}
                                onChange={(e) => setNotas(e.target.value)}
                                placeholder="Ej: sin cebolla, tocar timbre fuerte..."
                                rows={3}
                                className="w-full rounded-lg border border-gray-300 p-2.5 bg-gray-50 text-sm"
                            />
                        </div>
                    </div>

                    {/* COLUMNA 2: ARMAR CARRITO */}
                    <div className="flex flex-col justify-between border-l pl-0 md:pl-6">
                        <div>
                            <h3 className="text-sm font-bold uppercase tracking-wider text-amber-700 mb-4">
                                2. Armar Carrito
                            </h3>

                            <div className="max-h-64 overflow-y-auto space-y-2 pr-2">
                                {isLoadingCatalogo ? (
                                    <div className="flex flex-col items-center justify-center py-12 text-gray-400 italic">
                                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-amber-700 mb-2"></div>
                                        Cargando catálogo...
                                    </div>
                                ) : productos.length === 0 ? (
                                    <p className="text-center text-sm text-gray-400 italic py-8">No hay productos disponibles.</p>
                                ) : (
                                    productos.map((prod) => {
                                        const cantidad = carrito[prod.id] || 0;
                                        return (
                                            <div
                                                key={prod.id}
                                                className="flex items-center justify-between p-2 rounded-xl bg-gray-50 border border-gray-100"
                                            >
                                                <div className="flex flex-col">
                                                    <span className="text-sm font-medium text-gray-800">{prod.nombre}</span>
                                                    <span className="text-xs text-gray-500">${prod.precio_base.toFixed(2)}</span>
                                                </div>

                                                <div className="flex items-center gap-2">
                                                    {cantidad > 0 && (
                                                        <>
                                                            <button
                                                                type="button"
                                                                onClick={() => handleCambiarCantidad(prod.id, -1)}
                                                                className="w-7 h-7 rounded-full bg-amber-100 text-amber-800 flex items-center justify-center font-bold"
                                                            >
                                                                -
                                                            </button>
                                                            <span className="w-6 text-center font-semibold text-sm">{cantidad}</span>
                                                        </>
                                                    )}
                                                    <button
                                                        type="button"
                                                        onClick={() => handleCambiarCantidad(prod.id, 1)}
                                                        className="w-7 h-7 rounded-full bg-amber-600 text-white flex items-center justify-center font-bold"
                                                    >
                                                        +
                                                    </button>
                                                </div>
                                            </div>
                                        );
                                    })
                                )}
                            </div>
                        </div>

                        {/* TOTAL Y ACCIONES */}
                        <div className="border-t pt-4 mt-4 space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="text-base font-medium text-gray-700">Total Estimado:</span>
                                <span className="text-2xl font-black text-amber-600">
                                    ${totalCalculado.toFixed(2)}
                                </span>
                            </div>

                            <div className="flex items-center gap-3">
                                <button
                                    type="button"
                                    onClick={onClose}
                                    className="flex-1 rounded-xl border border-gray-300 py-2.5 text-center text-sm font-semibold text-gray-700"
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    disabled={isPending || Object.keys(carrito).length === 0}
                                    className="flex-1 rounded-xl bg-amber-600 py-2.5 text-center text-sm font-semibold text-white disabled:opacity-50"
                                >
                                    {isPending ? "Guardando..." : "🚀 Guardar Pedido"}
                                </button>
                            </div>
                        </div>

                    </div>
                </form>
            </div>
        </div>
    );
}