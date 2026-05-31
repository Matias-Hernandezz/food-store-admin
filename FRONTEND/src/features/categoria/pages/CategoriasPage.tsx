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
  const { data, isLoading, isError } = useCategorias();

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold" style={{ color: "#2d1e0f" }}>Categorías</h1>
          <p className="text-sm mt-0.5" style={{ color: "#9a8070" }}>Gestioná las categorías de tus productos</p>
        </div>
        <Button onClick={() => { setEditing(null); setFormOpen(true); }}>+ Nueva categoría</Button>
      </div>
      <CategoriaTable data={data?.data ?? []} total={data?.total ?? 0} isLoading={isLoading} isError={isError} onEdit={(cat) => { setEditing(cat); setFormOpen(true); }} />
      <CategoriaForm open={formOpen} onClose={() => { setFormOpen(false); setEditing(null); }} editing={editing} categorias={data?.data ?? []} />
    </div>
  );
}
