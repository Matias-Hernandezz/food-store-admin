#!/usr/bin/env python
"""
Carga access token y webhook secret de Mercado Pago en la DB de control.

Uso:
  python scripts/set_mp_tokens.py --slug demo --access-token TEST-... --webhook-secret ...
"""

import argparse
import sys
from pathlib import Path

from sqlmodel import Session, select

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.control.db import get_control_engine
from app.control.models import Tenant
from app.core.mercado_pago.token_cipher import encrypt_secret


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", required=True)
    parser.add_argument("--access-token", required=True)
    parser.add_argument("--webhook-secret", default="")
    args = parser.parse_args()

    with Session(get_control_engine()) as session:
        tenant = session.exec(select(Tenant).where(Tenant.slug == args.slug)).first()
        if not tenant:
            print(f"No existe tenant '{args.slug}' en control")
            return 1
        tenant.mp_access_token = encrypt_secret(args.access_token.strip())
        wh = (args.webhook_secret or "").strip()
        tenant.mp_webhook_secret = encrypt_secret(wh) if wh else None
        session.add(tenant)
        session.commit()

    print(f"MP configurado para '{args.slug}'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
