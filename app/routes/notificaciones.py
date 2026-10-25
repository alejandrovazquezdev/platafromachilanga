from __future__ import annotations

from flask import Blueprint, jsonify, request

from .. import db
from ..models import Suscripcion

notificaciones_bp = Blueprint("notificaciones", __name__, url_prefix="/api/notificaciones")


@notificaciones_bp.post("/suscribir")
def suscribir():
    data = request.get_json(silent=True) or {}
    endpoint = (data.get("endpoint") or "").strip()
    keys = data.get("keys") or {}
    p256dh = (keys.get("p256dh") or "").strip()
    auth = (keys.get("auth") or "").strip()

    if not endpoint.startswith("https://") or not p256dh or not auth:
        return jsonify({"ok": False, "error": "Suscripción inválida."}), 400

    suscripcion = Suscripcion.query.filter_by(endpoint=endpoint).first()
    if suscripcion is None:
        suscripcion = Suscripcion(endpoint=endpoint)
        db.session.add(suscripcion)
    suscripcion.p256dh = p256dh[:300]
    suscripcion.auth = auth[:100]
    suscripcion.user_agent = (request.user_agent.string or "")[:300]
    suscripcion.activa = True
    db.session.commit()
    return jsonify({"ok": True})


@notificaciones_bp.post("/desuscribir")
def desuscribir():
    data = request.get_json(silent=True) or {}
    endpoint = (data.get("endpoint") or "").strip()
    if endpoint:
        Suscripcion.query.filter_by(endpoint=endpoint).update({"activa": False})
        db.session.commit()
    return jsonify({"ok": True})
