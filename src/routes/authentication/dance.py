from flask import Flask, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google

from src.config import config_instance
from src.routes.authentication.handlers import do_login_auth, auth_logger

app = Flask(__name__)
app.secret_key = config_instance().SECRET_KEY

google_dance = make_google_blueprint(client_id=config_instance().GOOGLE_SETTINGS.GOOGLE_CLIENT_ID,
                                     client_secret=config_instance().GOOGLE_SETTINGS.GOOGLE_CLIENT_SECRET,
                                     redirect_url="authorized",
                                     scope=["https://www.googleapis.com/auth/userinfo.email",
                                            "https://www.googleapis.com/auth/userinfo.profile",
                                            "openid"])


@google_dance.route("/login/google")
def login_google():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")

    user_info = resp.json()
    email = user_info["email"]
    oauth_id = user_info["sub"]
    auth_logger.info("login Google")
    auth_logger.info(f"email {email} is authorized oauth_id {oauth_id}")

    assert resp.ok, resp.text
    return "You are {email} on Google".format(email=resp.json()["email"])
    # return "You are {email} on Google".format(email=resp.json()["email"])


@google_dance.route("/google/authorized")
def google_authorized():
    """
    **google_authorized**
        will login user if user does not exist will create a new user then login user
    :return:
    """
    if not google.authorized:
        return "Access denied"
    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    user_info = resp.json()
    email = user_info["email"]
    oauth_id = user_info["sub"]
    auth_logger.info("Google Authorized")
    auth_logger.info(f"email {email} is authorized oauth_id {oauth_id}")
    assert resp.ok, resp.text
    return "You are {email} on Google".format(email=resp.json()["email"])
