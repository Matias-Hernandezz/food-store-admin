"""OAuth Mercado Pago por tenant."""

from unittest.mock import AsyncMock, patch

import pytest
from sqlmodel import Session, select

from app.control.models import Tenant, TenantStatus
from app.core.config import settings
from app.core.mercado_pago.oauth import build_oauth_state, parse_oauth_state, save_oauth_tokens
from app.core.mercado_pago.token_cipher import decrypt_secret, encrypt_secret
from tests.conftest import test_engine

@pytest.fixture()
def control_schema():
    from app.control.models import Tenant as T

    T.metadata.create_all(test_engine)
    yield
    T.metadata.drop_all(test_engine)


@pytest.fixture()
def mp_oauth_settings(monkeypatch):
    monkeypatch.setattr(settings, "mp_app_id", "test-app-id")
    monkeypatch.setattr(settings, "mp_client_secret", "test-secret")
    monkeypatch.setattr(settings, "mp_oauth_redirect_uri", "http://test/callback")


@pytest.fixture()
def demo_tenant(control_schema):
    with Session(test_engine) as s:
        s.add(
            Tenant(
                slug="demo",
                nombre="Demo",
                estado=TenantStatus.ACTIVE.value,
                db_name="foodstore_test",
            )
        )
        s.commit()


def test_oauth_state_roundtrip(mp_oauth_settings):
    state = build_oauth_state("demo")
    assert parse_oauth_state(state) == "demo"


def test_encrypt_decrypt_roundtrip():
    enc = encrypt_secret("TEST-ACCESS")
    assert decrypt_secret(enc) == "TEST-ACCESS"


def test_save_oauth_tokens_encripta(control_schema, demo_tenant):
    save_oauth_tokens(
        "demo",
        {
            "access_token": "TEST-ACCESS-123",
            "refresh_token": "TEST-REFRESH",
            "expires_in": 3600,
            "user_id": 999,
            "public_key": "TEST-PUB",
        },
    )
    with Session(test_engine) as s:
        tenant = s.exec(select(Tenant).where(Tenant.slug == "demo")).first()
    assert tenant is not None
    assert decrypt_secret(tenant.mp_access_token) == "TEST-ACCESS-123"
    assert tenant.mp_user_id == "999"


def test_build_authorize_url_contains_client(mp_oauth_settings):
    from app.core.mercado_pago.oauth import build_authorize_url

    url = build_authorize_url("demo")
    assert "test-app-id" in url
    assert "auth.mercadopago.com" in url


@pytest.mark.asyncio
async def test_callback_guarda_tokens(demo_tenant, mp_oauth_settings):
    from app.modules.integrations.mp_router import mp_oauth_callback

    state = build_oauth_state("demo")
    mock_response = {
        "access_token": "AT-OK",
        "refresh_token": "RT-OK",
        "expires_in": 1800,
        "user_id": 1,
        "public_key": "PUB",
    }
    with patch(
        "app.modules.integrations.mp_router.exchange_authorization_code",
        new=AsyncMock(return_value=mock_response),
    ):
        res = await mp_oauth_callback(code="auth-code", state=state, error=None)
    assert res.status_code == 302
    with Session(test_engine) as s:
        tenant = s.exec(select(Tenant).where(Tenant.slug == "demo")).first()
    assert decrypt_secret(tenant.mp_access_token) == "AT-OK"
