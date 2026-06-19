"""
Tests del módulo Auth — Section 13.3 (Rubric)

Patrón: Arrange (crear usuario) → Act (endpoint) → Assert (status + body)
La autenticación usa login_as() del conftest.
"""

import pytest
from fastapi.testclient import TestClient

from tests.helpers import login_as


# ══════════════════════════════════════════════════════════════════════════════
# REGISTER
# ══════════════════════════════════════════════════════════════════════════════

class TestRegister:
    def test_register_ok(self, client: TestClient):
        """POST /api/v1/auth/register → 201 + UsuarioRead con rol CLIENT."""
        res = client.post("/api/v1/auth/register", json={
            "nombre": "Juan",
            "apellido": "Perez",
            "email": "juan@test.com",
            "password": "Secure1234!",
        })
        assert res.status_code == 201
        data = res.json()
        assert data["nombre"] == "Juan"
        assert data["apellido"] == "Perez"
        assert data["email"] == "juan@test.com"
        assert "CLIENT" in data["roles"]

    def test_register_email_duplicado(self, client: TestClient):
        """POST /api/v1/auth/register con email existente → 409."""
        body = {
            "nombre": "Pedro", "apellido": "Lopez",
            "email": "dup@test.com", "password": "Secure1234!",
        }
        assert client.post("/api/v1/auth/register", json=body).status_code == 201

        res = client.post("/api/v1/auth/register", json=body)
        assert res.status_code == 409
        assert "ya está registrado" in res.json()["detail"]

    def test_register_password_corta(self, client: TestClient):
        """POST /api/v1/auth/register con password < 8 chars → 422."""
        res = client.post("/api/v1/auth/register", json={
            "nombre": "Corto", "apellido": "Pass",
            "email": "corto@test.com", "password": "123",
        })
        assert res.status_code == 422

    def test_register_nombre_corto(self, client: TestClient):
        """POST /api/v1/auth/register con nombre < 2 chars → 422."""
        res = client.post("/api/v1/auth/register", json={
            "nombre": "A", "apellido": "Bc",
            "email": "short@test.com", "password": "Secure1234!",
        })
        assert res.status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════════════════════

class TestLogin:
    def test_login_ok(self, client: TestClient, admin_user):
        """POST /api/v1/auth/login → 200 + cookies + UsuarioRead."""
        res = client.post("/api/v1/auth/login", json={
            "email": admin_user["email"],
            "password": admin_user["password"],
        })
        assert res.status_code == 200
        data = res.json()
        assert data["email"] == admin_user["email"]
        assert "ADMIN" in data["roles"]
        assert "access_token" in res.headers.get("set-cookie", "")

    def test_login_credenciales_invalidas(self, client: TestClient, admin_user):
        """POST /api/v1/auth/login con password incorrecto → 401."""
        res = client.post("/api/v1/auth/login", json={
            "email": admin_user["email"],
            "password": "WrongPass123!",
        })
        assert res.status_code == 401

    def test_login_usuario_inexistente(self, client: TestClient):
        """POST /api/v1/auth/login con email no registrado → 401."""
        res = client.post("/api/v1/auth/login", json={
            "email": "noexiste@test.com", "password": "Whatever123!",
        })
        assert res.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
# LOGOUT + REFRESH
# ══════════════════════════════════════════════════════════════════════════════

class TestLogoutRefresh:
    def test_logout_revoca_refresh(self, client: TestClient, admin_user):
        """Logout revoca el refresh token → no se puede refrescar."""
        login_as(client, admin_user["email"], admin_user["password"])

        # Refresh antes del logout (debe funcionar)
        assert client.post("/api/v1/auth/refresh").status_code == 204

        # Logout
        assert client.post("/api/v1/auth/logout").status_code == 204

        # Refresh con token revocado → 401
        assert client.post("/api/v1/auth/refresh").status_code == 401

    def test_refresh_ok(self, client: TestClient, admin_user):
        """POST /api/v1/auth/refresh con cookie válida → 204 + nueva cookie."""
        login_as(client, admin_user["email"], admin_user["password"])

        res = client.post("/api/v1/auth/refresh")
        assert res.status_code == 204
        assert "access_token" in res.headers.get("set-cookie", "")


# ══════════════════════════════════════════════════════════════════════════════
# ME
# ══════════════════════════════════════════════════════════════════════════════

class TestMe:
    def test_me_autenticado(self, client: TestClient, admin_user):
        """GET /api/v1/auth/me → 200 + UsuarioRead."""
        login_as(client, admin_user["email"], admin_user["password"])

        res = client.get("/api/v1/auth/me")
        assert res.status_code == 200
        data = res.json()
        assert data["email"] == admin_user["email"]
        assert "ADMIN" in data["roles"]

    def test_me_sin_token(self, client: TestClient):
        """GET /api/v1/auth/me sin cookie → 401."""
        res = client.get("/api/v1/auth/me")
        assert res.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
# RATE LIMIT
# ══════════════════════════════════════════════════════════════════════════════

class TestRateLimit:
    def test_rate_limit_login(self, client: TestClient):
        """5+ intentos fallidos en 15 min → 429 Too Many Requests."""
        for _ in range(5):
            res = client.post("/api/v1/auth/login", json={
                "email": "noexiste@test.com", "password": "wrong",
            })
            assert res.status_code == 401

        res = client.post("/api/v1/auth/login", json={
            "email": "noexiste@test.com", "password": "wrong",
        })
        assert res.status_code == 429

    def test_rate_limit_register(self, client: TestClient):
        """5+ registros consecutivos desde misma IP → 429."""
        for i in range(5):
            res = client.post("/api/v1/auth/register", json={
                "nombre": "Rate", "apellido": "Limit",
                "email": f"ratelimit{i}@test.com",
                "password": "Secure1234!",
            })
            assert res.status_code == 201, f"Iteración {i}: {res.text}"

        res = client.post("/api/v1/auth/register", json={
            "nombre": "Rate", "apellido": "Limit",
            "email": "ratelimit_over@test.com",
            "password": "Secure1234!",
        })
        assert res.status_code == 429, f"Esperado 429, obtenido {res.status_code}"
