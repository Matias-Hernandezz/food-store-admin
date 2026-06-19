"""
Tests del módulo Uploads — Cloudinary (con mocks)
"""

from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from tests.helpers import login_as


@pytest.fixture()
def admin_auth(client: TestClient, admin_user):
    login_as(client, admin_user["email"], admin_user["password"])


class TestUpload:
    def test_upload_imagen_ok(self, client, admin_auth):
        """POST /api/v1/uploads/imagen → 201, CloudinaryResponse."""
        fake_image = BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

        mock_result = {
            "secure_url": "https://res.cloudinary.com/demo/image/upload/v1/test.jpg",
            "public_id": "foodstore/test_abc123",
            "width": 800, "height": 600, "format": "jpg", "resource_type": "image",
        }
        with patch("cloudinary.uploader.upload", return_value=mock_result):
            res = client.post("/api/v1/uploads/imagen", files={
                "file": ("test.jpg", fake_image, "image/jpeg"),
            }, data={"folder": "foodstore"})

        assert res.status_code == 201, res.text
        data = res.json()
        assert data["secure_url"] == mock_result["secure_url"]
        assert data["public_id"] == mock_result["public_id"]
        assert data["width"] == 800
        assert data["height"] == 600

    def test_upload_formato_invalido(self, client, admin_auth):
        """POST /api/v1/uploads/imagen con text/plain → 400."""
        fake_text = BytesIO(b"esto no es una imagen")

        res = client.post("/api/v1/uploads/imagen", files={
            "file": ("doc.txt", fake_text, "text/plain"),
        }, data={"folder": "foodstore"})

        assert res.status_code == 400
        assert "formato" in res.json()["detail"].lower()

    def test_upload_excede_tamano(self, client, admin_auth):
        """POST /api/v1/uploads/imagen > 5 MB → 400."""
        big_data = BytesIO(b"\x00" * (6 * 1024 * 1024))

        res = client.post("/api/v1/uploads/imagen", files={
            "file": ("big.jpg", big_data, "image/jpeg"),
        }, data={"folder": "foodstore"})

        assert res.status_code == 400

    def test_upload_sin_auth(self, client):
        """POST /api/v1/uploads/imagen sin login → 401."""
        fake = BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

        res = client.post("/api/v1/uploads/imagen", files={
            "file": ("test.png", fake, "image/png"),
        }, data={"folder": "foodstore"})

        assert res.status_code == 401


class TestDelete:
    def test_delete_imagen_ok(self, client, admin_auth):
        """DELETE /api/v1/uploads/imagen/{public_id} → 204."""
        with patch("cloudinary.uploader.destroy", return_value={"result": "ok"}):
            res = client.delete("/api/v1/uploads/imagen/test_abc123")

        assert res.status_code == 204

    def test_delete_sin_auth(self, client):
        """DELETE sin login → 401."""
        res = client.request("DELETE", "/api/v1/uploads/imagen/test_abc123")
        assert res.status_code == 401
