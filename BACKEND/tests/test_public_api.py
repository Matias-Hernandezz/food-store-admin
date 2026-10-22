"""API pública (landings / guest checkout)."""

from fastapi.testclient import TestClient


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
