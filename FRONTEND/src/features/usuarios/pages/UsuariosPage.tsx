import { useState, useEffect, type FormEvent } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useUsuarios } from "../hooks/useUsuarios";
import { usuariosApi } from "../api/usuariosApi";
import { Icons } from "../../../shared/components/ui/Icons";

const ROLES = ["ADMIN", "STOCK", "PEDIDOS", "CLIENT"];

const ROL_COLOR: Record<string, React.CSSProperties> = {
  ADMIN: { backgroundColor: "#fee2e2", color: "#991b1b" },
  STOCK: { backgroundColor: "#dbeafe", color: "#1e40af" },
  PEDIDOS: { backgroundColor: "#ede9fe", color: "#5b21b6" },
  CLIENT: { backgroundColor: "#dcfce7", color: "#166534" },
};

export function UsuariosPage() {
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const { data: usuarios, isLoading } = useUsuarios({ search: search || undefined });

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => setSearch(searchInput), 300);
    return () => clearTimeout(timer);
  }, [searchInput]);
  const { asignarRol: asignar, quitarRol: quitar, softDeleteUser: eliminar, createUser, createUserPending: creando } = useUsuarios({ enabled: false });
  const queryClient = useQueryClient();
  const [confirmarId, setConfirmarId] = useState<number | null>(null);
  const [mostrarForm, setMostrarForm] = useState(false);
  const [form, setForm] = useState({ nombre: "", apellido: "", email: "", celular: "", password: "" });
  const [rolesSeleccionados, setRolesSeleccionados] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const toggleRol = (rol: string) => {
    setRolesSeleccionados((prev) =>
      prev.includes(rol) ? prev.filter((r) => r !== rol) : [...prev, rol]
    );
  };

  const handleCrear = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!form.nombre || !form.apellido || !form.email || !form.password) {
      setError("Completá todos los campos obligatorios");
      return;
    }
    try {
      const usuarioCreado = await createUser({
        nombre: form.nombre,
        apellido: form.apellido,
        email: form.email,
        celular: form.celular || undefined,
        password: form.password,
      });
      // Asignar roles seleccionados después de crear el usuario
      if (rolesSeleccionados.length > 0) {
        try {
          await Promise.all(
            rolesSeleccionados.map((rol) =>
              usuariosApi.asignarRol(usuarioCreado.id, rol)
            )
          );
        } catch {
          // Si falla la asignación de roles, igual limpiamos el form
        }
        queryClient.invalidateQueries({ queryKey: ["usuarios"] });
      }
      setForm({ nombre: "", apellido: "", email: "", celular: "", password: "" });
      setRolesSeleccionados([]);
      setMostrarForm(false);
    } catch (err) {
      setError((err as Error).message ?? "Error al crear usuario");
    }
  };

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-t-transparent rounded-full animate-spin" style={{ borderColor: "#C87A2E", borderTopColor: "transparent" }} />
    </div>
  );

  const activos = usuarios?.filter((u) => !u.deleted_at) ?? [];
  const eliminados = usuarios?.filter((u) => u.deleted_at) ?? [];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: "#2d1e0f" }}>Usuarios</h1>
          <p className="text-sm mt-1" style={{ color: "#9a8070" }}>{activos.length} usuarios activos{search ? ` · "${search}"` : ""}</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: "#9a8070" }}>
              <Icons.Search size={16} />
            </span>
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Buscar por nombre, apellido o email..."
              className="rounded-xl pl-9 pr-4 py-2 text-sm outline-none w-72"
              style={{ border: "1px solid #E5E2DA", color: "#2d1e0f", backgroundColor: "#fff" }}
            />
          </div>
          <button
            onClick={() => setMostrarForm(!mostrarForm)}
            className="bg-[#C87A2E] text-white font-bold px-5 py-2.5 rounded-xl hover:bg-[#B06920] transition-colors text-sm"
          >
            {mostrarForm ? "Cancelar" : "＋ Nuevo Usuario"}
          </button>
        </div>
      </div>

      {/* ─── Formulario crear usuario ──────────────────────────────────── */}
      {mostrarForm && (
        <div className="rounded-2xl p-6 mb-6 shadow-sm" style={{ backgroundColor: "#fff", border: "1px solid #E5E2DA" }}>
          <h3 className="font-bold text-sm mb-4" style={{ color: "#2d1e0f" }}>Crear nuevo usuario</h3>
          <form onSubmit={handleCrear} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider mb-1.5" style={{ color: "#9a8070" }}>Nombre *</label>
                <input type="text" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                  className="w-full rounded-lg px-3 py-2 text-sm outline-none" style={{ border: "1px solid #E5E2DA", color: "#2d1e0f" }} />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider mb-1.5" style={{ color: "#9a8070" }}>Apellido *</label>
                <input type="text" value={form.apellido} onChange={(e) => setForm({ ...form, apellido: e.target.value })}
                  className="w-full rounded-lg px-3 py-2 text-sm outline-none" style={{ border: "1px solid #E5E2DA", color: "#2d1e0f" }} />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider mb-1.5" style={{ color: "#9a8070" }}>Email *</label>
                <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="w-full rounded-lg px-3 py-2 text-sm outline-none" style={{ border: "1px solid #E5E2DA", color: "#2d1e0f" }} />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider mb-1.5" style={{ color: "#9a8070" }}>Celular</label>
                <input type="tel" value={form.celular} onChange={(e) => setForm({ ...form, celular: e.target.value })}
                  className="w-full rounded-lg px-3 py-2 text-sm outline-none" style={{ border: "1px solid #E5E2DA", color: "#2d1e0f" }} />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider mb-1.5" style={{ color: "#9a8070" }}>Contraseña *</label>
                <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
                  className="w-full rounded-lg px-3 py-2 text-sm outline-none" style={{ border: "1px solid #E5E2DA", color: "#2d1e0f" }} />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider mb-1.5" style={{ color: "#9a8070" }}>Roles</label>
                <div className="flex gap-1.5 flex-wrap">
                  {ROLES.map((rol) => {
                    const selected = rolesSeleccionados.includes(rol);
                    return (
                      <button
                        key={rol}
                        type="button"
                        onClick={() => toggleRol(rol)}
                        className="text-xs font-bold px-2.5 py-1 rounded-full transition-all"
                        style={{
                          border: selected ? "2px solid transparent" : "2px dashed #E5E2DA",
                          backgroundColor: selected ? (ROL_COLOR[rol]?.backgroundColor ?? "#E5E2DA") : "#fff",
                          color: selected ? (ROL_COLOR[rol]?.color ?? "#6b5a4e") : "#9a8070",
                        }}
                      >
                        {selected ? `✓ ${rol}` : rol}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
            {error && (
              <p className="text-xs" style={{ color: "#dc2626" }}>{error}</p>
            )}
            <button type="submit" disabled={creando}
              className="bg-[#C87A2E] text-white font-bold px-6 py-2.5 rounded-xl hover:bg-[#B06920] transition-colors text-sm disabled:opacity-50">
              {creando ? "Creando..." : "Crear Usuario"}
            </button>
          </form>
        </div>
      )}

      {/* ─── Tabla de usuarios ─────────────────────────────────────────── */}
      <div className="rounded-2xl overflow-hidden shadow-sm" style={{ backgroundColor: "#fff", border: "1px solid #E5E2DA" }}>
        <table className="w-full">
          <thead>
            <tr style={{ borderBottom: "1px solid #E5E2DA", backgroundColor: "#ede3d9" }}>
              {["Usuario", "Email", "Roles", "Acciones"].map((h) => (
                <th key={h} className="text-left text-xs font-bold uppercase tracking-wider px-5 py-3" style={{ color: "#9a8070" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {activos.map((u) => (
              <tr key={u.id} className="transition-colors" style={{ borderBottom: "1px solid #E5E2DA", backgroundColor: "#fff" }}
                onMouseEnter={e => (e.currentTarget.style.backgroundColor = "#F2E8D5")}
                onMouseLeave={e => (e.currentTarget.style.backgroundColor = "#fff")}>
                <td className="px-5 py-4">
                  <p className="font-semibold text-sm" style={{ color: "#2d1e0f" }}>{u.nombre} {u.apellido}</p>
                  <p className="text-xs" style={{ color: "#9a8070" }}>#{u.id}</p>
                </td>
                <td className="px-5 py-4 text-sm" style={{ color: "#6b5a4e" }}>{u.email}</td>
                <td className="px-5 py-4">
                  <div className="flex gap-1 flex-wrap">
                    {u.roles.map((r) => (
                      <span key={r} onClick={() => quitar({ id: u.id, rol: r })} title="Click para quitar"
                        className="text-xs font-bold px-2 py-0.5 rounded-full cursor-pointer transition-opacity hover:opacity-70"
                        style={ROL_COLOR[r] ?? { backgroundColor: "#E5E2DA", color: "#6b5a4e" }}>
                        {r} ✕
                      </span>
                    ))}
                    <select onChange={(e) => { if (e.target.value) { asignar({ id: u.id, rol: e.target.value }); e.target.value = ""; } }}
                      className="text-xs rounded-full px-2 py-0.5 cursor-pointer focus:outline-none"
                      style={{ border: "1px dashed #E5E2DA", color: "#9a8070", backgroundColor: "#fff" }}>
                      <option value="">+ rol</option>
                      {ROLES.filter((r) => !u.roles.includes(r)).map((r) => <option key={r} value={r}>{r}</option>)}
                    </select>
                  </div>
                </td>
                <td className="px-5 py-4">
                  {confirmarId === u.id ? (
                    <div className="flex gap-2">
                      <button onClick={() => { eliminar(u.id); setConfirmarId(null); }} className="text-xs px-3 py-1 rounded-lg text-white" style={{ backgroundColor: "#dc2626" }}>Confirmar</button>
                      <button onClick={() => setConfirmarId(null)} className="text-xs px-3 py-1 rounded-lg" style={{ border: "1px solid #E5E2DA", color: "#6b5a4e" }}>Cancelar</button>
                    </div>
                  ) : (
                    <button onClick={() => setConfirmarId(u.id)} className="text-xs font-medium transition-colors" style={{ color: "#dc2626" }}>Eliminar</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {activos.length === 0 && (
          <div className="text-center py-12" style={{ color: "#9a8070" }}>
            <p>No hay usuarios activos</p>
          </div>
        )}
      </div>

      {eliminados.length > 0 && (
        <div className="mt-6">
          <h2 className="text-sm font-bold uppercase tracking-wider mb-3" style={{ color: "#9a8070" }}>Eliminados ({eliminados.length})</h2>
          <div className="space-y-2">
            {eliminados.map((u) => (
              <div key={u.id} className="flex justify-between items-center rounded-xl px-4 py-3 opacity-60" style={{ backgroundColor: "#F2E8D5" }}>
                <span className="text-sm" style={{ color: "#9a8070" }}>{u.nombre} {u.apellido} — {u.email}</span>
                <span className="text-xs" style={{ color: "#dc2626" }}>Eliminado</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
