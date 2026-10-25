from app import db
from app.models import Comercio

from .conftest import csrf, paso1_data, paso2_data, paso3_data, paso4_data


def test_paginas_publicas(client):
    for ruta in ("/", "/como-funciona", "/aviso-de-privacidad", "/directorio", "/panel"):
        assert client.get(ruta).status_code == 200, ruta


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


def test_directorio_filtra(client):
    respuesta = client.get("/directorio?alcaldia=Coyoac%C3%A1n")
    html = respuesta.get_data(as_text=True)
    assert respuesta.status_code == 200
    assert "Abarrotes Doña Mari" in html


def test_editar_comercio(client, app):
    with app.app_context():
        comercio = Comercio.query.first()
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
