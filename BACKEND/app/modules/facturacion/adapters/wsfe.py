"""Adaptador WSFE homologación/producción (requiere certificados X.509)."""

from pathlib import Path

from app.core.config import settings
from app.modules.dominio_3.pedidos.models import Pedido
from app.modules.facturacion.adapters.base import EmisionResult, FacturacionError, Facturador
from app.modules.facturacion.models import ConfigFiscal


class WsfeFacturador(Facturador):
    """
    Integración directa WSAA + WSFEv1.
    Sin certificados configurados, falla con mensaje claro (no emite en producción por error).
    """

    def emitir(self, pedido: Pedido, config: ConfigFiscal, numero: int) -> EmisionResult:
        cert = Path(settings.arca_cert_path or "")
        key = Path(settings.arca_key_path or "")
        if not cert.is_file() or not key.is_file():
            raise FacturacionError(
                "WSFE: configurá ARCA_CERT_PATH y ARCA_KEY_PATH con el certificado del local. "
                "Usá adapter=mock en homologación sin certificados."
            )

        if settings.arca_ambiente not in ("homologacion", "produccion"):
            raise FacturacionError("ARCA_AMBIENTE debe ser homologacion o produccion")

        raise FacturacionError(
            "WSFE: certificados detectados pero la llamada SOAP aún no está cableada en este entorno. "
            "Usá adapter=mock para pruebas de flujo; completá WSFE con tu contador en homologación AFIP."
        )
