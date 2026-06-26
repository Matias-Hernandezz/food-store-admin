"""
Fixtures globales para tests de Food Store.

Estrategia de BD: PostgreSQL de test (evita problemas de dialecto con ARRAY, DATE_TRUNC, etc.)
La DB foodstore_test debe existir. El engine crea/destruye tablas por sesión de test.

Uso:
    pytest tests/ -v
"""

import os
import pytest
from typing import Generator

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select

# ── Configurar DB de test antes de importar la app ──────────────────────
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/foodstore_test",
)

# Forzar que el app use la misma DB de test (el WS endpoint usa Session(engine) directo)
os.environ["POSTGRES_DB"] = "foodstore_test"

# Motor compartido para toda la sesión de tests
test_engine = create_engine(TEST_DATABASE_URL, echo=False)


def _import_all_models():
    """Importa todos los modelos para que SQLModel.metadata los registre."""
    import app.modules.dominio_1.auth.models          # noqa: F401
    import app.modules.dominio_1.usuarios.models      # noqa: F401
    import app.modules.dominio_1.direcciones.models    # noqa: F401
    import app.modules.dominio_2.categorias.models      # noqa: F401
    import app.modules.dominio_2.ingredientes.models     # noqa: F401
    import app.modules.dominio_2.productos.models        # noqa: F401
    import app.modules.dominio_2.unidad_medida.models   # noqa: F401
    import app.modules.dominio_3.pedidos.models         # noqa: F401
    import app.modules.dominio_3.pagos.models           # noqa: F401


def _seed_catalogos(session: Session) -> None:
    """Inserta los catálogos obligatorios (roles, estados, formas de pago, unidades)."""
    from app.modules.dominio_1.usuarios.models import Rol
    from app.modules.dominio_3.pedidos.models import FormaPago, EstadoPedido
    from app.modules.dominio_2.unidad_medida.models import UnidadMedida

    # Roles
    for codigo, nombre, desc in [
        ("ADMIN", "Administrador", "CRUD completo"),
        ("STOCK", "Gestor de Stock", "Stock y disponibilidad"),
        ("PEDIDOS", "Gestor de Pedidos", "Avanzar estados"),
        ("CLIENT", "Cliente", "Catálogo, carrito y pedidos propios"),
    ]:
        if not session.get(Rol, codigo):
            session.add(Rol(codigo=codigo, nombre=nombre, descripcion=desc))

    # Estados de pedido
    for codigo, desc, orden, terminal in [
        ("PENDIENTE", "Pedido creado", 1, False),
        ("CONFIRMADO", "Pago confirmado", 2, False),
        ("EN_PREP", "En preparación", 3, False),
        ("ENTREGADO", "Entrega confirmada", 4, True),
        ("CANCELADO", "Pedido cancelado", 5, True),
    ]:
        if not session.get(EstadoPedido, codigo):
            session.add(EstadoPedido(codigo=codigo, descripcion=desc, orden=orden, es_terminal=terminal))

    # Formas de pago
    for codigo, desc, hab in [
        ("EFECTIVO", "Efectivo", True),
        ("MERCADOPAGO", "Mercado Pago", True),
        ("TRANSFERENCIA", "Transferencia", True),
    ]:
        if not session.get(FormaPago, codigo):
            session.add(FormaPago(codigo=codigo, descripcion=desc, habilitado=hab))

    # Unidades de medida
    for nombre, simbolo, tipo in [
        ("kilogramo", "kg", "peso"),
        ("gramo", "g", "peso"),
        ("litro", "L", "volumen"),
        ("mililitro", "ml", "volumen"),
        ("unidad", "ud", "contable"),
        ("porciones", "porc", "contable"),
    ]:
        existing = session.exec(select(UnidadMedida).where(UnidadMedida.nombre == nombre)).first()
        if not existing:
            session.add(UnidadMedida(nombre=nombre, simbolo=simbolo, tipo=tipo))

    session.commit()


# ══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def engine():
    """Motor PostgreSQL para toda la sesión de tests."""
    _import_all_models()
    SQLModel.metadata.create_all(test_engine)
    yield test_engine
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture()
def db_session(engine) -> Generator[Session, None, None]:
    """Session limpia por test. Rollback automático al finalizar."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    _seed_catalogos(session)

    yield session

    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """TestClient con get_session sobreescrita para usar la BD de test."""
    from app.main import app
    from app.core.db import get_session

    def _override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = _override_get_session

    # Limpiar estado del rate limiter entre tests
    app.state.limiter.reset()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ── Helpers de autenticación ──────────────────────────────────────────────

def _create_user(session: Session, nombre: str, email: str, password: str, rol: str):
    """Crea un usuario con rol asignado. Retorna (Usuario, raw_password)."""
    from app.core.security import hash_password
    from app.modules.dominio_1.usuarios.models import Usuario, UsuarioRol

    usuario = Usuario(
        nombre=nombre,
        apellido="Test",
        email=email,
        password_hash=hash_password(password),
    )
    session.add(usuario)
    session.flush()
    session.add(UsuarioRol(usuario_id=usuario.id, rol_codigo=rol))
    session.commit()
    return usuario


@pytest.fixture()
def admin_user(db_session: Session) -> dict:
    """Crea usuario ADMIN en BD. NO hace login. Retorna datos del usuario."""
    user = _create_user(db_session, "Admin", "admin@test.com", "Admin1234!", "ADMIN")
    return {"id": user.id, "email": "admin@test.com", "password": "Admin1234!"}


@pytest.fixture()
def client_user(db_session: Session) -> dict:
    """Crea usuario CLIENT en BD. NO hace login. Retorna datos del usuario."""
    user = _create_user(db_session, "Cliente", "cliente@test.com", "Cliente1234!", "CLIENT")
    return {"id": user.id, "email": "cliente@test.com", "password": "Cliente1234!"}


@pytest.fixture()
def pedidos_user(db_session: Session) -> dict:
    """Crea usuario PEDIDOS en BD. NO hace login. Retorna datos del usuario."""
    user = _create_user(db_session, "Pedidos", "pedidos@test.com", "Pedidos1234!", "PEDIDOS")
    return {"id": user.id, "email": "pedidos@test.com", "password": "Pedidos1234!"}


# ── Factories ────────────────────────────────────────────────────────────

@pytest.fixture()
def categoria_factory(db_session: Session):
    """Factory: crea una Categoria. Retorna Categoria."""
    from app.modules.dominio_2.categorias.models import Categoria

    def _create(nombre: str = "Test Categoria", parent_id: int | None = None):
        cat = Categoria(nombre=nombre, descripcion="Cat de test", parent_id=parent_id)
        db_session.add(cat)
        db_session.commit()
        db_session.refresh(cat)
        return cat

    return _create


@pytest.fixture()
def producto_factory(db_session: Session):
    """Factory: crea un Producto con stock y categoría. Retorna Producto."""
    from decimal import Decimal
    from app.modules.dominio_2.productos.models import Producto, ProductoCategoria
    from app.modules.dominio_2.categorias.models import Categoria

    def _create(
        nombre: str = "Producto Test",
        precio: Decimal = Decimal("100.00"),
        stock: int = 50,
        disponible: bool = True,
    ):
        # Asegurar que existe al menos una categoría
        cat = db_session.exec(select(Categoria).limit(1)).first()
        if not cat:
            cat = Categoria(nombre="Base")
            db_session.add(cat)
            db_session.commit()
            db_session.refresh(cat)

        producto = Producto(
            nombre=nombre,
            precio_base=precio,
            stock_cantidad=stock,
            disponible=disponible,
        )
        db_session.add(producto)
        db_session.flush()

        db_session.add(ProductoCategoria(producto_id=producto.id, categoria_id=cat.id, es_principal=True))
        db_session.commit()
        db_session.refresh(producto)
        return producto

    return _create


@pytest.fixture()
def pedido_factory(db_session: Session):
    """Factory: crea un Pedido en PENDIENTE con 1 DetallePedido. Retorna Pedido."""
    from decimal import Decimal
    from app.modules.dominio_3.pedidos.models import Pedido, DetallePedido, HistorialEstadoPedido
    from app.modules.dominio_2.productos.models import Producto

    def _create(
        usuario_id: int,
        producto_id: int | None = None,
        estado: str = "PENDIENTE",
        forma_pago: str = "MERCADOPAGO",
    ):
        if producto_id is None:
            # Buscar o crear un producto
            prod = db_session.exec(select(Producto).where(Producto.disponible == True)).first()
            if not prod:
                from app.modules.dominio_2.categorias.models import Categoria
                from app.modules.dominio_2.productos.models import ProductoCategoria
                cat = db_session.exec(select(Categoria).limit(1)).first()
                if not cat:
                    cat = Categoria(nombre="Base")
                    db_session.add(cat)
                    db_session.commit()
                prod = Producto(nombre="Prod Test", precio_base=Decimal("100.00"), stock_cantidad=50, disponible=True)
                db_session.add(prod)
                db_session.flush()
                db_session.add(ProductoCategoria(producto_id=prod.id, categoria_id=cat.id, es_principal=True))
                db_session.commit()
            producto_id = prod.id

        pedido = Pedido(
            usuario_id=usuario_id,
            estado_codigo=estado,
            forma_pago_codigo=forma_pago,
            subtotal=Decimal("100.00"),
            descuento=Decimal("0.00"),
            costo_envio=Decimal("50.00"),
            total=Decimal("150.00"),
        )
        db_session.add(pedido)
        db_session.flush()

        db_session.add(DetallePedido(
            pedido_id=pedido.id,
            producto_id=producto_id,
            cantidad=1,
            nombre_snapshot="Producto Test",
            precio_snapshot=Decimal("100.00"),
            subtotal=Decimal("100.00"),
        ))

        db_session.add(HistorialEstadoPedido(
            pedido_id=pedido.id,
            estado_desde=None,
            estado_hacia=estado,
            usuario_id=usuario_id,
            motivo="Creación inicial",
        ))
        db_session.commit()
        db_session.refresh(pedido)
        return pedido

    return _create
