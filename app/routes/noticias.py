from __future__ import annotations

from flask import Blueprint, abort, render_template, request

from ..constants import CATEGORIAS_NOTICIA
from ..models import Noticia
from ..search import filtrar

noticias_bp = Blueprint("noticias", __name__, url_prefix="/noticias")


@noticias_bp.route("/")
def lista():
    categoria = (request.args.get("categoria") or "").strip()
    q = (request.args.get("q") or "").strip()[:80]

    query = Noticia.query.filter_by(publicada=True)
    if categoria in CATEGORIAS_NOTICIA:
        query = query.filter_by(categoria=categoria)
    noticias = query.order_by(Noticia.destacada.desc(), Noticia.creada_en.desc()).all()
    if q:
        noticias = filtrar(
            noticias,
            q,
            lambda n: [n.titulo, n.resumen, n.cuerpo, n.categoria_label, n.fuente_nombre],
        )
    return render_template(
        "noticias/lista.html",
        noticias=noticias,
        categoria=categoria,
        q=q,
        total=len(noticias),
    )


@noticias_bp.route("/<slug>")
def detalle(slug: str):
    noticia = Noticia.query.filter_by(slug=slug, publicada=True).first()
    if noticia is None:
        abort(404)
    relacionadas = (
        Noticia.query.filter(
            Noticia.publicada.is_(True),
            Noticia.id != noticia.id,
            Noticia.categoria == noticia.categoria,
        )
        .order_by(Noticia.creada_en.desc())
        .limit(3)
        .all()
    )
    return render_template("noticias/detalle.html", noticia=noticia, relacionadas=relacionadas)
