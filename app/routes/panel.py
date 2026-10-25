from __future__ import annotations

from flask import Blueprint, redirect, render_template, session, url_for

from .. import db
from ..models import Comercio

panel_bp = Blueprint("panel", __name__)


def _qr_svg(comercio: Comercio) -> str | None:
    try:
        import segno

        url = url_for("directorio.ficha", slug=comercio.slug, _external=True)
        return segno.make(url, error="m").svg_inline(
            scale=4, border=2, dark="#9F2241", light="#ffffff"
        )
    except Exception:
        return None


@panel_bp.route("/panel/editar")
def editar():
    comercio = None
    comercio_id = session.get("comercio_id")
    if comercio_id:
        comercio = db.session.get(Comercio, comercio_id)
    if comercio is None:
        comercio = Comercio.query.order_by(Comercio.visitas.desc()).first()
    if comercio is None:
        return redirect(url_for("registro.paso1"))

    session["registro_draft"] = {
        "nombre": comercio.nombre,
        "tipo": comercio.tipo,
        "giro": comercio.giro,
        "descripcion": comercio.descripcion,
        "anios_operando": comercio.anios_operando,
        "personas": comercio.personas or "",
        "rfc": comercio.rfc,
        "alcaldia": comercio.alcaldia,
        "colonia": comercio.colonia,
        "calle": comercio.calle,
        "referencias": comercio.referencias,
        "lat": comercio.lat,
        "lng": comercio.lng,
        "ubicacion_label": "",
        "horario": comercio.horario or {},
        "dias_tianguis": comercio.dias_tianguis,
        "numero_puesto": comercio.numero_puesto,
        "productos": [
            {
                "nombre": p.nombre,
                "categoria": p.categoria,
                "precio": p.precio,
                "unidad": p.unidad,
            }
            for p in comercio.productos
        ],
        "metodos_pago": comercio.metodos_pago or [],
        "interes_pos": comercio.interes_pos,
        "contacto_nombre": comercio.contacto_nombre,
        "telefono": comercio.telefono,
        "whatsapp": comercio.whatsapp,
        "email": comercio.email,
        "como_se_entero": comercio.como_se_entero,
        "consent": True,
    }
    session["editando_id"] = comercio.id
    session["comercio_id"] = comercio.id
    return redirect(url_for("registro.paso1"))


@panel_bp.route("/panel/ficha-imprimible")
def ficha_imprimible():
    comercio = None
    comercio_id = session.get("comercio_id")
    if comercio_id:
        comercio = db.session.get(Comercio, comercio_id)
    if comercio is None:
        comercio = Comercio.query.order_by(Comercio.visitas.desc()).first()
    if comercio is None:
        return redirect(url_for("registro.paso1"))
    return render_template(
        "panel/ficha_imprimible.html",
        comercio=comercio,
        qr_svg=_qr_svg(comercio),
    )


@panel_bp.route("/panel")
def inicio():
    comercio = None
    comercio_id = session.get("comercio_id")
    if comercio_id:
        comercio = db.session.get(Comercio, comercio_id)

    demo = comercio is None
    if comercio is None:
        comercio = Comercio.query.order_by(Comercio.visitas.desc()).first()
    if comercio is None:
        return redirect(url_for("registro.paso1"))

    productos = list(comercio.productos)
    recomendaciones = [
        {
            "hecho": bool(comercio.descripcion),
            "titulo": "Agrega una descripción de tu comercio",
            "detalle": "Una o dos frases ayudan a que la gente sepa qué encontrar.",
            "url": url_for("panel.editar"),
        },
        {
            "hecho": len(productos) >= 3,
            "titulo": "Publica al menos 3 productos",
            "detalle": "Muestra lo que más vendes y el precio de referencia.",
            "url": url_for("panel.editar"),
        },
        {
            "hecho": bool(comercio.horario),
            "titulo": "Confirma tus horarios",
            "detalle": "La gente decide visitarte si sabe cuándo estás abierto.",
            "url": url_for("panel.editar"),
        },
        {
            "hecho": bool(comercio.whatsapp),
            "titulo": "Activa pedidos por WhatsApp",
            "detalle": "Un canal directo para pedidos y dudas del barrio.",
            "url": url_for("panel.editar"),
        },
    ]

    actividad = [
        {
            "icono": "eye",
            "titulo": "Tu ficha recibió visitas",
            "detalle": f"{max(comercio.visitas, 0)} personas vieron tu comercio esta semana.",
            "cuando": "Hoy",
        },
        {
            "icono": "package",
            "titulo": "Productos publicados",
            "detalle": f"{len(productos)} productos visibles en tu ficha.",
            "cuando": "Esta semana",
        },
        {
            "icono": "card",
            "titulo": (
                "Interés en punto de venta"
                if comercio.interes_pos == "si"
                else "Punto de venta"
            ),
            "detalle": (
                "Un asesor puede contactarte para cotizar el equipo."
                if comercio.interes_pos == "si"
                else "Puedes solicitar información cuando quieras."
            ),
            "cuando": "Pendiente",
        },
    ]

    return render_template(
        "panel/inicio.html",
        comercio=comercio,
        productos=productos,
        demo=demo,
        porcentaje=comercio.porcentaje_completo,
        recomendaciones=recomendaciones,
        actividad=actividad,
        qr_svg=_qr_svg(comercio),
        ultimo_folio=session.get("ultimo_folio"),
    )
