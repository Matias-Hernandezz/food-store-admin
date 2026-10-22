from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.db import get_session
from app.core.deps import get_active_user, require_role
from app.modules.dominio_1.usuarios.models import Usuario
from app.modules.facturacion.schemas import ComprobanteRead, ConfigFiscalRead, ConfigFiscalUpdate
from app.modules.facturacion.service import FacturacionService

router = APIRouter(
    prefix="/api/v1/facturacion",
    tags=["Facturación"],
    dependencies=[Depends(require_role(["OWNER"]))],
)


@router.get("/config", response_model=ConfigFiscalRead)
def obtener_config(
    _user: Annotated[Usuario, Depends(get_active_user)],
    session: Session = Depends(get_session),
):
    return FacturacionService(session).get_config()


@router.put("/config", response_model=ConfigFiscalRead)
def guardar_config(
    body: ConfigFiscalUpdate,
    _user: Annotated[Usuario, Depends(get_active_user)],
    session: Session = Depends(get_session),
):
    return FacturacionService(session).update_config(body)


@router.get("/pedidos/{pedido_id}", response_model=ComprobanteRead | None)
def comprobante_pedido(
    pedido_id: int,
    _user: Annotated[Usuario, Depends(get_active_user)],
    session: Session = Depends(get_session),
):
    return FacturacionService(session).get_comprobante_pedido(pedido_id)


@router.post("/pedidos/{pedido_id}/emitir", response_model=ComprobanteRead)
def emitir_comprobante(
    pedido_id: int,
    _user: Annotated[Usuario, Depends(get_active_user)],
    session: Session = Depends(get_session),
):
    return FacturacionService(session).emitir_para_pedido(pedido_id)
