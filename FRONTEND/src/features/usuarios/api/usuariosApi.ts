import api from "../../../shared/api/axiosClient";

const BASE = "/api/v1/usuarios";

export interface UsuarioAdmin {
    id: number;
    nombre: string;
    apellido: string;
    email: string;
    celular: string | null;
    roles: string[];
    deleted_at: string | null;
}

export const usuariosApi = {
    getAll: (search?: string) => {
        const params = new URLSearchParams();
        if (search) params.set("search", search);
        const qs = params.toString();
        return api.get<UsuarioAdmin[]>(`${BASE}${qs ? `?${qs}` : ""}`).then((r) => r.data);
    },

    asignarRol: (id: number, rol_codigo: string) =>
        api.post<UsuarioAdmin>(`${BASE}/${id}/roles`, { rol_codigo }).then((r) => r.data),

    quitarRol: (id: number, rol_codigo: string) =>
        api.delete(`${BASE}/${id}/roles/${rol_codigo}`),

    softDelete: (id: number) =>
        api.delete(`${BASE}/${id}`),
};
