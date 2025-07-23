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


# Recoleccion de stats correcta cuando una pagina esta vacia
@patch("app.services.rick_and_morty_api.requests.get")
def test_get_all_characters_stats_empty_first_page(mock_get):
    # Defino los returns.
    mock_get.side_effect = [
        # Primera pagina vacia
        MockResponse({
            "info": {"next": "next-url"},
            "results": [
            ]
        }),
        # Segunda pagina
        MockResponse({
            "info": {"next": None},
            "results": [
                {"name": "Morty", "species": "Human", "status": "Alive"},
                {"name": "Birdperson", "species": "Alien", "status": "Dead"},
            ]
        }),
    ]

    # Ejecuto el metodo
    api = RickAndMortyAPI()
    stats = api.get_all_characters_stats()

    # Verifico que los stats se calcularon correctamente segun los datos dados
    assert stats["character_names"] == ["Morty", "Birdperson"]
    assert stats["human_count"] == 1
    assert stats["not_human_count"] == 1
    assert stats["alive_count"] == 1
    assert stats["dead_count"] == 1


# Recoleccion de stats correcta cuando los jsons no tienen todos los datos
@patch("app.services.rick_and_morty_api.requests.get")
def test_get_all_characters_stats_incomplete_object(mock_get):
    # Defino los returns.
    mock_get.side_effect = [
        # Primera pagina
        MockResponse({
            "info": {"next": "next-url"},
            "results": [
                # Json incompleto pero valido
                {"name": "Rick"},
                {"name": "Birdperson", "species": "Alien", "status": "Dead"},
            ]
        }),
        # Segunda pagina
        MockResponse({
            "info": {"next": None},
            "results": [
                {"name": "Morty", "species": "Human"},
            ]
        }),
    ]

    # Ejecuto el metodo
    api = RickAndMortyAPI()
    stats = api.get_all_characters_stats()

    # Verifico que los stats se calcularon correctamente segun los datos dados
    assert stats["character_names"] == ["Rick", "Birdperson", "Morty"]
    assert stats["human_count"] == 1  # Morty es el unico explicitamente humano
    assert stats["not_human_count"] == 2
    assert stats["alive_count"] == 0
    assert stats["dead_count"] == 1


# Recoleccion de stats correcta cuando los datos no son strings
@patch("app.services.rick_and_morty_api.requests.get")
def test_get_all_characters_stats_unexpected_data_types(mock_get):
    # Defino los returns.
    mock_get.side_effect = [
        # Primera pagina
        MockResponse({
            "info": {"next": "next-url"},
            "results": [
                {"name": "Rick", "species": "Human", "status": False},
                {"name": "Birdperson", "species": None, "status": "Dead"},
                {"name": "Beth", "species": "Robot", "status": True},
                {"name": "Jerry", "species": True, "status": "Unknown"},
            ]
        }),
        # Segunda pagina
        MockResponse({
            "info": {"next": None},
            "results": [
                {"name": None, "species": "Human", "status": "Alive"},
                {"name": True, "species": "Robot", "status": "Alive"},
                {"name": 3, "species": "Robot", "status": "Dead"},
                {"name": "Morty", "species": 72, "status": "Dead"},
                {"name": "Summer", "species": "Human", "status": 0},
            ]
        }),
    ]

    # Ejecuto el metodo
    api = RickAndMortyAPI()
    stats = api.get_all_characters_stats()

    # Verifico que los stats se calcularon correctamente segun los datos dados
    assert stats["character_names"] == [
        "Rick", "Birdperson", "Beth", "Jerry", "Morty", "Summer"
        ]
    assert stats["human_count"] == 3
    assert stats["not_human_count"] == 6
    assert stats["alive_count"] == 2
    assert stats["dead_count"] == 3


# Recoleccion de stats correcta cuando las ultimas paginas estan vacias
@patch("app.services.rick_and_morty_api.requests.get")
def test_get_all_characters_stats_empty_last_page(mock_get):
    # Defino los returns.
    mock_get.side_effect = [
        # Primera pagina
        MockResponse({
            "info": {"next": "next-url"},
            "results": [
                {"name": "Morty", "species": "Human", "status": "Alive"},
                {"name": "Birdperson", "species": "Alien", "status": "Dead"},
            ]
        }),
        # Segunda pagina vacia
        MockResponse({
            "info": {"next": "next-url"},
            "results": [
            ]
        }),
        # Tercera pagina vacia
        MockResponse({
            "info": {"next": None},
            "results": [
            ]
        }),
    ]

    # Ejecuto el metodo
    api = RickAndMortyAPI()
    stats = api.get_all_characters_stats()

    # Verifico que los stats se calcularon correctamente segun los datos dados
    assert stats["character_names"] == ["Morty", "Birdperson"]
    assert stats["human_count"] == 1
    assert stats["not_human_count"] == 1
    assert stats["alive_count"] == 1
    assert stats["dead_count"] == 1


# Recoleccion de stats no falla cuandoal API devuelve una estructura inesperada
@patch("app.services.rick_and_morty_api.requests.get")
def test_get_all_characters_stats_missing_results(mock_get):
    # Defino los returns.
    mock_get.side_effect = [
        # Primera pagina
        MockResponse({
            "info": {"next": "next-url"},
            "data": {"something": "unexpected"}
        }),
        # Segunda pagina vacia
        MockResponse({
            "info": {"next": None},
        }),
    ]

    # Ejecuto el metodo
    api = RickAndMortyAPI()
    stats = api.get_all_characters_stats()

    # Verifico que los stats no son incorrectos
    assert stats["character_names"] == []
    assert stats["human_count"] == 0
    assert stats["not_human_count"] == 0
    assert stats["alive_count"] == 0
    assert stats["dead_count"] == 0


# Manejo correcto del error cuando la paginacion de la API es incorrecta
@patch("app.services.rick_and_morty_api.requests.get")
def test_get_all_characters_stats_bad_pagination(mock_get):
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
            "info": {"next": "next-url"},
            "results": [
                {"name": "Morty", "species": "Human", "status": "Alive"},
            ]
        }),
        # Tercer pagina lanza un error
        MockResponse({}, status_code=400, raise_http=True)
    ]

    # Ejecuto el metodo
    api = RickAndMortyAPI()

    # Capturo el error
    with pytest.raises(ExternalAPIError) as exc_info:
        api.get_all_characters_stats()

    # Verifico que el error fue manejado como se esperaba
    assert "HTTP error" in str(exc_info.value)
    assert exc_info.value.status_code == 400


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


# Test de funcionamiento correcto con varios resultados
@patch("app.services.rick_and_morty_api.requests.get")
def test_get_location_by_name_and_type_found_many(mock_get):
    # seteo el valor de la respuesta del request
    mock_get.return_value = MockResponse({
        "results": [
            {"name": "Earth (C-137)", "type": "Planet"},
            {"name": "Earth (C-138)", "type": "Planet"},
            {"name": "Earth (C-127)", "type": "Planet"},
            {"name": "Earth (C-1137)", "type": "Planet"},
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


# Test del comportamiento cuando el servicio externo no devuelve results
@patch("app.services.rick_and_morty_api.requests.get")
def test_get_location_by_name_and_type_no_results(mock_get):
    # seteo el valor de la respuesta del request
    mock_get.return_value = MockResponse({"data": []})

    api = RickAndMortyAPI()

    # Capturo el valor de la excepcion en exc_info
    with pytest.raises(ExternalAPIError) as exc_info:
        api.get_location_by_name_and_type(name="fake", type_="ghost planet")

    # Checkeo que exc_info contiene la informacion esperada
    assert "No matching location found" in str(exc_info.value)
    assert exc_info.value.status_code == 404


# Test de busqueda correcta con ambos parametros
@patch("app.services.rick_and_morty_api.requests.get")
def test_get_location_by_name_and_type_bad_json(mock_get):
    # seteo el valor de la respuesta del request
    # el request retorna un dict sin name o type
    mock_get.return_value = MockResponse({
        "results": [
            {}
        ]
    })

    api = RickAndMortyAPI()

    # Capturo el error en exc_info
    with pytest.raises(ExternalAPIError) as exc_info:
        api.get_location_by_name_and_type(name="earth", type_="planet")

    # Verifico que el error ha sido manejado correctamente
    assert "Invalid JSON response" in str(exc_info.value)
    assert exc_info.value.status_code == 502

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


# region - Tests for extract_character_stats

# Test de ejecucion correcta con datos correctos
def test_extract_stats_basic_case():
    characters = [
        {"name": "Rick", "species": "Human", "status": "Alive"},
        {"name": "Morty", "species": "Human", "status": "Alive"},
        {"name": "Birdperson", "species": "Bird-Person", "status": "Dead"},
    ]
    result = RickAndMortyAPI().extract_character_stats(characters)

    assert result["character_names"] == ["Rick", "Morty", "Birdperson"]
    assert result["human_count"] == 2
    assert result["not_human_count"] == 1
    assert result["dead_count"] == 1
    assert result["alive_count"] == 2


# Test de ejecucion correcta con datos vacios
def test_extract_stats_empty_list():
    result = RickAndMortyAPI().extract_character_stats([])
    assert result == {
        "character_names": [],
        "human_count": 0,
        "not_human_count": 0,
        "dead_count": 0,
        "alive_count": 0,
    }


# test con datos faltantes
def test_extract_stats_missing_fields():
    characters = [
        {},
        {"name": "Summer"},
        {"species": "Human"},
        {"status": "Dead"},
    ]
    result = RickAndMortyAPI().extract_character_stats(characters)

    assert result["character_names"] == ["Summer"]
    assert result["human_count"] == 1
    assert result["not_human_count"] == 3
    assert result["dead_count"] == 1
    assert result["alive_count"] == 0


# Test con tipos de datos incorrectos
def test_extract_stats_weird_species_status():
    characters = [
        {"name": "Unknown1", "species": "Alien", "status": "Weird"},
        {"name": "Unknown2", "species": "Robot", "status": None},
        {"name": "Unknown3", "species": None, "status": "Dead"},
    ]
    result = RickAndMortyAPI().extract_character_stats(characters)

    assert result["character_names"] == ["Unknown1", "Unknown2", "Unknown3"]
    assert result["human_count"] == 0
    assert result["not_human_count"] == 3
    assert result["dead_count"] == 1
    assert result["alive_count"] == 0


# Test con nombre incorrecto
def test_extract_stats_invalid_name_type():
    characters = [
        {"name": 123, "species": "Human", "status": "Alive"},
        {"name": None, "species": "Alien", "status": "Dead"},
        {"name": True, "species": "Alien", "status": "Dead"},
        {"name": False, "species": "Alien", "status": "Dead"},
    ]
    result = RickAndMortyAPI().extract_character_stats(characters)

    assert result["character_names"] == []
    assert result["human_count"] == 1
    assert result["not_human_count"] == 3
    assert result["dead_count"] == 3
    assert result["alive_count"] == 1

# endregion
