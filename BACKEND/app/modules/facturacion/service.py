import secrets
from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.core.pedido_fsm import ESTADO_CANCELADO
from app.modules.dominio_3.pedidos.models import Pedido
from app.modules.facturacion.adapters.base import FacturacionError
from app.modules.facturacion.adapters.mock import MockFacturador
from app.modules.facturacion.adapters.wsfe import WsfeFacturador
from app.modules.facturacion.models import ComprobanteFiscal, ConfigFiscal, now_utc
from app.modules.facturacion.schemas import ComprobanteRead, ConfigFiscalRead, ConfigFiscalUpdate


def _adapter_for(config: ConfigFiscal):
    if config.adapter == "wsfe":
        return WsfeFacturador()
    return MockFacturador()


class FacturacionService:
    def __init__(self, session: Session):
        self.session = session

    def get_config(self) -> ConfigFiscalRead:
        row = self._config()
        return ConfigFiscalRead.model_validate(row)

    def update_config(self, data: ConfigFiscalUpdate) -> ConfigFiscalRead:
        row = self._config()
        row.cuit = data.cuit.replace("-", "").strip()[:11]
        row.razon_social = data.razon_social.strip()
        row.punto_venta = data.punto_venta
        row.condicion_iva = data.condicion_iva
        row.adapter = data.adapter
        row.habilitado = data.habilitado
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return ConfigFiscalRead.model_validate(row)

    def get_comprobante_pedido(self, pedido_id: int) -> ComprobanteRead | None:
        row = self.session.exec(
            select(ComprobanteFiscal).where(ComprobanteFiscal.pedido_id == pedido_id)
        ).first()
        return ComprobanteRead.model_validate(row) if row else None

    def emitir_para_pedido(self, pedido_id: int) -> ComprobanteRead:
        config = self._config()
        if not config.habilitado:
            raise HTTPException(status_code=400, detail="Facturación no habilitada para este local")

        existente = self.session.exec(
            select(ComprobanteFiscal).where(ComprobanteFiscal.pedido_id == pedido_id)
        ).first()
        if existente and existente.estado == "AUTORIZADO":
            return ComprobanteRead.model_validate(existente)

        pedido = self.session.get(Pedido, pedido_id)
        if not pedido or pedido.deleted_at:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        if pedido.estado_codigo == ESTADO_CANCELADO:
            raise HTTPException(status_code=400, detail="No se factura un pedido cancelado")

        numero = self._siguiente_numero(config.punto_venta)
        idem = existente.idempotency_key if existente else secrets.token_hex(16)

        comp = existente or ComprobanteFiscal(
            pedido_id=pedido_id,
            numero=numero,
            importe_total=Decimal(str(pedido.total)).quantize(Decimal("0.01")),
            idempotency_key=idem,
            estado="PENDIENTE_CAE",
        )
        comp.updated_at = now_utc()
        self.session.add(comp)
        self.session.flush()

        try:
            result = _adapter_for(config).emitir(pedido, config, numero)
            comp.estado = "AUTORIZADO"
            comp.cae = result.cae
            comp.cae_vencimiento = result.cae_vencimiento
            comp.tipo_comprobante = result.tipo_comprobante
            comp.numero = result.numero
            comp.qr_payload = result.qr_payload
            comp.error_detalle = None
        except FacturacionError as e:
            comp.estado = "RECHAZADO"
            comp.error_detalle = str(e)
            self.session.add(comp)
            self.session.commit()
            raise HTTPException(status_code=502, detail=str(e)) from e

        self.session.add(comp)
        self.session.commit()
        self.session.refresh(comp)
        return ComprobanteRead.model_validate(comp)

    def _config(self) -> ConfigFiscal:
        row = self.session.exec(select(ConfigFiscal).order_by(ConfigFiscal.id)).first()
        if not row:
            row = ConfigFiscal()
            self.session.add(row)
            self.session.commit()
            self.session.refresh(row)
        return row

    def _siguiente_numero(self, punto_venta: int) -> int:
        last = self.session.exec(
            select(ComprobanteFiscal)
            .where(ComprobanteFiscal.numero > 0)
            .order_by(ComprobanteFiscal.numero.desc())
        ).first()
        return (last.numero + 1) if last else 1
