"""Catálogos y etiquetas del módulo de registro."""

TIPOS = {
    "mercado": {
        "label": "Mercado público",
        "desc": "Local o puesto dentro de un mercado",
        "icono": "store",
    },
    "tianguis": {
        "label": "Tianguis",
        "desc": "Puesto en vía pública o plancha",
        "icono": "tent",
    },
    "tienda": {
        "label": "Tienda de barrio",
        "desc": "Abarrotes, miscelánea o similar",
        "icono": "shop",
    },
    "local": {
        "label": "Local o negocio",
        "desc": "Fonda, taller, artesanías u otro",
        "icono": "building",
    },
}

GIROS = {
    "abarrotes": "Abarrotes y alimentos",
    "alimentos": "Alimentos preparados y bebidas",
    "frutas": "Frutas, verduras y legumbres",
    "artesanias": "Artesanías y productos locales",
    "ropa": "Ropa, calzado y accesorios",
    "servicios": "Servicios y oficios",
    "otro": "Otro giro",
}

ALCALDIAS = [
    "Álvaro Obregón",
    "Azcapotzalco",
    "Benito Juárez",
    "Coyoacán",
    "Cuajimalpa de Morelos",
    "Cuauhtémoc",
    "Gustavo A. Madero",
    "Iztacalco",
    "Iztapalapa",
    "La Magdalena Contreras",
    "Miguel Hidalgo",
    "Milpa Alta",
    "Tláhuac",
    "Tlalpan",
    "Venustiano Carranza",
    "Xochimilco",
]

DIAS = [
    ("lunes", "Lunes"),
    ("martes", "Martes"),
    ("miercoles", "Miércoles"),
    ("jueves", "Jueves"),
    ("viernes", "Viernes"),
    ("sabado", "Sábado"),
    ("domingo", "Domingo"),
]

METODOS = {
    "efectivo": "Efectivo",
    "transferencia": "Transferencia",
    "tarjeta": "Tarjeta",
    "vales": "Vales de despensa",
    "pedidos": "Pedidos por WhatsApp",
}

INTERES_POS = {
    "si": "Sí, quiero información",
    "no": "No por ahora",
    "ya": "Ya tengo punto de venta",
}

COMO_SE_ENTERO = [
    "Un vecino o vecina",
    "Redes sociales",
    "El mercado o tianguis",
    "Una autoridad o programa",
    "Otro",
]


def tipo_label(value):
    return TIPOS.get(value, {}).get("label", "Comercio")


def giro_label(value):
    return GIROS.get(value, "Otro giro")


def metodo_label(value):
    return METODOS.get(value, value)


def interes_label(value):
    return INTERES_POS.get(value, "Por definir")

# Centroides aproximados para ubicar un comercio nuevo en el mapa.
ALCALDIA_COORDS = {
    "Álvaro Obregón": (19.359, -99.205),
    "Azcapotzalco": (19.486, -99.185),
    "Benito Juárez": (19.379, -99.158),
    "Coyoacán": (19.346, -99.161),
    "Cuajimalpa de Morelos": (19.355, -99.300),
    "Cuauhtémoc": (19.432, -99.133),
    "Gustavo A. Madero": (19.482, -99.113),
    "Iztacalco": (19.395, -99.097),
    "Iztapalapa": (19.356, -99.092),
    "La Magdalena Contreras": (19.333, -99.230),
    "Miguel Hidalgo": (19.432, -99.200),
    "Milpa Alta": (19.192, -99.023),
    "Tláhuac": (19.270, -99.003),
    "Tlalpan": (19.296, -99.165),
    "Venustiano Carranza": (19.423, -99.100),
    "Xochimilco": (19.257, -99.104),
}

CATEGORIAS_NOTICIA = {
    "regulacion": {"label": "Regulación", "icono": "shield", "clase": "regulacion"},
    "apoyos": {"label": "Apoyos", "icono": "heart", "clase": "apoyos"},
    "tramites": {"label": "Trámites", "icono": "file", "clase": "tramites"},
    "digitalizacion": {"label": "Digitalización", "icono": "card", "clase": "digitalizacion"},
    "seguridad": {"label": "Seguridad", "icono": "alert", "clase": "seguridad"},
    "avisos": {"label": "Avisos", "icono": "bell", "clase": "avisos"},
}

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def categoria_noticia_label(value):
    return CATEGORIAS_NOTICIA.get(value, {}).get("label", "Aviso")

CATEGORIAS_NOTICIA_LABELS = {clave: datos["label"] for clave, datos in CATEGORIAS_NOTICIA.items()}
