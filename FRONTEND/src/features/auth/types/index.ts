// features/auth/types/index.ts
export interface LoginInput {
    email: string;
    password: string;
}

export interface UsuarioCreate {
    nombre: string;
    apellido: string;
    email: string;
    celular?: string;
    password: string;
}

export interface UsuarioRead {
    id: number;
    nombre: string;
    apellido: string;
    email: string;
    celular: string | null;
    roles: string[];
    deleted_at: string | null;
}