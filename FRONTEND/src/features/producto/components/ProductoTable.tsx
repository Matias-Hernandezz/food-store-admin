import { useState } from "react";
import { Button, Badge, ConfirmDialog, SkeletonRow, ErrorState, EmptyState, SearchInput } from "../../../shared/components/ui";
import { useDeleteProducto, useRestoreProducto } from "../hooks/useProducto";
import type { Producto } from "../../../shared/types";

interface ProductoTableProps {
  data: Producto[];
  total: number;
  isLoading: boolean;
  isError: boolean;
  onEdit: (p: Producto) => void;
}

export function ProductoTable({ data, total, isLoading, isError, onEdit }: ProductoTableProps) {
  const [search, setSearch] = useState("");
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [restoreId, setRestoreId] = useState<number | null>(null);
  const deleteMutation = useDeleteProducto();
  const restoreMutation = useRestoreProducto();

  const filtered = data
    .filter((p) => p.nombre.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => (a.deleted_at && !b.deleted_at ? -1 : !a.deleted_at && b.deleted_at ? 1 : 0));

  async function handleConfirmDelete() {
    if (deleteId === null) return;
    await deleteMutation.mutateAsync(deleteId);
    setDeleteId(null);
  }

  async function handleConfirmRestore() {
    if (restoreId === null) return;
    await restoreMutation.mutateAsync(restoreId);
    setRestoreId(null);
  }

  function formatPrice(value: string | number) {
    return new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS", minimumFractionDigits: 2 }).format(Number(value));
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between gap-4">
        <SearchInput value={search} onChange={setSearch} placeholder="Buscar producto..." />
        <span className="text-xs whitespace-nowrap" style={{ color: "#9a8070" }}>{total} registros</span>
      </div>

      <div className="rounded-xl overflow-hidden" style={{ border: "1px solid #E5E2DA" }}>
        <table className="w-full text-sm">
          <thead>
            <tr style={{ backgroundColor: "#ede3d9" }}>
              {["ID", "Nombre", "Precio", "Unidad", "Stock", "Estado", "Acciones"].map((h, i) => (
                <th key={h} className={`px-4 py-3 text-xs font-bold uppercase tracking-wider ${i === 6 ? "text-right" : "text-left"}`} style={{ color: "#9a8070" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {isLoading && Array.from({ length: 4 }).map((_, i) => (
              <tr key={i} style={{ borderTop: "1px solid #E5E2DA" }}><td colSpan={7}><SkeletonRow /></td></tr>
            ))}
            {isError && <tr><td colSpan={7}><ErrorState /></td></tr>}
            {!isLoading && !isError && filtered.length === 0 && <tr><td colSpan={7}><EmptyState message="No se encontraron productos" /></td></tr>}
            {!isLoading && !isError && filtered.map((prod) => {
              const isDeleted = !!prod.deleted_at;
              return (
                <tr key={prod.id} className="transition-colors"
                  style={{ borderTop: "1px solid #E5E2DA", backgroundColor: "#fff", opacity: isDeleted ? 0.6 : 1 }}
                  onMouseEnter={e => (e.currentTarget.style.backgroundColor = "#F2E8D5")}
                  onMouseLeave={e => (e.currentTarget.style.backgroundColor = "#fff")}>
                  <td className="px-4 py-3 font-mono text-xs" style={{ color: "#9a8070" }}>{prod.id}</td>
                  <td className="px-4 py-3">
                    <p className="font-medium" style={{ color: "#2d1e0f" }}>
                      {prod.nombre}
                      {isDeleted && <span className="ml-2 text-xs" style={{ color: "#9a8070" }}>(eliminado)</span>}
                    </p>
                    {prod.descripcion && <p className="text-xs truncate max-w-xs" style={{ color: "#9a8070" }}>{prod.descripcion}</p>}
                  </td>
                  <td className="px-4 py-3 font-semibold font-mono" style={{ color: "#C87A2E" }}>{formatPrice(prod.precio_base)}</td>
                  <td className="px-4 py-3">
                    <span className="text-xs font-medium whitespace-nowrap" style={{ color: "#2d1e0f" }}>
                      {prod.unidad_venta?.simbolo
                        ? (prod.cantidad_venta != null ? `${Number(prod.cantidad_venta)} ${prod.unidad_venta.simbolo}` : prod.unidad_venta.simbolo)
                        : "—"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="font-mono text-sm" style={{ color: prod.stock_cantidad === 0 ? "#dc2626" : "#2d1e0f" }}>{prod.stock_cantidad}</span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-col gap-1">
                      {isDeleted ? (
                        <Badge variant="danger">Eliminado</Badge>
                      ) : (
                        prod.disponible && prod.stock_cantidad > 0 ? <Badge variant="success">Disponible</Badge> : <Badge variant="danger">No disponible</Badge>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2 justify-end">
                      {isDeleted ? (
                        <Button variant="ghost" onClick={() => setRestoreId(prod.id)} className="text-xs px-3 py-1" style={{ color: "#16a34a", border: "1px solid #16a34a", fontWeight: 600 }}>Restaurar</Button>
                      ) : (
                        <>
                          <Button variant="ghost" onClick={() => onEdit(prod)} className="text-xs px-3 py-1">Editar</Button>
                          <Button variant="danger" onClick={() => setDeleteId(prod.id)} className="text-xs px-3 py-1">Eliminar</Button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <ConfirmDialog open={deleteId !== null} message="¿Estás seguro que querés eliminar este producto?" onConfirm={handleConfirmDelete} onCancel={() => setDeleteId(null)} loading={deleteMutation.isPending} />
      <ConfirmDialog open={restoreId !== null} message="¿Querés restaurar este producto?" onConfirm={handleConfirmRestore} onCancel={() => setRestoreId(null)} loading={restoreMutation.isPending} confirmLabel="Restaurar" />
    </div>
  );
}
