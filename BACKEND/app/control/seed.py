"""Registra el local demo en la DB de control (modo multi)."""

import argparse

from sqlmodel import Session, select

from app.control.db import get_control_engine
from app.control.models import Tenant, TenantDomain, TenantStatus
from app.core.config import settings


def seed_demo_tenant(
    slug: str = "demo",
    nombre: str = "Local demo",
    db_name: str | None = None,
    host: str | None = None,
) -> None:
    db_name = db_name or settings.postgres_db

    with Session(get_control_engine()) as session:
        existing = session.exec(select(Tenant).where(Tenant.slug == slug)).first()
        if existing:
            print(f"Tenant '{slug}' ya existe (id={existing.id})")
            return

        tenant = Tenant(
            slug=slug,
            nombre=nombre,
            estado=TenantStatus.ACTIVE.value,
            db_name=db_name,
        )
        session.add(tenant)
        session.commit()
        session.refresh(tenant)

        if host:
            session.add(
                TenantDomain(tenant_id=tenant.id, host=host.lower(), is_primary=True)
            )
            session.commit()

        print(f"Tenant '{slug}' creado → DB {db_name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed DB de control (tenants)")
    parser.add_argument("--slug", default="demo")
    parser.add_argument("--nombre", default="Local demo")
    parser.add_argument("--db-name", default=None)
    parser.add_argument("--host", default=None, help="Dominio custom (ej. burger.localtest.me)")
    args = parser.parse_args()
    seed_demo_tenant(args.slug, args.nombre, args.db_name, args.host)


if __name__ == "__main__":
    main()
