import requests
from flask import request, render_template, Blueprint, flash, jsonify, make_response, redirect, url_for
from oauthlib.oauth2 import TokenExpiredError

from src.routes.authentication.dance import google

from src.config import config_instance
from src.databases.models.schemas.account import AccountCreate
from src.exceptions import UnresponsiveServer, InvalidSignatureError
from src.logger import init_logger
from src.main import user_session
from src.routes.authentication.handlers import user_details, get_headers, auth_required, create_authentication_token, \
    verify_signature, do_login, do_login_auth

auth_handler = Blueprint("auth", __name__)

auth_logger = init_logger('auth_logger')


@auth_handler.route('/register', methods=['POST'])
@user_details
def register(user_data: dict[str, str]):
    if not user_data:

        user_data = request.get_json()

        account_base = AccountCreate(**user_data)
        _path = config_instance().GATEWAY_SETTINGS.CREATE_USER_URL
        _base = config_instance().GATEWAY_SETTINGS.BASE_URL
        _url = f"{_base}{_path}"
        _headers = get_headers(user_data=account_base.dict())

        with requests.Session() as request_session:
            try:
                response = request_session.post(url=_url, data=account_base.json(), headers=_headers)

            except requests.exceptions.ConnectionError:
                raise UnresponsiveServer()
            except requests.exceptions.Timeout:
                raise UnresponsiveServer()

        if response.status_code not in [200, 201, 401]:
            raise UnresponsiveServer()

        if not verify_signature(response=response):
            raise InvalidSignatureError()

        response_data = response.json()
        if response_data and response_data.get('status', False):
            uuid = response_data.get('payload', {}).get('uuid')
            if uuid:
                user_session[uuid] = response_data.get('payload', {})

            return jsonify(response_data)
        else:
            payload = dict(status=False, message=response_data.get("message"), payload={})
            return jsonify(payload)

    else:
        payload = dict(status=False, message="You are already logged in", payload={})
        return jsonify(payload)


@auth_handler.route('/login', methods=['GET', 'POST'])
def login():
    """
    **login - POST **
        will authenticate login credentials and also create new
        user_session
    ** login GET **
        will return the login form
    :return:
    """
    if request.method == 'POST':
        request_data = request.get_json()
        email = request_data['username']
        password = request_data['password']
        return do_login(email, password)
        # Check user credentials using API endpoint

    elif request.method == 'GET':
        return render_template('login.html')


@auth_handler.route('/logout', methods=['GET'])
@auth_required
def logout(user_data: dict[str, str]):
    """
        convert to JSON based messages , the flow will be handled by the front page
    :return:
    """

    uuid = user_data.get('uuid')
    # removes login information from session
    user_session.update({f"{uuid}": {}})
    # TODO - consider sending the message to the gateway indicating the action to logout
    flash('You have been logged out.', 'success')
    response = make_response(render_template('login.html'), 200)
    # set the session cookie to expire
    response.set_cookie('uuid', '', max_age=0)
    # removing the authentication token
    response.headers.set('X-Auth-Token', '')
    # user completely logged out bye bye
    return response


@auth_handler.route("/google/authorized")
def google_authorized():
    """
    **google_authorized**
        will login user if user does not exist will create a new user then login user
    :return:
    """
    if not google.authorized:
        return redirect(url_for('google.login'))
    try:
        resp = google.get("/oauth2/v2/userinfo")
    except TokenExpiredError:
        response = redirect(url_for('google.login'))
        auth_logger.error("Token Expired")
        response.set_cookie('session', '')
        return response

    assert resp.ok, resp.text

    user_info = resp.json()

    auth_logger.info(f"Google User : {user_info}")
    email = user_info["email"]
    # oauth_id = user_info["sub"]
    auth_logger.info("Google Authorized")
    auth_logger.info(f"email {email} is authorized oauth_id")

    if user_info.get('verified_email', False):
        name = user_info.get('name')
        given_name = user_info.get('given_name')
        family_name = user_info.get('family_name')
        response = do_login_auth(email=email, id=user_info.get('id'), name=name, given_name=given_name, family_name=family_name)
        return response

    return redirect(url_for('account.account'))

