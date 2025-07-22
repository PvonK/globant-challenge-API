from flask import Blueprint, request, jsonify
from app.services.rick_and_morty_api import RickAndMortyAPI

location_bp = Blueprint("location", __name__)


@location_bp.route("/location", methods=["GET"])
def location():
    """
    GET /location?name=earth&type=planet endpoint

    gets one the location that corresponds to the inputed parameters

    Query Parameters:

        - name: str (optional)
        - type: str (optional)

    Returns a JSON containing:

        - name: The name of the location found
        - type: The type of location found (Planet, Country, etc.)
    """
    name = request.args.get("name")
    type_ = request.args.get("type")

    external_api = RickAndMortyAPI()
    location_data = external_api.get_location_by_name_and_type(
        name=name,
        type_=type_
        )

    result = {
        "name": location_data.get("name"),
        "type": location_data.get("type")
    }

    return jsonify(result), 200, {"Content-Type": "application/json"}
