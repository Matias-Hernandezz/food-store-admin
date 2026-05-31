from typing import Generic, TypeVar, Type, Optional, Sequence
from sqlmodel import Session, select

ModelT = TypeVar("ModelT")

class BaseRepository(Generic[ModelT]):
    def __init__(self, session: Session, model: Type[ModelT]):
        self.session = session
        self.model = model

    def get_by_id(self, record_id: int) -> Optional[ModelT]:
        return self.session.get(self.model, record_id)

    def get_all(self, offset: int = 0, limit: int = 100) -> Sequence[ModelT]:
        statement = select(self.model).offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def add(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        self.session.flush()  
        self.session.refresh(instance)
        return instance

    def delete(self, instance: ModelT) -> None:
        self.session.delete(instance)
        self.session.flush()
    