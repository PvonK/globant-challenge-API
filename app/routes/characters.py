from flask import Blueprint, jsonify
from app.services.rick_and_morty_api import RickAndMortyAPI

characters_bp = Blueprint("characters", __name__)


@characters_bp.route("/characters", methods=["GET"])
def characters():
    """
    GET /characters endpoint

    returns a list of character names and some statistics

    Returns a JSON containing:

        - character_names: list of all names
        - human_count: number of humans
        - not_human_count: number of non-humans
        - dead_count: number of dead characters
        - alive_count: number of alive characters
    """
    external_api = RickAndMortyAPI()
    result = external_api.get_all_characters_stats()

    return jsonify(result), 200, {"Content-Type": "application/json"}
