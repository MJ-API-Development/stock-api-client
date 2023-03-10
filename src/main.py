from celery import Celery
import certifi
from flask import Flask, url_for, session
from authlib.oauth2.rfc6749 import OAuth2Token
from authlib.integrations.flask_client import OAuth, token_update
from flask_mail import Mail


from src.config import config_instance

from flask import Flask, redirect, url_for


app = Flask(__name__)

oauth = OAuth(app)

celery = Celery(main='EOD-MAILER')
mail = Mail()


def create_app(config=config_instance()) -> Flask:
    """

    :param config:
    :return:
    """
    app = Flask(__name__, template_folder="template", static_folder="static")

    app.config.from_object(config)
    with app.app_context():
        from src.routes.home import home_route
        from src.mail.send_emails import send_mail_route
        from src.routes.documentations import docs_route
        from src.authentication.routes import auth_handler

        mail.init_app(app)
        # celery.config_from_object(config.CELERY_SETTINGS)
        app.register_blueprint(home_route)
        app.register_blueprint(send_mail_route)
        app.register_blueprint(docs_route)
        app.register_blueprint(auth_handler)

    return app
