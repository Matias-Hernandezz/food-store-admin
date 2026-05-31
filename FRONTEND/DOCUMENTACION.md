## DOCUMENTACIÓN DEL FRONTEND - ADMIN PANEL

### RESUMEN EJECUTIVO

Se desarrolló un **Admin Panel** completo en **React + TypeScript + Tailwind CSS 4** que consume los endpoints de la API del backend FastAPI. La aplicación implementa:

- ✅ **3 módulos principales**: Categorías, Ingredientes y Productos
- ✅ **CRUD completo** para cada módulo (Crear, Leer, Actualizar, Eliminar)
- ✅ **React Router** con navegación entre módulos
- ✅ **TanStack Query** para manejo de estado del servidor
- ✅ **Componentes reutilizables** con TypeScript tipado
- ✅ **Interfaz limpia y funcional** con Tailwind CSS

---

## ARQUITECTURA Y ESTRUCTURA DEL PROYECTO

### Carpetas Principales

```
src/
├── types/                 # Tipado TypeScript
│   └── index.ts          # Interfaces de Categoría, Ingrediente, Producto
├── services/              # Configuración de API
│   └── api.ts            # Cliente Axios configurado
├── hooks/                 # React Hooks personalizados
│   ├── useCategorias.ts
│   ├── useIngredientes.ts
│   ├── useProductos.ts
│   └── index.ts          # Exportaciones
├── components/            # Componentes reutilizables
│   ├── Modal.tsx         # Modal genérico
│   ├── StateComponents.tsx # Loading, Error, Empty
│   └── index.ts          # Exportaciones
├── pages/                 # Páginas principales
│   ├── CategoriasPage.tsx
│   ├── IngredientesPage.tsx
│   ├── ProductosPage.tsx
├── App.tsx               # Router y Provider principal
├── main.tsx              # Punto de entrada
└── index.css             # Estilos Tailwind
```

---

## 1. TIPADO - TypeScript (/src/types/index.ts)

Todas las entidades están correctamente tipadas:

```typescript
export interface Categoria {
  id: number
  parent_id?: number | null
  nombre: string
  descripcion?: string | null
  imagen_url?: string | null
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

export interface CategoriaCreate {
  parent_id?: number | null
  nombre: string
  descripcion?: string | null
  imagen_url?: string | null
}

export interface CategoriaUpdate {
  parent_id?: number | null
  nombre?: string
  descripcion?: string | null
  imagen_url?: string | null
}
```

**Ventajas:**
- Autocompletado en IDE
- Detección de errores en tiempo de compilación
- Documentación automática de la forma de los datos

---

## 2. CLIENTE HTTP - AXIOS (/src/services/api.ts)

Configuración centralizada del cliente HTTP:

```typescript
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para manejo de errores
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)
```

**Beneficios:**
- Configuración única para toda la aplicación
- Fácil de cambiar la URL base
- Manejo centralizado de errores

---

## 3. HOOKS PERSONALIZADOS - TanStack Query (/src/hooks/useCategorias.ts)

Implementación de **useQuery** y **useMutation** para sincronización con servidor:

```typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../services/api'
import { Categoria, CategoriaCreate, CategoriaUpdate } from '../types'

// LECTURA - Obtener todas las categorías
export const useCategorias = (offset = 0, limit = 20) => {
  return useQuery({
    queryKey: ['categorias', offset, limit],
    queryFn: async () => {
      const response = await apiClient.get('/categorias', {
        params: { offset, limit },
      })
      return response.data.data as Categoria[]
    },
  })
}

// CREACIÓN - Crear nueva categoría
export const useCreateCategoria = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: CategoriaCreate) => {
      const response = await apiClient.post('/categorias', data)
      return response.data as Categoria
    },
    onSuccess: () => {
      // Invalida el cache para refrescar automáticamente la lista
      queryClient.invalidateQueries({ queryKey: ['categorias'] })
    },
  })
}

// ACTUALIZACIÓN - Editar categoría existente
export const useUpdateCategoria = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: CategoriaUpdate }) => {
      const response = await apiClient.patch(\`/categorias/\${id}\`, data)
      return response.data as Categoria
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categorias'] })
    },
  })
}

// ELIMINACIÓN - Borrar categoría
export const useDeleteCategoria = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(\`/categorias/\${id}\`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categorias'] })
    },
  })
}
```

### Cómo funciona TanStack Query:

**useQuery:**
- ✅ Maneja el estado de carga (isLoading)
- ✅ Cachea automáticamente los datos
- ✅ Refetch automático si expira el cache
- ✅ Estados de error (error)

**useMutation:**
- ✅ Envía datos al servidor
- ✅ Ejecuta callbacks (onSuccess)
- ✅ invalidateQueries refresca la UI automáticamente
- ✅ Estados de carga durante la petición (isPending)

---

## 4. COMPONENTES REUTILIZABLES

### Modal Component (/src/components/Modal.tsx)

```typescript
interface ModalProps {
  isOpen: boolean
  title: string
  onClose: () => void
  children: React.ReactNode
}

export const Modal: React.FC<ModalProps> = ({ isOpen, title, onClose, children }) => {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg max-w-md w-full mx-4">
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-lg font-semibold">{title}</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-2xl">×</button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  )
}
```

**Uso en componentes:**
- Props totalmente tipadas con TypeScript
- Reutilizable para cualquier contenido
- Cerrable con X o función onClose()

### State Components (/src/components/StateComponents.tsx)

```typescript
export const Loading = () => (
  <div className="flex items-center justify-center p-8">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    <span className="ml-3 text-gray-600">Cargando...</span>
  </div>
)

export const Error: React.FC<ErrorProps> = ({ message = 'Ha ocurrido un error', onRetry }) => (
  <div className="bg-red-50 border border-red-200 rounded p-4 mb-4">
    <p className="text-red-800 font-semibold">{message}</p>
    {onRetry && (
      <button onClick={onRetry} className="mt-2 px-4 py-2 bg-red-600 text-white rounded">
        Reintentar
      </button>
    )}
  </div>
)

export const Empty = ({ message = 'No hay datos' }: { message?: string }) => (
  <div className="text-center py-8">
    <p className="text-gray-500">{message}</p>
  </div>
)
```

**Ventajas:**
- Feedback visual en cada estado
- Consistent UX en toda la app
- Reutilizable en cualquier page

---

## 5. PÁGINAS - CRUD COMPLETO

### CategoriasPage (/src/pages/CategoriasPage.tsx) - Estructura de un Módulo

Cada módulo sigue el mismo patrón:

```typescript
import { useState } from 'react'
import { useCategorias, useCreateCategoria, useUpdateCategoria, useDeleteCategoria } from '../hooks/useCategorias'
import { Modal } from '../components/Modal'
import { Loading, Error, Empty } from '../components/StateComponents'
import { CategoriaCreate, CategoriaUpdate, Categoria } from '../types'

export const CategoriasPage: React.FC = () => {
  // 1. ESTADO LOCAL
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState<CategoriaCreate>({
    nombre: '',
    descripcion: '',
    imagen_url: '',
  })

  // 2. QUERIES Y MUTATIONS (TanStack Query)
  const { data: categorias = [], isLoading, error } = useCategorias()
  const createMutation = useCreateCategoria()
  const updateMutation = useUpdateCategoria()
  const deleteMutation = useDeleteCategoria()

  // 3. MANEJADORES
  const handleOpenModal = (categoria?: Categoria) => {
    if (categoria) {
      // Modo edición: carga los datos existentes
      setEditingId(categoria.id)
      setFormData({
        nombre: categoria.nombre,
        descripcion: categoria.descripcion || '',
        imagen_url: categoria.imagen_url || '',
      })
    } else {
      // Modo creación: vacía el formulario
      setEditingId(null)
      setFormData({
        nombre: '',
        descripcion: '',
        imagen_url: '',
      })
    }
    setIsModalOpen(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editingId) {
        // UPDATE
        await updateMutation.mutateAsync({ id: editingId, data: formData })
      } else {
        // CREATE
        await createMutation.mutateAsync(formData)
      }
      handleCloseModal()
    } catch (err) {
      console.error('Error:', err)
    }
  }

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Estás seguro?')) {
      try {
        // DELETE
        await deleteMutation.mutateAsync(id)
      } catch (err) {
        console.error('Error:', err)
      }
    }
  }

  return (
    <div className="p-6">
      {/* ENCABEZADO */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Categorías</h1>
        <button onClick={() => handleOpenModal()} className="px-4 py-2 bg-blue-600 text-white rounded">
          + Nueva Categoría
        </button>
      </div>

      {/* ESTADOS DE CARGA */}
      {isLoading && <Loading />}
      {error && <Error message="Error al cargar categorías" />}
      {!isLoading && categorias.length === 0 && <Empty message="No hay categorías" />}

      {/* TABLA */}
      {!isLoading && categorias.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse border border-gray-300">
            <thead className="bg-gray-100">
              <tr>
                <th className="border border-gray-300 px-4 py-2 text-left">ID</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Nombre</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Descripción</th>
                <th className="border border-gray-300 px-4 py-2 text-center">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {categorias.map((cat) => (
                <tr key={cat.id} className="hover:bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2">{cat.id}</td>
                  <td className="border border-gray-300 px-4 py-2">{cat.nombre}</td>
                  <td className="border border-gray-300 px-4 py-2">{cat.descripcion}</td>
                  <td className="border border-gray-300 px-4 py-2 text-center space-x-2">
                    <button onClick={() => handleOpenModal(cat)} className="px-3 py-1 bg-yellow-500 text-white rounded">
                      Editar
                    </button>
                    <button onClick={() => handleDelete(cat.id)} className="px-3 py-1 bg-red-600 text-white rounded">
                      Eliminar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* MODAL CON FORMULARIO */}
      <Modal isOpen={isModalOpen} title={editingId ? 'Editar Categoría' : 'Nueva Categoría'} onClose={handleCloseModal}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-1">Nombre</label>
            <input
              type="text"
              value={formData.nombre}
              onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              className="w-full border border-gray-300 rounded px-3 py-2"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-1">Descripción</label>
            <textarea
              value={formData.descripcion || ''}
              onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
              className="w-full border border-gray-300 rounded px-3 py-2"
              rows={3}
            />
          </div>
          <div className="flex gap-2 pt-4">
            <button type="submit" disabled={createMutation.isPending} className="flex-1 px-4 py-2 bg-blue-600 text-white rounded">
              Guardar
            </button>
            <button type="button" onClick={handleCloseModal} className="flex-1 px-4 py-2 bg-gray-300 text-gray-800 rounded">
              Cancelar
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
```

---

## 6. ROUTER Y PROVIDER PRINCIPAL (/src/App.tsx)

```typescript
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import { CategoriasPage } from './pages/CategoriasPage'
import { IngredientesPage } from './pages/IngredientesPage'
import { ProductosPage } from './pages/ProductosPage'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          {/* NAVIGATION BAR */}
          <nav className="bg-white shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center h-16">
                <h1 className="text-2xl font-bold text-blue-600">Admin Panel</h1>
                <div className="flex gap-8">
                  <Link to="/categorias" className="px-3 py-2 text-gray-700 hover:text-blue-600">
                    Categorías
                  </Link>
                  <Link to="/ingredientes" className="px-3 py-2 text-gray-700 hover:text-blue-600">
                    Ingredientes
                  </Link>
                  <Link to="/productos" className="px-3 py-2 text-gray-700 hover:text-blue-600">
                    Productos
                  </Link>
                </div>
              </div>
            </div>
          </nav>

          {/* ROUTES */}
          <main className="max-w-7xl mx-auto">
            <Routes>
              <Route path="/categorias" element={<CategoriasPage />} />
              <Route path="/ingredientes" element={<IngredientesPage />} />
              <Route path="/productos" element={<ProductosPage />} />
              <Route path="/" element={<CategoriasPage />} />
            </Routes>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  )
}
```

**Estructura:**
1. **QueryClientProvider** - Envuelve toda la app para TanStack Query
2. **BrowserRouter** - Habilita routing en la app
3. **Navigation** - Links a los diferentes módulos
4. **Routes** - Define qué componente renderizar en cada ruta

---

## 7. ESTILOS - TAILWIND CSS

Tailwind CSS 4 proporciona estilos utilitarios directamente en JSX:

```jsx
// Ejemplo de clases Tailwind usadas
<button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
  Guardar
</button>

/* Clases utilizadas:
- px-4 py-2: Padding horizontal y vertical
- bg-blue-600: Fondo azul
- text-white: Texto blanco
- rounded: Bordes redondeados
- hover:bg-blue-700: Cambio de color al pasar mouse
*/
```

**Ventajas de Tailwind:**
- ✅ No escribir CSS custom
- ✅ Consistencia visual automática
- ✅ Responsive built-in
- ✅ Rápido de prototipar

---

## 8. FLUJO DE DATOS - EJEMPLO COMPLETO

### Crear una nueva Categoría:

```
1. Usuario hace click en "+ Nueva Categoría"
   ↓
2. handleOpenModal() abre el modal vacío
   ↓
3. Usuario completa el formulario
   ↓
4. Usuario hace click en "Guardar"
   ↓
5. handleSubmit() ejecuta createMutation.mutateAsync(formData)
   ↓
6. API Client (axios) envía POST /categorias con los datos
   ↓
7. Backend valida y guarda en BD
   ↓
8. onSuccess callback en el mutation invalida el cache
   ↓
9. TanStack Query detecta que el cache expiró
   ↓
10. useQuery ejecuta nuevamente queryFn y trae datos actualizados
    ↓
11. Componente re-renderiza con la nueva categoría en la tabla
    ↓
12. Modal se cierra automáticamente
```

---

## 9. MANEJO DE ERRORES Y ESTADOS DE CARGA

### Estados en Tiempo Real:

```typescript
// isLoading: Mientras se obtienen datos
{isLoading && <Loading />}

// error: Si la petición falla
{error && <Error message="Error al cargar categorías" />}

// empty: Si no hay datos
{!isLoading && categorias.length === 0 && <Empty />}

// isPending: Mientras se envía formulario
<button disabled={createMutation.isPending}>
  {createMutation.isPending ? 'Guardando...' : 'Guardar'}
</button>
```

---

## 10. INSTALACIÓN Y EJECUCIÓN

### Dependencias Instaladas:

```bash
npm install react-router-dom @tanstack/react-query axios
npm install -D tailwindcss postcss autoprefixer
```

### Estructura de Configuración:

- **tailwind.config.ts** - Configuración de Tailwind
- **postcss.config.js** - Procesador CSS
- **index.css** - Directivas de Tailwind (@tailwind)

### Para ejecutar:

```bash
npm run dev
# Abre en http://localhost:5173
```

---

## RESUMEN DE TECNOLOGÍAS

| Tecnología | Propósito | Beneficio |
|-----------|----------|----------|
| React 19 | UI Framework | Component-based, fast rendering |
| TypeScript | Tipado estático | Detecta errores en tiempo de compilación |
| React Router | Navegación | Multi-page experience sin recargas |
| TanStack Query | State management del servidor | Caching automático, sincronización |
| Tailwind CSS | Estilos | Utility-first, development rápido |
| Axios | HTTP Client | Interceptors, configuración centralizada |

---

## PUNTOS CLAVE DE LA IMPLEMENTACIÓN

✅ **Separación de responsabilidades**: Hooks, componentes y páginas tienen roles específicos
✅ **TypeScript en todo**: Tipado fuerte desde tipos hasta props
✅ **Reutilización**: Modal, Loading, Error componentes se reutilizan
✅ **Manejo de estado**: TanStack Query maneja server state automáticamente
✅ **UX**: Feedback visual en cada acción (loading, error, success)
✅ **Performance**: Caching automático evita peticiones innecesarias
✅ **Escalabilidad**: Patrón de módulos permite agregar nuevas entidades fácilmente

