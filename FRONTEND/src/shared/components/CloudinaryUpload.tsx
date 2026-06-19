import { useState, useRef } from "react";
import { uploadApi, type CloudinaryResponse } from "../api/uploadApi";

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
                // Validar tipo antes de subir
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
            // Resetear el input para permitir re-subir el mismo archivo
            if (fileInputRef.current) fileInputRef.current.value = "";
        }
    };

    const handleRemove = async (url: string) => {
        // Intentar extraer public_id de la URL de Cloudinary
        // Formato: https://res.cloudinary.com/{cloud}/image/upload/v1234567890/foodstore/imagen.jpg
        const match = url.match(/\/upload\/(?:v\d+\/)?(.+?)\.\w+$/);
        if (match) {
            try {
                await uploadApi.delete(match[1]);
            } catch {
                // Si falla el delete, al menos quitamos la URL localmente
            }
        }
        onChange(images.filter((u) => u !== url));
    };

    return (
        <div className="flex flex-col gap-2">
            <label className="text-xs font-semibold uppercase tracking-wider" style={{ color: "#9a8070" }}>
                {label}
                {images.length > 0 && (
                    <span className="ml-2 normal-case font-normal" style={{ color: "#f97316" }}>
                        {images.length} de {max}
                    </span>
                )}
            </label>

            {/* Previsualización de imágenes subidas */}
            {images.length > 0 && (
                <div className="flex flex-wrap gap-2 p-3 rounded-lg" style={{ backgroundColor: "#fdf9f6", border: "1px solid #d6c9be" }}>
                    {images.map((url, idx) => (
                        <div key={`${url}-${idx}`} className="relative group w-20 h-20 rounded-lg overflow-hidden" style={{ border: "1px solid #d6c9be" }}>
                            <img src={url} alt="" className="w-full h-full object-cover" />
                            <button
                                type="button"
                                onClick={() => handleRemove(url)}
                                className="absolute top-0.5 right-0.5 w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                                title="Eliminar imagen"
                            >
                                ✕
                            </button>
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
                            backgroundColor: uploading ? "#e8ddd5" : "#fff",
                            border: "2px dashed #d6c9be",
                            color: uploading ? "#9a8070" : "#f97316",
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
                                style={{ border: "1px solid #d6c9be", color: "#2d1e0f" }}
                            />
                            <button
                                type="button"
                                onClick={handleAddUrl}
                                className="text-xs font-bold px-3 py-2 rounded-lg text-white"
                                style={{ backgroundColor: "#f97316" }}
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