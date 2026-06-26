"""
Tests del módulo Usuarios — CRUD admin de usuarios + roles.

Endpoints:
  GET    /api/v1/usuarios               → listar (ADMIN)
  GET    /api/v1/usuarios?search=X       → búsqueda (ADMIN)
  PATCH  /api/v1/usuarios/{id}          → actualizar (ADMIN)
  DELETE /api/v1/usuarios/{id}          → soft delete (ADMIN)
  POST   /api/v1/usuarios/{id}/roles     → asignar rol (ADMIN)
  DELETE /api/v1/usuarios/{id}/roles/{r} → quitar rol (ADMIN)
"""

import pytest
from fastapi.testclient import TestClient

from tests.helpers import login_as


@pytest.fixture()
def admin_auth(client: TestClient, admin_user):
    """Loguea como ADMIN. Las cookies quedan en el TestClient."""
    login_as(client, admin_user["email"], admin_user["password"])


@pytest.fixture()
def client_auth(client: TestClient, client_user):
    """Loguea como CLIENT."""
    login_as(client, client_user["email"], client_user["password"])


# ══════════════════════════════════════════════════════════════════════════════
# LISTAR USUARIOS
# ══════════════════════════════════════════════════════════════════════════════

class TestListarUsuarios:
    def test_listar_admin_ok(self, client: TestClient, admin_auth):
        """GET /api/v1/usuarios → 200, lista de usuarios activos."""
        res = client.get("/api/v1/usuarios")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # al menos el admin_user

    def test_listar_con_search(self, client: TestClient, admin_auth, admin_user):
        """GET /api/v1/usuarios?search=admin → filtra por email."""
        res = client.get("/api/v1/usuarios?search=admin")
        assert res.status_code == 200
        data = res.json()
        assert any(u["email"] == admin_user["email"] for u in data)

    def test_listar_sin_auth(self, client: TestClient):
        """GET /api/v1/usuarios sin token → 401."""
        res = client.get("/api/v1/usuarios")
        assert res.status_code == 401

    def test_listar_cliente_no_admin(self, client: TestClient, client_auth):
        """GET /api/v1/usuarios con CLIENT → 403."""
        res = client.get("/api/v1/usuarios")
        assert res.status_code == 403


# ══════════════════════════════════════════════════════════════════════════════
# ACTUALIZAR USUARIO
# ══════════════════════════════════════════════════════════════════════════════

class TestActualizarUsuario:
    def test_actualizar_ok(self, client: TestClient, admin_auth, client_user):
        """PATCH /api/v1/usuarios/{id} → 200, actualiza nombre."""
        uid = client_user["id"]
        res = client.patch(f"/api/v1/usuarios/{uid}", json={
            "nombre": "Actualizado",
            "apellido": "TestMod",
        })
        assert res.status_code == 200
        data = res.json()
        assert data["nombre"] == "Actualizado"
        assert data["apellido"] == "TestMod"

    def test_actualizar_no_existe(self, client: TestClient, admin_auth):
        """PATCH /api/v1/usuarios/99999 → 404."""
        res = client.patch("/api/v1/usuarios/99999", json={"nombre": "XX"})
        assert res.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# SOFT DELETE USUARIO
# ══════════════════════════════════════════════════════════════════════════════

class TestSoftDeleteUsuario:
    def test_soft_delete_ok(self, client: TestClient, admin_auth, client_user):
        """DELETE /api/v1/usuarios/{id} → 204, soft-deletea."""
        uid = client_user["id"]
        res = client.delete(f"/api/v1/usuarios/{uid}")
        assert res.status_code == 204

        # Verificar que ya no aparece en listado activo
        res2 = client.get("/api/v1/usuarios")
        emails = [u["email"] for u in res2.json()]
        assert client_user["email"] not in emails

    def test_soft_delete_no_existe(self, client: TestClient, admin_auth):
        """DELETE /api/v1/usuarios/99999 → 404."""
        res = client.delete("/api/v1/usuarios/99999")
        assert res.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# ROLES
# ══════════════════════════════════════════════════════════════════════════════

class TestRoles:
    def test_asignar_rol_ok(self, client: TestClient, admin_auth, client_user):
        """POST /api/v1/usuarios/{id}/roles?rol_codigo=STOCK → 200."""
        uid = client_user["id"]
        res = client.post(f"/api/v1/usuarios/{uid}/roles?rol_codigo=STOCK")
        assert res.status_code == 200
        data = res.json()
        assert "STOCK" in data["roles"]
        assert "CLIENT" in data["roles"]  # sigue teniendo CLIENT

    def test_asignar_rol_inexistente(self, client: TestClient, admin_auth, client_user):
        """POST /api/v1/usuarios/{id}/roles?rol_codigo=NOSOY → 404."""
        uid = client_user["id"]
        res = client.post(f"/api/v1/usuarios/{uid}/roles?rol_codigo=NOSOY")
        assert res.status_code == 404

    def test_quitar_rol_ok(self, client: TestClient, admin_auth, client_user):
        """DELETE /api/v1/usuarios/{id}/roles/CLIENT → 200, quita CLIENT."""
        # Primero asignamos STOCK para no dejar al usuario sin roles
        uid = client_user["id"]
        client.post(f"/api/v1/usuarios/{uid}/roles?rol_codigo=STOCK")

        res = client.delete(f"/api/v1/usuarios/{uid}/roles/CLIENT")
        assert res.status_code == 200
        data = res.json()
        assert "CLIENT" not in data["roles"]
        assert "STOCK" in data["roles"]
