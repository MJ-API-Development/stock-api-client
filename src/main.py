from flask import Flask, url_for

from src.routes.home import home_route


def create_app(config_class) -> Flask:
    """

    :param config:
    :return:
    """
    app = Flask(__name__, template_folder="../template", static_folder="../static")

    app.config.from_object(config_class)
    with app.app_context():

        app.register_blueprint(home_route)

    return app

