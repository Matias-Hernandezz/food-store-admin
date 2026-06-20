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
let isRefreshing = false;
let failedQueue: Array<{
    resolve: (token: string) => void;
    reject: (err: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null) {
    failedQueue.forEach(({ resolve, reject }) => {
        if (error) reject(error);
        else resolve(token!);
    });
    failedQueue = [];
}

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Solo reintentar 401 una vez y solo si no es el endpoint de refresh/login
        if (
            error.response?.status === 401 &&
            !originalRequest._retry &&
            !originalRequest.url?.includes("/auth/refresh") &&
            !originalRequest.url?.includes("/auth/login")
        ) {
            // Si ya hay un refresh en curso, encolar esta request
            if (isRefreshing) {
                return new Promise<string>((resolve, reject) => {
                    failedQueue.push({ resolve, reject });
                }).then((token) => {
                    originalRequest.headers.Authorization = `Bearer ${token}`;
                    return api(originalRequest);
                });
            }

            originalRequest._retry = true;
            isRefreshing = true;

            try {
                const newToken = await useAuthStore.getState().refreshToken();
                processQueue(null, newToken);
                originalRequest.headers.Authorization = `Bearer ${newToken}`;
                return api(originalRequest);
            } catch (refreshError) {
                processQueue(refreshError, null);
                useAuthStore.getState().logout();
                if (window.location.pathname !== "/login") {
                    window.location.href = "/login";
                }
                return Promise.reject(refreshError);
            } finally {
                isRefreshing = false;
            }
        }

        return Promise.reject(error);
    }
);

export default api;
export { API_BASE_URL };
