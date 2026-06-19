
from sqlalchemy.orm import joinedload
from typing import Optional
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.dominio_3.Pedidos.models import (
    Pedido, DetallePedido, HistorialEstadoPedido,
    FormaPago, EstadoPedido
)

class PedidoRepository(BaseRepository[Pedido]):

    def __init__(self, session: Session):
        super().__init__( session, Pedido)

    def update(self, pedido: Pedido):
        self.session.add(pedido)
        self.session.flush()    

    def get_by_id_con_detalles(self, pedido_id: int) -> Optional[Pedido]:
        return self.session.exec(
            select(Pedido).where(
                Pedido.id == pedido_id,
                Pedido.deleted_at.is_(None),  
            ).options(joinedload(Pedido.direccion_entrega))
        ).first()

    def get_by_usuario(
        self, usuario_id: int, offset: int = 0, limit: int = 20
    ) -> list[Pedido]:
        from app.modules.dominio_3.Pedidos.models import Pedido
        return list(
            self.session.exec(
                select(Pedido)
                .options(joinedload(Pedido.direccion))
                .where(Pedido.usuario_id == usuario_id,
                       Pedido.deleted_at.is_(None))  
                .order_by(Pedido.created_at.desc()) 
                .offset(offset)
                .limit(limit)
            ).unique().all()
        )

    def get_all_activos(self, offset: int = 0, limit: int = 20) -> list[Pedido]:
        from app.modules.dominio_3.Pedidos.models import Pedido
        return list(
            self.session.exec(
                select(Pedido)
                .options(joinedload(Pedido.direccion))
                .where(Pedido.deleted_at.is_(None)) 
                .order_by(Pedido.created_at.desc())  
                .offset(offset)
                .limit(limit)
            ).unique().all()
        )

    def count_by_usuario(self, usuario_id: int) -> int:
        return len(self.get_by_usuario(usuario_id, 0, 9999))

    def count_all(self) -> int:
        return len(self.get_all_activos(0, 9999))


class DetallePedidoRepository(BaseRepository[DetallePedido]):

    def __init__(self, session: Session):
        super().__init__( session, DetallePedido)

    def get_by_pedido(self, pedido_id: int) -> list[DetallePedido]:
        return list(
            self.session.exec(
                select(DetallePedido).where(DetallePedido.pedido_id == pedido_id)
            ).all()
        )


class HistorialRepository(BaseRepository[HistorialEstadoPedido]):

    def __init__(self, session: Session):
        super().__init__( session, HistorialEstadoPedido)

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
        super().__init__( session, FormaPago)

    def get_habilitadas(self) -> list[FormaPago]:
        return list(
            self.session.exec(
                select(FormaPago).where(FormaPago.habilitado == True)  
            ).all()
        )

class EstadoPedidoRepository(BaseRepository[EstadoPedido]):

    def __init__(self, session: Session):
        super().__init__( session, EstadoPedido)

    def get_by_codigo(self, codigo: str) -> Optional[EstadoPedido]:
        return self.session.get(EstadoPedido, codigo)

