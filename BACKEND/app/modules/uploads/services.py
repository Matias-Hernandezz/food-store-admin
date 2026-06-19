
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status

from app.modules.uploads.schemas import CloudinaryResponse


ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


class CloudinaryService:
    """Servicio para subir y eliminar imágenes en Cloudinary."""

    @staticmethod
    def _validate(file: UploadFile) -> bytes:
        """Valida tipo MIME y tamaño. Retorna los bytes del archivo."""
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato no permitido: {file.content_type}. "
                f"Usar: {', '.join(ALLOWED_MIME_TYPES)}",
            )

        content = file.file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La imagen excede el tamaño máximo de {MAX_FILE_SIZE_MB} MB",
            )

        return content

    @staticmethod
    def upload(file: UploadFile, folder: str = "foodstore") -> CloudinaryResponse:
        """
        Sube una imagen a Cloudinary.

        Args:
            file: Archivo multipart (campo 'file' del form).
            folder: Carpeta destino en Cloudinary (ej: 'foodstock/productos').

        Returns:
            CloudinaryResponse con secure_url, public_id, y metadatos.
        """
        content = CloudinaryService._validate(file)

        try:
            result = cloudinary.uploader.upload(
                content,
                folder=folder,
                resource_type="image",
                overwrite=False,
                unique_filename=True,
                allowed_formats=["jpg", "jpeg", "png", "webp"],
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al subir a Cloudinary: {str(e)}",
            )

        return CloudinaryResponse(
            secure_url=result["secure_url"],
            public_id=result["public_id"],
            width=result.get("width", 0),
            height=result.get("height", 0),
            format=result.get("format", "unknown"),
            resource_type=result.get("resource_type", "image"),
        )

    @staticmethod
    def destroy(public_id: str) -> None:
        """
        Elimina una imagen de Cloudinary por su public_id.

        Args:
            public_id: Identificador público de la imagen en Cloudinary.
        """
        try:
            result = cloudinary.uploader.destroy(public_id, resource_type="image")
            if result.get("result") not in ("ok", "not found"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al eliminar de Cloudinary: {result}",
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar de Cloudinary: {str(e)}",
            )
