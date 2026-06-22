from fastapi import HTTPException, status
from datetime import datetime, timezone
from app.modules.dominio_2.Categoria.unit_of_work import CategoriaUnitOfWork
from app.modules.dominio_2.Categoria.schemas import CategoriaCreate, CategoriaUpdate, CategoriaRead, CategoriaList
from app.modules.dominio_2.Categoria.models import Categoria


class CategoriaService:
    """Lógica de negocio del módulo Categorías.

    Recibe un CategoriaUnitOfWork del router (ya abierto via context manager).
    El commit/rollback lo gestiona el UoW, NUNCA el service.
    """

    def __init__(self, uow: CategoriaUnitOfWork) -> None:
        self.uow = uow

    # ── Helpers privados ──────────────────────────────────────────────────────

    def _get_or_404(self, categoria_id: int) -> Categoria:
        categoria = self.uow.categorias.get_by_id(categoria_id)
        if not categoria or categoria.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoria con id={categoria_id} no encontrada",
            )
        return categoria

    def _assert_nombre_unique(self, nombre: str) -> None:
        if self.uow.categorias.get_by_nombre(nombre):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El nombre '{nombre}' ya está en uso",
            )

    def _validate_parent_id(self, parent_id: int, current_id: int | None = None) -> None:
        if current_id and parent_id == current_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Una categoría no puede ser padre de sí misma."
            )
        parent = self.uow.categorias.get_by_id(parent_id)
        if not parent or parent.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoria padre con id={parent_id} no encontrada",
            )

    # ── Casos de uso ─────────────────────────────────────────────────────────

    def create(self, data: CategoriaCreate) -> CategoriaRead:
        self._assert_nombre_unique(data.nombre)
        if data.parent_id is not None:
            self._validate_parent_id(data.parent_id)
        categoria = Categoria.model_validate(data)
        self.uow.categorias.add(categoria)
        return CategoriaRead.model_validate(categoria)

    def get_all(self, offset: int = 0, limit: int = 20, incluir_eliminados: bool = False) -> CategoriaList:
        if incluir_eliminados:
            categorias = self.uow.categorias.get_all(offset=offset, limit=limit)
            total = self.uow.categorias.count()
        else:
            categorias = self.uow.categorias.get_active(offset=offset, limit=limit)
            total = self.uow.categorias.count_active()
        return CategoriaList(
            data=[CategoriaRead.model_validate(c) for c in categorias],
            total=total,
        )

    def get_by_id(self, categoria_id: int) -> CategoriaRead:
        categoria = self._get_or_404(categoria_id)
        return CategoriaRead.model_validate(categoria)

    def update(self, categoria_id: int, data: CategoriaUpdate) -> CategoriaRead:
        categoria = self._get_or_404(categoria_id)

        if data.nombre and data.nombre != categoria.nombre:
            self._assert_nombre_unique(data.nombre)

        if data.parent_id is not None and data.parent_id != categoria.parent_id:
            self._validate_parent_id(data.parent_id, current_id=categoria_id)

        patch = data.model_dump(exclude_unset=True)
        for field, value in patch.items():
            setattr(categoria, field, value)

        self.uow.categorias.add(categoria)
        return CategoriaRead.model_validate(categoria)

    def soft_delete(self, categoria_id: int) -> None:
        categoria = self._get_or_404(categoria_id)
        categoria.deleted_at = datetime.now(timezone.utc)
        self.uow.categorias.add(categoria)

    def restore(self, categoria_id: int) -> CategoriaRead:
        categoria = self.uow.categorias.get_by_id(categoria_id)
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoria con id={categoria_id} no encontrada",
            )
        if categoria.deleted_at is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La categoría no está eliminada",
            )
        # Verificar que no exista otra categoria activa con el mismo nombre
        existente = self.uow.categorias.get_by_nombre(categoria.nombre)
        if existente and existente.id != categoria_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"No se puede restaurar: ya existe una categoría activa con el nombre '{categoria.nombre}'",
            )
        self.uow.categorias.restore(categoria)
        return CategoriaRead.model_validate(categoria)
