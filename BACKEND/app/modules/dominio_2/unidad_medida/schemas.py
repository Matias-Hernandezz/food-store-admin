from pydantic import BaseModel


class UnidadMedidaRead(BaseModel):
    id: int
    nombre: str
    simbolo: str
    tipo: str

    class Config:
        from_attributes = True
