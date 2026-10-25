from flask import Blueprint, render_template

from ..models import Comercio, Producto

main_bp = Blueprint("main", __name__)

ESTADISTICAS = [
    ("339", "mercados públicos", "en la Ciudad de México"),
    ("1,367", "tianguis registrados", "en las 16 alcaldías"),
    ("86,931", "unidades de abarrotes", "y comercio al por menor"),
]

BENEFICIOS = [
    {
        "icono": "map-pin",
        "titulo": "Que te encuentren",
        "texto": "Tu comercio aparece en el directorio y en el mapa de comercio popular de la ciudad.",
        "detalle": "Ficha pública con horarios, giro y productos.",
    },
    {
        "icono": "card",
        "titulo": "Cobra como quieras",
        "texto": "Te acompañamos a dar el paso al punto de venta: tarjeta, transferencia y registros claros.",
        "detalle": "Sin costo y a tu ritmo.",
    },
    {
        "icono": "package",
        "titulo": "Muestra lo que vendes",
        "texto": "Publica tus productos, precios y promociones; comparte tu ficha por WhatsApp.",
        "detalle": "Hasta 6 productos en tu ficha.",
    },
]

PASOS = [
    ("01", "Cuéntanos qué vendes", "Nombre, tipo de comercio y giro. Sin RFC obligatorio."),
    ("02", "Dinos dónde y cuándo", "Alcaldía, colonia, dirección y horarios."),
    ("03", "Sube tu oferta", "Productos, precios y formas de pago."),
    ("04", "Recibe tu ficha", "Tu comercio queda visible y con un panel para compartirlo."),
]

FAQS = [
    (
        "¿Es obligatorio tener RFC?",
        "No. Puedes registrarte solo con los datos de tu comercio. El RFC es opcional y no lo usamos para trámites fiscales.",
    ),
    (
        "¿Van a compartir mis datos con el SAT u otra autoridad?",
        "No. Los datos se usan para publicar tu ficha y operar la plataforma. Cualquier transferencia se haría solo con tu consentimiento o por mandato legal.",
    ),
    (
        "¿Tiene algún costo?",
        "No. El registro y la ficha pública son gratuitos. El punto de venta es opcional y se cotiza por separado.",
    ),
    (
        "¿Qué pasa si no tengo internet en mi local?",
        "Puedes registrarte desde tu celular, en el mercado o con apoyo de una persona facilitadora. Después puedes actualizar tu ficha cuando tengas conexión.",
    ),
    (
        "¿Puedo ocultar mi ficha?",
        "Sí. Desde tu panel puedes solicitar que tu comercio deje de aparecer en el directorio sin perder tu registro.",
    ),
]


@main_bp.route("/")
def inicio():
    destacados = (
        Comercio.query.filter_by(estado="publicado")
        .order_by(Comercio.visitas.desc())
        .limit(3)
        .all()
    )
    return render_template(
        "main/inicio.html",
        estadisticas=ESTADISTICAS,
        beneficios=BENEFICIOS,
        pasos=PASOS,
        faqs=FAQS,
        destacados=destacados,
        total_comercios=Comercio.query.filter_by(estado="publicado").count(),
        total_productos=Producto.query.count(),
    )


@main_bp.route("/como-funciona")
def como_funciona():
    return render_template(
        "main/como_funciona.html",
        pasos=PASOS,
        faqs=FAQS,
        beneficios=BENEFICIOS,
    )


@main_bp.route("/aviso-de-privacidad")
def aviso_privacidad():
    return render_template("main/aviso_privacidad.html")
