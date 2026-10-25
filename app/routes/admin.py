from __future__ import annotations

import secrets
from datetime import datetime
from urllib.parse import urlparse

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .. import db
from ..constants import CATEGORIAS_NOTICIA
from ..models import Comercio, Noticia, NotificacionLog, SolicitudDigitalizacion, Suscripcion, slugify
from ..push import enviar_push, push_configurado

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.before_request
def proteger_admin():
    if not current_app.config.get("ADMIN_PASSWORD"):
        abort(404)
    if request.endpoint == "admin.login":
        return None
    if not session.get("admin_ok"):
        return redirect(url_for("admin.login", next=request.path))
    return None


def _destino_seguro(valor: str | None) -> str:
    if not valor:
        return url_for("admin.dashboard")
    parsed = urlparse(valor)
    if parsed.netloc or not valor.startswith("/") or valor.startswith("//"):
        return url_for("admin.dashboard")
    return valor


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin_ok"):
        return redirect(url_for("admin.dashboard"))
    error = None
    if request.method == "POST":
        password = request.form.get("password", "")
        if secrets.compare_digest(password, current_app.config["ADMIN_PASSWORD"]):
            session["admin_ok"] = True
            session.permanent = False
            return redirect(_destino_seguro(request.form.get("next")))
        error = "Contraseña incorrecta."
    return render_template("admin/login.html", error=error, next=request.args.get("next", ""))


@admin_bp.route("/logout")
def logout():
    session.pop("admin_ok", None)
    return redirect(url_for("admin.login"))


@admin_bp.route("/")
def dashboard():
    stats = {
        "noticias": Noticia.query.count(),
        "publicadas": Noticia.query.filter_by(publicada=True).count(),
        "suscripciones": Suscripcion.query.filter_by(activa=True).count(),
        "comercios": Comercio.query.count(),
        "solicitudes": SolicitudDigitalizacion.query.count(),
    }
    ultimas = Noticia.query.order_by(Noticia.creada_en.desc()).limit(6).all()
    logs = NotificacionLog.query.order_by(NotificacionLog.enviada_en.desc()).limit(5).all()
    solicitudes = (
        SolicitudDigitalizacion.query.order_by(SolicitudDigitalizacion.creada_en.desc()).limit(5).all()
    )
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        ultimas=ultimas,
        logs=logs,
        solicitudes=solicitudes,
        push_ok=push_configurado(),
    )


@admin_bp.route("/noticias")
def noticias():
    todas = Noticia.query.order_by(Noticia.creada_en.desc()).all()
    return render_template("admin/noticias.html", noticias=todas, push_ok=push_configurado())


@admin_bp.route("/noticias/nueva", methods=["GET", "POST"])
@admin_bp.route("/noticias/<int:noticia_id>/editar", methods=["GET", "POST"])
def noticia_form(noticia_id: int | None = None):
    noticia = db.session.get(Noticia, noticia_id) if noticia_id else None
    if noticia_id and noticia is None:
        abort(404)

    if request.method == "POST":
        titulo = (request.form.get("titulo") or "").strip()[:200]
        resumen = (request.form.get("resumen") or "").strip()[:320]
        cuerpo = (request.form.get("cuerpo") or "").strip()
        categoria = (request.form.get("categoria") or "").strip()
        fuente_nombre = (request.form.get("fuente_nombre") or "").strip()[:120]
        fuente_url = (request.form.get("fuente_url") or "").strip()[:300]
        publicada = request.form.get("publicada") == "on"
        destacada = request.form.get("destacada") == "on"
        notificar = request.form.get("notificar") == "on"

        error = None
        if len(titulo) < 5:
            error = "El título es demasiado corto."
        elif len(resumen) < 10:
            error = "El resumen es demasiado corto."
        elif len(cuerpo) < 20:
            error = "El cuerpo de la noticia es demasiado corto."
        elif categoria not in CATEGORIAS_NOTICIA:
            error = "Elige una categoría válida."

        if error:
            flash(error, "error")
            return render_template(
                "admin/noticia_form.html",
                noticia=noticia,
                valores=request.form,
                errores={"general": error},
                push_ok=push_configurado(),
            )

        if noticia is None:
            base = slugify(titulo)
            slug = base
            i = 2
            while Noticia.query.filter_by(slug=slug).first():
                slug = f"{base}-{i}"
                i += 1
            noticia = Noticia(slug=slug, creada_en=datetime.now())
            db.session.add(noticia)

        noticia.titulo = titulo
        noticia.resumen = resumen
        noticia.cuerpo = cuerpo
        noticia.categoria = categoria
        noticia.fuente_nombre = fuente_nombre
        noticia.fuente_url = fuente_url
        noticia.publicada = publicada
        noticia.destacada = destacada
        db.session.commit()

        flash("Noticia guardada.", "ok")
        if notificar and publicada:
            resultado = enviar_push(
                titulo,
                resumen,
                url_for("noticias.detalle", slug=noticia.slug, _external=True),
                noticia,
            )
            flash(resultado["mensaje"], "ok" if resultado["ok"] else "error")
        return redirect(url_for("admin.noticias"))

    return render_template(
        "admin/noticia_form.html",
        noticia=noticia,
        valores={},
        errores={},
        push_ok=push_configurado(),
    )


@admin_bp.route("/noticias/<int:noticia_id>/notificar", methods=["POST"])
def notificar_noticia(noticia_id: int):
    noticia = db.session.get(Noticia, noticia_id)
    if noticia is None:
        abort(404)
    resultado = enviar_push(
        noticia.titulo,
        noticia.resumen,
        url_for("noticias.detalle", slug=noticia.slug, _external=True),
        noticia,
    )
    flash(resultado["mensaje"], "ok" if resultado["ok"] else "error")
    return redirect(url_for("admin.noticias"))


@admin_bp.route("/notificar", methods=["GET", "POST"])
def notificar():
    if request.method == "POST":
        titulo = (request.form.get("titulo") or "").strip()[:200]
        cuerpo = (request.form.get("cuerpo") or "").strip()[:400]
        url = (request.form.get("url") or "").strip()[:300]
        if len(titulo) < 3 or len(cuerpo) < 3:
            flash("Escribe un título y un mensaje.", "error")
        else:
            resultado = enviar_push(titulo, cuerpo, url)
            flash(resultado["mensaje"], "ok" if resultado["ok"] else "error")
            return redirect(url_for("admin.notificar"))

    logs = NotificacionLog.query.order_by(NotificacionLog.enviada_en.desc()).limit(12).all()
    return render_template(
        "admin/notificar.html",
        logs=logs,
        push_ok=push_configurado(),
        suscripciones=Suscripcion.query.filter_by(activa=True).count(),
    )


@admin_bp.route("/suscripciones")
def suscripciones():
    activas = Suscripcion.query.filter_by(activa=True).order_by(Suscripcion.creada_en.desc()).all()
    return render_template("admin/suscripciones.html", suscripciones=activas)
