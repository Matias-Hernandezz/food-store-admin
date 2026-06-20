from pydantic import BaseModel


class CloudinaryResponse(BaseModel):
    """Respuesta después de subir una imagen a Cloudinary."""
    secure_url: str
    public_id: str
    width: int
    height: int
    format: str
    resource_type: str

    model_config = {"from_attributes": True}
