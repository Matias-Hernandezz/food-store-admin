import { useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useAuthStore } from "./store/authStore";
import { useUIStore } from "./store/uiStore";
import { ProtectedRoute } from "./features/auth/components/ProtectedRoute";
import { AdminLayout } from "./shared/components/AdminLayout";
import { CategoriasPage } from "./features/categoria/pages/CategoriasPage";
import { ProductosPage } from "./features/producto/pages/ProductosPage";
import { IngredientesPage } from "./features/ingrediente/pages/IngredientesPage";
import { UsuariosPage } from "./features/usuarios/pages/UsuariosPage";
import { PedidosKanbanPage } from "./features/pedidos/pages/PedidosKanbanPage";
import { LoginPage } from "./features/auth/pages/LoginPage";
import { UnauthorizedPage } from "./features/auth/pages/UnauthorizedPage";
import { DashboardPage } from "./features/panel/pages/DashboardPage";
import { EstadisticasPage } from "./features/pedidos/pages/EstadisticasPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 30,
      retry: 1,
    },
  },
});

function AuthGate({ children }: { children: React.ReactNode }) {
  const fetchUser = useAuthStore((s) => s.fetchUser);
  const isLoading = useAuthStore((s) => s.isLoading);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: "#f5ede6" }}>
        <div className="w-8 h-8 border-2 border-[#c8722a] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return <>{children}</>;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthGate>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />
            <Route path="/" element={<Navigate to="/admin/panel" replace />} />
            <Route
              path="/admin/*"
              element={
                <ProtectedRoute roles={["ADMIN", "PEDIDOS", "STOCK"]}>
                  <AdminLayout>
                    <Routes>
                      <Route path="categorias" element={<CategoriasPage />} />
                      <Route path="productos" element={<ProductosPage />} />
                      <Route path="ingredientes" element={<IngredientesPage />} />
                      <Route path="usuarios" element={<UsuariosPage />} />
                      <Route path="pedidos" element={<PedidosKanbanPage />} />
                      <Route path="cocina" element={<Navigate to="/admin/pedidos" replace />} />
                      <Route path="panel" element={<DashboardPage />} />
                      <Route path="estadisticas" element={<EstadisticasPage />} />
                    </Routes>
                  </AdminLayout>
                </ProtectedRoute>
}

function ToastContainer() {
  const toasts = useUIStore((s) => s.toasts);
  const removeToast = useUIStore((s) => s.removeToast);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-6 right-6 z-[9999] flex flex-col gap-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          onClick={() => removeToast(t.id)}
          className={`px-4 py-3 rounded-xl shadow-lg text-sm font-bold cursor-pointer animate-[slideIn_0.3s_ease] max-w-xs ${
            t.type === "success"
              ? "bg-[#c8722a] text-white"
              : t.type === "error"
              ? "bg-red-600 text-white"
              : "bg-gray-800 text-white"
          }`}
        >
          {t.message}
        </div>
      ))}
      <style>{`
        @keyframes slideIn {
          from { opacity: 0; transform: translateX(100px); }
          to { opacity: 1; transform: translateX(0); }
        }
      `}</style>
    </div>
  );
}
            />
          </Routes>
        </BrowserRouter>
      </AuthGate>
      <ToastContainer />
    </QueryClientProvider>
  );
}
