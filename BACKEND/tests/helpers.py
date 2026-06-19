"""
Helpers compartidos entre tests.
"""
from fastapi.testclient import TestClient


def login_as(client: TestClient, email: str, password: str) -> None:
    """Hace login. Las cookies quedan automáticamente en el TestClient (httpx)."""
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login falló ({email}): {res.json()}"
