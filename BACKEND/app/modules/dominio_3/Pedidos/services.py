from app.modules.dominio_1.Usuarios.models import DireccionEntrega
from app.modules.dominio_1.Usuarios.schemas import DireccionCreate, DireccionRead
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status

from app.core.unit_of_work import UnitOfWork
from app.modules.dominio_3.Pedidos.models import (
    Pedido, DetallePedido, HistorialEstadoPedido,
)
from app.modules.dominio_3.Pedidos.schemas import (
    PedidoCreate, PedidoRead, PedidoList,
    DetallePedidoRead, HistorialRead, AvanzarEstadoInput,
)

TRANSICIONES: dict[str, list[str]] = {
    "PENDIENTE":  ["CONFIRMADO", "CANCELADO"],
    "CONFIRMADO": ["PREPARACION", "CANCELADO"],
    "PREPARACION":    ["ENVIADO"],
    "ENVIADO":  ["ENTREGADO"],
    "ENTREGADO":  [],  
    "CANCELADO":  [],   
}

#
CANCELABLES_POR_CLIENTE = {"PENDIENTE", "CONFIRMADO"}


class PedidoService:

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    
    def crear(self, data: PedidoCreate, usuario_id: int) -> PedidoRead:
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

        total = subtotal  

        
        pedido = Pedido(
            usuario_id=usuario_id,
            direccion_id=data.direccion_id,
            estado_codigo="PENDIENTE",
            forma_pago_codigo=data.forma_pago_codigo,
            subtotal=subtotal,
            descuento=Decimal("0.00"),
            costo_envio=Decimal("0.00"),
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

        return self._to_read(pedido)

    def avanzar_estado(
        self,
        pedido_id: int,
        nuevo_estado: str,
        actor_id: int,
        roles: list[str],
        data: AvanzarEstadoInput,
    ) -> PedidoRead:
        
        pedido = self._get_o_404(pedido_id)
        estado_actual = pedido.estado_codigo
        permitidos = TRANSICIONES.get(estado_actual, [])
        if nuevo_estado not in permitidos:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Transición inválida: {estado_actual} → {nuevo_estado}. "
                       f"Permitidos: {permitidos}",
            )

        
        if "CLIENT" in roles and not any(r in ["ADMIN", "PEDIDOS"] for r in roles):
            if nuevo_estado != "CANCELADO":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="El cliente solo puede cancelar su pedido",
                )
            if estado_actual not in CANCELABLES_POR_CLIENTE:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Solo podés cancelar desde PENDIENTE o CONFIRMADO. Estado actual: {estado_actual}",
                )

       
        estado_anterior = pedido.estado_codigo
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

        return self._to_read(pedido)

    
    def listar(
        self,
        usuario_id: int,
        roles: list[str],
        offset: int,
        limit: int,
    ) -> PedidoList:
       
        es_admin = any(r in ["ADMIN", "PEDIDOS"] for r in roles)

        if es_admin:
            pedidos = self.uow.pedidos.get_all_activos(offset, limit)
            total   = self.uow.pedidos.count_all()
        else:
            pedidos = self.uow.pedidos.get_by_usuario(usuario_id, offset, limit)
            total   = self.uow.pedidos.count_by_usuario(usuario_id)

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
        return PedidoRead(
            id=pedido.id,
            usuario_id=pedido.usuario_id,
            direccion_id=pedido.direccion_id,
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
        )

    def crear_direccion(self, usuario_id: int, data: DireccionCreate) -> DireccionRead:
        if not data.items:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El pedido debe tener al menos un ítem",
            )
        direccion = self.uow.direcciones.get_by_id(data.direccion_id)
        if not direccion or direccion.usuario_id != usuario_id or direccion.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La dirección seleccionada es inválida o no pertenece a tu cuenta.",
            )
        metodo_pago = self.uow.formas_pago.get_by_id(data.forma_pago_codigo)
        if not metodo_pago or not metodo_pago.habilitado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forma de pago inválida o no habilitada",
            )
        with self.uow:
            if data.es_principal:
                self.uow.direcciones.desmarcar_principal(usuario_id)
            
            nueva_dir = DireccionEntrega(**data.model_dump(), usuario_id=usuario_id)
            self.uow.direcciones.add(nueva_dir)
            return DireccionRead.model_validate(nueva_dir)

    def listar_direcciones(self, usuario_id: int) -> list[DireccionRead]:
        with self.uow:
            direcciones = self.uow.direcciones.get_by_usuario(usuario_id)
            return [DireccionRead.model_validate(d) for d in direcciones]