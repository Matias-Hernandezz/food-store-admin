from typing import Generic, TypeVar, Type, Optional, Sequence
from datetime import datetime, timezone
from sqlmodel import Session, select, func

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

    def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelT]:
        return self.get_all(offset=skip, limit=limit)

    def count(self) -> int:
        statement = select(func.count()).select_from(self.model)
        return self.session.exec(statement).one()

    def add(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        self.session.flush()  
        self.session.refresh(instance)
        return instance

    def create(self, instance: ModelT) -> ModelT:
        return self.add(instance)

    def update(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        self.session.flush()
        self.session.refresh(instance)
        return instance

    def delete(self, instance: ModelT) -> None:
        self.session.delete(instance)
        self.session.flush()

    def hard_delete(self, instance: ModelT) -> None:
        self.delete(instance)

    def soft_delete(self, instance: ModelT) -> None:
        if hasattr(instance, "deleted_at"):
            instance.deleted_at = datetime.now(timezone.utc)
            self.session.add(instance)
            self.session.flush()
            self.session.refresh(instance)