from flask import Flask, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google

from src.config import config_instance

app = Flask(__name__)
app.secret_key = config_instance().SECRET_KEY

google_dance = make_google_blueprint(client_id=config_instance().GOOGLE_SETTINGS.GOOGLE_CLIENT_ID,
                                     client_secret=config_instance().GOOGLE_SETTINGS.GOOGLE_CLIENT_SECRET,
                                     redirect_url="https://eod-stock-api.site/google/authorized",
                                     redirect_to="https://eod-stock-api.site/account",
                                     authorized_url="/google/authorized",
                                     scope=["https://www.googleapis.com/auth/userinfo.email",
                                            "https://www.googleapis.com/auth/userinfo.profile",
                                            "openid"])


@google_dance.route("/login/google")
def login_google():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    return "You are {email} on Google".format(email=resp.json()["email"])


@google_dance.route("/google/authorized")
def google_authorized():
    """

    :return:
    """
    if not google.authorized:
        return "Access denied"
    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    return "You are {email} on Google".format(email=resp.json()["email"])

