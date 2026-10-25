from __future__ import annotations

from urllib.parse import urlparse

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .. import db
from ..models import Comercio, Cuenta

auth_bp = Blueprint("auth", __name__)


def _destino_seguro(valor: str | None) -> str:
    if not valor:
        return url_for("panel.inicio")
    parsed = urlparse(valor)
    if parsed.netloc or not valor.startswith("/") or valor.startswith("//"):
        return url_for("panel.inicio")
    return valor


@auth_bp.route("/iniciar-sesion", methods=["GET", "POST"])
@auth_bp.route("/login", methods=["GET", "POST"], endpoint="login_alias")
def login():
    if session.get("comercio_id") and db.session.get(Comercio, session["comercio_id"]):
        return redirect(url_for("panel.inicio"))

    error = None
    if request.method == "POST":
        email = (request.form.get("usuario") or "").strip().lower()
        password = request.form.get("contra") or ""
        cuenta = Cuenta.query.filter_by(email=email, activa=True).first()
        if cuenta is None or not cuenta.check_password(password):
            error = "Correo o contraseña incorrectos. Revisa tus datos."
        else:
            session.clear()
            session["comercio_id"] = cuenta.comercio_id
            session["cuenta_id"] = cuenta.id
            session.permanent = True
            return redirect(_destino_seguro(request.form.get("next") or request.args.get("next")))

    return render_template(
        "auth/login.html",
        error=error,
        next=request.args.get("next", request.form.get("next", "")),
    )


@auth_bp.route("/salir")
def logout():
    session.clear()
    flash("Cerraste sesión.", "ok")
    return redirect(url_for("auth.login"))


@auth_bp.route("/IS.html")
def legado_login():
    return redirect(url_for("auth.login"))


@auth_bp.route("/dashboard.html")
def legado_dashboard():
    return redirect(url_for("panel.inicio"))
