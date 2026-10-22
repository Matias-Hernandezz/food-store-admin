import cloudinary
from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_user:     str = "postgres"
    postgres_password: str = "postgres"
    postgres_db:       str = "db-parcial-1"
    postgres_host:     str = "localhost"
    postgres_port:     int = 5432

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    control_postgres_db: str = "foodstore_control"

    @computed_field
    @property
    def CONTROL_DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.control_postgres_db}"
        )

    # legacy = una sola DB (comportamiento actual); multi = resolver por slug/dominio
    tenant_mode: str = "legacy"
    default_tenant_slug: str = ""
    tenant_base_domain: str = ""

    public_tienda_abierta: bool = True

    # ── Seguridad ────────────────────────────────────────────────────────
    SECURE_COOKIES: bool = False   # True en producción (requiere HTTPS)
    SECRET_KEY: str
    ALGORITHM:  str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS ──────────────────────────────────────────────────────────────
    cors_origins: str = "http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174,http://client.localtest.me:5174,http://admin.localtest.me:5173"

    # ── MercadoPago ──────────────────────────────────────────────────────
    MP_ACCESS_TOKEN: str = ""
    MP_WEBHOOK_SECRET: str = ""   # clave secreta para validar firma del webhook
    MP_NOTIFICATION_URL: str = ""
    api_public_base_url: str = ""
    mp_app_id: str = ""
    mp_client_secret: str = ""
    mp_oauth_redirect_uri: str = ""
    mp_oauth_admin_return_url: str = "http://localhost:5175"
    mp_token_encryption_key: str = ""

    # ── Redis (WebSocket multi-worker; vacío = solo proceso) ─────────────
    redis_url: str = ""
    redis_ws_channel: str = "foodstore:ws"

    # ── Cloudinary ───────────────────────────────────────────────────────
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY:    str = ""
    CLOUDINARY_API_SECRET: str = ""

    model_config = {
        "env_file":          ".env",
        "env_file_encoding": "utf-8",
        "extra":             "ignore",
    }


settings = Settings()

# Inicializar SDK de Cloudinary al arrancar el módulo
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)
