from collections import OrderedDict
from threading import Lock

from sqlalchemy.engine import Engine
from sqlmodel import create_engine

_MAX_TENANT_ENGINES = 32
_pool: OrderedDict[str, Engine] = OrderedDict()
_lock = Lock()


def get_engine_for_url(database_url: str) -> Engine:
    with _lock:
        if database_url in _pool:
            _pool.move_to_end(database_url)
            return _pool[database_url]

        eng = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=5,
        )
        _pool[database_url] = eng
        while len(_pool) > _MAX_TENANT_ENGINES:
            _pool.popitem(last=False)
        return eng
