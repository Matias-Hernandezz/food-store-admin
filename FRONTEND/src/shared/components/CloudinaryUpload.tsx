import { useState, useRef } from "react";
import { uploadApi, type CloudinaryResponse } from "../api/uploadApi";

/** Aplica transformaciones Cloudinary on-the-fly a la URL */
function transformedUrl(url: string, w = 200, h = 200): string {
    if (!url.includes("cloudinary.com")) return url;
    return url.replace("/upload/", `/upload/c_fill,w_${w},h_${h},g_auto,q_auto,f_auto/`);
}

/** Extrae el public_id de una URL de Cloudinary */
function extractPublicId(url: string): string | null {
    const match = url.match(/\/upload\/(?:v\d+\/)?(.+?)\.\w+$/);
    return match ? match[1] : null;
}

interface CloudinaryUploadProps {
    /** URLs actuales de imágenes (para edición) */
    images: string[];
    /** Callback cuando cambia la lista de imágenes (secure_urls) */
    onChange: (urls: string[]) => void;
    /** Máximo de imágenes permitidas */
    max?: number;
    /** Carpeta en Cloudinary */
    folder?: string;
    /** Texto del label */
    label?: string;
}

export function CloudinaryUpload({
    images,
    onChange,
    max = 5,
    folder = "foodstore",
    label = "Imágenes",
}: CloudinaryUploadProps) {
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [urlInput, setUrlInput] = useState("");
    const [showUrlInput, setShowUrlInput] = useState(false);
    const [deletingUrl, setDeletingUrl] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleAddUrl = () => {
        const url = urlInput.trim();
        if (!url) return;
        if (!url.includes("cloudinary.com")) {
            setError("Pegá una URL válida de Cloudinary (res.cloudinary.com)");
            return;
        }
        if (images.length >= max) {
            setError(`Máximo ${max} imágenes`);
            return;
        }
        onChange([...images, url]);
        setUrlInput("");
        setError(null);
    };

    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (!files || files.length === 0) return;

        setError(null);
        setUploading(true);

        try {
            const results: CloudinaryResponse[] = [];
            for (const file of Array.from(files)) {
                if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
                    setError(`Formato no soportado: ${file.name}. Usá JPEG, PNG o WebP.`);
                    continue;
                }
                if (file.size > 5 * 1024 * 1024) {
                    setError(`Imagen muy grande: ${file.name}. Máximo 5 MB.`);
                    continue;
                }
                const result = await uploadApi.upload(file, folder);
                results.push(result);
            }

            if (results.length > 0) {
                const newUrls = results.map((r) => r.secure_url);
                const updated = [...images, ...newUrls].slice(0, max);
                onChange(updated);
            }
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : "Error al subir imagen");
        } finally {
            setUploading(false);
            if (fileInputRef.current) fileInputRef.current.value = "";
        }
    };

    /** Solo quita la URL del array local — no borra de Cloudinary */
    const handleRemove = (url: string) => {
        onChange(images.filter((u) => u !== url));
    };

    /** Borra la imagen de Cloudinary y la quita del array local (rúbrica 10.2) */
    const handleDeleteFromCloudinary = async (url: string) => {
        const publicId = extractPublicId(url);
        setDeletingUrl(url);

        if (publicId) {
            try {
                await uploadApi.delete(publicId);
            } catch {
                setError("No se pudo eliminar la imagen de Cloudinary");
            }
        }

        setDeletingUrl(null);
        onChange(images.filter((u) => u !== url));
    };

    return (
        <div className="flex flex-col gap-2">
            <label className="text-xs font-semibold uppercase tracking-wider" style={{ color: "#9a8070" }}>
                {label}
                {images.length > 0 && (
                    <span className="ml-2 normal-case font-normal" style={{ color: "#C87A2E" }}>
                        {images.length} de {max}
                    </span>
                )}
            </label>

            {/* Previsualización de imágenes subidas */}
            {images.length > 0 && (
                <div className="flex flex-wrap gap-2 p-3 rounded-lg" style={{ backgroundColor: "#F2E8D5", border: "1px solid #E5E2DA" }}>
                    {images.map((url, idx) => (
                        <div key={`${url}-${idx}`} className="relative group w-20 h-20 rounded-lg overflow-hidden" style={{ border: "1px solid #E5E2DA" }}>
                            <img src={transformedUrl(url)} alt="" className="w-full h-full object-cover" />
                            {/* Overlay con botones que aparece al hacer hover */}
                            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-all flex flex-col items-end justify-between p-1 opacity-0 group-hover:opacity-100">
                                {/* ✕ Quitar del array */}
                                <button
                                    type="button"
                                    onClick={() => handleRemove(url)}
                                    className="w-5 h-5 bg-gray-500 text-white rounded-full text-xs flex items-center justify-center hover:bg-gray-600"
                                    title="Quitar del formulario"
                                >
                                    ✕
                                </button>
                                {/* 🗑 Eliminar de Cloudinary */}
                                <button
                                    type="button"
                                    onClick={() => handleDeleteFromCloudinary(url)}
                                    disabled={deletingUrl === url}
                                    className="w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center hover:bg-red-600 disabled:opacity-50"
                                    title="Eliminar de Cloudinary"
                                >
                                    {deletingUrl === url ? (
                                        <div className="w-3 h-3 border border-t-transparent rounded-full animate-spin" style={{ borderBottomColor: "#fff", borderLeftColor: "#fff", borderRightColor: "#fff" }} />
                                    ) : (
                                        "🗑"
                                    )}
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Botón de upload */}
            {images.length < max && (
                <div className="flex flex-col gap-2">
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/jpeg,image/png,image/webp"
                        multiple
                        onChange={handleFileSelect}
                        className="hidden"
                        id="cloudinary-upload-input"
                    />
                    <label
                        htmlFor="cloudinary-upload-input"
                        className="inline-flex items-center gap-2 px-4 py-3 rounded-lg cursor-pointer transition-colors text-sm font-medium"
                        style={{
                            backgroundColor: uploading ? "#E5E2DA" : "#fff",
                            border: "2px dashed #E5E2DA",
                            color: uploading ? "#9a8070" : "#C87A2E",
                            pointerEvents: uploading ? "none" : "auto",
                        }}
                    >
                        {uploading ? (
                            <>
                                <div className="w-4 h-4 border-2 border-t-transparent rounded-full animate-spin" style={{ borderColor: "#9a8070", borderTopColor: "transparent" }} />
                                Subiendo...
                            </>
                        ) : (
                            <>
                                <span>📷</span>
                                Subir imagen{max > 1 ? "es" : ""}
                            </>
                        )}
                    </label>

                    {/* ── Pegar URL ─────────────────────────────────── */}
                    {!showUrlInput ? (
                        <button
                            type="button"
                            onClick={() => setShowUrlInput(true)}
                            className="text-xs underline self-start"
                            style={{ color: "#9a8070" }}
                        >
                            o pegar link de Cloudinary
                        </button>
                    ) : (
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={urlInput}
                                onChange={(e) => setUrlInput(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && handleAddUrl()}
                                placeholder="https://res.cloudinary.com/..."
                                className="flex-1 rounded-lg px-3 py-2 text-xs outline-none"
                                style={{ border: "1px solid #E5E2DA", color: "#2d1e0f" }}
                            />
                            <button
                                type="button"
                                onClick={handleAddUrl}
                                className="text-xs font-bold px-3 py-2 rounded-lg text-white"
                                style={{ backgroundColor: "#C87A2E" }}
                            >
                                Agregar
                            </button>
                            <button
                                type="button"
                                onClick={() => { setShowUrlInput(false); setUrlInput(""); }}
                                className="text-xs px-2"
                                style={{ color: "#9a8070" }}
                            >
                                ✕
                            </button>
                        </div>
                    )}
                </div>
            )}

            {error && (
                <p className="text-xs" style={{ color: "#dc2626" }}>
                    {error}
                </p>
            )}
        </div>
    );
}
