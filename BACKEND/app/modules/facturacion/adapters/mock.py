import base64
import json
from datetime import date, timedelta
from decimal import Decimal

from app.modules.dominio_3.pedidos.models import Pedido
from app.modules.facturacion.adapters.base import EmisionResult, Facturador
from app.modules.facturacion.models import ConfigFiscal


def _qr_payload(cuit: str, pto_vta: int, tipo: int, numero: int, importe: Decimal, cae: str) -> str:
    """URL AFIP QR (datos mínimos para demo / homologación visual)."""
    data = {
        "ver": 1,
        "fecha": date.today().isoformat(),
        "cuit": int(cuit),
        "ptoVta": pto_vta,
        "tipoCmp": tipo,
        "nroCmp": numero,
        "importe": float(importe),
        "moneda": "PES",
        "ctz": 1,
        "tipoDocRec": 99,
        "nroDocRec": 0,
        "tipoCodAut": "E",
        "codAut": int(cae) if cae.isdigit() else 0,
    }
    raw = base64.b64encode(json.dumps(data, separators=(",", ":")).encode()).decode()
    return f"https://www.afip.gob.ar/fe/qr/?p={raw}"


class MockFacturador(Facturador):
    def emitir(self, pedido: Pedido, config: ConfigFiscal, numero: int) -> EmisionResult:
        tipo = 11 if config.condicion_iva == "MONOTRIBUTO" else 6
        cae = f"7{numero:012d}"[:14]
        vto = date.today() + timedelta(days=10)
        qr = _qr_payload(config.cuit, config.punto_venta, tipo, numero, pedido.total, cae)
        return EmisionResult(
            cae=cae,
            cae_vencimiento=vto,
            numero=numero,
            tipo_comprobante=tipo,
            qr_payload=qr,
        )
