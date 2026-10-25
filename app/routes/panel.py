from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from .. import db
from ..models import Comercio, Producto

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


def _comercio_actual() -> Comercio | None:
    comercio_id = session.get("comercio_id")
    if not comercio_id:
        return None
    return db.session.get(Comercio, comercio_id)


def _ir_a_login():
    return redirect(url_for("auth.login", next=request.path))


@panel_bp.route("/panel")
def inicio():
    comercio = _comercio_actual()
    if comercio is None:
        return _ir_a_login()

    productos = sorted(comercio.productos, key=lambda p: p.id, reverse=True)
    return render_template(
        "panel/dashboard.html",
        comercio=comercio,
        productos=productos,
        cuenta=comercio.cuenta,
    )


@panel_bp.post("/panel/productos")
def agregar_producto():
    comercio = _comercio_actual()
    if comercio is None:
        return _ir_a_login()

    nombre = (request.form.get("nombre") or "").strip()[:140]
    precio_raw = (request.form.get("precio") or "").strip().replace("$", "").replace(",", "")
    descripcion = (request.form.get("descripcion") or "").strip()[:240]

    if len(nombre) < 2:
        flash("Escribe el nombre del producto.", "error")
        return redirect(url_for("panel.inicio"))

    try:
        precio = float(precio_raw)
        if precio < 0:
            raise ValueError
        precio_texto = f"${precio:,.2f}"
    except (TypeError, ValueError):
        flash("Escribe un precio válido, por ejemplo 250.00.", "error")
        return redirect(url_for("panel.inicio"))

    db.session.add(
        Producto(
            comercio_id=comercio.id,
            nombre=nombre,
            categoria="Producto",
            precio=precio_texto,
            unidad="pieza",
            descripcion=descripcion,
        )
    )
    db.session.commit()
    flash("Producto agregado a tu tienda.", "ok")
    return redirect(url_for("panel.inicio"))


@panel_bp.route("/panel/editar")
def editar():
    comercio = _comercio_actual()
    if comercio is None:
        return _ir_a_login()

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
        "password": "",
        "password_confirm": "",
        "consent": True,
    }
    session["editando_id"] = comercio.id
    session["comercio_id"] = comercio.id
    return redirect(url_for("registro.paso1"))


@panel_bp.route("/panel/ficha-imprimible")
def ficha_imprimible():
    comercio = _comercio_actual()
    if comercio is None:
        return _ir_a_login()
    return render_template(
        "panel/ficha_imprimible.html",
        comercio=comercio,
        qr_svg=_qr_svg(comercio),
    )
