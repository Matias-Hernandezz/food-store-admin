from fastapi import HTTPException, status
from sqlmodel import Session
from datetime import datetime, timezone
from app.modules.dominio_2.Categoria.unit_of_work import CategoriaUnitOfWork
from app.modules.dominio_2.Categoria.schemas import CategoriaCreate, CategoriaUpdate, CategoriaRead, CategoriaList
from app.modules.dominio_2.Categoria.models import Categoria

class CategoriaService:
    def __init__(self, session: Session) -> None:
        """
        Inicializa el servicio con una sesión de base de datos.
        Delega la transacción en CategoriaUnitOfWork.
        """
        self._session = session

    # ── Helpers privados ──────────────────────────────────────────────────────

    def _get_or_404(self, uow: CategoriaUnitOfWork, categoria_id: int) -> Categoria:
        
        categoria = uow.categorias.get_by_id(categoria_id)
        
        if not categoria or categoria.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoria con id={categoria_id} no encontrada",
            )
        return categoria

    def _assert_nombre_unique(self, uow: CategoriaUnitOfWork, nombre: str) -> None:
        
        if uow.categorias.get_by_nombre(nombre):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El nombre '{nombre}' ya está en uso",
            )

    def _validate_parent_id(self, uow: CategoriaUnitOfWork, parent_id: int, current_id: int | None = None) -> Categoria:
        
        if current_id and parent_id == current_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Una categoría no puede ser padre de sí misma."
            )
            
        parent = uow.categorias.get_by_id(parent_id)
        if not parent or parent.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoria padre con id={parent_id} no encontrada",
            )
        return parent

    # ── Casos de uso ─────────────────────────────────────────────────────────

    def create(self, data: CategoriaCreate) -> CategoriaRead:
        
        with CategoriaUnitOfWork(self._session) as uow:
            self._assert_nombre_unique(uow, data.nombre)
            
            if data.parent_id is not None:
                self._validate_parent_id(uow, data.parent_id)
                
            categoria = Categoria.model_validate(data)
            uow.categorias.add(categoria)
            result = CategoriaRead.model_validate(categoria)
        return result

    def get_all(self, offset: int = 0, limit: int = 20) -> CategoriaList:
       
        with CategoriaUnitOfWork(self._session) as uow:
            categorias = uow.categorias.get_active(offset=offset, limit=limit)
            total = uow.categorias.count_active()
            result = CategoriaList(
                data=[CategoriaRead.model_validate(c) for c in categorias],
                total=total,
            )
        return result

    def get_by_id(self, categoria_id: int) -> CategoriaRead:
        
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)
            result = CategoriaRead.model_validate(categoria)
        return result

    def update(self, categoria_id: int, data: CategoriaUpdate) -> CategoriaRead:
       
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)

            if data.nombre and data.nombre != categoria.nombre:
                self._assert_nombre_unique(uow, data.nombre)
                
            if data.parent_id is not None and data.parent_id != categoria.parent_id:
                self._validate_parent_id(uow, data.parent_id, current_id=categoria_id)

            patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(categoria, field, value)
                
            uow.categorias.add(categoria)
            result = CategoriaRead.model_validate(categoria)
        return result

    def soft_delete(self, categoria_id: int) -> None:
        
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)
            categoria.deleted_at = datetime.now(timezone.utc)
            uow.categorias.add(categoria)