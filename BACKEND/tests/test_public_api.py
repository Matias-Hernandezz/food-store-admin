"""API pública (landings / guest checkout)."""

from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session


def test_public_catalogo_sin_auth(client: TestClient, producto_factory):
    producto_factory(nombre="Public Burger", disponible=True)
    res = client.get("/api/v1/public/catalogo")
    assert res.status_code == 200
    body = res.json()
    assert "productos" in body
    assert any(p["nombre"] == "Public Burger" for p in body["productos"])


def test_public_pedido_y_seguimiento(client: TestClient, producto_factory):
    producto = producto_factory(stock=10, disponible=True)
    payload = {
        "cliente": {
            "nombre": "Ana",
            "apellido": "Pública",
            "email": "ana.publica@test.com",
            "celular": "1112223333",
        },
        "items": [{"producto_id": producto.id, "cantidad": 1, "personalizacion": []}],
        "forma_pago_codigo": "EFECTIVO",
        "tipo_pedido": "PICKUP",
    }
    res = client.post("/api/v1/public/pedidos", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["estado_codigo"] == "PENDIENTE"
    token = data["tracking_token"]
    assert len(token) > 20

    seg = client.get(f"/api/v1/public/pedidos/seguimiento/{token}")
    assert seg.status_code == 200
    assert seg.json()["pedido_id"] == data["pedido_id"]

    hist = client.get(f"/api/v1/public/pedidos/seguimiento/{token}/historial")
    assert hist.status_code == 200
    assert len(hist.json()) >= 1

    assert client.get("/api/v1/public/pedidos/seguimiento/token-invalido").status_code == 404


def test_public_pedido_reactiva_cuenta_baja(
    client: TestClient, producto_factory, client_user: dict, db_session: Session,
):
    from app.modules.dominio_1.usuarios.repository import UsuarioRepository

    usuarios = UsuarioRepository(db_session)
    u = usuarios.get_by_email(client_user["email"])
    assert u is not None
    u.deleted_at = datetime.now(timezone.utc)
    usuarios.add(u)
    db_session.commit()

    producto = producto_factory(stock=5, disponible=True)
    payload = {
        "cliente": {
            "nombre": "Cliente",
            "apellido": "Otra vez",
            "email": client_user["email"],
        },
        "items": [{"producto_id": producto.id, "cantidad": 1, "personalizacion": []}],
        "forma_pago_codigo": "EFECTIVO",
        "tipo_pedido": "PICKUP",
    }
    res = client.post("/api/v1/public/pedidos", json=payload)
    assert res.status_code == 201, res.text

    db_session.expire_all()
    u2 = usuarios.get_by_email(client_user["email"])
    assert u2 is not None
    assert u2.deleted_at is None
    assert u2.apellido == "Otra vez"


def test_public_pedido_delivery_direccion_minima(client: TestClient, producto_factory):
    """Checkout invitado sin provincia ni CP (como el formulario web)."""
    producto = producto_factory(stock=10, disponible=True)
    payload = {
        "cliente": {
            "nombre": "Matias",
            "apellido": "Hernandez",
            "email": "guest.delivery@test.com",
        },
        "items": [{"producto_id": producto.id, "cantidad": 1, "personalizacion": []}],
        "forma_pago_codigo": "EFECTIVO",
        "tipo_pedido": "DELIVERY",
        "direccion": {
            "alias": "Entrega",
            "linea1": "lucio v mansilla",
            "linea2": "1444",
            "ciudad": "godoy cruz",
        },
    }
    res = client.post("/api/v1/public/pedidos", json=payload)
    assert res.status_code == 201, res.text
    assert res.json()["tipo_pedido"] == "DELIVERY"


def test_public_seguimiento_no_filtra_otro_token(
    client: TestClient, producto_factory,
):
    p = producto_factory()
    base = {
        "cliente": {"nombre": "A", "apellido": "B", "email": "a1@test.com"},
        "items": [{"producto_id": p.id, "cantidad": 1, "personalizacion": []}],
        "forma_pago_codigo": "EFECTIVO",
        "tipo_pedido": "PICKUP",
    }
    t1 = client.post("/api/v1/public/pedidos", json=base).json()["tracking_token"]
    base["cliente"]["email"] = "b2@test.com"
    t2 = client.post("/api/v1/public/pedidos", json=base).json()["tracking_token"]

    seg1 = client.get(f"/api/v1/public/pedidos/seguimiento/{t1}").json()
    seg2 = client.get(f"/api/v1/public/pedidos/seguimiento/{t2}").json()
    assert seg1["pedido_id"] != seg2["pedido_id"]
