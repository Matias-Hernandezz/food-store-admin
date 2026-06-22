import { useState } from "react";
import { Button, Badge, ConfirmDialog, SkeletonRow, ErrorState, EmptyState, SearchInput } from "../../../shared/components/ui";
import { useDeleteIngrediente, useRestoreIngrediente } from "../hooks/useIngrediente";
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
  const [restoreId, setRestoreId] = useState<number | null>(null);
  const deleteMutation = useDeleteIngrediente();
  const restoreMutation = useRestoreIngrediente();

  const filtered = data
    .filter((i) => i.nombre.toLowerCase().includes(search.toLowerCase()))
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

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between gap-4">
        <SearchInput value={search} onChange={setSearch} placeholder="Buscar ingrediente..." />
        <span className="text-xs whitespace-nowrap" style={{ color: "#9a8070" }}>{total} registros</span>
      </div>

      <div className="rounded-xl overflow-hidden" style={{ border: "1px solid #E5E2DA" }}>
        <table className="w-full text-sm">
          <thead>
            <tr style={{ backgroundColor: "#ede3d9" }}>
              {["ID", "Nombre", "Descripción", "Alérgeno", "Estado", "Acciones"].map((h, i) => (
                <th key={h} className={`px-4 py-3 text-xs font-bold uppercase tracking-wider ${i === 5 ? "text-right" : "text-left"}`} style={{ color: "#9a8070" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {isLoading && Array.from({ length: 4 }).map((_, i) => (
              <tr key={i} style={{ borderTop: "1px solid #E5E2DA" }}><td colSpan={6}><SkeletonRow /></td></tr>
            ))}
            {isError && <tr><td colSpan={6}><ErrorState /></td></tr>}
            {!isLoading && !isError && filtered.length === 0 && <tr><td colSpan={6}><EmptyState message="No se encontraron ingredientes" /></td></tr>}
            {!isLoading && !isError && filtered.map((ing) => {
              const isDeleted = !!ing.deleted_at;
              return (
                <tr key={ing.id} className="transition-colors"
                  style={{ borderTop: "1px solid #E5E2DA", backgroundColor: "#fff", opacity: isDeleted ? 0.6 : 1 }}
                  onMouseEnter={e => (e.currentTarget.style.backgroundColor = "#F2E8D5")}
                  onMouseLeave={e => (e.currentTarget.style.backgroundColor = "#fff")}>
                  <td className="px-4 py-3 font-mono text-xs" style={{ color: "#9a8070" }}>{ing.id}</td>
                  <td className="px-4 py-3 font-medium" style={{ color: "#2d1e0f" }}>
                    {ing.nombre}
                    {isDeleted && <span className="ml-2 text-xs" style={{ color: "#9a8070" }}>(eliminado)</span>}
                  </td>
                  <td className="px-4 py-3 max-w-xs truncate" style={{ color: "#9a8070" }}>{ing.descripcion ?? <span className="italic" style={{ color: "#9a8070" }}>sin descripción</span>}</td>
                  <td className="px-4 py-3">{ing.es_alergeno ? <Badge variant="warning">⚠ Alérgeno</Badge> : <Badge variant="default">No</Badge>}</td>
                  <td className="px-4 py-3">
                    {isDeleted ? <Badge variant="danger">Eliminado</Badge> : <Badge variant="success">Activo</Badge>}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2 justify-end">
                      {isDeleted ? (
                        <Button variant="ghost" onClick={() => setRestoreId(ing.id)} className="text-xs px-3 py-1" style={{ color: "#16a34a", border: "1px solid #16a34a", fontWeight: 600 }}>Restaurar</Button>
                      ) : (
                        <>
                          <Button variant="ghost" onClick={() => onEdit(ing)} className="text-xs px-3 py-1">Editar</Button>
                          <Button variant="danger" onClick={() => setDeleteId(ing.id)} className="text-xs px-3 py-1">Eliminar</Button>
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

      <ConfirmDialog open={deleteId !== null} message="¿Estás seguro que querés eliminar este ingrediente?" onConfirm={handleConfirmDelete} onCancel={() => setDeleteId(null)} loading={deleteMutation.isPending} />
      <ConfirmDialog open={restoreId !== null} message="¿Querés restaurar este ingrediente?" onConfirm={handleConfirmRestore} onCancel={() => setRestoreId(null)} loading={restoreMutation.isPending} confirmLabel="Restaurar" />
    </div>
  );
}
