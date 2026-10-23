from sqlmodel import Session

from app.modules.local_config.models import LocalPerfil
from app.modules.local_config.schemas import LocalPerfilRead, LocalPerfilUpdate


class LocalPerfilService:
    def __init__(self, session: Session):
        self.session = session

    def get(self) -> LocalPerfilRead:
        row = self._get_or_create()
        return LocalPerfilRead.model_validate(row)

    def update(self, data: LocalPerfilUpdate) -> LocalPerfilRead:
        row = self._get_or_create()
        patch = data.model_dump(exclude_unset=True)
        for key, value in patch.items():
            setattr(row, key, value)
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return LocalPerfilRead.model_validate(row)

    def _get_or_create(self) -> LocalPerfil:
        row = self.session.get(LocalPerfil, 1)
        if row:
            return row
        row = LocalPerfil(id=1, nombre_negocio="Food Store")
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row
