import { useState } from "react";
import { Button } from "../../../shared/components/ui";
import { IngredienteTable } from "../components/IngredienteTable";
import { IngredienteForm } from "../components/IngredienteForm";
import { useIngredientes } from "../hooks/useIngrediente";
import type { Ingrediente } from "../../../shared/types";

export function IngredientesPage() {
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Ingrediente | null>(null);
  const [verEliminados, setVerEliminados] = useState(false);

  const { data, isLoading, isError } = useIngredientes({ page: 0, pageSize: 100, incluirEliminados: verEliminados });

  function handleEdit(ing: Ingrediente) {
    setEditing(ing);
    setFormOpen(true);
  }

  function handleNew() {
    setEditing(null);
    setFormOpen(true);
  }

  function handleClose() {
    setFormOpen(false);
    setEditing(null);
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold" style={{ color: "#2d1e0f" }}>Ingredientes</h1>
          <p className="text-sm mt-0.5" style={{ color: "#9a8070" }}>Administrá los ingredientes y alérgenos</p>
        </div>
        <div className="flex gap-2 items-center">
          <label className="flex items-center gap-2 text-sm cursor-pointer" style={{ color: "#9a8070" }}>
            <input
              type="checkbox"
              checked={verEliminados}
              onChange={(e) => setVerEliminados(e.target.checked)}
              className="w-4 h-4 accent-[#C87A2E]"
            />
            Ver eliminados
          </label>
          <Button onClick={handleNew}>+ Nuevo ingrediente</Button>
        </div>
      </div>

      <IngredienteTable
        data={data?.data ?? []}
        total={data?.total ?? 0}
        isLoading={isLoading}
        isError={isError}
        onEdit={handleEdit}
      />

      <IngredienteForm
        open={formOpen}
        onClose={handleClose}
        editing={editing}
      />
    </div>
  );
}
