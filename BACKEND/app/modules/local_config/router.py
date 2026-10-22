from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.db import get_session
from app.core.deps import get_active_user, require_role
from app.modules.dominio_1.usuarios.models import Usuario
from decimal import Decimal

from app.modules.local_config.delivery_fee import get_delivery_fee_admin, set_delivery_fee_admin
from app.modules.local_config.zonas_service import ZonasEnvioService
from app.modules.local_config.schemas import (
    DeliveryFeeRead,
    DeliveryFeeUpdate,
    HorariosEstadoRead,
    HorariosUpdateRequest,
    ZonasEnvioListRead,
    ZonasEnvioReplaceRequest,
)
from app.modules.local_config.service import HorariosService

router = APIRouter(
    prefix="/api/v1/config",
    tags=["Configuración local"],
    dependencies=[Depends(require_role(["OWNER"]))],
)


@router.get("/horarios", response_model=HorariosEstadoRead)
def obtener_horarios(
    _user: Annotated[Usuario, Depends(get_active_user)],
    session: Session = Depends(get_session),
):
    return HorariosService(session).get_admin()


@router.put("/horarios", response_model=HorariosEstadoRead)
def guardar_horarios(
    body: HorariosUpdateRequest,
    _user: Annotated[Usuario, Depends(get_active_user)],
    session: Session = Depends(get_session),
):
    try:
        return HorariosService(session).replace_all(body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/delivery-fee", response_model=DeliveryFeeRead)
def obtener_delivery_fee(
    _user: Annotated[Usuario, Depends(get_active_user)],
):
    return get_delivery_fee_admin()


@router.put("/delivery-fee", response_model=DeliveryFeeRead)
def guardar_delivery_fee(
    body: DeliveryFeeUpdate,
    _user: Annotated[Usuario, Depends(get_active_user)],
):
    try:
        return set_delivery_fee_admin(Decimal(str(body.delivery_app_fee_percent)))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/zonas-envio", response_model=ZonasEnvioListRead)
def obtener_zonas_envio(
    _user: Annotated[Usuario, Depends(get_active_user)],
    session: Session = Depends(get_session),
):
    return ZonasEnvioService(session).list_admin()


@router.put("/zonas-envio", response_model=ZonasEnvioListRead)
def guardar_zonas_envio(
    body: ZonasEnvioReplaceRequest,
    _user: Annotated[Usuario, Depends(get_active_user)],
    session: Session = Depends(get_session),
):
    try:
        return ZonasEnvioService(session).replace_all(body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
