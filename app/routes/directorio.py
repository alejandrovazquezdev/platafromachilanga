from __future__ import annotations

import json

from flask import Blueprint, render_template, request
from sqlalchemy import or_

from .. import db
from ..constants import ALCALDIAS, GIROS, TIPOS
from ..models import Comercio
from ..search import filtrar

directorio_bp = Blueprint("directorio", __name__)


def _filtros():
    return {
        "q": (request.args.get("q") or "").strip()[:80],
        "alcaldia": (request.args.get("alcaldia") or "").strip(),
        "giro": (request.args.get("giro") or "").strip(),
        "tipo": (request.args.get("tipo") or "").strip(),
        "abierto": request.args.get("abierto") == "1",
    }


@directorio_bp.route("/directorio")
def lista():
    filtros = _filtros()
    query = Comercio.query.filter_by(estado="publicado")

    if filtros["alcaldia"] in ALCALDIAS:
        query = query.filter_by(alcaldia=filtros["alcaldia"])
    if filtros["giro"] in GIROS:
        query = query.filter_by(giro=filtros["giro"])
    if filtros["tipo"] in TIPOS:
        query = query.filter_by(tipo=filtros["tipo"])

    comercios = query.order_by(Comercio.visitas.desc(), Comercio.nombre.asc()).all()
    if filtros["abierto"]:
        comercios = [c for c in comercios if c.abierto_ahora]
    if filtros["q"]:
        comercios = filtrar(
            comercios,
            filtros["q"],
            lambda c: [
                c.nombre,
                c.colonia,
                c.alcaldia,
                c.giro_label,
                c.tipo_label,
                c.descripcion,
                " ".join(p.nombre for p in c.productos),
            ],
        )
    mapa = [c.to_public_dict() for c in comercios]
    return render_template(
        "directorio/lista.html",
        comercios=comercios,
        total=len(comercios),
        filtros=filtros,
        mapa_json=json.dumps(mapa, ensure_ascii=False),
    )


@directorio_bp.route("/comercio/<slug>")
def ficha(slug: str):
    comercio = Comercio.query.filter_by(slug=slug, estado="publicado").first_or_404()
    relacionados = (
        Comercio.query.filter(
            Comercio.id != comercio.id,
            Comercio.estado == "publicado",
            or_(Comercio.alcaldia == comercio.alcaldia, Comercio.giro == comercio.giro),
        )
        .order_by(Comercio.visitas.desc())
        .limit(3)
        .all()
    )
    return render_template(
        "directorio/ficha.html",
        comercio=comercio,
        relacionados=relacionados,
        mapa_json=json.dumps([comercio.to_public_dict()], ensure_ascii=False),
    )
