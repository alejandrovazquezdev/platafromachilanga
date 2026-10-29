from app import db
from app.models import Comercio

from .conftest import csrf, paso1_data, paso2_data, paso3_data, paso4_data


def test_paginas_publicas(client):
    for ruta in ("/", "/como-funciona", "/aviso-de-privacidad", "/directorio"):
        assert client.get(ruta).status_code == 200, ruta
    respuesta = client.get("/panel")
    assert respuesta.status_code == 302
    assert "/iniciar-sesion" in respuesta.headers["Location"]


def _login_demo(client):
    html = client.get("/iniciar-sesion").get_data(as_text=True)
    import re

    token = re.search(r'name="_csrf_token" value="([^"]+)"', html).group(1)
    return client.post(
        "/iniciar-sesion",
        data={"_csrf_token": token, "usuario": "donamari@chilangaton.mx", "contra": "Centlalli2026"},
        follow_redirects=False,
    )


def test_login_demo_y_dashboard(client, app):
    respuesta = _login_demo(client)
    assert respuesta.status_code == 302
    assert "/panel" in respuesta.headers["Location"]
    panel = client.get("/panel")
    assert panel.status_code == 200
    assert "PANEL DE CONTROL" in panel.get_data(as_text=True)
    assert "Abarrotes Doña Mari" in panel.get_data(as_text=True)


def test_agregar_producto_dashboard(client, app):
    _login_demo(client)
    html = client.get("/panel").get_data(as_text=True)
    import re

    token = re.search(r'name="_csrf_token" value="([^"]+)"', html).group(1)
    respuesta = client.post(
        "/panel/productos",
        data={"_csrf_token": token, "nombre": "Producto Nuevo", "precio": "123.50", "descripcion": "Prueba"},
    )
    assert respuesta.status_code == 302
    panel = client.get("/panel")
    assert "Producto Nuevo" in panel.get_data(as_text=True)
    assert "$123.50" in panel.get_data(as_text=True)


def test_login_invalido(client):
    import re

    html = client.get("/iniciar-sesion").get_data(as_text=True)
    token = re.search(r'name="_csrf_token" value="([^"]+)"', html).group(1)
    respuesta = client.post(
        "/iniciar-sesion",
        data={"_csrf_token": token, "usuario": "nadie@example.com", "contra": "mal"},
    )
    assert respuesta.status_code == 200
    assert "incorrectos" in respuesta.get_data(as_text=True)


def test_salud(client):
    respuesta = client.get("/salud")
    assert respuesta.status_code == 200
    assert respuesta.get_json()["status"] == "ok"
    assert respuesta.get_json()["comercios"] >= 1


def test_ficha_publica(client, app):
    with app.app_context():
        comercio = Comercio.query.first()
        slug = comercio.slug
    respuesta = client.get(f"/comercio/{slug}")
    assert respuesta.status_code == 200
    assert comercio.nombre in respuesta.get_data(as_text=True)


def test_404(client):
    assert client.get("/esto-no-existe").status_code == 404


def test_csrf_rechazado(client):
    respuesta = client.post("/registro/paso-1", data={"nombre": "X"})
    assert respuesta.status_code == 400


def test_flujo_registro_completo(client, app):
    token = csrf(client)
    r = client.post("/registro/paso-1", data=paso1_data(token))
    assert r.status_code == 302 and r.headers["Location"].endswith("/registro/paso-2")

    token = csrf(client, "/registro/paso-2")
    r = client.post("/registro/paso-2", data=paso2_data(token))
    assert r.status_code == 302 and r.headers["Location"].endswith("/registro/paso-3")

    token = csrf(client, "/registro/paso-3")
    r = client.post("/registro/paso-3", data=paso3_data(token))
    assert r.status_code == 302 and r.headers["Location"].endswith("/registro/paso-4")

    token = csrf(client, "/registro/paso-4")
    r = client.post("/registro/paso-4", data=paso4_data(token))
    assert r.status_code == 302
    assert "/registro/confirmacion/" in r.headers["Location"]

    confirmacion = client.get(r.headers["Location"])
    assert confirmacion.status_code == 200
    assert "Tamales de Prueba" in confirmacion.get_data(as_text=True)
    assert "<svg" in confirmacion.get_data(as_text=True)

    panel = client.get("/panel")
    assert panel.status_code == 200
    assert "Tamales de Prueba" in panel.get_data(as_text=True)

    with app.app_context():
        assert Comercio.query.filter_by(nombre="Tamales de Prueba").count() == 1
        from app.models import Cuenta

        assert Cuenta.query.filter_by(email="prueba@example.com").count() == 1


def test_directorio_filtra(client):
    respuesta = client.get("/directorio?alcaldia=Coyoac%C3%A1n")
    html = respuesta.get_data(as_text=True)
    assert respuesta.status_code == 200
    assert "Abarrotes Doña Mari" in html


def test_editar_comercio(client, app):
    _login_demo(client)
    with app.app_context():
        from app.models import Cuenta

        cuenta = Cuenta.query.filter_by(email="donamari@chilangaton.mx").first()
        comercio = cuenta.comercio
        comercio_id = comercio.id
        folio = comercio.folio

    assert client.get("/panel/editar").status_code == 302
    assert client.get("/registro/paso-1").status_code == 200

    token = csrf(client)
    r = client.post(
        "/registro/paso-1",
        data=paso1_data(token, nombre="Nombre Editado"),
    )
    assert r.status_code == 302

    token = csrf(client, "/registro/paso-2")
    assert client.post("/registro/paso-2", data=paso2_data(token)).status_code == 302

    token = csrf(client, "/registro/paso-3")
    assert client.post("/registro/paso-3", data=paso3_data(token)).status_code == 302

    token = csrf(client, "/registro/paso-4")
    r = client.post("/registro/paso-4", data=paso4_data(token))
    assert r.status_code == 302

    with app.app_context():
        editado = db.session.get(Comercio, comercio_id)
        assert editado.nombre == "Nombre Editado"
        assert editado.folio == folio


def test_paginas_nuevas(client):
    for ruta in (
        "/noticias/",
        "/marco-legal",
        "/preguntas-frecuentes",
        "/digitaliza",
        "/manifest.webmanifest",
        "/sw.js",
    ):
        assert client.get(ruta).status_code == 200, ruta


def test_noticia_detalle(client, app):
    from app.models import Noticia

    with app.app_context():
        noticia = Noticia.query.filter_by(publicada=True).first()
        slug = noticia.slug
        titulo = noticia.titulo
    respuesta = client.get(f"/noticias/{slug}")
    assert respuesta.status_code == 200
    assert titulo in respuesta.get_data(as_text=True)


def test_busqueda_difusa(client):
    respuesta = client.get("/directorio?q=coyacan")
    assert respuesta.status_code == 200
    assert "Abarrotes Doña Mari" in respuesta.get_data(as_text=True)


def test_digitaliza_solicitud(client, app):
    from app.models import SolicitudDigitalizacion

    token = csrf(client, "/digitaliza")
    respuesta = client.post(
        "/digitaliza",
        data={
            "_csrf_token": token,
            "nombre": "Prueba Digitaliza",
            "comercio": "Fonda de prueba",
            "telefono": "5512345678",
            "alcaldia": "Tlalpan",
            "interes": "terminal",
            "consent": "on",
        },
    )
    assert respuesta.status_code == 302
    with app.app_context():
        assert SolicitudDigitalizacion.query.count() == 1


def test_admin_requiere_login(client, app):
    app.config["ADMIN_PASSWORD"] = "clave-de-prueba"
    respuesta = client.get("/admin/")
    assert respuesta.status_code == 302
    assert "/admin/login" in respuesta.headers["Location"]


def test_admin_login(client, app):
    app.config["ADMIN_PASSWORD"] = "clave-de-prueba"
    html = client.get("/admin/login").get_data(as_text=True)
    import re

    token = re.search(r'name="_csrf_token" value="([^"]+)"', html).group(1)
    respuesta = client.post(
        "/admin/login",
        data={"_csrf_token": token, "password": "clave-de-prueba"},
        follow_redirects=False,
    )
    assert respuesta.status_code == 302
    assert client.get("/admin/").status_code == 200
    assert client.get("/admin/noticias").status_code == 200


def test_suscripcion_push(client):
    html = client.get("/").get_data(as_text=True)
    import re

    token = re.search(r'name="csrf-token" content="([^"]+)"', html).group(1)
    respuesta = client.post(
        "/api/notificaciones/suscribir",
        json={"endpoint": "https://example.com/push/test", "keys": {"p256dh": "clave", "auth": "auth"}},
        headers={"X-CSRF-Token": token},
    )
    assert respuesta.status_code == 200
    assert respuesta.get_json()["ok"] is True


def test_chat_desactivado_sin_api_key(client, app):
    app.config["OPENAI_API_KEY"] = ""
    app.config["CHAT_ENABLED"] = False
    import re

    html = client.get("/").get_data(as_text=True)
    token = re.search(r'name="csrf-token" content="([^"]+)"', html).group(1)
    respuesta = client.post(
        "/api/chat",
        json={"messages": [{"role": "user", "content": "Hola"}]},
        headers={"X-CSRF-Token": token},
    )
    assert respuesta.status_code == 200
    assert "no está configurado" in respuesta.get_json()["reply"].lower()
