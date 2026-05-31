import { useState, Fragment } from "react";
import { Button, Badge, ConfirmDialog, SkeletonRow, ErrorState, EmptyState, SearchInput } from "../../../shared/components/ui";
import { useDeleteCategoria } from "../hooks/useCategoria";
import type { Categoria } from "../../../shared/types";

interface CategoriaTableProps {
  data: Categoria[];
  total: number;
  isLoading: boolean;
  isError: boolean;
  onEdit: (c: Categoria) => void;
}

export function CategoriaTable({ data, total, isLoading, isError, onEdit }: CategoriaTableProps) {
  const [search, setSearch] = useState("");
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());
  const deleteMutation = useDeleteCategoria();

  const padres = data.filter((c) => c.parent_id === null);
  const hijas = data.filter((c) => c.parent_id !== null);
  const hayBusqueda = search.trim().length > 0;
  const filtradas = hayBusqueda ? data.filter((c) => c.nombre.toLowerCase().includes(search.toLowerCase())) : [];

  function toggleExpand(id: number) {
    setExpanded((prev) => { const next = new Set(prev); next.has(id) ? next.delete(id) : next.add(id); return next; });
  }

  function getHijas(parentId: number) { return hijas.filter((c) => c.parent_id === parentId); }

  async function handleConfirmDelete() {
    if (deleteId === null) return;
    await deleteMutation.mutateAsync(deleteId);
    setDeleteId(null);
  }

  const AccionesCell = ({ cat }: { cat: Categoria }) => (
    <div className="flex gap-2 justify-end">
      <Button variant="ghost" onClick={() => onEdit(cat)} className="text-xs px-3 py-1">Editar</Button>
      <Button variant="danger" onClick={() => setDeleteId(cat.id)} className="text-xs px-3 py-1">Eliminar</Button>
    </div>
  );

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between gap-4">
        <SearchInput value={search} onChange={setSearch} placeholder="Buscar categoría..." />
        <span className="text-xs whitespace-nowrap" style={{ color: "#9a8070" }}>{total} registros</span>
      </div>

      <div className="rounded-xl overflow-hidden" style={{ border: "1px solid #d6c9be" }}>
        <table className="w-full text-sm">
          <thead>
            <tr style={{ backgroundColor: "#ede3d9" }}>
              {["ID", "Nombre", "Descripción", "Estado", "Acciones"].map((h, i) => (
                <th key={h} className={`px-4 py-3 text-xs font-bold uppercase tracking-wider ${i === 4 ? "text-right" : "text-left"}`} style={{ color: "#9a8070" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {isLoading && Array.from({ length: 4 }).map((_, i) => (
              <tr key={i} style={{ borderTop: "1px solid #e8ddd5" }}><td colSpan={5}><SkeletonRow /></td></tr>
            ))}
            {isError && <tr><td colSpan={5}><ErrorState /></td></tr>}
            {!isLoading && !isError && data.length === 0 && <tr><td colSpan={5}><EmptyState message="No se encontraron categorías" /></td></tr>}

            {!isLoading && !isError && hayBusqueda && (
              filtradas.length === 0
                ? <tr><td colSpan={5}><EmptyState message="Sin resultados" /></td></tr>
                : filtradas.map((cat) => (
                  <tr key={cat.id} className="transition-colors" style={{ borderTop: "1px solid #e8ddd5", backgroundColor: "#fff" }}
                    onMouseEnter={e => (e.currentTarget.style.backgroundColor = "#fdf9f6")}
                    onMouseLeave={e => (e.currentTarget.style.backgroundColor = "#fff")}>
                    <td className="px-4 py-3 font-mono text-xs" style={{ color: "#9a8070" }}>{cat.id}</td>
                    <td className="px-4 py-3 font-medium" style={{ color: "#2d1e0f" }}>
                      {cat.parent_id !== null && <span className="mr-2" style={{ color: "#c8722a" }}>↳</span>}{cat.nombre}
                    </td>
                    <td className="px-4 py-3 max-w-xs truncate" style={{ color: "#9a8070" }}>{cat.descripcion ?? <span className="italic" style={{ color: "#c8b4a0" }}>sin descripción</span>}</td>
                    <td className="px-4 py-3">{cat.deleted_at ? <Badge variant="danger">Inactiva</Badge> : <Badge variant="success">Activa</Badge>}</td>
                    <td className="px-4 py-3"><AccionesCell cat={cat} /></td>
                  </tr>
                ))
            )}

            {!isLoading && !isError && !hayBusqueda && padres.map((padre) => {
              const subcats = getHijas(padre.id);
              const isOpen = expanded.has(padre.id);
              return (
                <Fragment key={padre.id}>
                  <tr className="transition-colors" style={{ borderTop: "1px solid #e8ddd5", backgroundColor: "#fff" }}
                    onMouseEnter={e => (e.currentTarget.style.backgroundColor = "#fdf9f6")}
                    onMouseLeave={e => (e.currentTarget.style.backgroundColor = "#fff")}>
                    <td className="px-4 py-3 font-mono text-xs" style={{ color: "#9a8070" }}>{padre.id}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {subcats.length > 0 ? (
                          <button onClick={() => toggleExpand(padre.id)} className="w-5 h-5 flex items-center justify-center rounded text-xs cursor-pointer transition-all" style={{ color: "#9a8070" }}>
                            {isOpen ? "▼" : "▶"}
                          </button>
                        ) : <span className="w-5 h-5" />}
                        <span className="font-semibold" style={{ color: "#2d1e0f" }}>{padre.nombre}</span>
                        {subcats.length > 0 && <span className="text-xs" style={{ color: "#9a8070" }}>({subcats.length})</span>}
                      </div>
                    </td>
                    <td className="px-4 py-3 max-w-xs truncate" style={{ color: "#9a8070" }}>{padre.descripcion ?? <span className="italic" style={{ color: "#c8b4a0" }}>sin descripción</span>}</td>
                    <td className="px-4 py-3">{padre.deleted_at ? <Badge variant="danger">Inactiva</Badge> : <Badge variant="success">Activa</Badge>}</td>
                    <td className="px-4 py-3"><AccionesCell cat={padre} /></td>
                  </tr>
                  {isOpen && subcats.map((hija) => (
                    <tr key={hija.id} className="transition-colors" style={{ borderTop: "1px solid #e8ddd5", backgroundColor: "#fdf9f6" }}
                      onMouseEnter={e => (e.currentTarget.style.backgroundColor = "#f5ede6")}
                      onMouseLeave={e => (e.currentTarget.style.backgroundColor = "#fdf9f6")}>
                      <td className="px-4 py-2.5 font-mono text-xs" style={{ color: "#c8b4a0" }}>{hija.id}</td>
                      <td className="px-4 py-2.5">
                        <div className="flex items-center gap-2 pl-7">
                          <span className="text-xs" style={{ color: "#c8b4a0" }}>└</span>
                          <span style={{ color: "#6b5a4e" }}>{hija.nombre}</span>
                        </div>
                      </td>
                      <td className="px-4 py-2.5 max-w-xs truncate text-xs" style={{ color: "#9a8070" }}>{hija.descripcion ?? <span className="italic" style={{ color: "#c8b4a0" }}>sin descripción</span>}</td>
                      <td className="px-4 py-2.5">{hija.deleted_at ? <Badge variant="danger">Inactiva</Badge> : <Badge variant="success">Activa</Badge>}</td>
                      <td className="px-4 py-2.5"><AccionesCell cat={hija} /></td>
                    </tr>
                  ))}
                </Fragment>
              );
            })}
          </tbody>
        </table>
      </div>

      <ConfirmDialog open={deleteId !== null} message="¿Estás seguro que querés eliminar esta categoría?" onConfirm={handleConfirmDelete} onCancel={() => setDeleteId(null)} loading={deleteMutation.isPending} />
    </div>
  );
}