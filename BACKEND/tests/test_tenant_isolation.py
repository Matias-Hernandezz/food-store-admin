"""
Aislamiento entre locales (M3.6): datos del tenant A no visibles con contexto B.

Requiere PostgreSQL local y permiso para CREATE DATABASE.
"""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlmodel import Session, select

from app.control.db import get_control_engine
from app.control.models import Tenant, TenantStatus
from app.core.config import settings
from app.core.tenant.engines import _pool as tenant_engine_pool
from tests.conftest import TEST_DATABASE_URL, _import_all_models, _seed_catalogos

ISO_DB_A = "foodstore_iso_a"
ISO_DB_B = "foodstore_iso_b"
SLUG_A = "iso-local-a"
SLUG_B = "iso-local-b"
PRODUCT_A = "Producto exclusivo Local A"
PRODUCT_B = "Producto exclusivo Local B"


def _admin_engine():
    base = TEST_DATABASE_URL.rsplit("/", 1)[0]
    return create_engine(f"{base}/postgres", isolation_level="AUTOCOMMIT")


def _tenant_engine(db_name: str):
    base = TEST_DATABASE_URL.rsplit("/", 1)[0]
    return create_engine(f"{base}/{db_name}", echo=False)


def _create_db_if_missing(name: str) -> None:
    eng = _admin_engine()
    with eng.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :n"),
            {"n": name},
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{name}"'))


def _drop_db(name: str) -> None:
    eng = _admin_engine()
    with eng.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))


def _add_product(session: Session, nombre: str):
    from app.modules.dominio_2.categorias.models import Categoria
    from app.modules.dominio_2.productos.models import Producto, ProductoCategoria

    cat = session.exec(select(Categoria).limit(1)).first()
    if not cat:
        cat = Categoria(nombre="Cat iso")
        session.add(cat)
        session.flush()

    producto = Producto(
        nombre=nombre,
        precio_base=Decimal("150.00"),
        stock_cantidad=20,
        disponible=True,
    )
    session.add(producto)
    session.flush()
    session.add(
        ProductoCategoria(producto_id=producto.id, categoria_id=cat.id, es_principal=True)
    )
    session.commit()
    session.refresh(producto)
    return producto


@pytest.fixture(scope="module")
def tenant_isolation_env():
    _import_all_models()
    tenant_engine_pool.clear()

    _create_db_if_missing(ISO_DB_A)
    _create_db_if_missing(ISO_DB_B)

    from sqlmodel import SQLModel

    eng_a = _tenant_engine(ISO_DB_A)
    eng_b = _tenant_engine(ISO_DB_B)
    SQLModel.metadata.drop_all(eng_a)
    SQLModel.metadata.drop_all(eng_b)
    SQLModel.metadata.create_all(eng_a)
    SQLModel.metadata.create_all(eng_b)

    with Session(eng_a) as s:
        _seed_catalogos(s)
        prod_a = _add_product(s, PRODUCT_A)
    with Session(eng_b) as s:
        _seed_catalogos(s)
        prod_b = _add_product(s, PRODUCT_B)

    import app.control.models as _control_models  # noqa: F401
    import app.control.db as control_db_module

    control_db_module._control_engine = None
    ctrl_eng = get_control_engine()
    Tenant.metadata.create_all(ctrl_eng)

    with Session(ctrl_eng) as s:
        for slug in (SLUG_A, SLUG_B):
            existing = s.exec(select(Tenant).where(Tenant.slug == slug)).first()
            if existing:
                s.delete(existing)
        s.add(
            Tenant(
                slug=SLUG_A,
                nombre="Local A",
                estado=TenantStatus.ACTIVE.value,
                db_name=ISO_DB_A,
            )
        )
        s.add(
            Tenant(
                slug=SLUG_B,
                nombre="Local B",
                estado=TenantStatus.ACTIVE.value,
                db_name=ISO_DB_B,
            )
        )
        s.commit()

    yield {
        "slug_a": SLUG_A,
        "slug_b": SLUG_B,
        "product_a_id": prod_a.id,
        "product_b_id": prod_b.id,
    }

    tenant_engine_pool.clear()
    eng_a.dispose()
    eng_b.dispose()
    ctrl_eng = get_control_engine()
    with Session(ctrl_eng) as s:
        for slug in (SLUG_A, SLUG_B):
            row = s.exec(select(Tenant).where(Tenant.slug == slug)).first()
            if row:
                s.delete(row)
        s.commit()
    try:
        _drop_db(ISO_DB_A)
        _drop_db(ISO_DB_B)
    except Exception:
        pass


@pytest.fixture()
def multi_client(tenant_isolation_env, monkeypatch):
    """TestClient en TENANT_MODE=multi sin override de sesión."""
    monkeypatch.setattr(settings, "tenant_mode", "multi")

    from app.main import app
    from app.core.db import get_session

    app.dependency_overrides.pop(get_session, None)

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
    tenant_engine_pool.clear()


def _product_names(client: TestClient, slug: str) -> list[str]:
    res = client.get(
        "/api/v1/public/catalogo",
        headers={"X-Tenant-Slug": slug},
    )
    assert res.status_code == 200, res.text
    return [p["nombre"] for p in res.json()["productos"]]


def test_catalogo_aislado_por_slug(multi_client: TestClient, tenant_isolation_env):
    names_a = _product_names(multi_client, tenant_isolation_env["slug_a"])
    names_b = _product_names(multi_client, tenant_isolation_env["slug_b"])

    assert PRODUCT_A in names_a
    assert PRODUCT_B not in names_a
    assert PRODUCT_B in names_b
    assert PRODUCT_A not in names_b


def test_seguimiento_token_no_filtra_entre_locales(multi_client: TestClient, tenant_isolation_env):
    slug_a = tenant_isolation_env["slug_a"]
    slug_b = tenant_isolation_env["slug_b"]
    product_id = tenant_isolation_env["product_a_id"]

    create = multi_client.post(
        "/api/v1/public/pedidos",
        headers={"X-Tenant-Slug": slug_a},
        json={
            "cliente": {
                "nombre": "Test",
                "apellido": "Aislado",
                "email": "aislado-a@test.com",
            },
            "items": [{"producto_id": product_id, "cantidad": 1, "personalizacion": []}],
            "forma_pago_codigo": "EFECTIVO",
            "tipo_pedido": "PICKUP",
        },
    )
    assert create.status_code == 201, create.text
    token = create.json()["tracking_token"]

    ok = multi_client.get(
        f"/api/v1/public/pedidos/seguimiento/{token}",
        headers={"X-Tenant-Slug": slug_a},
    )
    assert ok.status_code == 200

    otro_local = multi_client.get(
        f"/api/v1/public/pedidos/seguimiento/{token}",
        headers={"X-Tenant-Slug": slug_b},
    )
    assert otro_local.status_code == 404


def test_slug_inexistente_404(multi_client: TestClient):
    res = multi_client.get(
        "/api/v1/public/catalogo",
        headers={"X-Tenant-Slug": "no-existe-xyz"},
    )
    assert res.status_code == 404
