from decimal import Decimal

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.core.config import settings
from app.core.pedido_fsm import ESTADO_CONFIRMADO, ESTADO_PENDIENTE, TIPO_DINE_IN
from app.core.security import hash_password
from app.modules.caja.models import TurnoCaja, now_utc
from app.modules.caja.schemas import (
    AbrirTurnoInput,
    CerrarTurnoInput,
    PedidoMostradorInput,
    PedidoMostradorResult,
    TurnoCajaRead,
)
from app.modules.dominio_1.usuarios.models import Usuario, UsuarioRol
from app.modules.dominio_1.usuarios.repository import UsuarioRepository, UsuarioRolRepository
from app.modules.dominio_3.pedidos.models import Pedido
from app.modules.dominio_3.pedidos.schemas import AvanzarEstadoInput, PedidoCreate, PedidoRead
from app.modules.dominio_3.pedidos.services import PedidoService
from app.modules.dominio_3.pedidos.unit_of_work import PedidoUnitOfWork


class CajaService:
    def __init__(self, session: Session):
        self.session = session

    def turno_actual(self) -> TurnoCajaRead | None:
        turno = self._turno_abierto()
        if not turno:
            return None
        return self._to_read(turno)

    def abrir_turno(self, usuario_id: int, data: AbrirTurnoInput) -> TurnoCajaRead:
        if self._turno_abierto():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya hay un turno abierto")
        turno = TurnoCaja(
            estado="OPEN",
            usuario_apertura_id=usuario_id,
            fondo_inicial=Decimal(str(data.fondo_inicial)).quantize(Decimal("0.01")),
        )
        self.session.add(turno)
        self.session.commit()
        self.session.refresh(turno)
        return self._to_read(turno)

    def cerrar_turno(self, usuario_id: int, data: CerrarTurnoInput) -> TurnoCajaRead:
        turno = self._turno_abierto()
        if not turno:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No hay turno abierto")

        efectivo_pedidos = self._sum_efectivo_turno(turno.id)
        esperado = turno.fondo_inicial + efectivo_pedidos
        turno.estado = "CLOSED"
        turno.usuario_cierre_id = usuario_id
        turno.efectivo_esperado = esperado.quantize(Decimal("0.01"))
        turno.efectivo_contado = Decimal(str(data.efectivo_contado)).quantize(Decimal("0.01"))
        turno.notas_cierre = data.notas_cierre
        turno.cerrado_en = now_utc()
        self.session.add(turno)
        self.session.commit()
        self.session.refresh(turno)
        return self._to_read(turno)

    async def crear_pedido_mostrador(self, user: Usuario, data: PedidoMostradorInput) -> PedidoMostradorResult:
        turno = self._turno_abierto()
        if not turno:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Abrí un turno de caja antes de cargar pedidos de mostrador",
            )

        cliente_id = self._get_mostrador_cliente_id()
        roles = [r.codigo for r in user.roles]

        pedido_create = PedidoCreate(
            items=data.items,
            forma_pago_codigo=data.forma_pago_codigo,
            tipo_pedido=TIPO_DINE_IN,
            direccion_id=None,
            notas=data.notas,
        )

        with PedidoUnitOfWork(self.session) as uow:
            result = PedidoService(uow).crear(
                pedido_create,
                cliente_id,
                turno_caja_id=turno.id,
            )
            pedido_read = result.pedido
            estado_anterior = result.estado_anterior

            if data.confirmar_pago and pedido_read.estado_codigo == "PENDIENTE":
                avance = PedidoService(uow).avanzar_estado(
                    pedido_id=pedido_read.id,
                    nuevo_estado=ESTADO_CONFIRMADO,
                    actor_id=user.id,
                    roles=roles,
                    data=AvanzarEstadoInput(
                        nuevo_estado=ESTADO_CONFIRMADO,
                        motivo="Pago en mostrador",
                    ),
                )
                pedido_read = avance.pedido
                estado_anterior = avance.estado_anterior

        await PedidoService.emitir_evento_estado_pedido(
            pedido=pedido_read,
            estado_anterior=estado_anterior,
            usuario_id=user.id,
            motivo=None,
        )

        return PedidoMostradorResult(pedido=pedido_read, turno_caja_id=turno.id)

    async def confirmar_cobro_pedido(self, user: Usuario, pedido_id: int) -> PedidoRead:
        turno = self._turno_abierto()
        if not turno:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Abrí un turno de caja antes de registrar cobros",
            )

        pedido = self.session.get(Pedido, pedido_id)
        if not pedido or pedido.deleted_at:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        if pedido.estado_codigo != ESTADO_PENDIENTE:
            raise HTTPException(status_code=400, detail="Solo se cobran pedidos en PENDIENTE")

        if not pedido.turno_caja_id:
            pedido.turno_caja_id = turno.id
            self.session.add(pedido)
            self.session.commit()

        roles = [r.codigo for r in user.roles]
        with PedidoUnitOfWork(self.session) as uow:
            result = PedidoService(uow).avanzar_estado(
                pedido_id=pedido_id,
                nuevo_estado=ESTADO_CONFIRMADO,
                actor_id=user.id,
                roles=roles,
                data=AvanzarEstadoInput(nuevo_estado=ESTADO_CONFIRMADO, motivo="Cobro en caja"),
            )

        await PedidoService.emitir_evento_estado_pedido(
            pedido=result.pedido,
            estado_anterior=result.estado_anterior,
            usuario_id=user.id,
            motivo="Cobro en caja",
        )
        return result.pedido

    def _turno_abierto(self) -> TurnoCaja | None:
        return self.session.exec(
            select(TurnoCaja).where(TurnoCaja.estado == "OPEN").order_by(TurnoCaja.id.desc())
        ).first()

    def _sum_efectivo_turno(self, turno_id: int) -> Decimal:
        rows = self.session.exec(
            select(Pedido).where(
                Pedido.turno_caja_id == turno_id,
                Pedido.forma_pago_codigo == "EFECTIVO",
                Pedido.deleted_at.is_(None),
            )
        ).all()
        return sum(Decimal(str(p.total)) for p in rows)

    def _to_read(self, turno: TurnoCaja) -> TurnoCajaRead:
        pedidos = self.session.exec(
            select(Pedido).where(Pedido.turno_caja_id == turno.id, Pedido.deleted_at.is_(None))
        ).all()
        efectivo = self._sum_efectivo_turno(turno.id)
        return TurnoCajaRead(
            id=turno.id,
            estado=turno.estado,
            abierto_en=turno.abierto_en,
            cerrado_en=turno.cerrado_en,
            usuario_apertura_id=turno.usuario_apertura_id,
            fondo_inicial=turno.fondo_inicial,
            efectivo_esperado=turno.efectivo_esperado,
            efectivo_contado=turno.efectivo_contado,
            notas_cierre=turno.notas_cierre,
            pedidos_turno=len(pedidos),
            total_efectivo_pedidos=efectivo,
        )

    def _get_mostrador_cliente_id(self) -> int:
        email = settings.mostrador_cliente_email.lower().strip()
        repo = UsuarioRepository(self.session)
        user = repo.get_by_email(email)
        if user and user.deleted_at is None:
            return user.id

        user = Usuario(
            nombre="Mostrador",
            apellido="Local",
            email=email,
            password_hash=hash_password("no-login-mostrador"),
        )
        repo.add(user)
        self.session.flush()
        UsuarioRolRepository(self.session).add(
            UsuarioRol(usuario_id=user.id, rol_codigo="CLIENT")
        )
        self.session.commit()
        return user.id
