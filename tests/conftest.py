import re

import pytest

from app import create_app, db


@pytest.fixture()
def app():
    app = create_app("config.TestingConfig")
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def csrf(client, path="/registro/paso-1"):
    html = client.get(path).get_data(as_text=True)
    match = re.search(r'name="_csrf_token" value="([^"]+)"', html)
    assert match, "No se encontró el token CSRF"
    return match.group(1)


def paso1_data(token, **overrides):
    data = {
        "_csrf_token": token,
        "nombre": "Tamales de Prueba",
        "tipo": "local",
        "giro": "alimentos",
        "descripcion": "Tamales de prueba para el flujo completo.",
        "anios_operando": "1 a 3 años",
        "personas": "2",
        "rfc": "",
    }
    data.update(overrides)
    return data


def paso2_data(token, **overrides):
    data = {
        "_csrf_token": token,
        "alcaldia": "Coyoacán",
        "colonia": "Del Carmen",
        "calle": "Calle Prueba 123",
        "referencias": "Junto al parque",
    }
    for dia in ("lunes", "martes", "miercoles", "jueves", "viernes"):
        data[f"abre_{dia}"] = "on"
        data[f"de_{dia}"] = "09:00"
        data[f"a_{dia}"] = "18:00"
    data.update(overrides)
    return data


def paso3_data(token, **overrides):
    data = {
        "_csrf_token": token,
        "producto_nombre[]": ["Tamal de prueba"],
        "producto_categoria[]": ["Tamales"],
        "producto_precio[]": ["$20"],
        "producto_unidad[]": ["pieza"],
        "metodos_pago": ["efectivo", "transferencia"],
        "interes_pos": "si",
    }
    data.update(overrides)
    return data


def paso4_data(token, **overrides):
    data = {
        "_csrf_token": token,
        "contacto_nombre": "Prueba Pérez",
        "telefono": "5512345678",
        "whatsapp": "5512345678",
        "email": "prueba@example.com",
        "password": "ClaveSegura123",
        "password_confirm": "ClaveSegura123",
        "como_se_entero": "Redes sociales",
        "consent": "on",
    }
    data.update(overrides)
    return data
