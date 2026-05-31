import { type ReactNode } from "react";
import { NavLink } from "react-router-dom";
import { useRole } from "../../features/usuarios/hooks/useRole";
import { Icons } from "./ui/Icons";

const NAV_ITEMS: { to: string; label: string; icon: ReactNode; required: string[] }[] = [
  { to: "/admin/categorias", label: "Categorías", icon: <Icons.Categoria width={18} height={18} />, required: ["ADMIN", "STOCK"] },
  { to: "/admin/productos", label: "Productos", icon: <Icons.Categoria width={18} height={18} />, required: ["ADMIN", "STOCK"] },
  { to: "/admin/ingredientes", label: "Ingredientes", icon: <Icons.Categoria width={18} height={18} />, required: ["ADMIN", "STOCK"] },
  { to: "/admin/usuarios", label: "Usuarios", icon: <Icons.Categoria width={18} height={18} />, required: ["ADMIN"] },
  { to: "/admin/pedidos", label: "Pedidos", icon: <Icons.Categoria width={18} height={18} />, required: ["ADMIN", "PEDIDOS"] },
];

export function AdminLayout({ children }: { children: ReactNode }) {
  const { hasRole, isAdmin } = useRole();

  const visibleItems = NAV_ITEMS.filter((item) =>
    isAdmin || item.required.some((role) => hasRole(role))
  );

  return (
    <div className="min-h-screen flex" style={{ backgroundColor: "#f5ede6" }}>
      <aside className="w-56 flex flex-col shrink-0" style={{ backgroundColor: "#1a1a1a", borderRight: "1px solid #2a2a2a" }}>
        <div className="px-5 py-6" style={{ borderBottom: "1px solid #2a2a2a" }}>
          <p className="text-xs font-bold uppercase tracking-widest" style={{ color: "#f97316" }}>Panel Admin</p>
          <h2 className="text-lg font-bold mt-0.5" style={{ color: "#f1f1f1" }}>Gestión</h2>
        </div>
        <nav className="flex flex-col gap-1 p-3 flex-1">
          {visibleItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              style={({ isActive }) => isActive
                ? { backgroundColor: "rgba(249,115,22,0.15)", color: "#f97316", border: "1px solid rgba(249,115,22,0.25)", borderRadius: 8, padding: "10px 12px", fontSize: 14, fontWeight: 600, display: "flex", alignItems: "center", gap: 12, transition: "all .15s" }
                : { color: "#888", border: "1px solid transparent", borderRadius: 8, padding: "10px 12px", fontSize: 14, fontWeight: 500, display: "flex", alignItems: "center", gap: 12, transition: "all .15s" }
              }
            >
              <span>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="px-5 py-4" style={{ borderTop: "1px solid #2a2a2a" }}>
          <p className="text-xs" style={{ color: "#444" }}>v1.0.0</p>
        </div>
      </aside>
      <main className="flex-1 p-8 overflow-auto" style={{ backgroundColor: "#f5ede6" }}>
        {children}
      </main>
    </div>
  );
}