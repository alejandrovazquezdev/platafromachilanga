from __future__ import annotations

import re
import secrets
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

from . import db
from .constants import (
    CATEGORIAS_NOTICIA,
    DIAS,
    GIROS,
    INTERES_POS,
    MESES,
    METODOS,
    TIPOS,
    categoria_noticia_label,
    giro_label,
    interes_label,
    metodo_label,
    tipo_label,
)

CDMX_TZ = ZoneInfo("America/Mexico_City")


def slugify(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    texto = re.sub(r"[^a-zA-Z0-9]+", "-", texto).strip("-").lower()
    return (texto[:80] or "comercio").strip("-")


class Comercio(db.Model):
    __tablename__ = "comercios"

    id = db.Column(db.Integer, primary_key=True)
    folio = db.Column(db.String(24), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(160), nullable=False)
    tipo = db.Column(db.String(24), nullable=False, default="local")
    giro = db.Column(db.String(32), nullable=False, default="otro")
    descripcion = db.Column(db.Text, default="")
    anios_operando = db.Column(db.String(24), default="")
    personas = db.Column(db.Integer, nullable=True)
    rfc = db.Column(db.String(13), default="")
    alcaldia = db.Column(db.String(60), default="")
    colonia = db.Column(db.String(90), default="")
    calle = db.Column(db.String(180), default="")
    referencias = db.Column(db.Text, default="")
    horario = db.Column(db.JSON, default=dict)
    dias_tianguis = db.Column(db.String(140), default="")
    numero_puesto = db.Column(db.String(40), default="")
    telefono = db.Column(db.String(24), default="")
    whatsapp = db.Column(db.String(24), default="")
    email = db.Column(db.String(140), default="")
    contacto_nombre = db.Column(db.String(140), default="")
    metodos_pago = db.Column(db.JSON, default=list)
    interes_pos = db.Column(db.String(16), default="no")
    como_se_entero = db.Column(db.String(80), default="")
    estado = db.Column(db.String(20), default="publicado")
    visitas = db.Column(db.Integer, default=0)
    lat = db.Column(db.Float, default=19.4326)
    lng = db.Column(db.Float, default=-99.1332)
    creado_en = db.Column(db.DateTime, default=lambda: datetime.now(CDMX_TZ).replace(tzinfo=None))

    productos = db.relationship(
        "Producto", backref="comercio", cascade="all, delete-orphan", order_by="Producto.id"
    )

    # --- Etiquetas ---------------------------------------------------------
    @property
    def tipo_label(self) -> str:
        return tipo_label(self.tipo)

    @property
    def tipo_desc(self) -> str:
        return TIPOS.get(self.tipo, {}).get("desc", "")

    @property
    def tipo_icono(self) -> str:
        return TIPOS.get(self.tipo, {}).get("icono", "store")

    @property
    def giro_label(self) -> str:
        return giro_label(self.giro)

    @property
    def metodos_pago_labels(self) -> list[str]:
        return [metodo_label(m) for m in (self.metodos_pago or [])]

    @property
    def interes_pos_label(self) -> str:
        return interes_label(self.interes_pos)

    @property
    def descripcion_corta(self) -> str:
        texto = (self.descripcion or "").strip()
        return texto if len(texto) <= 150 else texto[:147].rstrip() + "…"

    @property
    def dia_hoy(self) -> tuple[str, str]:
        idx = datetime.now(CDMX_TZ).weekday()
        return DIAS[idx]

    @property
    def horario_hoy_texto(self) -> str:
        clave, _ = self.dia_hoy
        dia = (self.horario or {}).get(clave) or {}
        if not dia.get("abre"):
            return "Cerrado hoy"
        return f"{dia.get('de', '')}–{dia.get('a', '')}"

    @property
    def abierto_ahora(self) -> bool:
        clave, _ = self.dia_hoy
        dia = (self.horario or {}).get(clave) or {}
        if not dia.get("abre"):
            return False
        try:
            ahora = datetime.now(CDMX_TZ).strftime("%H:%M")
            return dia.get("de", "00:00") <= ahora <= dia.get("a", "23:59")
        except Exception:
            return False

    @property
    def porcentaje_completo(self) -> int:
        checks = [
            bool(self.descripcion),
            bool(self.alcaldia and self.colonia),
            bool(self.telefono or self.whatsapp),
            bool(self.horario),
            len(self.productos) >= 3,
            bool(self.metodos_pago),
            bool(self.interes_pos and self.interes_pos != "no"),
            bool(self.calle),
        ]
        return round(sum(checks) / len(checks) * 100)

    @property
    def coordenadas(self) -> tuple[float, float]:
        return (self.lat or 19.4326, self.lng or -99.1332)

    def to_public_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "slug": self.slug,
            "tipo": self.tipo_label,
            "giro": self.giro_label,
            "alcaldia": self.alcaldia,
            "colonia": self.colonia,
            "lat": self.coordenadas[0],
            "lng": self.coordenadas[1],
            "descripcion": self.descripcion_corta,
            "horario": self.horario_hoy_texto,
            "abierto": self.abierto_ahora,
            "metodos": self.metodos_pago_labels,
            "productos": len(self.productos),
        }

    def __repr__(self) -> str:
        return f"<Comercio {self.folio} {self.nombre}>"


class Producto(db.Model):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    comercio_id = db.Column(db.Integer, db.ForeignKey("comercios.id"), nullable=False)
    nombre = db.Column(db.String(140), nullable=False)
    categoria = db.Column(db.String(60), default="")
    precio = db.Column(db.String(40), default="")
    unidad = db.Column(db.String(40), default="")
    descripcion = db.Column(db.String(240), default="")

    def __repr__(self) -> str:
        return f"<Producto {self.nombre}>"


def nuevo_folio() -> str:
    anio = datetime.now(CDMX_TZ).year
    for _ in range(20):
        folio = f"CH-{anio}-{secrets.randbelow(9000) + 1000}"
        if not Comercio.query.filter_by(folio=folio).first():
            return folio
    return f"CH-{anio}-{secrets.token_hex(3).upper()}"


def nuevo_slug(nombre: str) -> str:
    base = slugify(nombre)
    slug = base
    i = 2
    while Comercio.query.filter_by(slug=slug).first():
        slug = f"{base}-{i}"
        i += 1
    return slug


class Noticia(db.Model):
    __tablename__ = "noticias"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(160), unique=True, nullable=False, index=True)
    titulo = db.Column(db.String(200), nullable=False)
    resumen = db.Column(db.String(320), nullable=False)
    cuerpo = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(32), nullable=False, default="avisos")
    fuente_nombre = db.Column(db.String(120), default="")
    fuente_url = db.Column(db.String(300), default="")
    publicada = db.Column(db.Boolean, default=True, nullable=False)
    destacada = db.Column(db.Boolean, default=False, nullable=False)
    creada_en = db.Column(db.DateTime, default=lambda: datetime.now(CDMX_TZ).replace(tzinfo=None))
    actualizada_en = db.Column(
        db.DateTime,
        default=lambda: datetime.now(CDMX_TZ).replace(tzinfo=None),
        onupdate=lambda: datetime.now(CDMX_TZ).replace(tzinfo=None),
    )

    @property
    def categoria_label(self) -> str:
        return categoria_noticia_label(self.categoria)

    @property
    def categoria_icono(self) -> str:
        return CATEGORIAS_NOTICIA.get(self.categoria, {}).get("icono", "bell")

    @property
    def categoria_clase(self) -> str:
        return CATEGORIAS_NOTICIA.get(self.categoria, {}).get("clase", "avisos")

    @property
    def fecha_larga(self) -> str:
        if not self.creada_en:
            return ""
        return f"{self.creada_en.day} de {MESES[self.creada_en.month - 1]} de {self.creada_en.year}"

    @property
    def parrafos(self) -> list[str]:
        return [p.strip() for p in (self.cuerpo or "").split("\n\n") if p.strip()]

    def __repr__(self) -> str:
        return f"<Noticia {self.slug}>"


class Suscripcion(db.Model):
    __tablename__ = "suscripciones"

    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.Text, unique=True, nullable=False)
    p256dh = db.Column(db.String(300), nullable=False)
    auth = db.Column(db.String(100), nullable=False)
    user_agent = db.Column(db.String(300), default="")
    activa = db.Column(db.Boolean, default=True, nullable=False)
    creada_en = db.Column(db.DateTime, default=lambda: datetime.now(CDMX_TZ).replace(tzinfo=None))

    def to_webpush(self) -> dict:
        return {
            "endpoint": self.endpoint,
            "keys": {"p256dh": self.p256dh, "auth": self.auth},
        }


class NotificacionLog(db.Model):
    __tablename__ = "notificaciones_log"

    id = db.Column(db.Integer, primary_key=True)
    noticia_id = db.Column(db.Integer, db.ForeignKey("noticias.id"), nullable=True)
    titulo = db.Column(db.String(200), nullable=False)
    cuerpo = db.Column(db.String(400), default="")
    url = db.Column(db.String(300), default="")
    total = db.Column(db.Integer, default=0)
    exitos = db.Column(db.Integer, default=0)
    fallos = db.Column(db.Integer, default=0)
    enviada_en = db.Column(db.DateTime, default=lambda: datetime.now(CDMX_TZ).replace(tzinfo=None))

    noticia = db.relationship("Noticia", backref="notificaciones")


class SolicitudDigitalizacion(db.Model):
    __tablename__ = "solicitudes_digitalizacion"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(140), nullable=False)
    comercio = db.Column(db.String(160), default="")
    telefono = db.Column(db.String(24), nullable=False)
    alcaldia = db.Column(db.String(60), default="")
    interes = db.Column(db.String(40), default="diagnostico")
    mensaje = db.Column(db.Text, default="")
    atendida = db.Column(db.Boolean, default=False, nullable=False)
    creada_en = db.Column(db.DateTime, default=lambda: datetime.now(CDMX_TZ).replace(tzinfo=None))

    def __repr__(self) -> str:
        return f"<SolicitudDigitalizacion {self.nombre}>"
