import { useState, useEffect } from "react";
import { Button, Input, Textarea, Modal } from "../../../shared/components/ui";
import { useCreateCategoria, useUpdateCategoria } from "../hooks/useCategoria";
import type { Categoria, CategoriaCreate } from "../../../shared/types";

interface CategoriaFormProps {
  open: boolean;
  onClose: () => void;
  editing?: Categoria | null;
  categorias: Categoria[];
}

const EMPTY: CategoriaCreate = { nombre: "", descripcion: "", imagen_url: "", parent_id: null };

export function CategoriaForm({ open, onClose, editing, categorias }: CategoriaFormProps) {
  const [form, setForm] = useState<CategoriaCreate>(EMPTY);
  const [errors, setErrors] = useState<Partial<Record<keyof CategoriaCreate, string>>>({});
  const createMutation = useCreateCategoria();
  const updateMutation = useUpdateCategoria();
  const isPending = createMutation.isPending || updateMutation.isPending;

  useEffect(() => {
    if (editing) { setForm({ nombre: editing.nombre, descripcion: editing.descripcion ?? "", imagen_url: editing.imagen_url ?? "", parent_id: editing.parent_id ?? null }); }
    else { setForm(EMPTY); }
    setErrors({});
  }, [editing, open]);

  function validate() {
    const e: typeof errors = {};
    if (!form.nombre.trim()) e.nombre = "El nombre es obligatorio";
    else if (form.nombre.length < 3) e.nombre = "Mínimo 3 caracteres";
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit() {
    if (!validate()) return;
    const payload = { ...form, descripcion: form.descripcion || null, imagen_url: form.imagen_url || null, parent_id: form.parent_id || null };
    try {
      if (editing) { await updateMutation.mutateAsync({ id: editing.id, data: payload }); }
      else { await createMutation.mutateAsync(payload); }
      onClose();
    } catch (e: unknown) { setErrors({ nombre: e instanceof Error ? e.message : "Error desconocido" }); }
  }

  const padres = categorias.filter((c) => c.id !== editing?.id);

  return (
    <Modal open={open} onClose={onClose} title={editing ? "Editar categoría" : "Nueva categoría"}>
      <div className="flex flex-col gap-4">
        <Input label="Nombre *" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} error={errors.nombre} placeholder="Ej: Pizzas" maxLength={100} />
        <Textarea label="Descripción" value={form.descripcion ?? ""} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} placeholder="Descripción opcional" maxLength={250} />
        <Input label="URL de imagen" value={form.imagen_url ?? ""} onChange={(e) => setForm({ ...form, imagen_url: e.target.value })} placeholder="https://..." />
        <div className="flex flex-col gap-1">
          <label className="text-xs font-semibold uppercase tracking-wider" style={{ color: "#9a8070" }}>Categoría padre</label>
          <select
            value={form.parent_id ?? ""}
            onChange={(e) => setForm({ ...form, parent_id: e.target.value ? Number(e.target.value) : null })}
            className="w-full rounded-lg px-3 py-2 text-sm outline-none transition-all"
            style={{ backgroundColor: "#fff", border: "1px solid #d6c9be", color: "#2d1e0f" }}
          >
            <option value="">Sin categoría padre</option>
            {padres.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
          </select>
        </div>
        <div className="flex gap-3 justify-end pt-2">
          <Button variant="ghost" onClick={onClose} type="button">Cancelar</Button>
          <Button onClick={handleSubmit} loading={isPending} type="button">{editing ? "Guardar cambios" : "Crear categoría"}</Button>
        </div>
      </div>
    </Modal>
  );
}