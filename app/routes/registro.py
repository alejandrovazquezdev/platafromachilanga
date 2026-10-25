from __future__ import annotations

import re
import secrets

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .. import db
from ..constants import ALCALDIAS, ALCALDIA_COORDS, COMO_SE_ENTERO, DIAS, GIROS, INTERES_POS, METODOS, TIPOS
from ..models import Comercio, Cuenta, Producto, nuevo_folio, nuevo_slug

registro_bp = Blueprint("registro", __name__)

DRAFT_KEY = "registro_draft"
EDIT_KEY = "editando_id"
PASOS = [
    {
        "n": 1,
        "titulo": "Tu comercio",
        "corto": "Comercio",
        "desc": "Lo esencial para identificarte.",
    },
    {
        "n": 2,
        "titulo": "Ubicación y horarios",
        "corto": "Ubicación",
        "desc": "Para que te encuentren.",
    },
    {
        "n": 3,
        "titulo": "Tu oferta",
        "corto": "Oferta",
        "desc": "Qué vendes y cómo cobras.",
    },
    {
        "n": 4,
        "titulo": "Contacto y publicación",
        "corto": "Publicación",
        "desc": "Revisa y comparte.",
    },
]

RE_TELEFONO = re.compile(r"^\d{10}$")
RE_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
RE_RFC = re.compile(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$")
RE_HORA = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def _draft() -> dict:
    return dict(session.get(DRAFT_KEY) or {})


def _guardar(draft: dict) -> None:
    session[DRAFT_KEY] = draft
    session.modified = True


def _texto(form, nombre: str, maximo: int = 220) -> str:
    return (form.get(nombre) or "").strip()[:maximo]


def _telefono_valido(valor: str) -> bool:
    digitos = re.sub(r"\D", "", valor or "")
    if len(digitos) == 12 and digitos.startswith("52"):
        digitos = digitos[2:]
    return bool(RE_TELEFONO.match(digitos))


def _horario_vacio() -> dict:
    return {
        clave: {"abre": clave not in ("domingo",), "de": "09:00", "a": "19:00"}
        for clave, _ in DIAS
    }


def _horario_actual(draft: dict) -> dict:
    horario = _horario_vacio()
    guardado = draft.get("horario") or {}
    for clave, _ in DIAS:
        dia = guardado.get(clave) or {}
        if dia:
            horario[clave] = {
                "abre": bool(dia.get("abre")),
                "de": dia.get("de", "09:00"),
                "a": dia.get("a", "19:00"),
            }
    return horario


def _productos_para_form(draft: dict) -> list[dict]:
    productos = draft.get("productos") or []
    return productos if productos else [{}]


def _contexto(paso: int, draft: dict, errores: dict | None = None, **extra):
    contexto = {
        "paso": paso,
        "pasos": PASOS,
        "draft": draft,
        "errores": errores or {},
        "horario": _horario_actual(draft),
        "productos_form": _productos_para_form(draft),
    }
    contexto.update(extra)
    return contexto


def _validar_paso1(form, draft: dict) -> dict:
    errores = {}
    draft["nombre"] = _texto(form, "nombre", 160)
    draft["tipo"] = _texto(form, "tipo", 24)
    draft["giro"] = _texto(form, "giro", 32)
    draft["descripcion"] = _texto(form, "descripcion", 600)
    draft["anios_operando"] = _texto(form, "anios_operando", 24)
    personas = _texto(form, "personas", 4)
    draft["personas"] = None
    draft["rfc"] = _texto(form, "rfc", 13).upper().replace(" ", "")

    if len(draft["nombre"]) < 2:
        errores["nombre"] = "Escribe el nombre de tu comercio."
    if draft["tipo"] not in TIPOS:
        errores["tipo"] = "Elige el tipo de comercio."
    if draft["giro"] not in GIROS:
        errores["giro"] = "Elige el giro principal."
    if personas:
        if not personas.isdigit() or int(personas) > 500:
            errores["personas"] = "Escribe un número entre 1 y 500."
        else:
            draft["personas"] = int(personas)
    if draft["rfc"] and not RE_RFC.match(draft["rfc"]):
        errores["rfc"] = "Revisa el RFC (12 o 13 caracteres) o déjalo vacío."
    return errores


def _validar_paso2(form, draft: dict) -> dict:
    errores = {}
    draft["alcaldia"] = _texto(form, "alcaldia", 60)
    draft["colonia"] = _texto(form, "colonia", 90)
    draft["calle"] = _texto(form, "calle", 180)
    draft["referencias"] = _texto(form, "referencias", 300)
    draft["dias_tianguis"] = _texto(form, "dias_tianguis", 140)
    draft["numero_puesto"] = _texto(form, "numero_puesto", 40)
    draft["ubicacion_label"] = _texto(form, "ubicacion_label", 300)
    try:
        lat = float(form.get("lat", ""))
        lng = float(form.get("lng", ""))
        if 14.0 <= lat <= 20.0 and -100.5 <= lng <= -98.0:
            draft["lat"] = lat
            draft["lng"] = lng
        else:
            draft.pop("lat", None)
            draft.pop("lng", None)
    except (TypeError, ValueError):
        draft.pop("lat", None)
        draft.pop("lng", None)

    if draft["alcaldia"] not in ALCALDIAS:
        errores["alcaldia"] = "Elige tu alcaldía."
    if len(draft["colonia"]) < 2:
        errores["colonia"] = "Escribe tu colonia o barrio."
    if len(draft["calle"]) < 4:
        errores["calle"] = "Escribe la calle y el número, o una referencia."
    if draft["tipo"] == "tianguis" and not draft["dias_tianguis"]:
        errores["dias_tianguis"] = "Dinos qué días instalas tu tianguis."

    horario = {}
    algun_dia = False
    for clave, etiqueta in DIAS:
        abre = form.get(f"abre_{clave}") == "on"
        de = (form.get(f"de_{clave}") or "09:00").strip()
        a = (form.get(f"a_{clave}") or "19:00").strip()
        if abre:
            algun_dia = True
            if not RE_HORA.match(de) or not RE_HORA.match(a):
                errores[f"horario_{clave}"] = f"Revisa el horario del {etiqueta.lower()}."
            elif de >= a:
                errores[f"horario_{clave}"] = f"La hora de cierre del {etiqueta.lower()} debe ser mayor."
        horario[clave] = {"abre": abre, "de": de, "a": a}
    draft["horario"] = horario
    if not algun_dia:
        errores["horario"] = "Marca al menos un día de atención."
    return errores


def _validar_paso3(form, draft: dict) -> dict:
    errores = {}
    nombres = form.getlist("producto_nombre[]")
    categorias = form.getlist("producto_categoria[]")
    precios = form.getlist("producto_precio[]")
    unidades = form.getlist("producto_unidad[]")

    productos = []
    for i, nombre in enumerate(nombres):
        nombre = (nombre or "").strip()[:140]
        if not nombre:
            continue
        productos.append(
            {
                "nombre": nombre,
                "categoria": (categorias[i] if i < len(categorias) else "").strip()[:60],
                "precio": (precios[i] if i < len(precios) else "").strip()[:40],
                "unidad": (unidades[i] if i < len(unidades) else "").strip()[:40],
            }
        )
    if not productos:
        errores["productos"] = "Agrega al menos un producto o servicio."
    if len(productos) > 6:
        errores["productos"] = "Por ahora puedes publicar hasta 6 productos."

    metodos = [m for m in form.getlist("metodos_pago") if m in METODOS]
    if not metodos:
        errores["metodos_pago"] = "Elige al menos una forma de pago."

    interes = _texto(form, "interes_pos", 16)
    if interes not in INTERES_POS:
        errores["interes_pos"] = "Dinos si te interesa el punto de venta."

    draft["productos"] = productos
    draft["metodos_pago"] = metodos
    draft["interes_pos"] = interes
    return errores


def _validar_paso4(form, draft: dict) -> dict:
    errores = {}
    draft["contacto_nombre"] = _texto(form, "contacto_nombre", 140)
    draft["telefono"] = _texto(form, "telefono", 24)
    draft["whatsapp"] = _texto(form, "whatsapp", 24)
    draft["email"] = _texto(form, "email", 140).lower()
    draft["password"] = form.get("password") or ""
    draft["password_confirm"] = form.get("password_confirm") or ""
    draft["como_se_entero"] = _texto(form, "como_se_entero", 80)
    draft["consent"] = form.get("consent") == "on"
    edit_id = session.get(EDIT_KEY)

    if len(draft["contacto_nombre"]) < 3:
        errores["contacto_nombre"] = "Escribe el nombre de la persona de contacto."
    if not _telefono_valido(draft["telefono"]):
        errores["telefono"] = "Escribe un teléfono de 10 dígitos."
    if draft["whatsapp"] and not _telefono_valido(draft["whatsapp"]):
        errores["whatsapp"] = "Revisa el número de WhatsApp."
    if not RE_EMAIL.match(draft["email"]):
        errores["email"] = "Escribe un correo válido; será tu usuario para entrar."
    else:
        existente = Cuenta.query.filter(Cuenta.email == draft["email"])
        if edit_id:
            existente = existente.filter(Cuenta.comercio_id != edit_id)
        if existente.first():
            errores["email"] = "Ese correo ya tiene una cuenta. Usa otro o inicia sesión."

    if not edit_id or draft["password"] or draft["password_confirm"]:
        if len(draft["password"]) < 8:
            errores["password"] = "La contraseña debe tener al menos 8 caracteres."
        if draft["password"] != draft["password_confirm"]:
            errores["password_confirm"] = "Las contraseñas no coinciden."

    if draft["como_se_entero"] and draft["como_se_entero"] not in COMO_SE_ENTERO:
        draft["como_se_entero"] = ""
    if not draft["consent"]:
        errores["consent"] = "Necesitamos tu consentimiento para publicar la ficha."
    return errores


def _paso_previo_completo(draft: dict, paso: int) -> bool:
    if paso <= 1:
        return True
    if not draft.get("nombre") or not draft.get("tipo") or not draft.get("giro"):
        return False
    if paso <= 2:
        return True
    if not draft.get("alcaldia") or not draft.get("colonia") or not draft.get("calle"):
        return False
    if paso <= 3:
        return True
    return bool(draft.get("productos") and draft.get("metodos_pago"))


@registro_bp.route("/registro")
def inicio():
    return redirect(url_for("registro.paso1"))


@registro_bp.route("/registro/reiniciar")
def reiniciar():
    session.pop(DRAFT_KEY, None)
    session.pop(EDIT_KEY, None)
    session.pop("comercio_id", None)
    session.pop("ultimo_folio", None)
    return redirect(url_for("registro.paso1"))


@registro_bp.route("/registro/paso-1", methods=["GET", "POST"])
def paso1():
    draft = _draft()
    errores = {}
    if request.method == "POST":
        if request.form.get("sitio_web"):
            abort(400)
        errores = _validar_paso1(request.form, draft)
        if not errores:
            _guardar(draft)
            return redirect(url_for("registro.paso2"))
    elif not draft.get("tipo"):
        draft["tipo"] = "tienda"
        draft["giro"] = draft.get("giro", "")

    return render_template("registro/paso1.html", **_contexto(1, draft, errores))


@registro_bp.route("/registro/paso-2", methods=["GET", "POST"])
def paso2():
    draft = _draft()
    if not _paso_previo_completo(draft, 2):
        flash("Primero completa los datos de tu comercio.", "aviso")
        return redirect(url_for("registro.paso1"))

    errores = {}
    if request.method == "POST":
        errores = _validar_paso2(request.form, draft)
        if not errores:
            _guardar(draft)
            return redirect(url_for("registro.paso3"))

    return render_template("registro/paso2.html", **_contexto(2, draft, errores))


@registro_bp.route("/registro/paso-3", methods=["GET", "POST"])
def paso3():
    draft = _draft()
    if not _paso_previo_completo(draft, 3):
        flash("Primero completa la ubicación de tu comercio.", "aviso")
        return redirect(url_for("registro.paso2"))

    errores = {}
    if request.method == "POST":
        errores = _validar_paso3(request.form, draft)
        if not errores:
            _guardar(draft)
            return redirect(url_for("registro.paso4"))

    return render_template("registro/paso3.html", **_contexto(3, draft, errores))


@registro_bp.route("/registro/paso-4", methods=["GET", "POST"])
def paso4():
    draft = _draft()
    if not _paso_previo_completo(draft, 4):
        flash("Primero completa tu oferta y formas de pago.", "aviso")
        return redirect(url_for("registro.paso3"))

    errores = {}
    if request.method == "POST":
        errores = _validar_paso4(request.form, draft)
        if not errores:
            try:
                comercio = _crear_comercio(draft)
            except Exception:
                db.session.rollback()
                errores["general"] = "No pudimos guardar el registro. Intenta de nuevo."
            else:
                session["comercio_id"] = comercio.id
                session["ultimo_folio"] = comercio.folio
                session.pop(DRAFT_KEY, None)
                return redirect(url_for("registro.confirmacion", folio=comercio.folio))

    return render_template("registro/paso4.html", **_contexto(4, draft, errores))


def _crear_comercio(draft: dict) -> Comercio:
    lat, lng = ALCALDIA_COORDS.get(draft.get("alcaldia"), (19.4326, -99.1332))
    if draft.get("lat") is not None and draft.get("lng") is not None:
        lat, lng = float(draft["lat"]), float(draft["lng"])
    telefono = draft.get("telefono", "")
    edit_id = session.get(EDIT_KEY)
    if edit_id:
        comercio = db.session.get(Comercio, edit_id)
        if comercio is None:
            raise ValueError("El comercio que intentas editar ya no existe.")
        for attr, value in {
            "nombre": draft.get("nombre", ""),
            "tipo": draft.get("tipo", "local"),
            "giro": draft.get("giro", "otro"),
            "descripcion": draft.get("descripcion", ""),
            "anios_operando": draft.get("anios_operando", ""),
            "personas": draft.get("personas"),
            "rfc": draft.get("rfc", ""),
            "alcaldia": draft.get("alcaldia", ""),
            "colonia": draft.get("colonia", ""),
            "calle": draft.get("calle", ""),
            "referencias": draft.get("referencias", ""),
            "horario": draft.get("horario") or {},
            "dias_tianguis": draft.get("dias_tianguis", ""),
            "numero_puesto": draft.get("numero_puesto", ""),
            "telefono": telefono,
            "whatsapp": draft.get("whatsapp") or telefono,
            "email": draft.get("email", ""),
            "contacto_nombre": draft.get("contacto_nombre", ""),
            "metodos_pago": draft.get("metodos_pago") or [],
            "interes_pos": draft.get("interes_pos", "no"),
            "como_se_entero": draft.get("como_se_entero", ""),
            "lat": lat,
            "lng": lng,
        }.items():
            setattr(comercio, attr, value)
        Producto.query.filter_by(comercio_id=comercio.id).delete()
        db.session.flush()
        for producto in draft.get("productos") or []:
            db.session.add(Producto(comercio_id=comercio.id, **producto))

        cuenta = Cuenta.query.filter_by(comercio_id=comercio.id).first()
        if cuenta is None and draft.get("password"):
            cuenta = Cuenta(comercio_id=comercio.id, email=draft["email"])
            db.session.add(cuenta)
        if cuenta is not None:
            cuenta.email = draft["email"]
            if draft.get("password"):
                cuenta.set_password(draft["password"])

        db.session.commit()
        session.pop(EDIT_KEY, None)
        return comercio

    comercio = Comercio(
        folio=nuevo_folio(),
        slug=nuevo_slug(draft.get("nombre", "comercio")),
        nombre=draft.get("nombre", ""),
        tipo=draft.get("tipo", "local"),
        giro=draft.get("giro", "otro"),
        descripcion=draft.get("descripcion", ""),
        anios_operando=draft.get("anios_operando", ""),
        personas=draft.get("personas"),
        rfc=draft.get("rfc", ""),
        alcaldia=draft.get("alcaldia", ""),
        colonia=draft.get("colonia", ""),
        calle=draft.get("calle", ""),
        referencias=draft.get("referencias", ""),
        horario=draft.get("horario") or {},
        dias_tianguis=draft.get("dias_tianguis", ""),
        numero_puesto=draft.get("numero_puesto", ""),
        telefono=telefono,
        whatsapp=draft.get("whatsapp") or telefono,
        email=draft.get("email", ""),
        contacto_nombre=draft.get("contacto_nombre", ""),
        metodos_pago=draft.get("metodos_pago") or [],
        interes_pos=draft.get("interes_pos", "no"),
        como_se_entero=draft.get("como_se_entero", ""),
        estado="publicado",
        visitas=0,
        lat=lat,
        lng=lng,
    )
    db.session.add(comercio)
    db.session.flush()
    cuenta = Cuenta(comercio_id=comercio.id, email=draft["email"])
    cuenta.set_password(draft["password"])
    db.session.add(cuenta)
    for producto in draft.get("productos") or []:
        db.session.add(Producto(comercio_id=comercio.id, **producto))
    db.session.commit()
    return comercio


@registro_bp.route("/registro/confirmacion/<folio>")
def confirmacion(folio: str):
    comercio = Comercio.query.filter_by(folio=folio).first_or_404()
    qr_svg = None
    try:
        import segno

        url = url_for("directorio.ficha", slug=comercio.slug, _external=True)
        qr = segno.make(url, error="m")
        qr_svg = qr.svg_inline(scale=4, border=2, dark="#9F2241", light="#ffffff")
    except Exception:
        qr_svg = None
    return render_template("registro/confirmacion.html", comercio=comercio, qr_svg=qr_svg)
