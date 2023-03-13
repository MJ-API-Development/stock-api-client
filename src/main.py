from flask import Flask, url_for, session


from src.config import config_instance

from flask import Flask, redirect, url_for


app = Flask(__name__)


def create_app(config=config_instance()) -> Flask:
    """

    :param config:
    :return:
    """
    app = Flask(__name__, template_folder="template", static_folder="static")

    app.config.from_object(config)
    with app.app_context():
        from src.routes.home import home_route
        from src.routes.documentations import docs_route
        from src.routes.authentication.routes import auth_handler
        from src.routes.accounts.route import account_handler

        # celery.config_from_object(config.CELERY_SETTINGS)
        app.register_blueprint(home_route)
        app.register_blueprint(docs_route)
        app.register_blueprint(auth_handler)
        app.register_blueprint(account_handler)

    return app
