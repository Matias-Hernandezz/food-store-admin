"""Máquina de estados de pedidos por tipo (envío / retiro / mostrador)."""

from app.core.roles import CASHIER, CLIENT, KITCHEN, OWNER

TIPO_DELIVERY = "DELIVERY"
TIPO_PICKUP = "PICKUP"
TIPO_DINE_IN = "DINE_IN"
TIPOS_PEDIDO = frozenset({TIPO_DELIVERY, TIPO_PICKUP, TIPO_DINE_IN})

ESTADO_PENDIENTE = "PENDIENTE"
ESTADO_CONFIRMADO = "CONFIRMADO"
ESTADO_EN_PREPARACION = "EN_PREPARACION"
ESTADO_PREPARADO = "PREPARADO"
ESTADO_EN_CAMINO = "EN_CAMINO"
ESTADO_ENTREGADO = "ENTREGADO"
ESTADO_CANCELADO = "CANCELADO"

ESTADOS_ACTIVOS = frozenset({
    ESTADO_PENDIENTE,
    ESTADO_CONFIRMADO,
    ESTADO_EN_PREPARACION,
    ESTADO_PREPARADO,
    ESTADO_EN_CAMINO,
    ESTADO_ENTREGADO,
    ESTADO_CANCELADO,
})

CANCELABLES_POR_CLIENTE = frozenset({ESTADO_PENDIENTE, ESTADO_CONFIRMADO})


def _grafo_retiro() -> dict[str, list[str]]:
    return {
        ESTADO_PENDIENTE: [ESTADO_CONFIRMADO, ESTADO_CANCELADO],
        ESTADO_CONFIRMADO: [ESTADO_EN_PREPARACION, ESTADO_CANCELADO],
        ESTADO_EN_PREPARACION: [ESTADO_PREPARADO, ESTADO_CANCELADO],
        ESTADO_PREPARADO: [ESTADO_ENTREGADO, ESTADO_CANCELADO],
        ESTADO_ENTREGADO: [],
        ESTADO_CANCELADO: [],
    }


def _grafo_envio() -> dict[str, list[str]]:
    grafo = _grafo_retiro()
    grafo[ESTADO_PREPARADO] = [ESTADO_EN_CAMINO, ESTADO_CANCELADO]
    grafo[ESTADO_EN_CAMINO] = [ESTADO_ENTREGADO, ESTADO_CANCELADO]
    return grafo


TRANSICIONES_POR_TIPO: dict[str, dict[str, list[str]]] = {
    TIPO_PICKUP: _grafo_retiro(),
    TIPO_DINE_IN: _grafo_retiro(),
    TIPO_DELIVERY: _grafo_envio(),
}

_TRANSICIONES_CLIENTE: dict[str, list[str]] = {
    ESTADO_PENDIENTE: [ESTADO_CANCELADO],
    ESTADO_CONFIRMADO: [ESTADO_CANCELADO],
    ESTADO_EN_PREPARACION: [],
    ESTADO_PREPARADO: [],
    ESTADO_EN_CAMINO: [],
    ESTADO_ENTREGADO: [],
    ESTADO_CANCELADO: [],
}

EVENTOS_WS: dict[str, str] = {
    ESTADO_PENDIENTE: "NUEVO_PEDIDO",
    ESTADO_CONFIRMADO: "PEDIDO_CONFIRMADO",
    ESTADO_EN_PREPARACION: "PEDIDO_EN_PREPARACION",
    ESTADO_PREPARADO: "PEDIDO_PREPARADO",
    ESTADO_EN_CAMINO: "PEDIDO_EN_CAMINO",
    ESTADO_ENTREGADO: "PEDIDO_ENTREGADO",
    ESTADO_CANCELADO: "PEDIDO_CANCELADO",
}


def inferir_tipo_pedido(tipo_explicito: str | None, direccion_id: int | None) -> str:
    if tipo_explicito:
        t = tipo_explicito.upper()
        if t not in TIPOS_PEDIDO:
            raise ValueError(f"tipo_pedido inválido: {tipo_explicito}")
        return t
    return TIPO_DELIVERY if direccion_id else TIPO_PICKUP


def transiciones_para(tipo_pedido: str, rol: str) -> dict[str, list[str]]:
    if rol == CLIENT:
        return _TRANSICIONES_CLIENTE
    return TRANSICIONES_POR_TIPO.get(tipo_pedido, TRANSICIONES_POR_TIPO[TIPO_DELIVERY])


def rol_operativo(roles: list[str]) -> str:
    if OWNER in roles:
        return OWNER
    if KITCHEN in roles:
        return KITCHEN
    if CASHIER in roles:
        return CASHIER
    if CLIENT in roles:
        return CLIENT
    return "SIN_ROL"
