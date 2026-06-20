import { type ReactNode, useState, useRef, useEffect } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useRole } from "../../features/usuarios/hooks/useRole";
import { useAuthStore } from "../../store/authStore";
import { useAdminOrdersFeed } from "../hooks/useAdminOrdersFeed";
import { Icons } from "./ui/Icons";
import { ConnectionBadge } from "./ConnectionBadge";

const PANEL_ITEMS = [
  { to: "/admin/panel",   label: "Panel",    icon: <Icons.Dashboard width={18} height={18} />, required: ["ADMIN", "PEDIDOS"] },
  { to: "/admin/usuarios", label: "Usuarios", icon: <Icons.Usuarios width={18} height={18} />, required: ["ADMIN"] },
];

const NAV_ITEMS: { to: string; label: string; icon: ReactNode; required: string[] }[] = [
  { to: "/admin/pedidos",     label: "Pedidos",      icon: <Icons.Pedidos width={18} height={18} />, required: ["ADMIN", "PEDIDOS"] },
];

const CATALOGO_ITEMS: { to: string; label: string; icon: ReactNode; required: string[] }[] = [
  { to: "/admin/categorias",  label: "Categorías",    icon: <Icons.Categoria width={18} height={18} />, required: ["ADMIN", "STOCK"] },
  { to: "/admin/productos",   label: "Productos",     icon: <Icons.Producto width={18} height={18} />, required: ["ADMIN", "STOCK"] },
  { to: "/admin/ingredientes", label: "Ingredientes", icon: <Icons.Ingrediente width={18} height={18} />, required: ["ADMIN", "STOCK"] },
];

const navLinkStyle = (isActive: boolean) =>
  isActive
    ? { backgroundColor: "rgba(249,115,22,0.15)", color: "#f97316", border: "1px solid rgba(249,115,22,0.25)", borderRadius: 8, padding: "10px 12px", fontSize: 14, fontWeight: 600, display: "flex", alignItems: "center", gap: 12, transition: "all .15s" }
    : { color: "#888", border: "1px solid transparent", borderRadius: 8, padding: "10px 12px", fontSize: 14, fontWeight: 500, display: "flex", alignItems: "center", gap: 12, transition: "all .15s" };

export function AdminLayout({ children }: { children: ReactNode }) {
  const { hasRole, isAdmin } = useRole();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();
  const [profileOpen, setProfileOpen] = useState(false);
  const profileRef = useRef<HTMLDivElement>(null);

  // WebSocket — conecta en todas las páginas del admin
  useAdminOrdersFeed();

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) {
        setProfileOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const topItems = PANEL_ITEMS.filter((item) =>
    isAdmin || item.required.some((role) => hasRole(role))
  );
  const visibleItems = NAV_ITEMS.filter((item) =>
    isAdmin || item.required.some((role) => hasRole(role))
  );
  const catalogoItems = CATALOGO_ITEMS.filter((item) =>
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
          {/* ── Panel + Usuarios arriba ────────────────────────────── */}
          {topItems.map((item) => (
            <NavLink key={item.to} to={item.to} style={({ isActive }) => navLinkStyle(isActive)}>
              <span>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
          <div className="my-2" style={{ borderTop: "1px solid #2a2a2a" }} />

          {/* ── Resto de items ────────────────────────────────────── */}
          {visibleItems.map((item) => (
            <NavLink key={item.to} to={item.to} style={({ isActive }) => navLinkStyle(isActive)}>
              <span>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
          <div className="my-2" style={{ borderTop: "1px solid #2a2a2a" }} />

          {/* ── Catálogo ──────────────────────────────────────────── */}
          {catalogoItems.map((item) => (
            <NavLink key={item.to} to={item.to} style={({ isActive }) => navLinkStyle(isActive)}>
              <span>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        {/* ── Perfil de usuario (clickeable) ──────────────────────── */}
        <div className="relative" ref={profileRef}>
          {/* Popover — arriba del botón */}
          {profileOpen && (
            <div
              className="absolute bottom-full left-0 right-0 mb-2 mx-2 rounded-xl p-4 z-50"
              style={{
                backgroundColor: "#222",
                border: "1px solid #333",
                boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
              }}
            >
              <div className="flex items-center gap-3 mb-3">
                <div
                  className="w-11 h-11 rounded-full flex items-center justify-center text-base font-bold shrink-0"
                  style={{ backgroundColor: "rgba(249,115,22,0.2)", color: "#f97316" }}
                >
                  {user?.nombre?.charAt(0)?.toUpperCase() ?? "A"}
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold truncate" style={{ color: "#f1f1f1" }}>
                    {user?.nombre ?? "Admin"} {user?.apellido ?? ""}
                  </p>
                  <p className="text-xs truncate" style={{ color: "#666" }}>
                    {user?.email ?? ""}
                  </p>
                </div>
              </div>

              {/* Roles */}
              <div className="flex flex-wrap gap-1.5 mb-3">
                {(user?.roles ?? []).map((rol) => (
                  <span
                    key={rol}
                    className="text-[10px] font-bold uppercase px-2 py-0.5 rounded"
                    style={{
                      backgroundColor: rol === "ADMIN" ? "rgba(249,115,22,0.15)" : "rgba(255,255,255,0.06)",
                      color: rol === "ADMIN" ? "#f97316" : "#888",
                    }}
                  >
                    {rol}
                  </span>
                ))}
              </div>

              <button
                onClick={async () => { await logout(); navigate("/login"); }}
                className="w-full text-left text-xs flex items-center gap-2 px-3 py-2 rounded-lg transition-colors"
                style={{ color: "#888", backgroundColor: "rgba(255,255,255,0.04)" }}
                onMouseEnter={(e) => { e.currentTarget.style.color = "#ef4444"; e.currentTarget.style.backgroundColor = "rgba(239,68,68,0.08)"; }}
                onMouseLeave={(e) => { e.currentTarget.style.color = "#888"; e.currentTarget.style.backgroundColor = "rgba(255,255,255,0.04)"; }}
              >
                <Icons.Logout width={16} height={16} />
                Cerrar Sesión
              </button>
            </div>
          )}

          {/* Botón de perfil — siempre visible */}
          <button
            onClick={() => setProfileOpen((p) => !p)}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors"
            style={{
              backgroundColor: profileOpen ? "rgba(255,255,255,0.06)" : "transparent",
              borderTop: "1px solid #2a2a2a",
            }}
            onMouseEnter={(e) => { if (!profileOpen) e.currentTarget.style.backgroundColor = "rgba(255,255,255,0.04)"; }}
            onMouseLeave={(e) => { if (!profileOpen) e.currentTarget.style.backgroundColor = "transparent"; }}
          >
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shrink-0"
              style={{ backgroundColor: "rgba(249,115,22,0.2)", color: "#f97316" }}
            >
              {user?.nombre?.charAt(0)?.toUpperCase() ?? "A"}
            </div>
            <div className="flex-1 min-w-0 text-left">
              <p className="text-sm font-medium truncate" style={{ color: "#e0e0e0" }}>
                {user?.nombre ?? "Admin"}
              </p>
              <p className="text-[10px] truncate uppercase tracking-wider" style={{ color: "#555" }}>
                {user?.roles?.[0] ?? ""}
              </p>
            </div>
            <Icons.ExpandLess
              width={16}
              height={16}
              style={{ color: "#555", transform: profileOpen ? "rotate(180deg)" : "rotate(0deg)", transition: "transform .2s" }}
            />
          </button>
        </div>
        <div className="px-5 py-3 flex items-center justify-between" style={{ borderTop: "1px solid #2a2a2a" }}>
          <p className="text-xs" style={{ color: "#444" }}>v1.0.0</p>
          <ConnectionBadge />
        </div>
      </aside>
      <main className="flex-1 p-8 overflow-auto" style={{ backgroundColor: "#f5ede6" }}>
        {children}
      </main>
    </div>
  );
}