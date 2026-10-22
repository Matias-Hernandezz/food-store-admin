from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.modules.dominio_3.pedidos.models import Pedido
from app.modules.facturacion.models import ConfigFiscal


@dataclass(frozen=True)
class EmisionResult:
    cae: str
    cae_vencimiento: date
    numero: int
    tipo_comprobante: int
    qr_payload: str


class FacturacionError(Exception):
    pass


class Facturador:
    """Puerto de emisión electrónica (ARCA / WSFE)."""

    def emitir(self, pedido: Pedido, config: ConfigFiscal, numero: int) -> EmisionResult:
        raise NotImplementedError
