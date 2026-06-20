from fastapi import HTTPException, status
from datetime import datetime, timezone
from app.modules.dominio_2.Ingrediente.unit_of_work import IngredienteUnitOfWork
from app.modules.dominio_2.Ingrediente.schemas import IngredienteCreate, IngredienteUpdate, IngredienteRead, IngredienteList
from app.modules.dominio_2.Ingrediente.models import Ingrediente


class IngredienteService:
    """Lógica de negocio del módulo Ingredientes.

    Recibe un IngredienteUnitOfWork del router (ya abierto via context manager).
    El commit/rollback lo gestiona el UoW, NUNCA el service.
    """

    def __init__(self, uow: IngredienteUnitOfWork) -> None:
        self.uow = uow

    def _get_or_404(self, ingrediente_id: int) -> Ingrediente:
        ingrediente = self.uow.ingredientes.get_by_id(ingrediente_id)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingrediente con id={ingrediente_id} no encontrado",
            )
        return ingrediente

    def _assert_nombre_unique(self, nombre: str) -> None:
        if self.uow.ingredientes.get_by_nombre(nombre):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El nombre '{nombre}' ya está en uso",
            )

    def create(self, data: IngredienteCreate) -> IngredienteRead:
        self._assert_nombre_unique(data.nombre)
        ingrediente = Ingrediente.model_validate(data)
        self.uow.ingredientes.add(ingrediente)
        return IngredienteRead.model_validate(ingrediente)

    def get_all(self, offset: int = 0, limit: int = 20) -> IngredienteList:
        ingredientes = self.uow.ingredientes.get_active(offset=offset, limit=limit)
        total = self.uow.ingredientes.count_active()
        return IngredienteList(
            data=[IngredienteRead.model_validate(i) for i in ingredientes],
            total=total,
        )

    def get_by_id(self, ingrediente_id: int) -> IngredienteRead:
        ingrediente = self._get_or_404(ingrediente_id)
        return IngredienteRead.model_validate(ingrediente)

    def update(self, ingrediente_id: int, data: IngredienteUpdate) -> IngredienteRead:
        ingrediente = self._get_or_404(ingrediente_id)

        if data.nombre and data.nombre != ingrediente.nombre:
            self._assert_nombre_unique(data.nombre)

        patch = data.model_dump(exclude_unset=True)
        for field, value in patch.items():
            setattr(ingrediente, field, value)

        self.uow.ingredientes.add(ingrediente)
        return IngredienteRead.model_validate(ingrediente)

    def delete(self, ingrediente_id: int) -> None:
        ingrediente = self._get_or_404(ingrediente_id)
        self.uow.ingredientes.soft_delete(ingrediente)
