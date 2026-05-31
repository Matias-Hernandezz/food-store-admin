export interface Categoria {
  id: number;
  parent_id: number | null;
  nombre: string;
  descripcion: string | null;
  imagen_url: string | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface CategoriaCreate {
  parent_id?: number | null;
  nombre: string;
  descripcion?: string | null;
  imagen_url?: string | null;
}

export interface CategoriaUpdate {
  parent_id?: number | null;
  nombre?: string;
  descripcion?: string | null;
  imagen_url?: string | null;
}

export interface CategoriaList {
  data: Categoria[];
  total: number;
}

// ─── INGREDIENTE ─────────────────────────────────────────────────────────────

export interface Ingrediente {
  id: number;
  nombre: string;
  descripcion: string | null;
  es_alergeno: boolean;
  created_at: string;
  updated_at: string;
}

export interface IngredienteCreate {
  nombre: string;
  descripcion?: string | null;
  es_alergeno?: boolean;
}

export interface IngredienteUpdate {
  nombre?: string;
  descripcion?: string | null;
  es_alergeno?: boolean;
}

export interface IngredienteList {
  data: Ingrediente[];
  total: number;
}

// ─── PRODUCTO ────────────────────────────────────────────────────────────────

export interface Producto {
  id: number;
  nombre: string;
  descripcion: string | null;
  precio_base: string;
  imagenes_url: string | null;
  stock_cantidad: number;
  disponible: boolean;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
  categoria_ids: number[];
  ingrediente_ids: number[];
}

export interface ProductoCreate {
  nombre: string;
  descripcion?: string | null;
  precio_base: number;
  imagenes_url?: string | null;
  stock_cantidad?: number;
  disponible?: boolean;
  categoria_ids: number[];
  ingrediente_ids?: number[];
}

export interface ProductoUpdate {
  nombre?: string;
  descripcion?: string | null;
  precio_base?: number;
  imagenes_url?: string | null;
  stock_cantidad?: number;
  disponible?: boolean;
  categoria_ids?: number[];
  ingrediente_ids?: number[];
}

export interface ProductoList {
  data: Producto[];
  total: number;
}

// ─── PAGINACION ───────────────────────────────────────────────────────────────

export interface PaginationParams {
  offset?: number;
  limit?: number;
}
