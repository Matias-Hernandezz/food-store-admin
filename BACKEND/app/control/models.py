from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from sqlalchemy import Column, Numeric, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.control.metadata import control_metadata


class TenantStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"


class Tenant(SQLModel, table=True, metadata=control_metadata):
    __tablename__ = "tenants"

    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(max_length=64, unique=True, index=True)
    nombre: str = Field(max_length=120)
    estado: str = Field(default=TenantStatus.ACTIVE.value, max_length=20)
    db_name: str = Field(max_length=64)
    db_user: str | None = Field(default=None, max_length=64)
    db_password: str | None = Field(default=None, max_length=256)
    mp_access_token: str | None = Field(default=None, max_length=2048)
    mp_refresh_token: str | None = Field(default=None, max_length=2048)
    mp_webhook_secret: str | None = Field(default=None, max_length=256)
    mp_public_key: str | None = Field(default=None, max_length=128)
    mp_user_id: str | None = Field(default=None, max_length=64)
    mp_token_expires_at: datetime | None = Field(default=None)
    delivery_app_fee_percent: Decimal = Field(
        default=Decimal("30.00"),
        sa_column=Column(Numeric(5, 2), nullable=False, server_default="30.00"),
        description="% comisión estimada apps delivery para KPI ahorro",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TenantDomain(SQLModel, table=True, metadata=control_metadata):
    __tablename__ = "tenant_domains"
    __table_args__ = (UniqueConstraint("host"),)

    id: int | None = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.id", index=True)
    host: str = Field(max_length=253, index=True)
    is_primary: bool = Field(default=False)
