from pydantic import BaseModel


class UnidadMedidaRead(BaseModel):
    id: int
    nombre: str
    simbolo: str
    tipo: str

    model_config = {"from_attributes": True}
