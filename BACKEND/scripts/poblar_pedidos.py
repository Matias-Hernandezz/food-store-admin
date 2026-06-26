"""
Script para poblar pedidos de prueba con fechas variadas.
Genera ~20 pedidos en los últimos 14 días con distintos estados.
Ejecutar: python scripts/poblar_pedidos.py (o desde seed.py)
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import random

from sqlmodel import Session, select
from app.core.db import engine, create_all_tables
from app.modules.dominio_1.usuarios.models import Usuario
from app.modules.dominio_1.direcciones.models import DireccionEntrega
from app.modules.dominio_2.productos.models import Producto
from app.modules.dominio_3.pedidos.models import Pedido, DetallePedido, HistorialEstadoPedido, FormaPago

# Estados en orden FSM para generar historial realista
ESTADOS_FSM = ["PENDIENTE", "CONFIRMADO", "EN_PREP", "ENTREGADO"]
ESTADOS_TERMINALES = {"ENTREGADO", "CANCELADO"}


def _fecha_aleatoria(dias_atras: int = 14) -> datetime:
    """Genera una fecha aleatoria en los últimos N días."""
    ahora = datetime.now(timezone.utc)
    dias = random.randint(0, dias_atras)
    horas = random.randint(8, 22)
    minutos = random.randint(0, 59)
    return ahora - timedelta(days=dias, hours=ahora.hour - horas, minutes=ahora.minute - minutos)


def run():
    print("\n=== Poblar Pedidos de Prueba ===\n")
    create_all_tables()

    with Session(engine) as session:
        # ── Obtener datos necesarios ────────────────────────────────────
        cliente = session.exec(
            select(Usuario).where(Usuario.email == "user@ejemplo.com")
        ).first()
        if not cliente:
            print("[!!] No se encontró el usuario cliente (user@ejemplo.com). Ejecutá seed.py primero.")
            return

        # Dirección del cliente
        direccion = session.exec(
            select(DireccionEntrega).where(
                DireccionEntrega.usuario_id == cliente.id,
                DireccionEntrega.deleted_at.is_(None),
            )
        ).first()

        # Si no tiene dirección, creamos una
        if not direccion:
            direccion = DireccionEntrega(
                usuario_id=cliente.id,
                alias="Casa",
                linea1="Av. Siempre Viva 742",
                ciudad="Springfield",
                provincia="Buenos Aires",
                es_principal=True,
            )
            session.add(direccion)
            session.flush()
            print("[+] Dirección creada para el cliente")

        # Productos disponibles
        productos = session.exec(
            select(Producto).where(
                Producto.disponible == True,
                Producto.deleted_at.is_(None),
            )
        ).all()
        if not productos:
            print("[!!] No hay productos en el catálogo. Ejecutá poblar_catalogo.py primero.")
            return

        # Forma de pago
        forma_pago = session.get(FormaPago, "MERCADOPAGO")
        if not forma_pago:
            forma_pago = session.get(FormaPago, "EFECTIVO")

        # ── Generar pedidos ─────────────────────────────────────────────
        creados = 0
        for i in range(20):
            fecha = _fecha_aleatoria(14)

            # Elegir 1-3 productos al azar
            items = random.sample(productos, min(random.randint(1, 3), len(productos)))
            subtotal = Decimal("0.00")
            detalles_data = []
            for prod in items:
                cant = random.randint(1, 3)
                precio = Decimal(str(prod.precio_base))
                sub = precio * cant
                subtotal += sub
                detalles_data.append({
                    "producto_id": prod.id,
                    "cantidad": cant,
                    "nombre_snapshot": prod.nombre,
                    "precio_snapshot": precio,
                    "subtotal": sub,
                })

            total = subtotal  # sin descuento ni envío para simplificar

            # Avanzar el pedido a un estado aleatorio (simula flujo real)
            corte = random.randint(0, len(ESTADOS_FSM))
            estados_recorridos = ESTADOS_FSM[:corte] if corte > 0 else ["PENDIENTE"]
            estado_final = estados_recorridos[-1]

            pedido = Pedido(
                usuario_id=cliente.id,
                direccion_id=direccion.id,
                estado_codigo=estado_final,
                forma_pago_codigo=forma_pago.codigo,
                subtotal=subtotal,
                descuento=Decimal("0.00"),
                costo_envio=Decimal("0.00"),
                total=total,
                notas=None,
                created_at=fecha,
                updated_at=fecha,
            )
            session.add(pedido)
            session.flush()

            # Detalles
            for d in detalles_data:
                session.add(DetallePedido(pedido_id=pedido.id, **d))

            # Historial (append-only)
            for idx, estado in enumerate(estados_recorridos):
                estado_anterior = estados_recorridos[idx - 1] if idx > 0 else None
                session.add(HistorialEstadoPedido(
                    pedido_id=pedido.id,
                    estado_desde=estado_anterior,
                    estado_hacia=estado,
                    usuario_id=cliente.id if idx == 0 else 1,  # cliente crea, admin avanza
                    motivo="Pedido creado" if idx == 0 else None,
                    created_at=fecha + timedelta(minutes=idx * 15),
                ))

            creados += 1

        session.commit()

    print(f"\n[+] {creados} pedidos de prueba creados.")
    print("   Estados variados, fechas en los últimos 14 días.")
    print("   Refrescá el dashboard para ver los gráficos con datos.\n")


if __name__ == "__main__":
    run()
