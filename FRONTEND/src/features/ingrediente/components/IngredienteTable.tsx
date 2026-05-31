import { useState } from "react";
import { Button, Badge, ConfirmDialog, SkeletonRow, ErrorState, EmptyState, SearchInput } from "../../../shared/components/ui";
import { useDeleteIngrediente } from "../hooks/useIngrediente";
import type { Ingrediente } from "../../../shared/types";

interface IngredienteTableProps {
  data: Ingrediente[];
  total: number;
  isLoading: boolean;
  isError: boolean;
  onEdit: (i: Ingrediente) => void;
}

export function IngredienteTable({ data, total, isLoading, isError, onEdit }: IngredienteTableProps) {
  const [search, setSearch] = useState("");
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const deleteMutation = useDeleteIngrediente();

  const filtered = data.filter((i) => i.nombre.toLowerCase().includes(search.toLowerCase()));

  async function handleConfirmDelete() {
    if (deleteId === null) return;
    await deleteMutation.mutateAsync(deleteId);
    setDeleteId(null);
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between gap-4">
        <SearchInput value={search} onChange={setSearch} placeholder="Buscar ingrediente..." />
        <span className="text-xs whitespace-nowrap" style={{ color: "#9a8070" }}>{total} registros</span>
      </div>

      <div className="rounded-xl overflow-hidden" style={{ border: "1px solid #d6c9be" }}>
        <table className="w-full text-sm">
          <thead>
            <tr style={{ backgroundColor: "#ede3d9" }}>
              {["ID", "Nombre", "Descripción", "Alérgeno", "Acciones"].map((h, i) => (
                <th key={h} className={`px-4 py-3 text-xs font-bold uppercase tracking-wider ${i === 4 ? "text-right" : "text-left"}`} style={{ color: "#9a8070" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {isLoading && Array.from({ length: 4 }).map((_, i) => (
              <tr key={i} style={{ borderTop: "1px solid #e8ddd5" }}><td colSpan={5}><SkeletonRow /></td></tr>
            ))}
            {isError && <tr><td colSpan={5}><ErrorState /></td></tr>}
            {!isLoading && !isError && filtered.length === 0 && <tr><td colSpan={5}><EmptyState message="No se encontraron ingredientes" /></td></tr>}
            {!isLoading && !isError && filtered.map((ing) => (
              <tr key={ing.id} className="transition-colors" style={{ borderTop: "1px solid #e8ddd5", backgroundColor: "#fff" }}
                onMouseEnter={e => (e.currentTarget.style.backgroundColor = "#fdf9f6")}
                onMouseLeave={e => (e.currentTarget.style.backgroundColor = "#fff")}>
                <td className="px-4 py-3 font-mono text-xs" style={{ color: "#9a8070" }}>{ing.id}</td>
                <td className="px-4 py-3 font-medium" style={{ color: "#2d1e0f" }}>{ing.nombre}</td>
                <td className="px-4 py-3 max-w-xs truncate" style={{ color: "#9a8070" }}>{ing.descripcion ?? <span className="italic" style={{ color: "#c8b4a0" }}>sin descripción</span>}</td>
                <td className="px-4 py-3">{ing.es_alergeno ? <Badge variant="warning">⚠ Alérgeno</Badge> : <Badge variant="default">No</Badge>}</td>
                <td className="px-4 py-3">
                  <div className="flex gap-2 justify-end">
                    <Button variant="ghost" onClick={() => onEdit(ing)} className="text-xs px-3 py-1">Editar</Button>
                    <Button variant="danger" onClick={() => setDeleteId(ing.id)} className="text-xs px-3 py-1">Eliminar</Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <ConfirmDialog open={deleteId !== null} message="¿Estás seguro que querés eliminar este ingrediente?" onConfirm={handleConfirmDelete} onCancel={() => setDeleteId(null)} loading={deleteMutation.isPending} />
    </div>
  );
}