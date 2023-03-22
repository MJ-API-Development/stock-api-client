import requests
from werkzeug.exceptions import HTTPException
from flask import request, render_template, redirect, url_for, session, Blueprint, flash, abort, jsonify
from functools import wraps
import hmac
import hashlib
from src.config import config_instance
from src.databases.models.schemas.account import AccountModel, AccountCreate
from src.exceptions import UnresponsiveServer, InvalidSignatureError
from src.logger import init_logger
from src.main import user_session

auth_handler = Blueprint("auth", __name__)

auth_logger = init_logger('auth_logger')


def create_header(secret_key: str, user_data: dict) -> str:
    data_str = ','.join([str(user_data[k]) for k in sorted(user_data.keys())])
    signature = hmac.new(secret_key.encode('utf-8'), data_str.encode('utf-8'), hashlib.sha256).hexdigest()
    return f"{data_str}|{signature}"


def get_headers(user_data: dict) -> dict[str, str]:
    secret_key = config_instance().SECRET_KEY
    signature = create_header(secret_key, user_data)
    return {'X-SIGNATURE': signature, 'Content-Type': 'application/json'}


@auth_handler.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_data = request.get_json()
        print(user_data)

        account_base = AccountCreate(**user_data)
        print(account_base)
        _path = config_instance().GATEWAY_SETTINGS.CREATE_USER_URL
        _base = config_instance().GATEWAY_SETTINGS.BASE_URL
        _url = f"{_base}{_path}"
        _headers = get_headers(user_data=account_base.dict())
        print(f"registering new user : {_url}")
        try:
            response = requests.post(url=_url, data=account_base.json(), headers=_headers)
            print(response.text)
        except requests.exceptions.ConnectionError:
            raise UnresponsiveServer()

        if response.status_code not in [200, 201, 401]:
            raise UnresponsiveServer()

        if not verify_signature(response=response):
            raise InvalidSignatureError()

        response_data = response.json()
        if response_data and response_data.get('status', False):
            flash('Account created successfully. Please log in.', 'success')
            uuid = response_data.get('payload', {}).get('uuid')
            if uuid:
                # session[uuid] = response_data.get('payload', {})
                user_session.update({f"{uuid}": response_data.get('payload', {})})

            message: str = "Account created successfully. Please log in.'"
            payload = dict(status=True, payload=response_data.get('payload'), message=message)
            return jsonify(payload)
        else:
            payload = dict(status=False, message=response_data.get("message", payload={}))
            return jsonify(payload)

    elif request.method == "GET":
        return render_template('login.html')


@auth_handler.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        request_data = request.get_json()
        email = request_data['username']
        password = request_data['password']
        auth_logger.info(f"login to account : {email}")
        # Check user credentials using API endpoint
        user_data = {'email': email, 'password': password}
        _headers = get_headers(user_data)
        _path = config_instance().GATEWAY_SETTINGS.LOGIN_URL
        _base = config_instance().GATEWAY_SETTINGS.BASE_URL
        _url = f"{_base}{_path}"
        auth_logger.info(f"login endpoint : {_url}")
        try:
            response = requests.post(url=_url, json=user_data, headers=_headers)
            auth_logger.info(f"response from gateway : {response.status_code}")
        except requests.exceptions.ConnectionError:
            raise UnresponsiveServer()

        if response.status_code not in [200, 201, 401]:
            auth_logger.info(f"response from gateway : {response.text}")
            raise UnresponsiveServer()

        if not verify_signature(response=response):
            raise InvalidSignatureError()

        response_data = response.json()

        if response_data and response_data.get('status', False):
            uuid = response_data.get('payload', {}).get('uuid')

            if uuid:
                # session[uuid] = response_data.get('payload')
                user_session.update({f"{uuid}": response_data.get('payload', {})})

                auth_logger.info(f"session : {session.get(uuid)}")

        return jsonify(response_data)

    elif request.method == 'GET':
        return render_template('login.html')


@auth_handler.route('/logout', methods=['POST'])
def logout():
    """
        convert to JSON based messages , the flow will be handled by the front page
    :return:
    """
    request_data = request.get_json()
    uuid = request_data['uuid']
    # session[uuid] = {}
    user_session.update({f"{uuid}": {}})
    # TODO - consider sending the message to the gateway indicating the action to logout
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


def auth_required(func):
    """
        checks if the user is logged in and also if the user is authorized to access a certain path
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        uuid = request.get_json('uuid')
        if uuid not in user_session:
            return redirect('/login')

        # Call the API to check if the user is authorized to access this resource
        _path = config_instance().GATEWAY_SETTINGS.AUTHORIZE_URL
        _base = config_instance().GATEWAY_SETTINGS.BASE_URL

        _url = f"{_base}{_path}"
        user_data = {'uuid': uuid, 'path': request.path, 'method': request.method}
        _headers = get_headers(user_data)
        try:
            response = requests.post(url=_url, json=user_data, headers=_headers)
        except requests.exceptions.ConnectionError:
            raise UnresponsiveServer()

        if response.status_code not in [200, 201, 401]:
            raise UnresponsiveServer()

        if not verify_signature(response=response):
            abort(401)

        response_data = response.json()

        if response_data and response_data.get('status', False):
            if response_data.get('payload').get("authorized"):
                return func(*args, **kwargs)
            else:
                abort(401)
        else:
            abort(401)

    return wrapper


def verify_signature(response):
    secret_key = config_instance().SECRET_KEY
    data_header = response.headers.get('X-SIGNATURE', '')
    data_str, signature_header = data_header.split('|')
    _signature = hmac.new(secret_key.encode('utf-8'), data_str.encode('utf-8'), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature_header, _signature)
