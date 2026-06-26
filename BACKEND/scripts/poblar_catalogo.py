"""
Script standalone para poblar productos e ingredientes del catálogo Food Store v6.

Ejecutar: python scripts/poblar_catalogo.py
Requiere: categorías ya creadas (ENTRADAS → Picadas, Empanadas, Bruschettas;
                               COMIDAS → Hamburguesas, Pastas, Pizzas;
                               BEBIDAS → Sin gas, Gaseosas, Cervezas, Coctelería, Combos)
"""

from decimal import Decimal
from sqlmodel import Session, select
from app.core.db import engine, create_all_tables
from app.modules.dominio_2.ingredientes.models import Ingrediente
from app.modules.dominio_2.productos.models import Producto
from app.modules.dominio_2.productos.models_shared import ProductoIngrediente
from app.modules.dominio_2.categorias.models import Categoria

# ─── INGREDIENTES ÚNICOS (sin repetir) ─────────────────────────────────────

INGREDIENTES = [
    # Carnes y Embutidos
    {"nombre": "Carne picada", "es_alergeno": False},
    {"nombre": "Roast beef", "es_alergeno": False},
    {"nombre": "Medallón de carne vacuno", "es_alergeno": False},
    {"nombre": "Pechuga de pollo", "es_alergeno": False},
    {"nombre": "Medallón de pollo crispy", "es_alergeno": False},
    {"nombre": "Salame", "es_alergeno": False},
    {"nombre": "Jamón cocido", "es_alergeno": False},
    {"nombre": "Prosciutto", "es_alergeno": False},
    {"nombre": "Panceta", "es_alergeno": False},
    {"nombre": "Chorizo colorado", "es_alergeno": False},
    {"nombre": "Salmón ahumado", "es_alergeno": True},
    {"nombre": "Lomo horneado", "es_alergeno": False},
    # Quesos y Lácteos
    {"nombre": "Queso Gouda", "es_alergeno": True},
    {"nombre": "Queso Muzzarella", "es_alergeno": True},
    {"nombre": "Queso Cheddar", "es_alergeno": True},
    {"nombre": "Queso Roquefort", "es_alergeno": True},
    {"nombre": "Queso Brie", "es_alergeno": True},
    {"nombre": "Queso Gruyere", "es_alergeno": True},
    {"nombre": "Queso Parmesano", "es_alergeno": True},
    {"nombre": "Queso Crema", "es_alergeno": True},
    {"nombre": "Leche", "es_alergeno": True},
    {"nombre": "Manteca", "es_alergeno": True},
    # Vegetales, Frutas y Legumbres
    {"nombre": "Lechuga", "es_alergeno": False},
    {"nombre": "Tomate redondo", "es_alergeno": False},
    {"nombre": "Tomate cherry", "es_alergeno": False},
    {"nombre": "Tomate seco", "es_alergeno": False},
    {"nombre": "Cebolla blanca", "es_alergeno": False},
    {"nombre": "Cebolla morada", "es_alergeno": False},
    {"nombre": "Ajo", "es_alergeno": False},
    {"nombre": "Rúcula", "es_alergeno": False},
    {"nombre": "Albahaca", "es_alergeno": False},
    {"nombre": "Espinaca", "es_alergeno": False},
    {"nombre": "Apio", "es_alergeno": False},
    {"nombre": "Choclo en grano", "es_alergeno": False},
    {"nombre": "Champiñones", "es_alergeno": False},
    {"nombre": "Morrón rojo", "es_alergeno": False},
    {"nombre": "Papa", "es_alergeno": False},
    {"nombre": "Zanahoria", "es_alergeno": False},
    {"nombre": "Nuez", "es_alergeno": True},
    {"nombre": "Aceitunas verdes", "es_alergeno": False},
    {"nombre": "Aceitunas negras", "es_alergeno": False},
    {"nombre": "Limón", "es_alergeno": False},
    {"nombre": "Naranja", "es_alergeno": False},
    {"nombre": "Pomelo", "es_alergeno": False},
    {"nombre": "Pepino", "es_alergeno": False},
    {"nombre": "Menta fresca", "es_alergeno": False},
    {"nombre": "Jengibre", "es_alergeno": False},
    {"nombre": "Ciboulette", "es_alergeno": False},
    {"nombre": "Medallón de lentejas", "es_alergeno": False},
    # Panificados y Masas
    {"nombre": "Pan francés", "es_alergeno": False},
    {"nombre": "Pan de hamburguesa", "es_alergeno": False},
    {"nombre": "Pan de masa madre", "es_alergeno": False},
    {"nombre": "Tapa de empanada", "es_alergeno": False},
    {"nombre": "Masa de pizza", "es_alergeno": False},
    {"nombre": "Fideos Spaghetti", "es_alergeno": False},
    {"nombre": "Masa de Ravioles", "es_alergeno": False},
    {"nombre": "Masa de Sorrentinos", "es_alergeno": False},
    {"nombre": "Masa de Ñoquis", "es_alergeno": False},
    # Aderezos, Salsas y Otros
    {"nombre": "Aceite de oliva", "es_alergeno": False},
    {"nombre": "Aceto balsámico", "es_alergeno": False},
    {"nombre": "Salsa de tomate", "es_alergeno": False},
    {"nombre": "Salsa BBQ", "es_alergeno": False},
    {"nombre": "Mayonesa clásica", "es_alergeno": True},  # huevo
    {"nombre": "Mayonesa vegana", "es_alergeno": False},
    {"nombre": "Hummus", "es_alergeno": False},
    {"nombre": "Huevo duro", "es_alergeno": True},
    {"nombre": "Sal fina", "es_alergeno": False},
    {"nombre": "Pimienta negra", "es_alergeno": False},
    {"nombre": "Orégano", "es_alergeno": False},
    {"nombre": "Ají molido", "es_alergeno": False},
    {"nombre": "Nuez moscada", "es_alergeno": False},
    {"nombre": "Hielo", "es_alergeno": False},
    # Bebidas y cócteles
    {"nombre": "Fernet", "es_alergeno": False},
    {"nombre": "Gaseosa Cola", "es_alergeno": False},
    {"nombre": "Vodka Skyy", "es_alergeno": False},
    {"nombre": "Gin Gordon's", "es_alergeno": False},
    {"nombre": "Agua Tónica", "es_alergeno": False},
    {"nombre": "Campari", "es_alergeno": False},
    {"nombre": "Jugo de Naranja", "es_alergeno": False},
    {"nombre": "Ron Blanco", "es_alergeno": False},
    {"nombre": "Cachaça", "es_alergeno": False},
    {"nombre": "Tequila", "es_alergeno": False},
    {"nombre": "Triple Sec", "es_alergeno": False},
    {"nombre": "Vermut Rosso", "es_alergeno": False},
    {"nombre": "Jarabe de azúcar", "es_alergeno": False},
    {"nombre": "Azúcar", "es_alergeno": False},
    {"nombre": "Soda", "es_alergeno": False},
]

# ─── ÍNDICE DE INGREDIENTES POR NOMBRE ─────────────────────────────────────

PRODUCTOS = [
    # ═══ ENTRADAS > Picadas ════════════════════════════════════════════
    {
        "nombre": "Picada Clásica",
        "descripcion": "Queso gouda, salame, jamón cocido, aceitunas verdes, pan.",
        "precio_base": 8500.00,
        "categoria": "Picadas",
        "imagenes_url": ["https://res.cloudinary.com/dsfrkmewm/image/upload/v1781634827/picada_clasica_txs1r7.png"],
        "ingredientes": [
            ("Queso Gouda", False), ("Salame", False), ("Jamón cocido", False),
            ("Aceitunas verdes", False), ("Pan francés", False),
        ],
    },
    {
        "nombre": "Picada Premium",
        "descripcion": "Prosciutto, queso brie, gruyere, lomo horneado, nueces, aceitunas negras.",
        "precio_base": 12900.00,
        "categoria": "Picadas",
        "imagenes_url": ["https://res.cloudinary.com/dsfrkmewm/image/upload/v1781634827/picada_premium_cyztuq.png"],
        "ingredientes": [
            ("Prosciutto", False), ("Queso Brie", False), ("Queso Gruyere", False),
            ("Lomo horneado", False), ("Nuez", False), ("Aceitunas negras", False),
            ("Pan francés", False),
        ],
    },
    {
        "nombre": "Picada Veggie",
        "descripcion": "Quesos variados, tomates cherry, hummus, bastones de zanahoria, champiñones.",
        "precio_base": 7900.00,
        "categoria": "Picadas",
        "imagenes_url": ["https://res.cloudinary.com/dsfrkmewm/image/upload/v1781634838/picada_vaggie_egiwzk.png"],
        "ingredientes": [
            ("Queso Gouda", False), ("Queso Muzzarella", False), ("Tomate cherry", False),
            ("Hummus", False), ("Zanahoria", False), ("Champiñones", False),
            ("Pan francés", False),
        ],
    },
    {
        "nombre": "Picada Mixta",
        "descripcion": "Salame, jamón cocido, queso gouda, aceitunas negras, pan de masa madre.",
        "precio_base": 7200.00,
        "categoria": "Picadas",
        "imagenes_url": ["https://res.cloudinary.com/dsfrkmewm/image/upload/v1781634825/picada_mixta_mmxzok.png"],
        "ingredientes": [
            ("Salame", False), ("Jamón cocido", False), ("Queso Gouda", False),
            ("Aceitunas negras", False), ("Pan de masa madre", False),
        ],
    },
    {
        "nombre": "Picada Criolla",
        "descripcion": "Chorizo colorado, queso gouda, aceitunas verdes, pan francés.",
        "precio_base": 6800.00,
        "categoria": "Picadas",
        "imagenes_url": ["https://res.cloudinary.com/dsfrkmewm/image/upload/v1781638962/picada_criolla_dpbtec.png"],
        "ingredientes": [
            ("Chorizo colorado", False), ("Queso Gouda", False),
            ("Aceitunas verdes", False), ("Pan francés", False),
        ],
    },

    # ═══ ENTRADAS > Empanadas y Bruschettas (comentadas — solo Picadas activas) ═══
    # {
    #     "nombre": "Empanada Carne Suave",
    #     "descripcion": "Carne picada, cebolla, huevo duro, aceitunas.",
    #     "precio_base": 1200.00,
    #     "categoria": "Empanadas",
    #     ...
    # },
    # (todas las empanadas y bruschettas comentadas)

    # ═══ COMIDAS > Hamburguesas ══════════════════════════════════════════
    {
        "nombre": "Burger Simple",
        "descripcion": "Medallón de carne, lechuga, tomate, pan de hamburguesa.",
        "precio_base": 6500.00,
        "categoria": "Hamburguesas",
        "imagenes_url": ["https://res.cloudinary.com/dsfrkmewm/image/upload/v1781637916/burga_simple_nbrnp2.png"],
        "ingredientes": [
            ("Pan de hamburguesa", False), ("Medallón de carne vacuno", False),
            ("Lechuga", False), ("Tomate redondo", False), ("Mayonesa clásica", False),
        ],
    },
    {
        "nombre": "Burger Criolla",
        "descripcion": "Medallón de carne, salsa criolla, cheddar, lechuga, pepino.",
        "precio_base": 7800.00,
        "categoria": "Hamburguesas",
        "imagenes_url": ["https://res.cloudinary.com/dsfrkmewm/image/upload/v1781638876/burger_criolla_njdajz.png"],
        "ingredientes": [
            ("Pan de hamburguesa", False), ("Medallón de carne vacuno", False),
            ("Queso Cheddar", False), ("Lechuga", False), ("Pepino", False),
            ("Cebolla morada", False), ("Tomate redondo", False),
        ],
    },
    {
        "nombre": "Bacon BBQ",
        "descripcion": "Medallón de carne, cheddar, panceta, cebolla caramelizada, salsa BBQ.",
        "precio_base": 8900.00,
        "categoria": "Hamburguesas",
        "imagenes_url": ["https://res.cloudinary.com/dsfrkmewm/image/upload/v1781638072/brb_burger_pbzkq1.png"],
        "ingredientes": [
            ("Pan de hamburguesa", False), ("Medallón de carne vacuno", False),
            ("Queso Cheddar", False), ("Panceta", False), ("Cebolla blanca", False),
            ("Salsa BBQ", False),
        ],
    },
    {
        "nombre": "Burger de Pollo",
        "descripcion": "Medallón de pollo crispy, cheddar, panceta.",
        "precio_base": 8200.00,
        "categoria": "Hamburguesas",
        "imagenes_url": ["https://res.cloudinary.com/dsfrkmewm/image/upload/v1781638669/pollo_burger_rkkwhy.png"],
        "ingredientes": [
            ("Pan de hamburguesa", False), ("Medallón de pollo crispy", False),
            ("Queso Cheddar", False), ("Panceta", False),
        ],
    },
    {
        "nombre": "Veggie Lentejas",
        "descripcion": "Medallón de lentejas, tomate, cebolla morada, mayonesa vegana.",
        "precio_base": 6800.00,
        "categoria": "Hamburguesas",
        "imagenes_url": ["https://res.cloudinary.com/dsfrkmewm/image/upload/v1781639178/burger_veggie_wmsnjw.png"],
        "ingredientes": [
            ("Pan de hamburguesa", False), ("Medallón de lentejas", False),
            ("Tomate redondo", False), ("Cebolla morada", False), ("Mayonesa vegana", False),
        ],
    },

    # ═══ COMIDAS > Pastas ════════════════════════════════════════════════
    {
        "nombre": "Spaghetti Boloñesa",
        "descripcion": "Spaghetti, salsa de tomate, carne picada.",
        "precio_base": 5800.00,
        "categoria": "Pastas",
        "imagenes_url": ["https://res.cloudinary.com/dsfrkmewm/image/upload/v1781580124/fideos_jov7nl.jpg"],
        "ingredientes": [
            ("Fideos Spaghetti", False), ("Salsa de tomate", False), ("Carne picada", False),
            ("Cebolla blanca", False), ("Ajo", False), ("Aceite de oliva", False),
            ("Sal fina", False), ("Pimienta negra", False),
        ],
    },
    {
        "nombre": "Ravioles de Verdura",
        "descripcion": "Masa de pasta, espinaca, salsa blanca.",
        "precio_base": 5200.00,
        "categoria": "Pastas",
        "ingredientes": [
            ("Masa de Ravioles", False), ("Espinaca", False), ("Leche", False),
            ("Manteca", False), ("Queso Parmesano", False), ("Nuez moscada", False),
        ],
    },
    {
        "nombre": "Sorrentinos de Jamón y Queso",
        "descripcion": "Masa de pasta, jamón cocido, muzzarella, salsa rosa.",
        "precio_base": 6200.00,
        "categoria": "Pastas",
        "imagenes_url": ["https://res.cloudinary.com/dsfrkmewm/image/upload/v1781580133/sorrentinos_k2ccpt.jpg"],
        "ingredientes": [
            ("Masa de Sorrentinos", False), ("Jamón cocido", False), ("Queso Muzzarella", False),
            ("Salsa de tomate", False), ("Leche", False),
        ],
    },
    {
        "nombre": "Ñoquis de Papa",
        "descripcion": "Ñoquis, salsa fileto, queso parmesano.",
        "precio_base": 4800.00,
        "categoria": "Pastas",
        "imagenes_url": ["https://res.cloudinary.com/dsfrkmewm/image/upload/v1781580125/%C3%B1oquis_jb4fbx.jpg"],
        "ingredientes": [
            ("Masa de Ñoquis", False), ("Salsa de tomate", False), ("Queso Parmesano", False),
            ("Manteca", False),
        ],
    },
    {
        "nombre": "Fettuccine Alfredo",
        "descripcion": "Fettuccine, salsa cremosa, panceta, parmesano.",
        "precio_base": 6800.00,
        "categoria": "Pastas",
        "ingredientes": [
            ("Fideos Spaghetti", False), ("Leche", False), ("Manteca", False),
            ("Panceta", False), ("Queso Parmesano", False), ("Sal fina", False),
        ],
    },

    # ═══ COMIDAS > Pizzas ════════════════════════════════════════════════
    {
        "nombre": "Pizza Muzzarella",
        "descripcion": "Masa de pizza, salsa de tomate, muzzarella, orégano.",
        "precio_base": 5500.00,
        "categoria": "Pizzas",
        "ingredientes": [
            ("Masa de pizza", False), ("Salsa de tomate", False), ("Queso Muzzarella", False),
            ("Orégano", False), ("Aceite de oliva", False),
        ],
    },
    {
        "nombre": "Pizza Napolitana",
        "descripcion": "Masa de pizza, muzzarella, tomate en rodajas, ajo.",
        "precio_base": 6200.00,
        "categoria": "Pizzas",
        "ingredientes": [
            ("Masa de pizza", False), ("Queso Muzzarella", False), ("Tomate redondo", False),
            ("Ajo", False), ("Orégano", False), ("Aceite de oliva", False),
        ],
    },
    {
        "nombre": "Pizza Fugazzeta",
        "descripcion": "Masa de pizza, muzzarella, cebolla, aceite de oliva.",
        "precio_base": 5800.00,
        "categoria": "Pizzas",
        "ingredientes": [
            ("Masa de pizza", False), ("Queso Muzzarella", False), ("Cebolla blanca", False),
            ("Aceite de oliva", False), ("Orégano", False),
        ],
    },
    # ═══ (reactivada: Calabresa) ═══
    {
        "nombre": "Pizza Calabresa",
        "descripcion": "Masa de pizza, muzzarella, chorizo colorado.",
        "precio_base": 6800.00,
        "categoria": "Pizzas",
        "ingredientes": [
            ("Masa de pizza", False), ("Queso Muzzarella", False), ("Chorizo colorado", False),
            ("Salsa de tomate", False), ("Orégano", False),
        ],
    },
    {
        "nombre": "Pizza Rúcula y Crudo",
        "descripcion": "Masa de pizza, muzzarella, rúcula, prosciutto, parmesano.",
        "precio_base": 7500.00,
        "categoria": "Pizzas",
        "ingredientes": [
            ("Masa de pizza", False), ("Queso Muzzarella", False), ("Rúcula", False),
            ("Prosciutto", False), ("Queso Parmesano", False), ("Aceite de oliva", False),
        ],
    },

    # ═══ BEBIDAS > Sin gas ══════════════════════════════════════════════
    {
        "nombre": "Agua Mineral 500ml",
        "descripcion": "Agua mineral sin gas, 500ml.",
        "precio_base": 1800.00,
        "categoria": "Sin gas",
        "ingredientes": [],
    },
    {
        "nombre": "Limonada con Menta y Jengibre",
        "descripcion": "Limonada fresca con menta y jengibre.",
        "precio_base": 2500.00,
        "categoria": "Sin gas",
        "ingredientes": [
            ("Limón", False), ("Menta fresca", False), ("Jengibre", False),
            ("Azúcar", False), ("Hielo", False),
        ],
    },
    {
        "nombre": "Jugo de Naranja Exprimido",
        "descripcion": "Jugo de naranja exprimido natural.",
        "precio_base": 2200.00,
        "categoria": "Sin gas",
        "ingredientes": [
            ("Naranja", False), ("Hielo", False),
        ],
    },
    {
        "nombre": "Agua Saborizada de Manzana",
        "descripcion": "Agua saborizada con esencia natural de manzana.",
        "precio_base": 1400.00,
        "categoria": "Sin gas",
        "ingredientes": [],
    },
    {
        "nombre": "Limonada Clásica",
        "descripcion": "Limonada natural con azúcar y hielo.",
        "precio_base": 1900.00,
        "categoria": "Sin gas",
        "ingredientes": [
            ("Limón", False), ("Azúcar", False), ("Hielo", False),
        ],
    },

    # ═══ BEBIDAS > Gaseosas ═════════════════════════════════════════════
    {
        "nombre": "Cola Regular 600ml",
        "descripcion": "Gaseosa cola regular, 600ml.",
        "precio_base": 2000.00,
        "categoria": "Gaseosas",
        "ingredientes": [],
    },
    {
        "nombre": "Cola Zero 600ml",
        "descripcion": "Gaseosa cola zero, 600ml.",
        "precio_base": 2000.00,
        "categoria": "Gaseosas",
        "ingredientes": [],
    },
    {
        "nombre": "Lima-Limón 600ml",
        "descripcion": "Gaseosa lima-limón, 600ml.",
        "precio_base": 2000.00,
        "categoria": "Gaseosas",
        "ingredientes": [],
    },
    {
        "nombre": "Naranja 600ml",
        "descripcion": "Gaseosa sabor naranja, 600ml.",
        "precio_base": 2000.00,
        "categoria": "Gaseosas",
        "ingredientes": [],
    },
    # ═══ (reactivada: Pomelo) ═══
    {
        "nombre": "Pomelo 600ml",
        "descripcion": "Gaseosa sabor pomelo, 600ml.",
        "precio_base": 2000.00,
        "categoria": "Gaseosas",
        "ingredientes": [],
    },

    # ═══ BEBIDAS > Cervezas ═════════════════════════════════════════════
    {
        "nombre": "Quilmes Cristal 1L",
        "descripcion": "Cerveza Quilmes Cristal, botella 1 litro.",
        "precio_base": 3200.00,
        "categoria": "Cervezas",
        "ingredientes": [],
    },
    {
        "nombre": "Andes Roja 1L",
        "descripcion": "Cerveza Andes Roja, botella 1 litro.",
        "precio_base": 3800.00,
        "categoria": "Cervezas",
        "ingredientes": [],
    },
    {
        "nombre": "Quilmes Stout 1L",
        "descripcion": "Cerveza Quilmes Stout, botella 1 litro.",
        "precio_base": 4000.00,
        "categoria": "Cervezas",
        "ingredientes": [],
    },
    {
        "nombre": "Patagonia IPA 730ml",
        "descripcion": "Cerveza Patagonia IPA, botella 730ml.",
        "precio_base": 5200.00,
        "categoria": "Cervezas",
        "ingredientes": [],
    },
    {
        "nombre": "Andes Origen 1L",
        "descripcion": "Cerveza Andes Origen, botella 1 litro.",
        "precio_base": 4500.00,
        "categoria": "Cervezas",
        "ingredientes": [],
    },

    # ═══ BEBIDAS > Coctelería ═══════════════════════════════════════════
    {
        "nombre": "Mojito Clásico",
        "descripcion": "Ron blanco, menta, lima, azúcar, soda.",
        "precio_base": 4800.00,
        "categoria": "Coctelería",
        "ingredientes": [
            ("Ron Blanco", False), ("Menta fresca", False), ("Limón", False),
            ("Azúcar", False), ("Soda", False), ("Hielo", False),
        ],
    },
    {
        "nombre": "Caipirinha",
        "descripcion": "Cachaça, lima, azúcar, hielo.",
        "precio_base": 4600.00,
        "categoria": "Coctelería",
        "ingredientes": [
            ("Cachaça", False), ("Limón", False), ("Azúcar", False), ("Hielo", False),
        ],
    },
    {
        "nombre": "Gin Tonic con Pepino",
        "descripcion": "Gin, agua tónica, pepino, cítricos.",
        "precio_base": 5200.00,
        "categoria": "Coctelería",
        "ingredientes": [
            ("Gin Gordon's", False), ("Agua Tónica", False), ("Pepino", False),
            ("Limón", False), ("Hielo", False),
        ],
    },
    {
        "nombre": "Margarita",
        "descripcion": "Tequila, triple sec, lima, sal.",
        "precio_base": 5500.00,
        "categoria": "Coctelería",
        "ingredientes": [
            ("Tequila", False), ("Triple Sec", False), ("Limón", False),
            ("Sal fina", False), ("Hielo", False),
        ],
    },
    # ═══ (reactivado: Negroni) ═══
    {
        "nombre": "Negroni",
        "descripcion": "Gin, vermut rosso, campari, naranja.",
        "precio_base": 5800.00,
        "categoria": "Coctelería",
        "ingredientes": [
            ("Gin Gordon's", False), ("Vermut Rosso", False), ("Campari", False),
            ("Naranja", False), ("Hielo", False),
        ],
    },

    # ═══ BEBIDAS > Combos ═══════════════════════════════════════════════
    {
        "nombre": "Combo Fernet",
        "descripcion": "1 Botella Fernet 750ml + 2 Gaseosas Cola 1.5L + Hielo.",
        "precio_base": 15000.00,
        "categoria": "Combos",
        "ingredientes": [
            ("Fernet", False), ("Gaseosa Cola", False), ("Hielo", False),
        ],
    },
    {
        "nombre": "Combo Vodka",
        "descripcion": "1 Botella Skyy 700ml + 4 Jugos de Naranja + Hielo.",
        "precio_base": 18000.00,
        "categoria": "Combos",
        "ingredientes": [
            ("Vodka Skyy", False), ("Jugo de Naranja", False), ("Hielo", False),
        ],
    },
    {
        "nombre": "Combo Gin",
        "descripcion": "1 Botella Gin Gordon's + 4 Aguas Tónicas + Cítricos.",
        "precio_base": 22000.00,
        "categoria": "Combos",
        "ingredientes": [
            ("Gin Gordon's", False), ("Agua Tónica", False), ("Limón", False),
            ("Hielo", False),
        ],
    },
    {
        "nombre": "Combo Campari",
        "descripcion": "1 Botella Campari + 3 Jugos de Naranja + Hielo.",
        "precio_base": 16000.00,
        "categoria": "Combos",
        "ingredientes": [
            ("Campari", False), ("Jugo de Naranja", False), ("Hielo", False),
        ],
    },
    {
        "nombre": "Combo Ron",
        "descripcion": "1 Botella Ron Blanco + 4 Gaseosas Cola + Hielo + Limón.",
        "precio_base": 17000.00,
        "categoria": "Combos",
        "ingredientes": [
            ("Ron Blanco", False), ("Gaseosa Cola", False), ("Hielo", False),
            ("Limón", False),
        ],
    },
]


def run():
    print("\n=== Poblar Catalogo -- Food Store v6 ===\n")
    create_all_tables()

    with Session(engine) as session:
        # ── 1. Crear ingredientes ──────────────────────────────────────
        print("Ingredientes:")
        ing_map: dict[str, Ingrediente] = {}
        for ing in INGREDIENTES:
            existente = session.exec(
                select(Ingrediente).where(Ingrediente.nombre == ing["nombre"])
            ).first()
            if existente:
                ing_map[ing["nombre"]] = existente
                print(f"  [=] {ing['nombre']}")
            else:
                nuevo = Ingrediente(
                    nombre=ing["nombre"],
                    es_alergeno=ing["es_alergeno"],
                )
                session.add(nuevo)
                session.flush()
                ing_map[ing["nombre"]] = nuevo
                print(f"  [+] {ing['nombre']}" + (" [ALERGENO]" if ing["es_alergeno"] else ""))
        session.commit()

        # ── 2. Cargar categorías existentes ─────────────────────────────
        print("\nCategorías detectadas:")
        cat_map: dict[str, Categoria] = {}
        todas = session.exec(select(Categoria)).all()
        for cat in todas:
            if cat.nombre:
                cat_map[cat.nombre] = cat
                print(f"  [OK] {cat.nombre} (id={cat.id})")

        # ── 3. Crear productos ──────────────────────────────────────────
        print("\nProductos:")
        creados = 0
        for p in PRODUCTOS:
            existente = session.exec(
                select(Producto).where(Producto.nombre == p["nombre"])
            ).first()
            if existente:
                print(f"  [=] {p['nombre']} (ya existe)")
                continue

            categoria = cat_map.get(p["categoria"])
            if not categoria:
                print(f"  [!!] {p['nombre']} — categoría '{p['categoria']}' NO ENCONTRADA. Saltando.")
                continue

            producto = Producto(
                nombre=p["nombre"],
                descripcion=p["descripcion"],
                precio_base=Decimal(str(p["precio_base"])),
                imagenes_url=p.get("imagenes_url", []),
                disponible=True,
                stock_cantidad=999,
            )
            producto.categorias.append(categoria)
            session.add(producto)
            session.flush()  # obtener producto.id

            # Asociar ingredientes via ProductoIngrediente (requiere unidad_medida_id)
            for ing_nombre, _ in p["ingredientes"]:
                ingrediente = ing_map.get(ing_nombre)
                if ingrediente:
                    pi = ProductoIngrediente(
                        producto_id=producto.id,
                        ingrediente_id=ingrediente.id,
                        es_removible=False,
                        unidad_medida_id=5,  # "unidad" (ud)
                    )
                    session.add(pi)
                else:
                    print(f"    [!!] Ingrediente '{ing_nombre}' no encontrado para {p['nombre']}")

            session.flush()
            creados += 1
            print(f"  [+] {p['nombre']} -> {p['categoria']} (${p['precio_base']:.2f})")

        session.commit()

    print(f"\nCatalogo poblado: {len(ing_map)} ingredientes, {creados} productos nuevos.")


if __name__ == "__main__":
    run()
