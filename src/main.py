from flask import Flask, make_response, jsonify, session, redirect, url_for
from flask_sitemap import Sitemap
from jwt import ExpiredSignatureError
from src.config import config_instance
from src.exceptions import UnAuthenticatedError


user_session = {}
sitemap = Sitemap()


def create_app(config=config_instance()) -> Flask:
    """

    :param config:
    :return:
    """
    app = Flask(__name__, template_folder="template", static_folder="static")

    app.config.from_object(config)
    with app.app_context():
        sitemap.init_app(app=app)

        from src.routes.home import home_route
        from src.routes.documentations import docs_route
        from src.routes.authentication.routes import auth_handler
        from src.routes.accounts.route import account_handler
        from src.routes.contacts.contact import contact_route
        from src.routes.apikeys.route import apikeys_route
        from src.routes.server_status import status_bp
        from src.routes.subscriptions.plan import plan_routes
        from src.routes.sitemap_route import sitemap_bp
        # celery.config_from_object(config.CELERY_SETTINGS)

        app.register_blueprint(home_route)
        app.register_blueprint(docs_route)
        app.register_blueprint(auth_handler)
        app.register_blueprint(account_handler)
        app.register_blueprint(contact_route)
        app.register_blueprint(apikeys_route)
        app.register_blueprint(status_bp)
        app.register_blueprint(plan_routes)
        app.register_blueprint(sitemap_bp)

        # Handle API Errors, all errors are re raised as HTTPException
        from src.exceptions import (InvalidSignatureError, ServerInternalError, UnresponsiveServer)

        app.register_error_handler(InvalidSignatureError,
                                   # Render a common error template
                                   lambda e: make_response(jsonify({'status': False, 'message': e.description}),
                                                           e.code))

        app.register_error_handler(ServerInternalError,
                                   lambda e: make_response(jsonify({'status': False, 'message': e.description}),
                                                           e.code))

        app.register_error_handler(UnresponsiveServer,
                                   lambda e: make_response(jsonify({'status': False, 'message': e.description}),
                                                           e.code))

        app.register_error_handler(ExpiredSignatureError,
                                   redirect(url_for('auth.login')))

        app.register_error_handler(InvalidSignatureError,
                                   redirect(url_for('auth.login')))

        app.register_error_handler(UnAuthenticatedError,
                                   redirect(url_for('auth.login')))

    return app
