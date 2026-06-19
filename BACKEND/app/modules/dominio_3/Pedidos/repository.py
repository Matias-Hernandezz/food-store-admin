from datetime import date
from typing import Optional

from sqlalchemy.orm import joinedload
from sqlmodel import Session, select, func

from app.core.repository import BaseRepository
from app.modules.dominio_3.Pedidos.models import (
    Pedido, DetallePedido, HistorialEstadoPedido,
    FormaPago, EstadoPedido
)


def _aplicar_filtro_fecha(stmt, desde: Optional[date] = None, hasta: Optional[date] = None):
    """Agrega filtro de rango de fechas sobre Pedido.created_at."""
    if desde:
        stmt = stmt.where(func.date(Pedido.created_at) >= desde)
    if hasta:
        stmt = stmt.where(func.date(Pedido.created_at) <= hasta)
    return stmt


def _aplicar_filtro_usuario(stmt, search: Optional[str] = None):
    """Agrega filtro por nombre o apellido de usuario (búsqueda parcial)."""
    if search:
        from app.modules.dominio_1.Usuarios.models import Usuario
        from sqlalchemy import or_
        stmt = stmt.join(Usuario, Pedido.usuario_id == Usuario.id).where(
            or_(
                Usuario.nombre.ilike(f"%{search}%"),
                Usuario.apellido.ilike(f"%{search}%"),
            )
        )
    return stmt


class PedidoRepository(BaseRepository[Pedido]):

    def __init__(self, session: Session):
        super().__init__(session, Pedido)

    def update(self, pedido: Pedido):
        self.session.add(pedido)
        self.session.flush()

    def get_by_id_con_detalles(self, pedido_id: int) -> Optional[Pedido]:
        return self.session.exec(
            select(Pedido).where(
                Pedido.id == pedido_id,
                Pedido.deleted_at.is_(None),
            ).options(joinedload(Pedido.direccion), joinedload(Pedido.usuario))
        ).first()

    def get_by_estados(
        self, estados: list[str], offset: int = 0, limit: int = 100,
        desde: Optional[date] = None, hasta: Optional[date] = None,
        search: Optional[str] = None,
    ) -> list[Pedido]:
        stmt = (
            select(Pedido)
            .options(joinedload(Pedido.direccion), joinedload(Pedido.usuario))
            .where(
                Pedido.deleted_at.is_(None),
                Pedido.estado_codigo.in_(estados),
            )
            .order_by(Pedido.created_at.desc())
            .offset(offset).limit(limit)
        )
        stmt = _aplicar_filtro_fecha(stmt, desde, hasta)
        stmt = _aplicar_filtro_usuario(stmt, search)
        return list(self.session.exec(stmt).unique().all())

    def count_by_estados(
        self, estados: list[str],
        desde: Optional[date] = None, hasta: Optional[date] = None,
        search: Optional[str] = None,
    ) -> int:
        stmt = (
            select(func.count(Pedido.id))
            .where(
                Pedido.deleted_at.is_(None),
                Pedido.estado_codigo.in_(estados),
            )
        )
        stmt = _aplicar_filtro_fecha(stmt, desde, hasta)
        stmt = _aplicar_filtro_usuario(stmt, search)
        return self.session.exec(stmt).one()

    def get_by_usuario(
        self, usuario_id: int, offset: int = 0, limit: int = 20,
        desde: Optional[date] = None, hasta: Optional[date] = None,
        search: Optional[str] = None,
    ) -> list[Pedido]:
        stmt = (
            select(Pedido)
            .options(joinedload(Pedido.direccion), joinedload(Pedido.usuario))
            .where(Pedido.usuario_id == usuario_id, Pedido.deleted_at.is_(None))
            .order_by(Pedido.created_at.desc())
            .offset(offset).limit(limit)
        )
        stmt = _aplicar_filtro_fecha(stmt, desde, hasta)
        stmt = _aplicar_filtro_usuario(stmt, search)
        return list(self.session.exec(stmt).unique().all())

    def get_all_activos(
        self, offset: int = 0, limit: int = 20,
        desde: Optional[date] = None, hasta: Optional[date] = None,
        search: Optional[str] = None,
        estado: Optional[str] = None,
    ) -> list[Pedido]:
        stmt = (
            select(Pedido)
            .options(joinedload(Pedido.direccion), joinedload(Pedido.usuario))
            .where(Pedido.deleted_at.is_(None))
            .order_by(Pedido.created_at.desc())
            .offset(offset).limit(limit)
        )
        if estado:
            stmt = stmt.where(Pedido.estado_codigo == estado)
        stmt = _aplicar_filtro_fecha(stmt, desde, hasta)
        stmt = _aplicar_filtro_usuario(stmt, search)
        return list(self.session.exec(stmt).unique().all())

    def count_by_usuario(
        self, usuario_id: int,
        desde: Optional[date] = None, hasta: Optional[date] = None,
        search: Optional[str] = None,
    ) -> int:
        stmt = (
            select(func.count(Pedido.id))
            .where(Pedido.usuario_id == usuario_id, Pedido.deleted_at.is_(None))
        )
        stmt = _aplicar_filtro_fecha(stmt, desde, hasta)
        stmt = _aplicar_filtro_usuario(stmt, search)
        return self.session.exec(stmt).one()

    def count_all(
        self, desde: Optional[date] = None, hasta: Optional[date] = None,
        search: Optional[str] = None,
        estado: Optional[str] = None,
    ) -> int:
        stmt = (
            select(func.count(Pedido.id))
            .where(Pedido.deleted_at.is_(None))
        )
        if estado:
            stmt = stmt.where(Pedido.estado_codigo == estado)
        stmt = _aplicar_filtro_fecha(stmt, desde, hasta)
        stmt = _aplicar_filtro_usuario(stmt, search)
        return self.session.exec(stmt).one()


class DetallePedidoRepository(BaseRepository[DetallePedido]):

    def __init__(self, session: Session):
        super().__init__(session, DetallePedido)

    def get_by_pedido(self, pedido_id: int) -> list[DetallePedido]:
        return list(
            self.session.exec(
                select(DetallePedido).where(DetallePedido.pedido_id == pedido_id)
            ).all()
        )


class HistorialRepository(BaseRepository[HistorialEstadoPedido]):

    def __init__(self, session: Session):
        super().__init__(session, HistorialEstadoPedido)

    def get_by_pedido(self, pedido_id: int) -> list[HistorialEstadoPedido]:
        return list(
            self.session.exec(
                select(HistorialEstadoPedido)
                .where(HistorialEstadoPedido.pedido_id == pedido_id)
                .order_by(HistorialEstadoPedido.created_at.asc())
            ).all()
        )


class FormaPagoRepository(BaseRepository[FormaPago]):

    def __init__(self, session: Session):
        super().__init__(session, FormaPago)

    def get_habilitadas(self) -> list[FormaPago]:
        return list(
            self.session.exec(
                select(FormaPago).where(FormaPago.habilitado == True)
            ).all()
        )


class EstadoPedidoRepository(BaseRepository[EstadoPedido]):

    def __init__(self, session: Session):
        super().__init__(session, EstadoPedido)

    def get_by_codigo(self, codigo: str) -> Optional[EstadoPedido]:
        return self.session.get(EstadoPedido, codigo)
