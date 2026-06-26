from typing import Optional, Sequence
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.dominio_3.pagos.models import Pago


class PagoRepository(BaseRepository[Pago]):
    def __init__(self,session:Session):
        super().__init__(session,Pago)

    def get_by_pedido_id(self,pedido_id:int)->Optional[Pago]:
        """Último pago asociado al pedido (ordenado por created_at DESC)."""
        statement=(
            select(Pago)
            .where(Pago.pedido_id==pedido_id)
            .order_by(Pago.created_at.desc())
            .limit(1)
        )
        return self.session.exec(statement).first()

    def get_by_mp_payment_id(self,mp_payment_id:int)->Optional[Pago]:
        statement=select(Pago).where(Pago.mp_payment_id==mp_payment_id)
        return self.session.exec(statement).first()

    def get_by_idempotency_key(self,idempotency_key:str)->Optional[Pago]:
        statement=select(Pago).where(Pago.idempotency_key==idempotency_key)
        return self.session.exec(statement).first()

    def get_by_external_reference(self,external_reference:str)->Optional[Pago]:
        statement=select(Pago).where(Pago.external_reference==external_reference)
        return self.session.exec(statement).first()

    def list_by_pedido(self,pedido_id:int)->Sequence[Pago]:
        """Todos los intentos de pago de un pedido (por si reintenta)."""
        statement=(
            select(Pago)
            .where(Pago.pedido_id==pedido_id)
            .order_by(Pago.created_at.desc())
        )
        return self.session.exec(statement).all()