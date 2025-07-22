import pytest
from unittest.mock import patch
from flask import Flask
from app.routes.location import location_bp
from app.exceptions.external_api import ExternalAPIError
from app.error_handlers import register_error_handlers


# creo el cliente sobre el que se ejecutaran las pruebas
@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(location_bp)
    register_error_handlers(app)

    app.testing = True
    return app.test_client()


# busqueda correcta con datos extra
def test_location_success(client):
    mock_location = {
        "name": "Earth (C-137)",
        "type": "Planet",

        # Ignora datos extra
        "dimension": "Dimension C-137",
    }

    with patch(
            "app.routes.location.RickAndMortyAPI.get_location_by_name_and_type"
            ) as mock_get_location:

        mock_get_location.return_value = mock_location

        # Hago un request correcto al endpoint
        response = client.get("/location?name=earth&type=planet")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"

        # Verifico que la data devuelta es correcta segun los datos devueltos
        # por el service
        data = response.get_json()
        assert data["name"] == "Earth (C-137)"
        assert data["type"] == "Planet"
        assert "dimension" not in data


# Busqueda no encontrada. (Servicio externo no devuelve la clave "results")
def test_location_not_found(client):
    with patch(
            "app.routes.location.RickAndMortyAPI.get_location_by_name_and_type"
            ) as mock_get_location:

        mock_get_location.side_effect = ExternalAPIError(
            "No matching location found",
            status_code=404
            )

        # ejecuto el endpoint
        response = client.get("/location?name=unknown&type=unknown")
        assert response.status_code == 404

        # verifico que el handler devolvio los valores de la excepcion
        data = response.get_json()
        assert data["error"] == "No matching location found"
        assert data["status_code"] == 404


# Busqueda sin parametros. El endpoint igual devuelve el resultado
# (El service extrae el primer resultado de la lista y el enpoint lo retorna)
def test_location_without_parameters(client):
    mock_location = {
        "name": "Citadel of Ricks",
        "type": "Space station"
    }

    with patch(
            "app.routes.location.RickAndMortyAPI.get_location_by_name_and_type"
            ) as mock_get_location:

        mock_get_location.return_value = mock_location

        # Ejecuto el endpoint
        response = client.get("/location")
        assert response.status_code == 200

        # verifico que el endpoint retorna los datos servidos por el service
        data = response.get_json()
        assert data["name"] == "Citadel of Ricks"
        assert data["type"] == "Space station"
