from unittest.mock import MagicMock

import pytest
from fastapi import Request

from app.core.config import settings
from app.core.tenant.resolver import resolve_slug_from_request, tenant_database_url
from app.control.models import Tenant


def test_resolve_slug_from_header():
    request = MagicMock(spec=Request)
    request.headers = {"x-tenant-slug": "burger", "host": "localhost:8000"}
    assert resolve_slug_from_request(request) == "burger"


def test_resolve_slug_from_subdomain(monkeypatch):
    monkeypatch.setattr(settings, "tenant_base_domain", "foodstore.local")
    request = MagicMock(spec=Request)
    request.headers = {"host": "burger.foodstore.local:8000"}
    assert resolve_slug_from_request(request) == "burger"


def test_tenant_database_url_uses_settings_password():
    tenant = Tenant(slug="x", nombre="X", db_name="tenant_x", estado="ACTIVE")
    url = tenant_database_url(tenant)
    assert url.endswith("/tenant_x")
    assert settings.postgres_user in url
