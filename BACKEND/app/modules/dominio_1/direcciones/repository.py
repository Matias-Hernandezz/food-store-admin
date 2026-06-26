from datetime import datetime, timezone
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.dominio_1.direcciones.models import DireccionEntrega


class DireccionRepository(BaseRepository[DireccionEntrega]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, DireccionEntrega)

    def get_activas_por_usuario(self, usuario_id: int) -> list[DireccionEntrega]:
        return list(
            self.session.exec(
                select(DireccionEntrega)
                .where(DireccionEntrega.usuario_id == usuario_id)
                .where(DireccionEntrega.deleted_at.is_(None))
            ).all()
        )

    def get_principal(self, usuario_id: int) -> DireccionEntrega | None:
        return self.session.exec(
            select(DireccionEntrega)
            .where(DireccionEntrega.usuario_id == usuario_id)
            .where(DireccionEntrega.es_principal.is_(True))
            .where(DireccionEntrega.deleted_at.is_(None))
        ).first()

    def desmarcar_principal(self, usuario_id: int) -> None:
        direcciones = self.session.exec(
            select(DireccionEntrega).where(
                DireccionEntrega.usuario_id == usuario_id,
                DireccionEntrega.es_principal.is_(True),
            )
        ).all()
        for d in direcciones:
            d.es_principal = False
            self.session.add(d)
        self.session.flush()

    def soft_delete(self, direccion_id: int) -> None:
        direccion = self.get_by_id(direccion_id)
        if direccion:
            direccion.deleted_at = datetime.now(timezone.utc)
            self.session.add(direccion)
            self.session.flush()
