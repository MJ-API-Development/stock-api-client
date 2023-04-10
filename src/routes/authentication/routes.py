import requests
from flask import request, render_template, Blueprint, flash, jsonify, make_response

from src.config import config_instance
from src.databases.models.schemas.account import AccountCreate
from src.exceptions import UnresponsiveServer, InvalidSignatureError
from src.logger import init_logger
from src.main import user_session
from src.routes.authentication.handlers import user_details, get_headers, auth_required, create_authentication_token, \
    verify_signature

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
        # Check user credentials using API endpoint
        user_data = {'email': email, 'password': password}
        _headers = get_headers(user_data)
        _path = config_instance().GATEWAY_SETTINGS.LOGIN_URL
        _base = config_instance().GATEWAY_SETTINGS.BASE_URL
        _url = f"{_base}{_path}"
        with requests.Session() as request_session:
            try:
                response = request_session.post(url=_url, json=user_data, headers=_headers)
                auth_logger.info(response.text)
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
                user_session.update({f"{uuid}": response_data.get('payload', {})})
        response = make_response(jsonify(response_data), 200)
        # Adding Authentication Token to the response
        response.headers['X-Auth-Token'] = create_authentication_token(user_data=response_data.get('payload', {}))
        return response

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
