from __future__ import annotations

import secrets
from datetime import datetime
from pathlib import Path

from flask import Flask, abort, current_app, jsonify, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from .constants import (
    ALCALDIAS,
    CATEGORIAS_NOTICIA,
    CATEGORIAS_NOTICIA_LABELS,
    COMO_SE_ENTERO,
    DIAS,
    GIROS,
    INTERES_POS,
    METODOS,
    TIPOS,
    categoria_noticia_label,
    giro_label,
    interes_label,
    metodo_label,
    tipo_label,
)

db = SQLAlchemy()


def create_app(config_object="config.Config") -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    uri = app.config["SQLALCHEMY_DATABASE_URI"]
    if uri.startswith("sqlite:///") and ":memory:" not in uri:
        Path(uri.replace("sqlite:///", "")).parent.mkdir(parents=True, exist_ok=True)

    db.init_app(app)

    from . import models  # noqa: F401  (registra los modelos)

    from .routes.admin import admin_bp
    from .routes.chat import chat_bp
    from .routes.directorio import directorio_bp
    from .routes.geocoding import geocoding_bp
    from .routes.main import main_bp
    from .routes.noticias import noticias_bp
    from .routes.notificaciones import notificaciones_bp
    from .routes.panel import panel_bp
    from .routes.registro import registro_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(registro_bp)
    app.register_blueprint(directorio_bp)
    app.register_blueprint(panel_bp)
    app.register_blueprint(noticias_bp)
    app.register_blueprint(notificaciones_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(geocoding_bp)

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.filters.update(
        tipo_label=tipo_label,
        giro_label=giro_label,
        metodo_label=metodo_label,
        interes_label=interes_label,
        categoria_noticia_label=categoria_noticia_label,
    )
    app.jinja_env.globals.update(
        TIPOS=TIPOS,
        GIROS=GIROS,
        ALCALDIAS=ALCALDIAS,
        DIAS=DIAS,
        METODOS=METODOS,
        INTERES_POS=INTERES_POS,
        COMO_SE_ENTERO=COMO_SE_ENTERO,
        CATEGORIAS_NOTICIA=CATEGORIAS_NOTICIA,
        CATEGORIAS_NOTICIA_LABELS=CATEGORIAS_NOTICIA_LABELS,
        tipo_label=tipo_label,
        giro_label=giro_label,
        metodo_label=metodo_label,
        interes_label=interes_label,
        anio_actual=datetime.now().year,
    )

    @app.context_processor
    def inject_csrf():
        if "_csrf_token" not in session:
            session["_csrf_token"] = secrets.token_urlsafe(32)
        return {
            "csrf_token": lambda: session["_csrf_token"],
            "vapid_public_key": current_app.config.get("VAPID_PUBLIC_KEY", ""),
            "push_enabled": current_app.config.get("PUSH_ENABLED", False),
        }

    @app.before_request
    def csrf_protect():
        if request.method == "POST":
            token = session.get("_csrf_token")
            enviado = request.form.get("_csrf_token", "") or request.headers.get("X-CSRF-Token", "")
            if not token or not secrets.compare_digest(token, enviado):
                abort(400, description="La sesión expiró. Vuelve a cargar la página e intenta de nuevo.")

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=(self)"
        )
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "script-src 'self' 'unsafe-inline' https://unpkg.com; "
            "img-src 'self' data: https://server.arcgisonline.com https://unpkg.com; "
            "connect-src 'self'; worker-src 'self'; manifest-src 'self'; frame-ancestors 'self'",
        )
        return response

    @app.template_filter("fecha")
    def formato_fecha(valor):
        if not valor:
            return ""
        return valor.strftime("%d/%m/%Y")

    @app.template_filter("categoria_noticia")
    def filtro_categoria_noticia(valor):
        return categoria_noticia_label(valor)

    @app.template_filter("precio")
    def formato_precio(valor):
        texto = (valor or "").strip()
        if not texto:
            return "Precio a consultar"
        return texto if texto.startswith("$") else f"${texto}"

    @app.route("/salud")
    def salud():
        from .models import Comercio

        return jsonify(
            {
                "status": "ok",
                "servicio": "chilangaton",
                "comercios": Comercio.query.count(),
                "hora": datetime.now().isoformat(timespec="seconds"),
            }
        )

    @app.errorhandler(400)
    def error_400(error):
        return render_template("errores/400.html", error=error), 400

    @app.errorhandler(404)
    def error_404(error):
        return render_template("errores/404.html"), 404

    @app.errorhandler(500)
    def error_500(error):
        db.session.rollback()
        return render_template("errores/500.html"), 500

    @app.errorhandler(HTTPException)
    def http_error(error):
        if error.code == 400:
            return render_template("errores/400.html", error=error), 400
        if error.code == 404:
            return render_template("errores/404.html"), 404
        return error

    @app.cli.command("init-db")
    def init_db_command():
        """Crea las tablas y carga los datos de demostración."""
        db.create_all()
        if app.config.get("SEED_DATA", True):
            from .data.seed import seed_if_empty

            seed_if_empty()
        print("Base lista.")

    with app.app_context():
        db.create_all()
        if app.config.get("SEED_DATA", True):
            from .data.seed import seed_if_empty, seed_noticias

            seed_if_empty()
            seed_noticias()

    return app
