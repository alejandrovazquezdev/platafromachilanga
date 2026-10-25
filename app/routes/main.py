from flask import Blueprint, current_app, flash, redirect, render_template, request, send_from_directory, url_for

from .. import db
from ..models import Comercio, Noticia, Producto, SolicitudDigitalizacion

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
    noticias_destacadas = (
        Noticia.query.filter_by(publicada=True)
        .order_by(Noticia.destacada.desc(), Noticia.creada_en.desc())
        .limit(3)
        .all()
    )
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
        noticias_destacadas=noticias_destacadas,
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


@main_bp.route("/digitaliza", methods=["GET", "POST"])
def digitaliza():
    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()[:140]
        comercio = (request.form.get("comercio") or "").strip()[:160]
        telefono = (request.form.get("telefono") or "").strip()[:24]
        alcaldia = (request.form.get("alcaldia") or "").strip()[:60]
        interes = (request.form.get("interes") or "diagnostico").strip()[:40]
        mensaje = (request.form.get("mensaje") or "").strip()[:600]
        errores = {}
        if len(nombre) < 3:
            errores["nombre"] = "Escribe tu nombre."
        digitos = "".join(c for c in telefono if c.isdigit())
        if len(digitos) == 12 and digitos.startswith("52"):
            digitos = digitos[2:]
        if len(digitos) != 10:
            errores["telefono"] = "Escribe un teléfono de 10 dígitos."
        if request.form.get("consent") != "on":
            errores["consent"] = "Acepta el aviso de privacidad para continuar."
        if errores:
            return render_template("main/digitaliza.html", errores=errores, valores=request.form)
        solicitud = SolicitudDigitalizacion(
            nombre=nombre,
            comercio=comercio,
            telefono=telefono,
            alcaldia=alcaldia,
            interes=interes,
            mensaje=mensaje,
        )
        db.session.add(solicitud)
        db.session.commit()
        flash("Recibimos tu solicitud. Te contactamos para agendar un diagnóstico.", "ok")
        return redirect(url_for("main.digitaliza") + "#solicitud")
    return render_template("main/digitaliza.html", errores={}, valores={})


@main_bp.route("/preguntas-frecuentes")
def preguntas_frecuentes():
    return render_template("main/preguntas_frecuentes.html", faqs=FAQS_COMPLETAS)


@main_bp.route("/marco-legal")
def marco_legal():
    return render_template("main/marco_legal.html")


@main_bp.route("/sw.js")
def service_worker():
    respuesta = send_from_directory(current_app.static_folder, "sw.js", mimetype="application/javascript")
    respuesta.headers["Service-Worker-Allowed"] = "/"
    respuesta.headers["Cache-Control"] = "no-cache"
    return respuesta


@main_bp.route("/manifest.webmanifest")
def manifest():
    respuesta = send_from_directory(
        current_app.static_folder, "manifest.webmanifest", mimetype="application/manifest+json"
    )
    respuesta.headers["Cache-Control"] = "public, max-age=3600"
    return respuesta


FAQS_COMPLETAS = [
    (
        "¿Es obligatorio registrar mi comercio?",
        "No. El registro es voluntario y gratuito. Sirve para que tu comercio aparezca en el directorio y tengas una ficha pública que puedes compartir.",
    ),
    (
        "¿Tiene algún costo?",
        "No. El registro y la ficha pública son gratuitos. El punto de venta es opcional y se cotiza por separado con el proveedor.",
    ),
    (
        "¿Necesito RFC para registrarme?",
        "No. El RFC es un campo opcional. Si decides proporcionarlo, no se muestra en tu ficha pública ni lo usamos para trámites fiscales.",
    ),
    (
        "¿Van a compartir mis datos con el SAT u otra autoridad?",
        "No compartimos tus datos para fines comerciales. Solo los usaríamos con tu consentimiento o por un mandato legal. El aviso de privacidad explica el detalle.",
    ),
    (
        "¿Qué pasa si no tengo internet en mi local?",
        "Puedes registrarte desde tu celular, en el mercado o con apoyo de una persona facilitadora. Después puedes actualizar tu ficha cuando tengas conexión.",
    ),
    (
        "¿Puedo ocultar mi ficha?",
        "Sí. Desde tu panel puedes solicitar que tu comercio deje de aparecer en el directorio sin perder tu registro.",
    ),
    (
        "¿Cómo actualizo mis productos o precios?",
        "Entra a tu panel y elige “Editar ficha”. Ahí puedes cambiar productos, precios, horarios y datos de contacto. Los cambios se reflejan en el directorio.",
    ),
    (
        "¿Qué es el punto de venta?",
        "Es una terminal o solución para cobrar con tarjeta. Es opcional. Si te interesa, te contactamos para orientarte sobre comisiones y equipos.",
    ),
    (
        "¿Cómo funcionan las notificaciones?",
        "Si activas los avisos en tu celular, te enviamos noticias, recordatorios y fechas importantes para tu comercio. Puedes desactivarlas desde tu navegador cuando quieras.",
    ),
    (
        "¿Quién puede ver mi teléfono?",
        "El teléfono y el WhatsApp se muestran en tu ficha para que tus clientes te contacten. El correo y el nombre de la persona de contacto no se publican.",
    ),
    (
        "¿El registro sustituye algún trámite de la alcaldía?",
        "No. Es una ficha informativa para la plataforma. Los trámites de funcionamiento, permisos y obligaciones fiscales se realizan en las autoridades correspondientes.",
    ),
]
