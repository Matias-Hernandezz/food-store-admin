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

    # ── JWT ──────────────────────────────────────────────────────────────
    SECRET_KEY: str
    ALGORITHM:  str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── MercadoPago ──────────────────────────────────────────────────────
    MP_ACCESS_TOKEN: str = ""
    MP_WEBHOOK_SECRET: str = ""   # clave secreta para validar firma del webhook
    MP_NOTIFICATION_URL: str = ""

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
