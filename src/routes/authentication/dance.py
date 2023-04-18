from flask import Flask, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google

from src.config import config_instance
from src.routes.authentication.handlers import do_login_auth, auth_logger

app = Flask(__name__)
app.secret_key = config_instance().SECRET_KEY

google_dance = make_google_blueprint(client_id=config_instance().GOOGLE_SETTINGS.GOOGLE_CLIENT_ID,
                                     client_secret=config_instance().GOOGLE_SETTINGS.GOOGLE_CLIENT_SECRET,
                                     redirect_url="/google/authorized",
                                     scope=["https://www.googleapis.com/auth/userinfo.email",
                                            "https://www.googleapis.com/auth/userinfo.profile",
                                            "openid"])


