
import logging

from sqlmodel import Session

logger = logging.getLogger(__name__)


class UnitOfWork:
    def __init__(self, session: Session):
        self._session = session

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            try:
                self._session.commit()
            except Exception as e:
                logger.exception("ERROR AL HACER COMMIT")
                raise e
        else:
            logger.error("ERROR EN UOW: %s", exc_val)
            self._session.rollback()
        # Siempre retornar False para no suprimir excepciones
        return False

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()
    