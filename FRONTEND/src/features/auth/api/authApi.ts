import api from "../../../shared/api/axiosClient";
import type { LoginInput, UsuarioRead, UsuarioCreate } from "../types";

const BASE = "/api/v1/auth";

export const authApi = {
    register: (data: UsuarioCreate) =>
        api.post<UsuarioRead>(`${BASE}/register`, data).then((r) => r.data),

    login: (data: LoginInput) =>
        api.post<UsuarioRead>(`${BASE}/login`, data).then((r) => r.data),

    logout: () =>
        api.post(`${BASE}/logout`),

    me: () =>
        api.get<UsuarioRead>(`${BASE}/me`).then((r) => r.data),

    refresh: () =>
        api.post(`${BASE}/refresh`),
};
