from flask import jsonify
from app.exceptions.external_api import ExternalAPIError


def register_error_handlers(app):
    @app.errorhandler(ExternalAPIError)
    def handle_external_api_error(e):
        response = {
            "error": str(e),
            "source": "external_api",
            "status_code": e.status_code or 500
        }
        return jsonify(response), e.status_code or 500, {
            "Content-Type": "application/json"
            }

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        response = {
            "error": "Internal server error",
            "details": str(e)
        }
        return jsonify(response), 500, {"Content-Type": "application/json"}
