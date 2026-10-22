from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.db import get_session
from app.core.deps import get_active_user, require_role
from app.modules.dominio_1.usuarios.models import Usuario
from app.modules.local_config.schemas import HorariosEstadoRead, HorariosUpdateRequest
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
