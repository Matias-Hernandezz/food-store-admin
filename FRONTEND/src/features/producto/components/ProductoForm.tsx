import { useState, useEffect } from "react";
import { Button, Input, Textarea, Modal } from "../../../shared/components/ui";
import { useCreateProducto, useUpdateProducto } from "../hooks/useProducto";
import type { Producto, ProductoCreate, Categoria, Ingrediente } from "../../../shared/types";

interface ProductoFormProps {
  open: boolean;
  onClose: () => void;
  editing?: Producto | null;
  categorias: Categoria[];
  ingredientes: Ingrediente[];
}

const EMPTY: ProductoCreate = { nombre: "", descripcion: "", precio_base: 0, imagenes_url: "", stock_cantidad: 0, disponible: true, categoria_ids: [], ingrediente_ids: [] };

export function ProductoForm({ open, onClose, editing, categorias, ingredientes }: ProductoFormProps) {
  const [form, setForm] = useState<ProductoCreate>(EMPTY);
  const [errors, setErrors] = useState<Partial<Record<string, string>>>({});
  const [busquedaIng, setBusquedaIng] = useState("");
  const createMutation = useCreateProducto();
  const updateMutation = useUpdateProducto();
  const isPending = createMutation.isPending || updateMutation.isPending;

  useEffect(() => {
    if (editing) {
      setForm({ nombre: editing.nombre, descripcion: editing.descripcion ?? "", precio_base: parseFloat(editing.precio_base), imagenes_url: editing.imagenes_url ?? "", stock_cantidad: editing.stock_cantidad, disponible: editing.disponible, categoria_ids: editing.categoria_ids ?? [], ingrediente_ids: editing.ingrediente_ids ?? [] });
    } else { setForm(EMPTY); }
    setErrors({}); setBusquedaIng("");
  }, [editing, open]);

  function validate() {
    const e: typeof errors = {};
    if (!form.nombre.trim()) e.nombre = "El nombre es obligatorio";
    else if (form.nombre.length < 3) e.nombre = "Mínimo 3 caracteres";
    if (form.precio_base < 0) e.precio_base = "El precio no puede ser negativo";
    if ((form.stock_cantidad ?? 0) < 0) e.stock_cantidad = "El stock no puede ser negativo";
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit() {
    if (!validate()) return;
    try {
      const payload = { ...form, descripcion: form.descripcion || null, imagenes_url: form.imagenes_url || null };
      if (editing) { await updateMutation.mutateAsync({ id: editing.id, data: payload }); }
      else { await createMutation.mutateAsync(payload); }
      onClose();
    } catch (e: unknown) { setErrors({ nombre: e instanceof Error ? e.message : "Error desconocido" }); }
  }

  const ingredientesFiltrados = ingredientes.filter((ing) => ing.nombre.toLowerCase().includes(busquedaIng.toLowerCase()));

  return (
    <Modal open={open} onClose={onClose} title={editing ? "Editar producto" : "Nuevo producto"}>
      <div className="flex flex-col gap-4 max-h-[70vh] overflow-y-auto pr-1">
        <Input label="Nombre *" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} error={errors.nombre} placeholder="Ej: Hamburguesa Doble Queso" maxLength={150} />
        <Textarea label="Descripción" value={form.descripcion ?? ""} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} placeholder="Descripción del producto" />
        <div className="grid grid-cols-2 gap-4">
          <Input label="Precio base *" type="number" min={0} step={0.01} value={form.precio_base === 0 ? "" : form.precio_base} onChange={(e) => setForm({ ...form, precio_base: e.target.value === "" ? 0 : parseFloat(e.target.value) })} error={errors.precio_base} placeholder="0.00" />
          <Input label="Stock" type="number" min={0} value={form.stock_cantidad === 0 ? "" : form.stock_cantidad} onChange={(e) => setForm({ ...form, stock_cantidad: e.target.value === "" ? 0 : parseInt(e.target.value) })} error={errors.stock_cantidad} placeholder="0" />
        </div>
        <Input label="URL de imagen" value={form.imagenes_url ?? ""} onChange={(e) => setForm({ ...form, imagenes_url: e.target.value })} placeholder="https://..." />

        <div className="flex items-center gap-3">
          <button type="button" onClick={() => setForm({ ...form, disponible: !form.disponible })} className="relative w-10 h-5 rounded-full transition-colors duration-200 cursor-pointer" style={{ backgroundColor: form.disponible ? "#f97316" : "#d6c9be" }}>
            <span className="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform duration-200" style={{ transform: form.disponible ? "translateX(20px)" : "translateX(0)" }} />
          </button>
          <span className="text-sm" style={{ color: "#6b5a4e" }}>{form.disponible ? "Disponible" : "No disponible"}</span>
        </div>

        {categorias.length > 0 && (
          <div className="flex flex-col gap-2">
            <label className="text-xs font-semibold uppercase tracking-wider" style={{ color: "#9a8070" }}>Categorías</label>
            <div className="flex flex-wrap gap-2 p-3 rounded-lg" style={{ backgroundColor: "#fdf9f6", border: "1px solid #d6c9be" }}>
              {categorias.map((cat) => {
                const selected = form.categoria_ids.includes(cat.id);
                return (
                  <button key={cat.id} type="button" onClick={() => setForm((prev) => ({ ...prev, categoria_ids: selected ? prev.categoria_ids.filter((c) => c !== cat.id) : [...prev.categoria_ids, cat.id] }))}
                    className="px-3 py-1 rounded-full text-xs font-medium transition-all cursor-pointer"
                    style={{ backgroundColor: selected ? "#f97316" : "#e8ddd5", color: selected ? "#fff" : "#6b5a4e" }}>
                    {cat.nombre}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {ingredientes.length > 0 && (
          <div className="flex flex-col gap-2">
            <label className="text-xs font-semibold uppercase tracking-wider" style={{ color: "#9a8070" }}>
              Ingredientes {(form.ingrediente_ids ?? []).length > 0 && <span className="ml-2 normal-case font-normal" style={{ color: "#f97316" }}>{(form.ingrediente_ids ?? []).length} seleccionado(s)</span>}
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-xs" style={{ color: "#9a8070" }}>🔍</span>
              <input type="text" value={busquedaIng} onChange={(e) => setBusquedaIng(e.target.value)} placeholder="Buscar ingrediente..." className="w-full rounded-lg pl-8 pr-3 py-2 text-sm outline-none transition-all" style={{ backgroundColor: "#fff", border: "1px solid #d6c9be", color: "#2d1e0f" }} />
            </div>
            <div className="flex flex-wrap gap-2 p-3 rounded-lg max-h-36 overflow-y-auto" style={{ backgroundColor: "#fdf9f6", border: "1px solid #d6c9be" }}>
              {ingredientesFiltrados.length === 0
                ? <p className="text-xs italic" style={{ color: "#c8b4a0" }}>Sin resultados para "{busquedaIng}"</p>
                : ingredientesFiltrados.map((ing) => {
                  const selected = (form.ingrediente_ids ?? []).includes(ing.id);
                  return (
                    <button key={ing.id} type="button"
                      onClick={() => setForm((prev) => ({ ...prev, ingrediente_ids: selected ? (prev.ingrediente_ids ?? []).filter((i) => i !== ing.id) : [...(prev.ingrediente_ids ?? []), ing.id] }))}
                      className="px-3 py-1 rounded-full text-xs font-medium transition-all cursor-pointer"
                      style={{ backgroundColor: selected ? "#f97316" : "#e8ddd5", color: selected ? "#fff" : "#6b5a4e", outline: ing.es_alergeno ? "1px solid #f59e0b" : "none" }}>
                      {ing.nombre}{ing.es_alergeno && " ⚠"}
                    </button>
                  );
                })}
            </div>
          </div>
        )}

        <div className="flex gap-3 justify-end pt-2">
          <Button variant="ghost" onClick={onClose} type="button">Cancelar</Button>
          <Button onClick={handleSubmit} loading={isPending} type="button">{editing ? "Guardar cambios" : "Crear producto"}</Button>
        </div>
      </div>
    </Modal>
  );
}