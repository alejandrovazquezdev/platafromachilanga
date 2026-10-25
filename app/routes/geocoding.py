from __future__ import annotations

import time
from collections import defaultdict, deque

import requests
from flask import Blueprint, jsonify, request

geocoding_bp = Blueprint("geocoding", __name__, url_prefix="/api")

_CACHE: dict[str, tuple[float, dict]] = {}
_LIMITES = defaultdict(deque)


def _permitido(ip: str) -> bool:
    ahora = time.time()
    cola = _LIMITES[ip]
    while cola and ahora - cola[0] > 60:
        cola.popleft()
    if len(cola) >= 10:
        return False
    cola.append(ahora)
    return True


@geocoding_bp.get("/geocodificar")
def geocodificar():
    consulta = (request.args.get("q") or "").strip()
    if len(consulta) < 5:
        return jsonify({"ok": False, "error": "Escribe una dirección o colonia más completa."}), 400

    clave = consulta.lower()
    guardado = _CACHE.get(clave)
    if guardado and time.time() - guardado[0] < 3600:
        return jsonify(guardado[1])

    if not _permitido(request.remote_addr or "local"):
        return jsonify({"ok": False, "error": "Demasiadas búsquedas. Espera un momento."}), 429

    try:
        respuesta = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "format": "json",
                "limit": 1,
                "q": consulta,
                "countrycodes": "mx",
                "addressdetails": 1,
            },
            headers={
                "User-Agent": "Chilangaton/1.0 (https://chilangaton.devs-quarkz.com)",
                "Accept-Language": "es",
            },
            timeout=8,
        )
        respuesta.raise_for_status()
        datos = respuesta.json()
    except Exception:
        return jsonify({"ok": False, "error": "No pudimos buscar la dirección en este momento."}), 502

    if not datos:
        return jsonify({"ok": False, "error": "No encontramos esa dirección. Prueba con la colonia y la alcaldía."})

    primero = datos[0]
    direccion = primero.get("address") or {}
    colonia = (
        direccion.get("suburb")
        or direccion.get("neighbourhood")
        or direccion.get("quarter")
        or direccion.get("city_district")
        or ""
    )
    alcaldia = (
        direccion.get("borough")
        or direccion.get("city_district")
        or direccion.get("state_district")
        or direccion.get("county")
        or direccion.get("city")
        or ""
    )
    calle = " ".join(
        parte
        for parte in (
            direccion.get("road")
            or direccion.get("pedestrian")
            or direccion.get("square")
            or direccion.get("place"),
            direccion.get("house_number"),
        )
        if parte
    )
    resultado = {
        "ok": True,
        "lat": float(primero["lat"]),
        "lng": float(primero["lon"]),
        "label": primero.get("display_name", consulta),
        "alcaldia": alcaldia,
        "colonia": colonia,
        "calle": calle,
    }
    _CACHE[clave] = (time.time(), resultado)
    return jsonify(resultado)
