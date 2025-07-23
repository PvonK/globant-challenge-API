import os
import requests
from urllib.parse import urlencode

# Manejo de errores de la API externa
from app.exceptions.external_api import ExternalAPIError

# Definicion de constantes
HUMAN = "Human"
ALIVE = "Alive"
DEAD = "Dead"


class RickAndMortyAPI:
    def __init__(self):
        self.base_url = os.getenv(
            "RICK_AND_MORTY_BASE_URL",
            "https://rickandmortyapi.com/api"
            )

    def get_all_characters_stats(self):
        # URL al que se le consulta la informacion de los personajes
        url = f"{self.base_url}/character"

        # Diccionario que almacenara el total final
        character_stats = {
            "character_names": [],
            "human_count": 0,
            "not_human_count": 0,
            "dead_count": 0,
            "alive_count": 0,
        }

        while url:
            response = self._get(url)
            # Podria haber agregado todos los personajes dentro de una variable
            # y despues calcular los stats pero preferi calcular los stats por
            # pagina ya que desconozco el tamaño de la lista completa
            # characters.extend(response.get("results", []))
            request_result = response.get("results", [])

            # extraigo la informacion que necesito de la respuesta al request
            extracted_char_stats = self.extract_character_stats(request_result)

            # Sumo los restultados de esta pagina al agregado total
            character_stats["character_names"] += extracted_char_stats.get(
                "character_names", []
                )
            character_stats["human_count"] += extracted_char_stats.get(
                "human_count", 0
                )
            character_stats["not_human_count"] += extracted_char_stats.get(
                "not_human_count", 0
                )
            character_stats["dead_count"] += extracted_char_stats.get(
                "dead_count", 0
                )
            character_stats["alive_count"] += extracted_char_stats.get(
                "alive_count", 0
                )

            # Redefino el URL al URL de la proxima pagina
            # (el cual la API almacena en el argumento "next")
            url = response.get("info", {}).get("next")

        return character_stats

    # Metodo opara extraer la informacion que necesito
    # de los requests a la API externa
    @staticmethod
    def extract_character_stats(character_list):
        character_names = []
        human_count = 0
        not_human_count = 0
        dead_count = 0
        alive_count = 0

        # Itero cada personaje en la lista de personajes
        for character in character_list:
            name = character.get("name")
            if name:
                character_names.append(name)

            if character.get("species") == HUMAN:
                human_count += 1
            else:
                not_human_count += 1

            if character.get("status") == ALIVE:
                alive_count += 1
            elif character.get("status") == DEAD:
                dead_count += 1

        return {
            "character_names": character_names,
            "human_count": human_count,
            "not_human_count": not_human_count,
            "dead_count": dead_count,
            "alive_count": alive_count,
        }

    def get_location_by_name_and_type(self, name=None, type_=None):
        query = {}
        if name:
            query["name"] = name
        if type_:
            query["type"] = type_

        url = f"{self.base_url}/location?{urlencode(query)}"
        response = self._get(url)

        if not response.get("results"):
            raise ExternalAPIError(
                "No matching location found",
                status_code=404
                )

        return response["results"][0]

    @staticmethod
    def _get(url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

        # Si surge un error en el request, levanto una excepcion
        # para comunicar el error del servicio externo
        except requests.exceptions.HTTPError as http_err:
            raise ExternalAPIError(
                f"HTTP error: {http_err}",
                status_code=response.status_code
                )

        except requests.exceptions.Timeout:
            raise ExternalAPIError(
                "Request timed out",
                status_code=504
                )

        except requests.exceptions.RequestException as e:
            raise ExternalAPIError(
                f"External API request failed: {e}",
                status_code=503
                )

        # Si no ocurrio una excepcion pero el resultado no es JSON valido
        try:
            return response.json()
        except ValueError:
            raise ExternalAPIError(
                "Invalid JSON response",
                status_code=502
                )
