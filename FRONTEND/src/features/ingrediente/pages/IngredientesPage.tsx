import { useState } from "react";
import { Button } from "../../../shared/components/ui";
import { IngredienteTable } from "../components/IngredienteTable";
import { IngredienteForm } from "../components/IngredienteForm";
import { useIngredientes } from "../hooks/useIngrediente";
import type { Ingrediente } from "../../../shared/types";

export function IngredientesPage() {
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Ingrediente | null>(null);

  const { data, isLoading, isError } = useIngredientes();

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
        <Button onClick={handleNew}>+ Nuevo ingrediente</Button>
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
