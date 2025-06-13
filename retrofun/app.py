from flask import Flask
from . import models
from config import config


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    models.init_db(app)

    from .routes import bp
    app.register_blueprint(bp)

    return app
