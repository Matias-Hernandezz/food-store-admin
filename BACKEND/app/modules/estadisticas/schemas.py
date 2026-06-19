from decimal import Decimal
from pydantic import BaseModel


class ResumenResponse(BaseModel):
    ventas_hoy: Decimal
    ticket_promedio: Decimal
    pedidos_activos: int
    mes_actual: Decimal


class VentasPeriodoItem(BaseModel):
    periodo: str
    total_ventas: Decimal
    cantidad_pedidos: int


class ProductoTopItem(BaseModel):
    producto_id: int
    nombre: str
    ingresos: Decimal
    cantidad_vendida: int


class PedidosEstadoItem(BaseModel):
    estado_codigo: str
    cantidad: int


class IngresosItem(BaseModel):
    forma_pago_codigo: str
    total: Decimal
    cantidad: int
