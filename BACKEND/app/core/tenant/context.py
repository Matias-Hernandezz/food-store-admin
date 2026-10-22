from contextvars import ContextVar

_current_tenant_slug: ContextVar[str | None] = ContextVar("tenant_slug", default=None)
_current_tenant_db_url: ContextVar[str | None] = ContextVar("tenant_db_url", default=None)


def get_current_tenant_slug() -> str | None:
    return _current_tenant_slug.get()


def get_current_tenant_db_url() -> str | None:
    return _current_tenant_db_url.get()


def set_tenant_context(slug: str, database_url: str) -> tuple:
    """Devuelve tokens para reset en finally."""
    t_slug = _current_tenant_slug.set(slug)
    t_url = _current_tenant_db_url.set(database_url)
    return t_slug, t_url


def reset_tenant_context(tokens: tuple) -> None:
    t_slug, t_url = tokens
    _current_tenant_slug.reset(t_slug)
    _current_tenant_db_url.reset(t_url)
