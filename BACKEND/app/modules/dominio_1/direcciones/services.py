from fastapi import HTTPException, status
from app.modules.dominio_1.direcciones.unit_of_work import DireccionUnitOfWork
from app.modules.dominio_1.direcciones.models import DireccionEntrega
from app.modules.dominio_1.direcciones.schemas import DireccionCreate, DireccionRead


class DireccionService:
    def __init__(self, uow: DireccionUnitOfWork) -> None:
        self.uow = uow

    def crear_direccion(self, usuario_id: int, data: DireccionCreate) -> DireccionRead:
        direccion = DireccionEntrega(
            usuario_id=usuario_id,
            alias=data.alias,
            linea1=data.linea1,
            linea2=data.linea2,
            ciudad=data.ciudad,
            provincia=data.provincia,
            codigo_postal=data.codigo_postal,
            latitud=data.latitud,
            longitud=data.longitud,
        )
        self.uow.direcciones.add(direccion)
        return DireccionRead.model_validate(direccion)

    def listar_direcciones(self, usuario_id: int) -> list[DireccionRead]:
        direcciones = self.uow.direcciones.get_activas_por_usuario(usuario_id)
        return [DireccionRead.model_validate(d) for d in direcciones]

    def establecer_principal(self, usuario_id: int, direccion_id: int) -> DireccionRead:
        direccion = self.uow.direcciones.get_by_id(direccion_id)
        if not direccion or direccion.usuario_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dirección no encontrada",
            )
        self.uow.direcciones.desmarcar_principal(usuario_id)
        direccion.es_principal = True
        self.uow.direcciones.add(direccion)
        return DireccionRead.model_validate(direccion)

    def eliminar_direccion(self, usuario_id: int, direccion_id: int) -> None:
        direccion = self.uow.direcciones.get_by_id(direccion_id)
        if not direccion or direccion.usuario_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dirección no encontrada",
            )
        self.uow.direcciones.soft_delete(direccion_id)
