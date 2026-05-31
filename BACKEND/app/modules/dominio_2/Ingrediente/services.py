from fastapi import HTTPException, status
from sqlmodel import Session
from datetime import datetime, timezone
from app.modules.dominio_2.Ingrediente.unit_of_work import IngredienteUnitOfWork
from app.modules.dominio_2.Ingrediente.schemas import IngredienteCreate, IngredienteUpdate, IngredienteRead, IngredienteList
from app.modules.dominio_2.Ingrediente.models import Ingrediente

class IngredienteService:
    def __init__(self, session: Session) -> None:
      
        self._session = session


    def _get_or_404(self, uow: IngredienteUnitOfWork, ingrediente_id: int) -> Ingrediente:
        ingrediente = uow.ingredientes.get_by_id(ingrediente_id)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingrediente con id={ingrediente_id} no encontrado",
            )
        return ingrediente

    def _assert_nombre_unique(self, uow: IngredienteUnitOfWork, nombre: str) -> None:
        if uow.ingredientes.get_by_nombre(nombre):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El nombre '{nombre}' ya está en uso",
            )


    def create(self, data: IngredienteCreate) -> IngredienteRead:
        
        with IngredienteUnitOfWork(self._session) as uow:
            self._assert_nombre_unique(uow, data.nombre)
            
            ingrediente = Ingrediente.model_validate(data)
            uow.ingredientes.add(ingrediente)
            result = IngredienteRead.model_validate(ingrediente)
        return result

    def get_all(self, offset: int = 0, limit: int = 20) -> IngredienteList:
        
        with IngredienteUnitOfWork(self._session) as uow:
            ingredientes = uow.ingredientes.get_active(offset=offset, limit=limit)
            total = uow.ingredientes.count_active()
            result = IngredienteList(
                data=[IngredienteRead.model_validate(i) for i in ingredientes],
                total=total,
            )
        return result

    def get_by_id(self, ingrediente_id: int) -> IngredienteRead:
       
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)
            result = IngredienteRead.model_validate(ingrediente)
        return result

    def update(self, ingrediente_id: int, data: IngredienteUpdate) -> IngredienteRead:
       
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)

            if data.nombre and data.nombre != ingrediente.nombre:
                self._assert_nombre_unique(uow, data.nombre)

            patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(ingrediente, field, value)
                
            uow.ingredientes.add(ingrediente)
            result = IngredienteRead.model_validate(ingrediente)
        return result

    def delete(self, ingrediente_id: int) -> None:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)
            uow.ingredientes.delete(ingrediente)