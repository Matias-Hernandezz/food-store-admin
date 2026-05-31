import { useState } from "react";
import { useUsuarios, useAsignarRol, useQuitarRol, useSoftDeleteUsuario } from "../hooks/useUsuarios";

const ROLES = ["ADMIN", "STOCK", "PEDIDOS", "CLIENT"];

const ROL_COLOR: Record<string, React.CSSProperties> = {
  ADMIN: { backgroundColor: "#fee2e2", color: "#991b1b" },
  STOCK: { backgroundColor: "#dbeafe", color: "#1e40af" },
  PEDIDOS: { backgroundColor: "#ede9fe", color: "#5b21b6" },
  CLIENT: { backgroundColor: "#dcfce7", color: "#166534" },
};

export function UsuariosPage() {
  const { data: usuarios, isLoading } = useUsuarios();
  const { mutate: asignar } = useAsignarRol();
  const { mutate: quitar } = useQuitarRol();
  const { mutate: eliminar } = useSoftDeleteUsuario();
  const [confirmarId, setConfirmarId] = useState<number | null>(null);

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-t-transparent rounded-full animate-spin" style={{ borderColor: "#c8722a", borderTopColor: "transparent" }} />
    </div>
  );

  const activos = usuarios?.filter((u) => !u.deleted_at) ?? [];
  const eliminados = usuarios?.filter((u) => u.deleted_at) ?? [];

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold" style={{ color: "#2d1e0f" }}>Usuarios</h1>
        <p className="text-sm mt-1" style={{ color: "#9a8070" }}>{activos.length} usuarios activos</p>
      </div>

      <div className="rounded-2xl overflow-hidden shadow-sm" style={{ backgroundColor: "#fff", border: "1px solid #d6c9be" }}>
        <table className="w-full">
          <thead>
            <tr style={{ borderBottom: "1px solid #e8ddd5", backgroundColor: "#ede3d9" }}>
              {["Usuario", "Email", "Roles", "Acciones"].map((h) => (
                <th key={h} className="text-left text-xs font-bold uppercase tracking-wider px-5 py-3" style={{ color: "#9a8070" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {activos.map((u) => (
              <tr key={u.id} className="transition-colors" style={{ borderBottom: "1px solid #f0e8e0", backgroundColor: "#fff" }}
                onMouseEnter={e => (e.currentTarget.style.backgroundColor = "#fdf9f6")}
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
                        style={ROL_COLOR[r] ?? { backgroundColor: "#e8ddd5", color: "#6b5a4e" }}>
                        {r} ✕
                      </span>
                    ))}
                    <select onChange={(e) => { if (e.target.value) { asignar({ id: u.id, rol: e.target.value }); e.target.value = ""; } }}
                      className="text-xs rounded-full px-2 py-0.5 cursor-pointer focus:outline-none"
                      style={{ border: "1px dashed #d6c9be", color: "#9a8070", backgroundColor: "#fff" }}>
                      <option value="">+ rol</option>
                      {ROLES.filter((r) => !u.roles.includes(r)).map((r) => <option key={r} value={r}>{r}</option>)}
                    </select>
                  </div>
                </td>
                <td className="px-5 py-4">
                  {confirmarId === u.id ? (
                    <div className="flex gap-2">
                      <button onClick={() => { eliminar(u.id); setConfirmarId(null); }} className="text-xs px-3 py-1 rounded-lg text-white" style={{ backgroundColor: "#dc2626" }}>Confirmar</button>
                      <button onClick={() => setConfirmarId(null)} className="text-xs px-3 py-1 rounded-lg" style={{ border: "1px solid #d6c9be", color: "#6b5a4e" }}>Cancelar</button>
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
            <p className="text-3xl mb-2">👥</p>
            <p>No hay usuarios activos</p>
          </div>
        )}
      </div>

      {eliminados.length > 0 && (
        <div className="mt-6">
          <h2 className="text-sm font-bold uppercase tracking-wider mb-3" style={{ color: "#9a8070" }}>Eliminados ({eliminados.length})</h2>
          <div className="space-y-2">
            {eliminados.map((u) => (
              <div key={u.id} className="flex justify-between items-center rounded-xl px-4 py-3 opacity-60" style={{ backgroundColor: "#fdf9f6" }}>
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