from sqlmodel import Session, select
from app.core.db import engine, create_all_tables
from app.core.security import hash_password
from app.modules.dominio_1.usuarios.models import Usuario, Rol, UsuarioRol
from app.modules.dominio_3.pedidos.models import FormaPago, EstadoPedido
from app.modules.dominio_2.unidad_medida.models import UnidadMedida
from app.modules.dominio_2.categorias.models import Categoria

ROLES = [
    {"codigo": "ADMIN",   "nombre": "Administrador",     "descripcion": "CRUD completo del sistema"},
    {"codigo": "STOCK",   "nombre": "Gestor de Stock",   "descripcion": "Leer productos, actualizar stock y disponibilidad"},
    {"codigo": "PEDIDOS", "nombre": "Gestor de Pedidos", "descripcion": "Ver y avanzar estados de pedidos"},
    {"codigo": "CLIENT",  "nombre": "Cliente",           "descripcion": "Catálogo, carrito y pedidos propios"},
]

FORMAS_PAGO = [
    {"codigo": "EFECTIVO",      "descripcion": "Efectivo contra entrega", "habilitado": True},
    {"codigo": "MERCADOPAGO",   "descripcion": "Mercado Pago",            "habilitado": True},
    {"codigo": "TRANSFERENCIA", "descripcion": "Transferencia Bancaria",  "habilitado": True},
]

ESTADOS_PEDIDO = [
    {"codigo": "PENDIENTE",  "descripcion": "Pedido creado, pago pendiente",   "orden": 1, "es_terminal": False},
    {"codigo": "CONFIRMADO", "descripcion": "Pago procesado y confirmado",      "orden": 2, "es_terminal": False},
    {"codigo": "EN_PREP",    "descripcion": "En preparación en cocina",         "orden": 3, "es_terminal": False},
    {"codigo": "ENTREGADO",  "descripcion": "Entrega confirmada",               "orden": 4, "es_terminal": True},
    {"codigo": "CANCELADO",  "descripcion": "Pedido cancelado",                 "orden": 5, "es_terminal": True},
]

UNIDADES_MEDIDA = [
    {"nombre": "kilogramo", "simbolo": "kg",   "tipo": "peso"},
    {"nombre": "gramo",     "simbolo": "g",    "tipo": "peso"},
    {"nombre": "litro",     "simbolo": "L",    "tipo": "volumen"},
    {"nombre": "mililitro", "simbolo": "ml",   "tipo": "volumen"},
    {"nombre": "unidad",    "simbolo": "ud",   "tipo": "contable"},
    {"nombre": "porciones", "simbolo": "porc", "tipo": "contable"},
]

# Estructura jerárquica: tupla (nombre, parent_name | None)
CATEGORIAS = [
    # ── Padres ──
    ({"nombre": "Entradas", "descripcion": "Picadas"}, None),
    ({"nombre": "Comidas",  "descripcion": "Hamburguesas, pastas y pizzas"},    None),
    ({"nombre": "Bebidas",  "descripcion": "Sin gas, gaseosas, cervezas, coctelería y combos"}, None),
    # ── Hijas ──
    ({"nombre": "Picadas",    "descripcion": "Tablas de fiambres y quesos"},       "Entradas"),
    ({"nombre": "Hamburguesas","descripcion": "Burgers clásicas, veggie y crispy"}, "Comidas"),
    ({"nombre": "Pastas",     "descripcion": "Spaghetti, ravioles, sorrentinos"},   "Comidas"),
    ({"nombre": "Pizzas",     "descripcion": "Muzzarella, napolitana, fugazzeta"},  "Comidas"),
    ({"nombre": "Sin gas",    "descripcion": "Aguas, limonadas y jugos naturales"}, "Bebidas"),
    ({"nombre": "Gaseosas",   "descripcion": "Cola, lima-limón, naranja, pomelo"},  "Bebidas"),
    ({"nombre": "Cervezas",   "descripcion": "Pintas artesanales"},                 "Bebidas"),
    ({"nombre": "Coctelería", "descripcion": "Mojito, caipirinha, gin tonic"},      "Bebidas"),
    ({"nombre": "Combos",     "descripcion": "Fernet, vodka, gin y campari"},       "Bebidas"),
]

ADMIN_USER = {
    "nombre":   "Administrador",
    "apellido": "Sistema",
    "email":    "admin@foodstore.com",
    "password": "Admin1234!",
    "rol":      "ADMIN",
}

USUARIOS_PRUEBA = [
    {"nombre": "Stockero", "email": "stock@ejemplo.com",   "rol": "STOCK"},
    {"nombre": "Vendedor", "email": "pedidos@ejemplo.com", "rol": "PEDIDOS"},
    {"nombre": "Cliente",  "email": "user@ejemplo.com",    "rol": "CLIENT"},
]


def run() -> None:
    print("=== Seed — Food Store v6.0 ===\n")
    # Las tablas las crea Alembic (alembic upgrade head) o create_all_tables() como fallback.
    # Si no existen todavia, las creamos aca.
    from sqlalchemy import inspect
    inspector = inspect(engine)
    if not inspector.has_table("rol"):
        print("(creando tablas con create_all_tables como fallback)")
        create_all_tables()
    else:
        print("(tablas ya existentes — omitiendo create_all_tables)")
    print()

    with Session(engine) as session:
        # ── Roles ─────────────────────────────────────────────────────────
        print("Roles:")
        for r in ROLES:
            existing = session.get(Rol, r["codigo"])
            if existing:
                print(f"  [=] Ya existe: {r['codigo']}")
            else:
                session.add(Rol(**r))
                print(f"  [+] Creado:    {r['codigo']} — {r['nombre']}")
        session.commit()

        # ── Formas de Pago ─────────────────────────────────────────────────
        print("\nFormas de Pago:")
        for fp in FORMAS_PAGO:
            existing_fp = session.get(FormaPago, fp["codigo"])
            if existing_fp:
                print(f"  [=] Ya existe: {fp['codigo']}")
            else:
                session.add(FormaPago(**fp))
                print(f"  [+] Creado:    {fp['codigo']} — {fp['descripcion']}")
        session.commit()

        # ── Estados de Pedido ──────────────────────────────────────────────
        print("\nEstados de Pedido:")
        for ep in ESTADOS_PEDIDO:
            existing = session.get(EstadoPedido, ep["codigo"])
            if existing:
                print(f"  [=] Ya existe: {ep['codigo']}")
            else:
                session.add(EstadoPedido(**ep))
                print(f"  [+] Creado:    {ep['codigo']} (orden={ep['orden']}, terminal={ep['es_terminal']})")
        session.commit()

        # ── Unidades de Medida ─────────────────────────────────────────────
        print("\nUnidades de Medida:")
        for um in UNIDADES_MEDIDA:
            existing = session.exec(
                select(UnidadMedida).where(UnidadMedida.nombre == um["nombre"])
            ).first()
            if existing:
                print(f"  [=] Ya existe: {um['nombre']} ({um['simbolo']})")
            else:
                session.add(UnidadMedida(**um))
                print(f"  [+] Creado:    {um['nombre']} ({um['simbolo']}) — {um['tipo']}")
        session.commit()

        # ── Categorías ─────────────────────────────────────────────────────
        print("\nCategorías:")
        padres_map: dict[str, int] = {}
        # Paso 1: crear padres
        for data, _ in CATEGORIAS:
            if _ is None:  # es padre
                existing = session.exec(
                    select(Categoria).where(Categoria.nombre == data["nombre"])
                ).first()
                if existing:
                    padres_map[data["nombre"]] = existing.id
                    print(f"  [=] Ya existe: {data['nombre']} (padre)")
                else:
                    cat = Categoria(**data)
                    session.add(cat)
                    session.flush()
                    padres_map[data["nombre"]] = cat.id
                    print(f"  [+] Creado:    {data['nombre']} (padre, id={cat.id})")
        session.commit()

        # Paso 2: crear hijas con parent_id
        for data, parent_name in CATEGORIAS:
            if parent_name is not None:
                parent_id = padres_map.get(parent_name)
                existing = session.exec(
                    select(Categoria).where(Categoria.nombre == data["nombre"])
                ).first()
                if existing:
                    print(f"  [=] Ya existe: {data['nombre']} -> {parent_name}")
                else:
                    cat = Categoria(parent_id=parent_id, **data)
                    session.add(cat)
                    print(f"  [+] Creado:    {data['nombre']} -> {parent_name}")
        session.commit()

        # ── Usuario admin ─────────────────────────────────────────────────
        print("\nUsuario admin:")
        existing_user = session.exec(
            select(Usuario).where(Usuario.email == ADMIN_USER["email"])
        ).first()

        if existing_user:
            print(f"  [=] Ya existe: {ADMIN_USER['email']}")
        else:
            usuario = Usuario(
                nombre=ADMIN_USER["nombre"],
                apellido=ADMIN_USER["apellido"],
                email=ADMIN_USER["email"],
                password_hash=hash_password(ADMIN_USER["password"]),
            )
            session.add(usuario)
            session.flush()
            session.add(UsuarioRol(usuario_id=usuario.id, rol_codigo="ADMIN"))
            session.commit()
            print(f"  [+] Creado: {ADMIN_USER['email']} / {ADMIN_USER['password']}  (rol=ADMIN)")

        # ── Usuarios de prueba ────────────────────────────────────────────
        print("\nUsuarios de prueba:")
        for u in USUARIOS_PRUEBA:
            existing_user = session.exec(
                select(Usuario).where(Usuario.email == u["email"])
            ).first()

            if existing_user:
                print(f"  [=] Ya existe: {u['email']}")
            else:
                usuario = Usuario(
                    nombre=u["nombre"],
                    apellido="Test",
                    email=u["email"],
                    password_hash=hash_password("123456"),
                )
                session.add(usuario)
                session.flush()
                session.add(UsuarioRol(usuario_id=usuario.id, rol_codigo=u["rol"]))
                session.commit()
                print(f"  [+] Creado: {u['email']} / 123456 (rol={u['rol']})")

        # ── Poblar catálogo ───────────────────────────────────────────────
        print("\nCatálogo:")
        from scripts.poblar_catalogo import run as poblar_catalogo
        poblar_catalogo()

        # ── Poblar pedidos de prueba ──────────────────────────────────────
        print("\nPedidos de prueba:")
        from scripts.poblar_pedidos import run as poblar_pedidos
        poblar_pedidos()

    print("\nSeed completado")
    print("\nCredenciales de acceso:")
    print(f"  Email    : {ADMIN_USER['email']}")
    print(f"  Password : {ADMIN_USER['password']}")
    print(f"  Rol      : ADMIN\n")


if __name__ == "__main__":
    run()
