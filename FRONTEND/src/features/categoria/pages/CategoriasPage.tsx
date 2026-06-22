// ── CategoriasPage ────────────────────────────────────────────────────────────
import { useState } from "react";
import { Button } from "../../../shared/components/ui";
import { CategoriaTable } from "../components/CategoriaTable";
import { CategoriaForm } from "../components/CategoriaForm";
import { useCategorias } from "../hooks/useCategoria";
import type { Categoria } from "../../../shared/types";

export function CategoriasPage() {
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Categoria | null>(null);
  const [verEliminados, setVerEliminados] = useState(false);
  const { data, isLoading, isError } = useCategorias(0, 100, verEliminados);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold" style={{ color: "#2d1e0f" }}>Categorías</h1>
          <p className="text-sm mt-0.5" style={{ color: "#9a8070" }}>Gestioná las categorías de tus productos</p>
        </div>
        <div className="flex gap-2 items-center">
          <label className="flex items-center gap-2 text-sm cursor-pointer" style={{ color: "#9a8070" }}>
            <input
              type="checkbox"
              checked={verEliminados}
              onChange={(e) => setVerEliminados(e.target.checked)}
              className="w-4 h-4 accent-[#C87A2E]"
            />
            Ver eliminadas
          </label>
          <Button onClick={() => { setEditing(null); setFormOpen(true); }}>+ Nueva categoría</Button>
        </div>
      </div>
      <CategoriaTable data={data?.data ?? []} total={data?.total ?? 0} isLoading={isLoading} isError={isError} onEdit={(cat) => { setEditing(cat); setFormOpen(true); }} />
      <CategoriaForm open={formOpen} onClose={() => { setFormOpen(false); setEditing(null); }} editing={editing} categorias={data?.data ?? []} />
    </div>
  );
}
