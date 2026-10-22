#!/usr/bin/env python
"""
Alta de un local: crea DB tenant_{slug}, migra esquema y registra en control.

Uso (desde BACKEND):
  python scripts/alta_local.py --slug burger --nombre "Burger Lab"
"""

import argparse
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlmodel import Session, select

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.control.db import get_control_engine
from app.control.models import Tenant, TenantDomain, TenantStatus
from app.core.config import settings


def _admin_engine():
    url = (
        f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
        f"@{settings.postgres_host}:{settings.postgres_port}/postgres"
    )
    return create_engine(url, isolation_level="AUTOCOMMIT")


def create_database(db_name: str) -> None:
    eng = _admin_engine()
    with eng.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :n"),
            {"n": db_name},
        ).scalar()
        if exists:
            print(f"DB {db_name} ya existe")
            return
        conn.execute(text(f'CREATE DATABASE "{db_name}"'))
        print(f"DB {db_name} creada")


def run_tenant_migrations(db_name: str) -> None:
    env = {
        **dict(__import__("os").environ),
        "POSTGRES_DB": db_name,
    }
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT,
        env=env,
        check=True,
    )


def register_tenant(slug: str, nombre: str, db_name: str, host: str | None) -> None:
    with Session(get_control_engine()) as session:
        if session.exec(select(Tenant).where(Tenant.slug == slug)).first():
            print(f"Tenant {slug} ya registrado en control")
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
            session.add(TenantDomain(tenant_id=tenant.id, host=host.lower(), is_primary=True))
            session.commit()
    print(f"Tenant {slug} registrado en control")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", required=True)
    parser.add_argument("--nombre", required=True)
    parser.add_argument("--host", default=None)
    parser.add_argument("--skip-migrate", action="store_true")
    parser.add_argument("--seed", action="store_true", help="Corre app.db.seed en la DB nueva")
    args = parser.parse_args()

    db_name = f"tenant_{args.slug.replace('-', '_')}"

    create_database(db_name)
    if not args.skip_migrate:
        run_tenant_migrations(db_name)
    if args.seed:
        env = {**dict(__import__("os").environ), "POSTGRES_DB": db_name}
        subprocess.run([sys.executable, "-m", "app.db.seed"], cwd=ROOT, env=env, check=True)

    register_tenant(args.slug, args.nombre, db_name, args.host)


if __name__ == "__main__":
    main()
