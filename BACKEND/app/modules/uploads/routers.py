from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from typing import Annotated

from app.core.deps import require_role
from app.modules.uploads.schemas import CloudinaryResponse
from app.modules.uploads.services import CloudinaryService

router = APIRouter(
    prefix="/api/v1/uploads",
    tags=["Uploads — Cloudinary"],
    dependencies=[Depends(require_role(["ADMIN"]))],
)


@router.post(
    "/imagen",
    response_model=CloudinaryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subir imagen a Cloudinary",
)
async def upload_imagen(
    file: UploadFile = File(...),
    folder: str = Form(default="foodstore"),
) -> CloudinaryResponse:
    """
    Sube una imagen a Cloudinary.

    - **file**: Archivo de imagen (JPEG, PNG o WebP, máx 5 MB).
    - **folder**: Carpeta en Cloudinary (default: 'foodstore').

    Retorna `secure_url` (URL CDN) y `public_id` (para eliminar después).
    """
    return CloudinaryService.upload(file, folder=folder)


@router.delete(
    "/imagen/{public_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar imagen de Cloudinary",
)
async def delete_imagen(public_id: str) -> None:
    """
    Elimina una imagen de Cloudinary por su `public_id`.

    Usar este endpoint al quitar una imagen de un producto o categoría.
    El `public_id` se obtiene de la respuesta del upload.
    """
    CloudinaryService.destroy(public_id)
