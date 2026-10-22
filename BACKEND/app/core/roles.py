"""Códigos de rol del tenant (DB, JWT, require_role)."""

OWNER = "OWNER"
STOCK = "STOCK"
KITCHEN = "KITCHEN"
CASHIER = "CASHIER"
CLIENT = "CLIENT"

# Staff del local que ve/gestiona pedidos de cualquier cliente
STAFF_ORDER_ROLES: tuple[str, ...] = (OWNER, KITCHEN, CASHIER)

# Quién recibe eventos WS por rol (nunca CLIENT: solo sala order:{id})
STAFF_WS_ROLES: tuple[str, ...] = (OWNER, KITCHEN, CASHIER)

# Panel admin (catálogo + usuarios + pedidos)
STAFF_PANEL_ROLES: tuple[str, ...] = (OWNER, STOCK, KITCHEN, CASHIER)


def is_staff_orders(roles: list[str]) -> bool:
    return any(r in STAFF_ORDER_ROLES for r in roles)


def is_owner(roles: list[str]) -> bool:
    return OWNER in roles
