"""
Tests del módulo Direcciones — CRUD de DireccionEntrega por usuario.

Endpoints:
  POST   /api/v1/direcciones                → crear (autenticado)
  GET    /api/v1/direcciones                → listar (autenticado)
  PATCH  /api/v1/direcciones/{id}/principal  → marcar principal (autenticado)
  DELETE /api/v1/direcciones/{id}           → soft delete (autenticado)
"""

import pytest
from fastapi.testclient import TestClient

from tests.helpers import login_as


@pytest.fixture()
def client_auth(client: TestClient, client_user):
    """Loguea como CLIENT."""
    login_as(client, client_user["email"], client_user["password"])


@pytest.fixture()
def direccion_payload():
    """Payload base para crear una dirección."""
    return {
        "alias": "Casa",
        "linea1": "Av. Siempre Viva 742",
        "linea2": "Dpto 4B",
        "ciudad": "Springfield",
        "provincia": "Buenos Aires",
        "codigo_postal": "1900",
    }


# ══════════════════════════════════════════════════════════════════════════════
# CREAR DIRECCIÓN
# ══════════════════════════════════════════════════════════════════════════════

class TestCrearDireccion:
    def test_crear_ok(self, client: TestClient, client_auth, direccion_payload):
        """POST /api/v1/direcciones → 201, DireccionRead."""
        res = client.post("/api/v1/direcciones", json=direccion_payload)
        assert res.status_code == 201
        data = res.json()
        assert data["alias"] == "Casa"
        assert data["ciudad"] == "Springfield"
        assert "id" in data

    def test_crear_sin_auth(self, client: TestClient, direccion_payload):
        """POST /api/v1/direcciones sin token → 401."""
        res = client.post("/api/v1/direcciones", json=direccion_payload)
        assert res.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
# LISTAR DIRECCIONES
# ══════════════════════════════════════════════════════════════════════════════

class TestListarDirecciones:
    def test_listar_ok(self, client: TestClient, client_auth, direccion_payload):
        """GET /api/v1/direcciones → 200, lista de direcciones."""
        # Crear una para tener algo que listar
        client.post("/api/v1/direcciones", json=direccion_payload)

        res = client.get("/api/v1/direcciones")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_listar_sin_auth(self, client: TestClient):
        """GET /api/v1/direcciones sin token → 401."""
        res = client.get("/api/v1/direcciones")
        assert res.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
# ESTABLECER PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

class TestEstablecerPrincipal:
    def test_principal_ok(self, client: TestClient, client_auth, direccion_payload):
        """PATCH /api/v1/direcciones/{id}/principal → 200, es_principal=true."""
        # Crear dirección
        res = client.post("/api/v1/direcciones", json=direccion_payload)
        assert res.status_code == 201
        dir_id = res.json()["id"]

        # Marcar como principal
        res2 = client.patch(f"/api/v1/direcciones/{dir_id}/principal")
        assert res2.status_code == 200
        assert res2.json()["es_principal"] is True

    def test_principal_no_existe(self, client: TestClient, client_auth):
        """PATCH /api/v1/direcciones/99999/principal → 404."""
        res = client.patch("/api/v1/direcciones/99999/principal")
        assert res.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# ELIMINAR DIRECCIÓN
# ══════════════════════════════════════════════════════════════════════════════

class TestEliminarDireccion:
    def test_eliminar_ok(self, client: TestClient, client_auth, direccion_payload):
        """DELETE /api/v1/direcciones/{id} → 204, soft-deletea."""
        res = client.post("/api/v1/direcciones", json=direccion_payload)
        assert res.status_code == 201
        dir_id = res.json()["id"]

        res2 = client.delete(f"/api/v1/direcciones/{dir_id}")
        assert res2.status_code == 204

        # Verificar que ya no aparece en listado
        res3 = client.get("/api/v1/direcciones")
        assert all(d["id"] != dir_id for d in res3.json())
