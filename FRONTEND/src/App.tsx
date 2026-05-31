import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./features/auth/context/AuthContext";
import { ProtectedRoute } from "./features/auth/components/ProtectedRoute";
import { AdminLayout } from "./shared/components/AdminLayout";
import { CategoriasPage } from "./features/categoria/pages/CategoriasPage";
import { ProductosPage } from "./features/producto/pages/ProductosPage";
import { IngredientesPage } from "./features/ingrediente/pages/IngredientesPage";
import { UsuariosPage } from "./features/usuarios/pages/UsuariosPage";
import { CajeroPedidosPage } from "./features/pedidos/pages/CajeroPedidosPage";
import { LoginPage } from "./features/auth/pages/LoginPage";
import { UnauthorizedPage } from "./features/auth/pages/UnauthorizedPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 30,
      retry: 1,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />
            <Route path="/" element={<Navigate to="/admin/categorias" replace />} />
            <Route
              path="/admin/*"
              element={
                <ProtectedRoute>
                  <AdminLayout>
                    <Routes>
                      <Route path="categorias" element={<CategoriasPage />} />
                      <Route path="productos" element={<ProductosPage />} />
                      <Route path="ingredientes" element={<IngredientesPage />} />
                      <Route path="usuarios" element={<UsuariosPage />} />
                      <Route path="pedidos" element={<CajeroPedidosPage />} />
                      <Route path="*" element={<Navigate to="categorias" replace />} />
                    </Routes>
                  </AdminLayout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
