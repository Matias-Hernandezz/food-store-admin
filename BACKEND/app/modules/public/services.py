import secrets
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session

from app.core.config import settings
from app.core.geocoding import geocode_address
from app.core.security import hash_password
from app.modules.dominio_1.direcciones.models import DireccionEntrega
from app.modules.dominio_1.direcciones.repository import DireccionRepository
from app.modules.dominio_1.usuarios.models import Usuario, UsuarioRol
from app.modules.dominio_1.usuarios.repository import UsuarioRepository, UsuarioRolRepository
from app.modules.dominio_2.categorias.services import CategoriaService
from app.modules.dominio_2.categorias.unit_of_work import CategoriaUnitOfWork
from app.modules.dominio_2.productos.services import ProductoService
from app.modules.dominio_2.productos.unit_of_work import ProductoUnitOfWork
from app.modules.dominio_3.pedidos.schemas import PedidoCreate
from app.modules.dominio_3.pedidos.services import PedidoService
from app.modules.dominio_3.pedidos.unit_of_work import PedidoUnitOfWork
from app.modules.local_config.service import HorariosService
from app.modules.local_config.zonas_service import ZonasEnvioService
from decimal import Decimal
from app.modules.public.entrega_service import EntregaPublicService
from app.modules.public.schemas import PublicUbicacionRead
from app.modules.local_config.schemas import PublicCotizarEnvioInput, PublicCotizarEnvioRead
from app.modules.public.schemas import (
    PublicCatalogoRead,
    PublicCategoriaRead,
    PublicDetalleRead,
    PublicHistorialRead,
    PublicPedidoCreate,
    PublicPedidoCreated,
    PublicProductoRead,
    PublicSeguimientoRead,
    PublicTiendaRead,
    PublicZonaEnvioRead,
)


class PublicApiService:
    def __init__(self, session: Session):
        self.session = session

    def tienda(self) -> PublicTiendaRead:
        horarios = HorariosService(self.session)
        abierto, mensaje, hoy, prox = horarios.estado_publico()
        zonas_svc = ZonasEnvioService(self.session)
        zonas = [
            PublicZonaEnvioRead(
                nombre=z.nombre,
                ciudad_match=z.ciudad_match,
                costo_envio=Decimal(str(z.costo_envio)),
                pedido_minimo=Decimal(str(z.pedido_minimo)),
            )
            for z in zonas_svc.list_public()
        ]
        return PublicTiendaRead(
            abierto=abierto,
            mensaje=mensaje,
            horario_hoy=hoy,
            proxima_apertura=prox,
            zonas_envio=zonas,
        )

    def cotizar_envio(self, data: PublicCotizarEnvioInput) -> PublicCotizarEnvioRead:
        subtotal = Decimal(str(data.subtotal)).quantize(Decimal("0.01"))
        costo, minimo, nombre = ZonasEnvioService(self.session).costo_y_minimo(data.ciudad)
        return PublicCotizarEnvioRead(
            costo_envio=float(costo),
            pedido_minimo=float(minimo),
            alcanza_minimo=subtotal >= minimo,
            zona_nombre=nombre,
        )

    def catalogo(self) -> PublicCatalogoRead:
        with CategoriaUnitOfWork(self.session) as cat_uow:
            cats = CategoriaService(cat_uow).get_all(offset=0, limit=200, incluir_eliminados=False)
            categorias = [
                PublicCategoriaRead(
                    id=c.id,
                    nombre=c.nombre,
                    descripcion=c.descripcion,
                    imagen_url=c.imagen_url,
                    parent_id=c.parent_id,
                )
                for c in cats.data
            ]

        with ProductoUnitOfWork(self.session) as prod_uow:
            productos_page = ProductoService(prod_uow).get_all(
                offset=0,
                limit=500,
                disponible=True,
                incluir_eliminados=False,
            )

        productos = [
            PublicProductoRead(
                id=p.id,
                nombre=p.nombre,
                descripcion=p.descripcion,
                precio_base=p.precio_base,
                imagenes_url=p.imagenes_url or [],
                disponible=p.disponible,
                categoria_ids=p.categoria_ids,
            )
            for p in productos_page.data
        ]
        return PublicCatalogoRead(categorias=categorias, productos=productos)

    def crear_pedido(self, data: PublicPedidoCreate) -> PublicPedidoCreated:
        if not HorariosService(self.session).puede_aceptar_pedidos():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El local no acepta pedidos en este momento",
            )

        usuario_id = self._resolve_cliente(data.cliente)
        direccion_id = data.direccion_id

        if data.direccion:
            direccion_id = self._crear_direccion(usuario_id, data.direccion)

        pedido_data = PedidoCreate(
            items=data.items,
            forma_pago_codigo=data.forma_pago_codigo,
            tipo_pedido=data.tipo_pedido,
            direccion_id=direccion_id,
            notas=data.notas,
        )

        with PedidoUnitOfWork(self.session) as uow:
            result = PedidoService(uow).crear(pedido_data, usuario_id)

        return PublicPedidoCreated(
            pedido_id=result.pedido.id,
            tracking_token=result.pedido.tracking_token,
            estado_codigo=result.pedido.estado_codigo,
            tipo_pedido=result.pedido.tipo_pedido,
            total=result.pedido.total,
        )

    def seguimiento(self, tracking_token: str) -> PublicSeguimientoRead:
        with PedidoUnitOfWork(self.session) as uow:
            pedido = uow.pedidos.get_by_tracking_token(tracking_token)
            if not pedido:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

            detalles = uow.detalles.get_by_pedido(pedido.id)
            ciudad = pedido.direccion.ciudad if pedido.direccion else None

            entrega = EntregaPublicService(self.session)
            dest = entrega._destino(pedido)
            rider = None
            if pedido.rider_lat is not None and pedido.rider_lng is not None:
                rider = PublicUbicacionRead(lat=pedido.rider_lat, lng=pedido.rider_lng)

            return PublicSeguimientoRead(
                pedido_id=pedido.id,
                estado_codigo=pedido.estado_codigo,
                tipo_pedido=pedido.tipo_pedido,
                subtotal=pedido.subtotal,
                costo_envio=pedido.costo_envio,
                total=pedido.total,
                created_at=pedido.created_at,
                updated_at=pedido.updated_at,
                ciudad=ciudad,
                destino=dest,
                destino_direccion=entrega._direccion_texto(pedido),
                rider=rider,
                rider_updated_at=pedido.rider_location_at,
                seguimiento_mapa_activo=entrega.seguimiento_mapa_activo(pedido),
                detalles=[
                    PublicDetalleRead(
                        cantidad=d.cantidad,
                        nombre_snapshot=d.nombre_snapshot,
                        precio_snapshot=d.precio_snapshot,
                        subtotal=d.subtotal,
                    )
                    for d in detalles
                ],
            )

    def historial_seguimiento(self, tracking_token: str) -> list[PublicHistorialRead]:
        with PedidoUnitOfWork(self.session) as uow:
            pedido = uow.pedidos.get_by_tracking_token(tracking_token)
            if not pedido:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
            registros = uow.historial.get_by_pedido(pedido.id)

        return [
            PublicHistorialRead(
                estado_desde=r.estado_desde,
                estado_hacia=r.estado_hacia,
                created_at=r.created_at,
            )
            for r in registros
        ]

    def pedido_id_for_tracking(self, tracking_token: str) -> int:
        with PedidoUnitOfWork(self.session) as uow:
            pedido = uow.pedidos.get_by_tracking_token(tracking_token)
            if not pedido:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
            return pedido.id

    def _resolve_cliente(self, cliente) -> int:
        email = cliente.email.lower().strip()
        usuarios = UsuarioRepository(self.session)
        existente = usuarios.get_by_email(email)
        if existente:
            if existente.deleted_at is not None:
                # Checkout invitado: la baja admin no debe impedir un pedido nuevo.
                existente.deleted_at = None
                existente.nombre = cliente.nombre.strip()
                existente.apellido = cliente.apellido.strip()
                if cliente.celular:
                    existente.celular = cliente.celular
                usuarios.add(existente)
                self.session.flush()
                roles = UsuarioRolRepository(self.session)
                if not roles.existe(existente.id, "CLIENT"):
                    roles.add(UsuarioRol(usuario_id=existente.id, rol_codigo="CLIENT"))
            return existente.id

        usuario = Usuario(
            nombre=cliente.nombre.strip(),
            apellido=cliente.apellido.strip(),
            email=email,
            celular=cliente.celular,
            password_hash=hash_password(secrets.token_urlsafe(32)),
        )
        usuarios.add(usuario)
        self.session.flush()
        UsuarioRolRepository(self.session).add(
            UsuarioRol(usuario_id=usuario.id, rol_codigo="CLIENT")
        )
        return usuario.id

    def _crear_direccion(self, usuario_id: int, data) -> int:
        repo = DireccionRepository(self.session)
        principal = repo.get_principal(usuario_id)
        direccion = DireccionEntrega(
            usuario_id=usuario_id,
            alias=data.alias,
            linea1=data.linea1,
            linea2=data.linea2,
            ciudad=data.ciudad,
            provincia=data.provincia,
            codigo_postal=data.codigo_postal,
            latitud=data.latitud,
            longitud=data.longitud,
            es_principal=principal is None,
        )
        if direccion.latitud is None or direccion.longitud is None:
            coords = geocode_address(
                linea1=direccion.linea1,
                linea2=direccion.linea2,
                ciudad=direccion.ciudad,
                provincia=direccion.provincia,
            )
            if coords:
                direccion.latitud, direccion.longitud = coords
        repo.add(direccion)
        self.session.flush()
        return direccion.id
