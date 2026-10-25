"""Envío de notificaciones Web Push."""

from __future__ import annotations

import json
from pathlib import Path

from flask import current_app, url_for

from . import db
from .models import Noticia, NotificacionLog, Suscripcion


def _ruta_llave() -> Path:
    ruta = Path(current_app.config.get("VAPID_PRIVATE_KEY_PATH", "vapid_private.pem"))
    if not ruta.is_absolute():
        ruta = Path(current_app.root_path).parent / ruta
    return ruta


def push_configurado() -> bool:
    return bool(
        current_app.config.get("VAPID_PUBLIC_KEY")
        and _ruta_llave().exists()
    )


def enviar_push(titulo: str, cuerpo: str, url: str = "", noticia: Noticia | None = None) -> dict:
    """Envía una notificación a todas las suscripciones activas.

    Devuelve un diccionario con total, exitos, fallos y un mensaje para el admin.
    Si no hay VAPID configurado, no intenta enviar y lo reporta.
    """
    if not push_configurado():
        return {
            "ok": False,
            "total": 0,
            "exitos": 0,
            "fallos": 0,
            "mensaje": "Web Push no está configurado (faltan VAPID_PUBLIC_KEY o la llave privada).",
        }

    try:
        from pywebpush import WebPushException, webpush
    except Exception:
        return {
            "ok": False,
            "total": 0,
            "exitos": 0,
            "fallos": 0,
            "mensaje": "Falta instalar pywebpush en el entorno.",
        }

    suscripciones = Suscripcion.query.filter_by(activa=True).all()
    payload = {
        "title": titulo,
        "body": cuerpo,
        "url": url or "/noticias",
        "icon": url_for("static", filename="img/icon-192.png"),
        "badge": url_for("static", filename="img/icon-192.png"),
        "tag": f"chilangaton-{noticia.id if noticia else 'aviso'}",
    }

    exitos = 0
    fallos = 0
    for suscripcion in suscripciones:
        try:
            webpush(
                subscription_info=suscripcion.to_webpush(),
                data=json.dumps(payload, ensure_ascii=False),
                vapid_private_key=str(_ruta_llave()),
                vapid_claims={"sub": current_app.config.get("VAPID_SUBJECT", "mailto:equipo@chilangaton.mx")},
                timeout=12,
            )
            exitos += 1
        except WebPushException as exc:
            fallos += 1
            status = getattr(getattr(exc, "response", None), "status_code", None)
            if status in (404, 410):
                suscripcion.activa = False
        except Exception:
            fallos += 1

    log = NotificacionLog(
        noticia_id=noticia.id if noticia else None,
        titulo=titulo[:200],
        cuerpo=cuerpo[:400],
        url=url[:300],
        total=len(suscripciones),
        exitos=exitos,
        fallos=fallos,
    )
    db.session.add(log)
    db.session.commit()

    if not suscripciones:
        mensaje = "No hay dispositivos suscritos todavía."
    elif exitos:
        mensaje = f"Notificación enviada a {exitos} dispositivo(s)."
    else:
        mensaje = "No se pudo entregar a ningún dispositivo."
    if fallos and exitos:
        mensaje += f" {fallos} fallo(s)."

    return {
        "ok": exitos > 0,
        "total": len(suscripciones),
        "exitos": exitos,
        "fallos": fallos,
        "mensaje": mensaje,
    }
