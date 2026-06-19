import { useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useAuthStore } from "./store/authStore";
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
            />
          </Routes>
        </BrowserRouter>
      </AuthGate>
    </QueryClientProvider>
  );
}
