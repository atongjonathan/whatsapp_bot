from flask import Flask
from .config import load_configurations
from .views import webhook_blueprint


def create_app():
    app = Flask(__name__)

    # Load configurations and logging settings
    load_configurations(app)

    # Import and register blueprints, if any
    app.register_blueprint(webhook_blueprint)

    return app
