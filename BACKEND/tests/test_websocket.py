"""
Tests del módulo WebSocket — Section 9 (Rubric)

El endpoint WS ahora usa Depends(get_session) para recibir la sesión,
lo que permite que los tests usen la DB de test vía dependency override.
"""

import json

import pytest
from fastapi.testclient import TestClient

from tests.helpers import login_as


def _get_token(client: TestClient, email: str, password: str) -> str:
    """Login y extrae el access_token para WS."""
    login_as(client, email, password)
    res = client.get("/api/v1/auth/token")
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


@pytest.fixture()
def admin_token(client: TestClient, admin_user) -> str:
    return _get_token(client, admin_user["email"], admin_user["password"])


@pytest.fixture()
def client_token(client: TestClient, client_user) -> str:
    return _get_token(client, client_user["email"], client_user["password"])


class TestConexionWebSocket:
    def test_ws_conexion_con_token(self, client, admin_token):
        """WS con token JWT válido → handshake exitoso (no cierra inmediatamente)."""
        with client.websocket_connect(
            f"/api/v1/pedidos/ws/pedidos?token={admin_token}"
        ) as ws:
            # El handshake se completa correctamente
            assert ws

    def test_ws_conexion_sin_token(self, client):
        """WS sin token → se cierra con 4001."""
        with pytest.raises(Exception):
            with client.websocket_connect("/api/v1/pedidos/ws/pedidos") as ws:
                ws.receive_text()

    def test_ws_conexion_token_invalido(self, client):
        """WS con token inválido → se cierra con 4001."""
        with pytest.raises(Exception):
            with client.websocket_connect(
                "/api/v1/pedidos/ws/pedidos?token=fake_token_xyz"
            ) as ws:
                ws.receive_text()


class TestSuscripcion:
    def test_ws_suscribe_order(self, client, admin_token):
        """Admin suscribe a cualquier pedido → recibe SUBSCRIBED."""
        with client.websocket_connect(
            f"/api/v1/pedidos/ws/pedidos?token={admin_token}"
        ) as ws:
            ws.send_text(json.dumps({"action": "subscribe-order", "pedido_id": 1}))
            data = ws.receive_json()
            assert data["event"] == "SUBSCRIBED"
            assert data["data"]["pedido_id"] == 1

    def test_ws_cliente_pedido_ajeno(self, client, client_token):
        """Cliente suscribe a pedido que no le pertenece → recibe ERROR."""
        with client.websocket_connect(
            f"/api/v1/pedidos/ws/pedidos?token={client_token}"
        ) as ws:
            ws.send_text(json.dumps({"action": "subscribe-order", "pedido_id": 99999}))
            data = ws.receive_json()
            assert data["event"] == "ERROR"
