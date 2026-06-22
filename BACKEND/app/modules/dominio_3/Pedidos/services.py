from typing import Optional
from datetime import date, datetime, timezone
from decimal import Decimal
from fastapi import HTTPException, status
from app.core.unit_of_work import UnitOfWork
from app.modules.dominio_3.Pedidos.models import (
    Pedido, DetallePedido, HistorialEstadoPedido,
)
from app.modules.dominio_3.Pedidos.schemas import (
    PedidoCreate, PedidoRead, PedidoList,
    DetallePedidoRead, HistorialRead, AvanzarEstadoInput,AvanzarEstadoResult,PagoRead
)

TRANSICIONES = {
    "PENDIENTE": ["CONFIRMADO", "CANCELADO"],
    "CONFIRMADO": ["EN_PREP", "CANCELADO"],
    "EN_PREP": ["ENTREGADO", "CANCELADO"],
    "ENTREGADO": [],
    "CANCELADO": [],
}
TRANSICIONES_POR_ROL: dict[str, dict[str, list[str]]] = {
    "ADMIN": TRANSICIONES,
    "PEDIDOS": {
        "PENDIENTE": ["CONFIRMADO", "CANCELADO"],
        "CONFIRMADO": ["EN_PREP", "CANCELADO"],
        "EN_PREP": ["ENTREGADO", "CANCELADO"],
        "ENTREGADO": [],
        "CANCELADO": [],
    },
    "CLIENT": {
        "PENDIENTE": ["CANCELADO"],
        "CONFIRMADO": ["CANCELADO"],
        "EN_PREP": [],
        "ENTREGADO": [],
        "CANCELADO": [],
    },
}

EVENTOS_WS = {
    "PENDIENTE": "NUEVO_PEDIDO",
    "CONFIRMADO": "PEDIDO_CONFIRMADO",
    "EN_PREP": "PEDIDO_EN_PREPARACION",
    "ENTREGADO": "PEDIDO_ENTREGADO",
    "CANCELADO": "PEDIDO_CANCELADO",
}

ROLES_POR_ESTADO = {
    "PENDIENTE": ["ADMIN", "PEDIDOS", "CLIENT"],
    "CONFIRMADO": ["ADMIN", "PEDIDOS", "CLIENT"],
    "EN_PREP": ["ADMIN", "PEDIDOS", "CLIENT"],
    "ENTREGADO": ["ADMIN", "PEDIDOS", "CLIENT"],
    "CANCELADO": ["ADMIN", "PEDIDOS", "CLIENT"],
}

CANCELABLES_POR_CLIENTE = {"PENDIENTE", "CONFIRMADO"}


class PedidoService:
    """Lógica de negocio del módulo Pedidos.

    Gestiona el ciclo de vida completo: creación, listado, detalle,
    transiciones de estado (FSM 5 estados) y emisión de eventos
    WebSocket post-commit. Opera dentro del Unit of Work provisto
    por el router.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    # ── crear ────────────────────────────────────────────────────────────
    def crear(self, data: PedidoCreate, usuario_id: int) -> AvanzarEstadoResult:
        """Crea un pedido desde el carrito con snapshot de precios.

        RN-02: primer registro de historial con estado_desde=None.
        RN-04: total, nombre y precio son snapshots inmutables.
        """
        if not data.items:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El pedido debe tener al menos un ítem",
            )

        
        forma = self.uow.formas_pago.get_by_id(data.forma_pago_codigo)
        if not forma or not forma.habilitado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forma de pago inválida o no habilitada",
            )

       
        detalles_data = []
        subtotal = Decimal("0.00")

        for item in data.items:
            producto = self.uow.productos.get_by_id(item.producto_id)
            if not producto or not producto.disponible:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Producto {item.producto_id} no disponible",
                )
            if producto.stock_cantidad < item.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuficiente para '{producto.nombre}'. Disponible: {producto.stock_cantidad}",
                )
            precio_snap = Decimal(str(producto.precio_base))
            sub = precio_snap * item.cantidad
            subtotal += sub
            detalles_data.append({
                "producto_id":     item.producto_id,
                "cantidad":        item.cantidad,
                "nombre_snapshot": producto.nombre,   
                "precio_snapshot": precio_snap,       
                "subtotal":        sub,
                "personalizacion": item.personalizacion,
            })

        costo_envio = Decimal("50.00")
        descuento = Decimal("0.00")
        total = subtotal - descuento + costo_envio  

        
        pedido = Pedido(
            usuario_id=usuario_id,
            direccion_id=data.direccion_id,
            estado_codigo="PENDIENTE",
            forma_pago_codigo=data.forma_pago_codigo,
            subtotal=subtotal,
            descuento=descuento,
            costo_envio=costo_envio,
            total=total,
            notas=data.notas,
        )
        pedido = self.uow.pedidos.add(pedido)

       
        for d in detalles_data:
            self.uow.detalles.add(DetallePedido(pedido_id=pedido.id, **d))

        self.uow.historial.add(
            HistorialEstadoPedido(
                pedido_id=pedido.id,
                estado_desde=None,
                estado_hacia="PENDIENTE",
                usuario_id=usuario_id,
                motivo="Pedido creado",
            )
        )

        return AvanzarEstadoResult(
            pedido=self._to_read(pedido),
            estado_anterior=None,   # es la creación, no hay estado previo (RN-02)
        )
    def _rol_operativo(self, roles: list[str]) -> str:
        if "ADMIN" in roles:
            return "ADMIN"
        if "PEDIDOS" in roles:
            return "PEDIDOS"
        if "CLIENT" in roles:
            return "CLIENT"
        return "SIN_ROL"
        
    def avanzar_estado(
        self,
        pedido_id: int,
        nuevo_estado: str,
        actor_id: int,
        roles: list[str],
        data: AvanzarEstadoInput,
    ) -> AvanzarEstadoResult:
        """Avanza el estado del pedido según la FSM de 5 estados.

        Validaciones:
        - RN-01: estados terminales no admiten transiciones salientes.
        - RN-03: HistorialEstadoPedido es append-only (solo INSERT).
        - RN-05: motivo obligatorio si nuevo_estado = CANCELADO.
        - RBAC: cada rol tiene transiciones permitidas distintas.
        """
        pedido = self._get_o_404(pedido_id)

        estado_actual = pedido.estado_codigo

        # ── RN-01: validación explícita de es_terminal contra la BD ──────
        estado_obj = self.uow.estados.get_by_codigo(estado_actual)
        if estado_obj and estado_obj.es_terminal:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"No se puede avanzar desde el estado terminal '{estado_actual}'",
            )

        rol = self._rol_operativo(roles)

        permitidos = TRANSICIONES_POR_ROL.get(rol, {}).get(estado_actual, [])

        if nuevo_estado not in permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Transicion no permitida para {rol}: {estado_actual} -> {nuevo_estado}",
            )

        if nuevo_estado == "CANCELADO" and not data.motivo:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El motivo es obligatorio al cancelar un pedido",
            )

        if rol == "CLIENT":
            if pedido.usuario_id != actor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No podes modificar un pedido de otro usuario",
                )
            if estado_actual not in CANCELABLES_POR_CLIENTE:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Solo podes cancelar desde PENDIENTE o CONFIRMADO",
                )

        estado_anterior     = pedido.estado_codigo
        pedido.estado_codigo = nuevo_estado
        pedido.updated_at = datetime.now(timezone.utc)

        self.uow.pedidos.update(pedido)

        self.uow.historial.add(
            HistorialEstadoPedido(
                pedido_id=pedido.id,
                estado_desde=estado_anterior,
                estado_hacia=nuevo_estado,
                usuario_id=actor_id,
                motivo=data.motivo,
            )
        )

        return AvanzarEstadoResult(
            pedido=self._to_read(pedido),
            estado_anterior=estado_anterior,
        )

    
    def listar(
        self,
        usuario_id: int,
        roles: list[str],
        offset: int,
        limit: int,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
        search: Optional[str] = None,
        estado: Optional[str] = None,
    ) -> PedidoList:
       
        es_admin = any(r in ["ADMIN", "PEDIDOS"] for r in roles)

        if es_admin:
            pedidos = self.uow.pedidos.get_all_activos(offset, limit, desde=desde, hasta=hasta, search=search, estado=estado)
            total   = self.uow.pedidos.count_all(desde=desde, hasta=hasta, search=search, estado=estado)
        else:
            pedidos = self.uow.pedidos.get_by_usuario(usuario_id, offset, limit, desde=desde, hasta=hasta, search=search)
            total   = self.uow.pedidos.count_by_usuario(usuario_id, desde=desde, hasta=hasta, search=search)

        return PedidoList(
            data=[self._to_read(p) for p in pedidos],
            total=total,
        )

    
    def obtener(self, pedido_id: int, usuario_id: int, roles: list[str]) -> PedidoRead:
        pedido = self._get_o_404(pedido_id)

        
        es_admin = any(r in ["ADMIN", "PEDIDOS"] for r in roles)
        if not es_admin and pedido.usuario_id != usuario_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="No tenés acceso a este pedido")

        return self._to_read(pedido)

   
    def historial(self, pedido_id: int) -> list[HistorialRead]:
        self._get_o_404(pedido_id)
        registros = self.uow.historial.get_by_pedido(pedido_id)
        return [
            HistorialRead(
                id=r.id,
                estado_desde=r.estado_desde,
                estado_hacia=r.estado_hacia,
                usuario_id=r.usuario_id,
                motivo=r.motivo,
                created_at=r.created_at,
            )
            for r in registros
        ]

    
    def _get_o_404(self, pedido_id: int) -> Pedido:
        pedido = self.uow.pedidos.get_by_id_con_detalles(pedido_id)
        if not pedido:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Pedido no encontrado")
        return pedido

    def _to_read(self, pedido: Pedido) -> PedidoRead:
        detalles = self.uow.detalles.get_by_pedido(pedido.id)
        pago_read: Optional[PagoRead] = None

        pago = self.uow.pagos.get_by_pedido_id(pedido.id)
        if pago:
            pago_read = PagoRead(
            id=pago.id,
            mp_payment_id=pago.mp_payment_id,
            mp_status=pago.mp_status,
            mp_status_detail=pago.mp_status_detail,
            transaction_amount=pago.transaction_amount,
            payment_method_id=pago.payment_method_id,
            external_reference=pago.external_reference,
            created_at=pago.created_at,
        )


        return PedidoRead(
            id=pedido.id,
            usuario_id=pedido.usuario_id,
            usuario_nombre=pedido.usuario.nombre if pedido.usuario else None,
            direccion_id=pedido.direccion_id,
            direccion=pedido.direccion,
            estado_codigo=pedido.estado_codigo,
            forma_pago_codigo=pedido.forma_pago_codigo,
            subtotal=pedido.subtotal,
            descuento=pedido.descuento,
            costo_envio=pedido.costo_envio,
            total=pedido.total,
            notas=pedido.notas,
            created_at=pedido.created_at,
            detalles=[
                DetallePedidoRead(
                    producto_id=d.producto_id,
                    cantidad=d.cantidad,
                    nombre_snapshot=d.nombre_snapshot,
                    precio_snapshot=d.precio_snapshot,
                    subtotal=d.subtotal,
                    personalizacion=d.personalizacion,
                )
                for d in detalles
            ],
            pago=pago_read,
        )
    def listar_por_estados(
        self, estados: list[str], offset: int, limit: int,
        desde: Optional[date] = None, hasta: Optional[date] = None,
        search: Optional[str] = None,
    ) -> PedidoList:
        pedidos = self.uow.pedidos.get_by_estados(estados, offset, limit, desde=desde, hasta=hasta, search=search)

        return PedidoList(
            data=[self._to_read(p) for p in pedidos],
            total=self.uow.pedidos.count_by_estados(estados, desde=desde, hasta=hasta, search=search),
        )
    def listar_cocina(
        self, offset: int, limit: int,
        desde: Optional[date] = None, hasta: Optional[date] = None,
        search: Optional[str] = None,
    ) -> PedidoList:
        return self.listar_por_estados(
            estados=["CONFIRMADO", "EN_PREP"],
            offset=offset, limit=limit,
            desde=desde, hasta=hasta,
            search=search,
        )
    @staticmethod    
    async def emitir_evento_estado_pedido(
        pedido: PedidoRead,
        estado_anterior: str | None,
        usuario_id: int | None,
        motivo: str | None,
    ) -> None:
        from app.core.ws_manager import ws_manager

        event = EVENTOS_WS.get(pedido.estado_codigo, "estado_cambiado")

        payload = ws_manager.make_event(
            event=event,
            pedido_id=pedido.id,
            estado_anterior=estado_anterior,
            estado_nuevo=pedido.estado_codigo,
            usuario_id=usuario_id,
            motivo=motivo,
            data=pedido.model_dump(mode="json"),
        )

        roles = ROLES_POR_ESTADO.get(pedido.estado_codigo, ["ADMIN", "PEDIDOS"])

        await ws_manager.broadcast_pedido(
            pedido_id=pedido.id,
            roles=roles,
            payload=payload,
        )
    
   
