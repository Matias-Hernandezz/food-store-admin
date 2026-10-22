"""Turno de caja y pedido mostrador."""

from fastapi.testclient import TestClient

from tests.helpers import login_as


def test_abrir_cerrar_turno(client: TestClient, admin_user):
    login_as(client, admin_user["email"], admin_user["password"])

    res = client.post("/api/v1/caja/turno/abrir", json={"fondo_inicial": 1000})
    assert res.status_code == 201, res.text
    turno_id = res.json()["id"]

    actual = client.get("/api/v1/caja/turno/actual")
    assert actual.status_code == 200
    assert actual.json()["id"] == turno_id

    cierre = client.post("/api/v1/caja/turno/cerrar", json={"efectivo_contado": 1000})
    assert cierre.status_code == 200
    assert cierre.json()["estado"] == "CLOSED"
