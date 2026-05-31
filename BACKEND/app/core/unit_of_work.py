
from sqlmodel import Session


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
                print(f"ERROR AL HACER COMMIT: {e}")
                raise e 
        else:
            print(f"ERROR EN UOW: {exc_val}")
            self._session.rollback()

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()
    
   