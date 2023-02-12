from celery import Celery
from flask import Flask, url_for
from flask_mail import Mail
from src.config import config_instance
celery = Celery(main='EOD-MAILER')
mail = Mail()


def create_app(config=config_instance()) -> Flask:
    """

    :param config:
    :return:
    """
    app = Flask(__name__, template_folder="../template", static_folder="../static")

    app.config.from_object(config)
    with app.app_context():
        from src.routes.home import home_route
        from src.mail.send_emails import send_mail_route
        mail.init_app(app)
        celery.config_from_object(config.CELERY_SETTINGS)
        app.register_blueprint(home_route)
        app.register_blueprint(send_mail_route)

    return app
