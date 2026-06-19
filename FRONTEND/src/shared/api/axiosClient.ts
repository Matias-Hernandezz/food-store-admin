import axios from "axios";
import { useAuthStore } from "../../store/authStore";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
});

// ── Request interceptor: attach Bearer token from authStore ─────────────
api.interceptors.request.use((config) => {
    const token = useAuthStore.getState().accessToken;
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// ── Response interceptor: 401 → refresh token → retry ──────────────────
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Solo reintentar 401 una vez y solo si no es el endpoint de refresh
        if (
            error.response?.status === 401 &&
            !originalRequest._retry &&
            !originalRequest.url?.includes("/auth/refresh") &&
            !originalRequest.url?.includes("/auth/login")
        ) {
            originalRequest._retry = true;

            try {
                const newToken = await useAuthStore.getState().refreshToken();
                originalRequest.headers.Authorization = `Bearer ${newToken}`;
                return api(originalRequest);
            } catch {
                // Refresh falló → logout y redirigir
                useAuthStore.getState().logout();
                if (window.location.pathname !== "/login") {
                    window.location.href = "/login";
                }
                return Promise.reject(error);
            }
        }

        return Promise.reject(error);
    }
);

export default api;
export { API_BASE_URL };
