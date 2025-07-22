from flask import Flask
from app.routes.characters import characters_bp
from app.routes.location import location_bp
from app.error_handlers import register_error_handlers


def create_app():
    app = Flask(__name__)
    app.register_blueprint(characters_bp)
    app.register_blueprint(location_bp)
    register_error_handlers(app)
    return app
