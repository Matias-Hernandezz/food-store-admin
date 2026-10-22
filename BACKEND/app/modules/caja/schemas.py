from datetime import datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel

from app.modules.dominio_3.pedidos.schemas import ItemCarritoInput, PedidoRead


class TurnoCajaRead(SQLModel):
    id: int
    estado: str
    abierto_en: datetime
    cerrado_en: datetime | None = None
    usuario_apertura_id: int
    fondo_inicial: Decimal
    efectivo_esperado: Decimal | None = None
    efectivo_contado: Decimal | None = None
    notas_cierre: str | None = None
    pedidos_turno: int = 0
    total_efectivo_pedidos: Decimal = Decimal("0.00")


class AbrirTurnoInput(SQLModel):
    fondo_inicial: Decimal = Field(default=Decimal("0.00"), ge=0)


class CerrarTurnoInput(SQLModel):
    efectivo_contado: Decimal = Field(ge=0)
    notas_cierre: str | None = None


class PedidoMostradorInput(SQLModel):
    items: list[ItemCarritoInput]
    forma_pago_codigo: str
    notas: str | None = None
    confirmar_pago: bool = True


class PedidoMostradorResult(SQLModel):
    pedido: PedidoRead
    turno_caja_id: int
