#!/usr/bin/env python
"""Aplica alembic upgrade head en cada tenant activo de la DB de control."""

import subprocess
import sys
from pathlib import Path

from sqlmodel import Session, select

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.control.db import get_control_engine
from app.control.models import Tenant, TenantStatus


def main() -> int:
    with Session(get_control_engine()) as session:
        tenants = session.exec(
            select(Tenant).where(Tenant.estado == TenantStatus.ACTIVE.value)
        ).all()

    if not tenants:
        print("No hay tenants activos en control")
        return 0

    ok: list[str] = []
    for tenant in tenants:
        print(f"Migrando {tenant.slug} ({tenant.db_name})...")
        env = {**dict(__import__("os").environ), "POSTGRES_DB": tenant.db_name}
        try:
            subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                cwd=ROOT,
                env=env,
                check=True,
            )
            ok.append(tenant.slug)
        except subprocess.CalledProcessError:
            print(f"ERROR en {tenant.slug}. Migrados hasta ahora: {', '.join(ok) or 'ninguno'}")
            return 1

    print(f"Listo: {', '.join(ok)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
