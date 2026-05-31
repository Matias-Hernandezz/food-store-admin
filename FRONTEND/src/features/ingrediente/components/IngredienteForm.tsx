import { useState, useEffect } from "react";
import { Button, Input, Textarea, Modal } from "../../../shared/components/ui";
import { useCreateIngrediente, useUpdateIngrediente } from "../hooks/useIngrediente";
import type { Ingrediente, IngredienteCreate } from "../../../shared/types";

interface IngredienteFormProps {
  open: boolean;
  onClose: () => void;
  editing?: Ingrediente | null;
}

const EMPTY: IngredienteCreate = { nombre: "", descripcion: "", es_alergeno: false };

export function IngredienteForm({ open, onClose, editing }: IngredienteFormProps) {
  const [form, setForm] = useState<IngredienteCreate>(EMPTY);
  const [errors, setErrors] = useState<Partial<Record<keyof IngredienteCreate, string>>>({});
  const createMutation = useCreateIngrediente();
  const updateMutation = useUpdateIngrediente();
  const isPending = createMutation.isPending || updateMutation.isPending;

  useEffect(() => {
    if (editing) { setForm({ nombre: editing.nombre, descripcion: editing.descripcion ?? "", es_alergeno: editing.es_alergeno }); }
    else { setForm(EMPTY); }
    setErrors({});
  }, [editing, open]);

  function validate() {
    const e: typeof errors = {};
    if (!form.nombre.trim()) e.nombre = "El nombre es obligatorio";
    else if (form.nombre.length < 2) e.nombre = "Mínimo 2 caracteres";
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit() {
    if (!validate()) return;
    try {
      if (editing) { await updateMutation.mutateAsync({ id: editing.id, data: { ...form, descripcion: form.descripcion || null } }); }
      else { await createMutation.mutateAsync({ ...form, descripcion: form.descripcion || null }); }
      onClose();
    } catch (e: unknown) { setErrors({ nombre: e instanceof Error ? e.message : "Error desconocido" }); }
  }

  return (
    <Modal open={open} onClose={onClose} title={editing ? "Editar ingrediente" : "Nuevo ingrediente"}>
      <div className="flex flex-col gap-4">
        <Input label="Nombre *" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} error={errors.nombre} placeholder="Ej: Cebolla Caramelizada" maxLength={100} />
        <Textarea label="Descripción" value={form.descripcion ?? ""} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} placeholder="Descripción opcional" />
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setForm({ ...form, es_alergeno: !form.es_alergeno })}
            className="relative w-10 h-5 rounded-full transition-colors duration-200 cursor-pointer"
            style={{ backgroundColor: form.es_alergeno ? "#f97316" : "#d6c9be" }}
          >
            <span className="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform duration-200" style={{ transform: form.es_alergeno ? "translateX(20px)" : "translateX(0)" }} />
          </button>
          <span className="text-sm" style={{ color: "#6b5a4e" }}>
            Es alérgeno {form.es_alergeno && <span className="ml-2 text-xs font-medium" style={{ color: "#f97316" }}>⚠ Marcado como alérgeno</span>}
          </span>
        </div>
        <div className="flex gap-3 justify-end pt-2">
          <Button variant="ghost" onClick={onClose} type="button">Cancelar</Button>
          <Button onClick={handleSubmit} loading={isPending} type="button">{editing ? "Guardar cambios" : "Crear ingrediente"}</Button>
        </div>
      </div>
    </Modal>
  );
}