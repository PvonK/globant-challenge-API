import pytest
from unittest.mock import patch
from app.services.rick_and_morty_api import RickAndMortyAPI
from app.exceptions.external_api import ExternalAPIError
from conftest import MockResponse
from requests.exceptions import Timeout, RequestException


# region - Tests for get_all_characters_stats

# Recoleccion de stats correcta de dos paginas de personajes
@patch("app.services.rick_and_morty_api.requests.get")
def test_get_all_characters_stats_success(mock_get):
    # Defino los returns. Uso side_effect en vez de return_value porque
    # necesito que el metodo se ejecute dos veces y de resultados distintos
    mock_get.side_effect = [
        # Primera pagina
        MockResponse({
            "info": {"next": "next-url"},
            "results": [
                {"name": "Rick", "species": "Human", "status": "Alive"},
                {"name": "Birdperson", "species": "Alien", "status": "Dead"},
            ]
        }),
        # Segunda pagina
        MockResponse({
            "info": {"next": None},
            "results": [
                {"name": "Morty", "species": "Human", "status": "Alive"},
            ]
        }),
    ]

    # Ejecuto el metodo
    api = RickAndMortyAPI()
    stats = api.get_all_characters_stats()

    # Verifico que los stats se calcularon correctamente segun los datos dados
    assert stats["character_names"] == ["Rick", "Birdperson", "Morty"]
    assert stats["human_count"] == 2
    assert stats["not_human_count"] == 1
    assert stats["alive_count"] == 2
    assert stats["dead_count"] == 1

# endregion


# region - Tests for get_location_by_name_and_type

# Test de busqueda correcta con ambos parametros
@patch("app.services.rick_and_morty_api.requests.get")
def test_get_location_by_name_and_type_found(mock_get):
    # seteo el valor de la respuesta del request
    mock_get.return_value = MockResponse({
        "results": [
            {"name": "Earth (C-137)", "type": "Planet"}
        ]
    })

    # ejecuto el metodo
    api = RickAndMortyAPI()
    result = api.get_location_by_name_and_type(name="earth", type_="planet")

    # Verifico que los valores retornados son los esperados
    assert result["name"] == "Earth (C-137)"
    assert result["type"] == "Planet"


# Test de busqueda correcta con unicamente el parametro 'type'
@patch("app.services.rick_and_morty_api.requests.get")
def test_get_location_by_type_found(mock_get):
    # seteo el valor de la respuesta del request
    mock_get.return_value = MockResponse({
        "results": [
            {"name": "France", "type": "Country"}
        ]
    })

    # ejecuto el metodo
    api = RickAndMortyAPI()
    result = api.get_location_by_name_and_type(type_="country")

    # Verifico que los valores retornados son los esperados
    assert result["name"] == "France"
    assert result["type"] == "Country"


# Test de busqueda correcta con unicamente el parametro 'name'
@patch("app.services.rick_and_morty_api.requests.get")
def test_get_location_by_name_found(mock_get):
    # seteo el valor de la respuesta del request
    mock_get.return_value = MockResponse({
        "results": [
            {"name": "Citadel of Ricks", "type": "Space station"}
        ]
    })

    # ejecuto el metodo
    api = RickAndMortyAPI()
    result = api.get_location_by_name_and_type(name="citadel")

    # Verifico que los valores retornados son los esperados
    assert result["name"] == "Citadel of Ricks"
    assert result["type"] == "Space station"


# Test del comportamiento cuando el servicio externo devuelve una lista vacia
@patch("app.services.rick_and_morty_api.requests.get")
def test_get_location_by_name_and_type_not_found(mock_get):
    # seteo el valor de la respuesta del request
    mock_get.return_value = MockResponse({"results": []})

    api = RickAndMortyAPI()

    # Capturo el valor de la excepcion en exc_info
    with pytest.raises(ExternalAPIError) as exc_info:
        api.get_location_by_name_and_type(name="fake", type_="ghost planet")

    # Checkeo que exc_info contiene la informacion esperada
    assert "No matching location found" in str(exc_info.value)
    assert exc_info.value.status_code == 404

# endregion


# region - Tests for _get

# Test del manejo de HTTPError en _get()
@patch("app.services.rick_and_morty_api.requests.get")
def test_get_http_error(mock_get):
    # Defino la respuesta del request y que debe lanzar un HTTPError
    mock_get.return_value = MockResponse({}, status_code=400, raise_http=True)

    api = RickAndMortyAPI()

    # Capturo el error
    with pytest.raises(ExternalAPIError) as exc_info:
        api._get("https://rickandmortyapi.com/api/character")

    # Verifico que el error fue manejado como se esperaba
    assert "HTTP error" in str(exc_info.value)
    assert exc_info.value.status_code == 400


# Test del manejo de Timeout en _get()
@patch(
    # Defino la respuesta del request y que debe lanzar un Timeout
    "app.services.rick_and_morty_api.requests.get",
    side_effect=Timeout("timeout")
    )
def test_get_timeout(mock_get):
    api = RickAndMortyAPI()

    # Capturo el error de timeout
    with pytest.raises(ExternalAPIError) as exc_info:
        api._get("http://fakeurl.com")

    # Verifico que el error fue manejado como se esperaba
    assert "Request timed out" in str(exc_info.value)
    assert exc_info.value.status_code == 504


# Test del manejo de RequestError en _get()
@patch(
    # Defino la respuesta del request y que debe lanzar un error de conexion
    "app.services.rick_and_morty_api.requests.get",
    side_effect=RequestException("Connection error")
    )
def test_get_request_exception(mock_get):
    api = RickAndMortyAPI()

    # Capturo el error de conexion
    with pytest.raises(ExternalAPIError) as exc_info:
        api._get("https://rickandmortyapi.com/api/character")

    # Verifico que el error fue manejado como se esperaba
    assert "External API request failed" in str(exc_info.value)
    assert exc_info.value.status_code == 503


# Test del manejo de responses que no son JSON en _get()
@patch("app.services.rick_and_morty_api.requests.get")
def test_get_invalid_json(mock_get):
    # Defino la respuesta del request que lanzara un ValueError
    # cuando se haga response.json()
    mock_get.return_value = MockResponse("not-a-json", is_json=False)

    api = RickAndMortyAPI()

    # Capturo el error en exc_info
    with pytest.raises(ExternalAPIError) as exc_info:
        api._get("http://fakeurl.com")

    # Verifico que el error ha sido manejado correctamente
    assert "Invalid JSON response" in str(exc_info.value)
    assert exc_info.value.status_code == 502


# endregion
