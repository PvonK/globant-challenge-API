import pytest
from unittest.mock import patch
from flask import Flask
from app.routes.characters import characters_bp
from app.exceptions.external_api import ExternalAPIError
from app.error_handlers import register_error_handlers


# creo el cliente sobre el que se ejecutaran las pruebas
@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(characters_bp)
    register_error_handlers(app)

    app.testing = True
    return app.test_client()


# Endpoint funciona correctamente
def test_characters_success(client):
    mock_stats = {
        "character_names": ["Rick", "Morty", "Summer"],
        "human_count": 2,
        "not_human_count": 1,
        "dead_count": 1,
        "alive_count": 2
    }

    # No uso el decorador por que poner 'mock_stats' como parametro
    # para definir el return value queda feo
    with patch(
            "app.routes.characters.RickAndMortyAPI.get_all_characters_stats"
            ) as mock_stats_method:

        # Defino el return value del metodo get_all_characters_stats
        mock_stats_method.return_value = mock_stats

        # Hago el request al endpoint que voy a testear (/characters)
        response = client.get("/characters")

        # checkeo que los valores de retorno son los esperados
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"

        # checkeo que la data es la correcta
        data = response.get_json()
        assert data["character_names"] == ["Rick", "Morty", "Summer"]
        assert data["human_count"] == 2
        assert data["not_human_count"] == 1
        assert data["dead_count"] == 1
        assert data["alive_count"] == 2


# Endpoint falla por que la api externa no esta disponible
def test_characters_external_api_failure(client):
    with patch(
            "app.routes.characters.RickAndMortyAPI.get_all_characters_stats"
            ) as mock_stats_method:

        # Defino el error del metodo get_all_characters_stats
        mock_stats_method.side_effect = ExternalAPIError(
            "API unavailable",
            status_code=503
            )

        # Ejecuto el endpoint
        response = client.get("/characters")

        # verifico que la respuesta de mi endpoint es la esperada dado el error
        assert response.status_code == 503

        data = response.get_json()
        assert data["error"] == "API unavailable"
        assert data["status_code"] == 503
