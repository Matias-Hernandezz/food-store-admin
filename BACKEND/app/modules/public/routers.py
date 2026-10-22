from fastapi import APIRouter, Depends, Request, WebSocket, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.rate_limit import limiter
from app.modules.dominio_3.pedidos.schemas import FormaPagoRead
from app.modules.dominio_3.pedidos.services import PedidoService
from app.modules.dominio_3.pedidos.unit_of_work import PedidoUnitOfWork
from app.modules.public.schemas import (
    PublicCatalogoRead,
    PublicHistorialRead,
    PublicPedidoCreate,
    PublicPedidoCreated,
    PublicSeguimientoRead,
    PublicTiendaRead,
)
from app.modules.public.services import PublicApiService
from app.modules.public.ws_handler import handle_seguimiento

router = APIRouter(prefix="/api/v1/public", tags=["API pública"])


def _svc(session: Session = Depends(get_session)) -> PublicApiService:
    return PublicApiService(session)


@router.get("/tienda", response_model=PublicTiendaRead)
@limiter.limit("120/minute")
def estado_tienda(request: Request, svc: PublicApiService = Depends(_svc)):
    return svc.tienda()


@router.get("/catalogo", response_model=PublicCatalogoRead)
@limiter.limit("120/minute")
def catalogo(request: Request, svc: PublicApiService = Depends(_svc)):
    return svc.catalogo()


@router.get("/formas-pago", response_model=list[FormaPagoRead])
@limiter.limit("60/minute")
def formas_pago(request: Request, session: Session = Depends(get_session)):
    with PedidoUnitOfWork(session) as uow:
        return uow.formas_pago.get_habilitadas()


@router.post(
    "/pedidos",
    response_model=PublicPedidoCreated,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("15/minute")
async def crear_pedido_publico(
    request: Request,
    data: PublicPedidoCreate,
    svc: PublicApiService = Depends(_svc),
):
    created = svc.crear_pedido(data)

    with PedidoUnitOfWork(svc.session) as uow:
        pedido = uow.pedidos.get_by_id_con_detalles(created.pedido_id)
        pedido_read = PedidoService(uow)._to_read(pedido)

    await PedidoService.emitir_evento_estado_pedido(
        pedido=pedido_read,
        estado_anterior=None,
        usuario_id=None,
        motivo="Pedido público creado",
    )

    return created


@router.get("/pedidos/seguimiento/{tracking_token}", response_model=PublicSeguimientoRead)
@limiter.limit("90/minute")
def seguimiento_pedido(
    request: Request,
    tracking_token: str,
    svc: PublicApiService = Depends(_svc),
):
    return svc.seguimiento(tracking_token)


@router.get(
    "/pedidos/seguimiento/{tracking_token}/historial",
    response_model=list[PublicHistorialRead],
)
@limiter.limit("90/minute")
def historial_seguimiento(
    request: Request,
    tracking_token: str,
    svc: PublicApiService = Depends(_svc),
):
    return svc.historial_seguimiento(tracking_token)


@router.websocket("/ws/seguimiento/{tracking_token}")
async def ws_seguimiento(
    websocket: WebSocket,
    tracking_token: str,
    db: Session = Depends(get_session),
):
    await handle_seguimiento(websocket, db, tracking_token)
