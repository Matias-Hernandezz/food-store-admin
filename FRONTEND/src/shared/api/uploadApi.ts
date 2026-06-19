import api from "./axiosClient";

export interface CloudinaryResponse {
    secure_url: string;
    public_id: string;
    width: number;
    height: number;
    format: string;
    resource_type: string;
}

const BASE = "/api/v1/uploads";

export const uploadApi = {
    /** Sube una imagen a Cloudinary vía el backend */
    upload: async (file: File, folder: string = "foodstore"): Promise<CloudinaryResponse> => {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("folder", folder);

        const res = await fetch(`${import.meta.env.VITE_API_URL ?? "http://localhost:8000"}${BASE}/imagen`, {
            method: "POST",
            credentials: "include",
            body: formData,
        });

        if (!res.ok) {
            const error = await res.json().catch(() => ({ detail: "Error al subir imagen" }));
            throw new Error(error.detail ?? `Error ${res.status}`);
        }

        return res.json();
    },

    /** Elimina una imagen de Cloudinary por su public_id */
    delete: (publicId: string) =>
        api.delete(`${BASE}/imagen/${encodeURIComponent(publicId)}`),
};
