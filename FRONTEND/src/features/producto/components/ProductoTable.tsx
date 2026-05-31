import { useState } from "react";
import { Button, Badge, ConfirmDialog, SkeletonRow, ErrorState, EmptyState, SearchInput } from "../../../shared/components/ui";
import { useDeleteProducto } from "../hooks/useProducto";
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
  const deleteMutation = useDeleteProducto();

  const filtered = data.filter((p) => p.nombre.toLowerCase().includes(search.toLowerCase()));

  async function handleConfirmDelete() {
    if (deleteId === null) return;
    await deleteMutation.mutateAsync(deleteId);
    setDeleteId(null);
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

      <div className="rounded-xl overflow-hidden" style={{ border: "1px solid #d6c9be" }}>
        <table className="w-full text-sm">
          <thead>
            <tr style={{ backgroundColor: "#ede3d9" }}>
              {["ID", "Nombre", "Precio", "Stock", "Estado", "Acciones"].map((h, i) => (
                <th key={h} className={`px-4 py-3 text-xs font-bold uppercase tracking-wider ${i === 5 ? "text-right" : "text-left"}`} style={{ color: "#9a8070" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {isLoading && Array.from({ length: 4 }).map((_, i) => (
              <tr key={i} style={{ borderTop: "1px solid #e8ddd5" }}><td colSpan={6}><SkeletonRow /></td></tr>
            ))}
            {isError && <tr><td colSpan={6}><ErrorState /></td></tr>}
            {!isLoading && !isError && filtered.length === 0 && <tr><td colSpan={6}><EmptyState message="No se encontraron productos" /></td></tr>}
            {!isLoading && !isError && filtered.map((prod) => (
              <tr key={prod.id} className="transition-colors" style={{ borderTop: "1px solid #e8ddd5", backgroundColor: "#fff" }}
                onMouseEnter={e => (e.currentTarget.style.backgroundColor = "#fdf9f6")}
                onMouseLeave={e => (e.currentTarget.style.backgroundColor = "#fff")}>
                <td className="px-4 py-3 font-mono text-xs" style={{ color: "#9a8070" }}>{prod.id}</td>
                <td className="px-4 py-3">
                  <p className="font-medium" style={{ color: "#2d1e0f" }}>{prod.nombre}</p>
                  {prod.descripcion && <p className="text-xs truncate max-w-xs" style={{ color: "#9a8070" }}>{prod.descripcion}</p>}
                </td>
                <td className="px-4 py-3 font-semibold font-mono" style={{ color: "#c8722a" }}>{formatPrice(prod.precio_base)}</td>
                <td className="px-4 py-3">
                  <span className="font-mono text-sm" style={{ color: prod.stock_cantidad === 0 ? "#dc2626" : "#2d1e0f" }}>{prod.stock_cantidad}</span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-col gap-1">
                    {prod.disponible ? <Badge variant="success">Disponible</Badge> : <Badge variant="danger">No disponible</Badge>}
                    {prod.deleted_at && <Badge variant="danger">Eliminado</Badge>}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex gap-2 justify-end">
                    <Button variant="ghost" onClick={() => onEdit(prod)} className="text-xs px-3 py-1">Editar</Button>
                    <Button variant="danger" onClick={() => setDeleteId(prod.id)} className="text-xs px-3 py-1">Eliminar</Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <ConfirmDialog open={deleteId !== null} message="¿Estás seguro que querés eliminar este producto?" onConfirm={handleConfirmDelete} onCancel={() => setDeleteId(null)} loading={deleteMutation.isPending} />
    </div>
  );
}