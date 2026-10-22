from sqlmodel import Session, create_engine

from app.core.config import settings

_control_engine = None


def get_control_engine():
    global _control_engine
    if _control_engine is None:
        _control_engine = create_engine(settings.CONTROL_DATABASE_URL, echo=False, pool_pre_ping=True)
    return _control_engine


def get_control_session():
    with Session(get_control_engine()) as session:
        yield session
