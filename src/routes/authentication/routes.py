import datetime
import functools
import json
import jwt
import requests
from werkzeug.exceptions import HTTPException
from flask import request, render_template, redirect, url_for, session, Blueprint, flash, abort, jsonify, make_response
from functools import wraps
import hmac
import hashlib
from src.config import config_instance
from src.databases.models.schemas.account import AccountModel, AccountCreate
from src.exceptions import UnresponsiveServer, InvalidSignatureError, ServerInternalError, UnAuthenticatedError
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
        # Check user credentials using API endpoint
        user_data = {'email': email, 'password': password}
        _headers = get_headers(user_data)
        _path = config_instance().GATEWAY_SETTINGS.LOGIN_URL
        _base = config_instance().GATEWAY_SETTINGS.BASE_URL
        _url = f"{_base}{_path}"
        try:
            response = requests.post(url=_url, json=user_data, headers=_headers)
            auth_logger.info(response.text)
        except requests.exceptions.ConnectionError:
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


@auth_handler.route('/logout', methods=['POST'])
def logout():
    """
        convert to JSON based messages , the flow will be handled by the front page
    :return:
    """
    request_data = request.get_json()
    uuid = request_data.get('uuid')

    user_session.update({f"{uuid}": {}})
    # TODO - consider sending the message to the gateway indicating the action to logout
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


def create_authentication_token(user_data: dict[str, str]):
    # Create a token payload with the user ID and expiration date
    payload = {
        'uuid': user_data.get('uuid'),
        'email': user_data.get('email'),
        'password': user_data.get('password_hash'),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }

    # Encode the payload using a secret key
    token = jwt.encode(payload=payload, key=config_instance().SECRET_KEY, algorithm='HS256')
    auth_logger.info(f"CREATED Token : {token}")
    return token


def verify_authentication_token(token: str):
    """
        :param token:
        :return:
    """
    if token is None or token == "":
        raise UnAuthenticatedError()
    try:
        # Decode the token using the secret key
        payload = jwt.decode(message=token, key=config_instance().SECRET_KEY, algorithms=['HS256'],
                             do_time_check=True, verify=True)

        # Check if the token has expired
        if datetime.datetime.utcnow() > datetime.datetime.fromtimestamp(payload['exp']):
            raise UnAuthenticatedError()

        # Return the protected resource
        auth_logger.info(f"Verified Token : {payload}")
        return payload

    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        raise UnAuthenticatedError()


def user_details(func):
    """
        Returns the user details if the user is logged in and authorized to access this route
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('X-Auth-Token', None)
        # Just Obtain user details no need to verify the token
        if token is None or token == "":
            kwargs['user_data'] = {}
            return func(*args, **kwargs)
        auth_logger.info(f"Token Issued from backend : {token}")
        payload = jwt.decode(jwt=token, key=config_instance().SECRET_KEY, algorithms=['HS256'])

        _uuid = payload.get('uuid', None)

        if user_session.get(_uuid):
            # User is authorized, so add user details to kwargs and call the wrapped function
            kwargs['user_data'] = user_session[_uuid]
            response = func(*args, **kwargs)
            # Add X-Auth-Token header to response
            # response.headers['X-Auth-Token'] = token
            return response
        else:
            kwargs['user_data'] = {}
            response = func(*args, **kwargs)
            # response.headers['X-Auth-Token'] = ""
            return response

    return wrapper


def auth_required(func):
    """will not allow the user to access the route if the user is not logged in and not authorized for the route"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        request_data = request.get_json()
        # uuid = request_data.get('uuid', kwargs.get('uuid'))
        # if uuid is None:
        token = request.headers.get('X-Auth-Token', None)
        if token is None:
            raise UnAuthenticatedError()

        payload = verify_authentication_token(token=token)
        _uuid = payload.get('uuid', None)

        if _uuid not in user_session:
            return redirect('/login')

        authorized, response_data = is_authorized(_uuid)

        if response_data and response_data.get('status', False) and authorized:
            kwargs['user_data'] = user_session[_uuid]
            response = func(*args, **kwargs)
            # Add X-Auth-Token header to response
            response.headers['X-Auth-Token'] = token
            return response
        else:
            abort(401)

    return wrapper


@functools.lru_cache(maxsize=1024)
def is_authorized(uuid):
    """
        checks with the gateway server if the user is logged in and also authorized to access a specific route
    :param uuid:
    :return:
    """
    _path = config_instance().GATEWAY_SETTINGS.AUTHORIZE_URL
    _base = config_instance().GATEWAY_SETTINGS.BASE_URL
    _url = f"{_base}{_path}"
    user_data = {'uuid': uuid, 'path': request.path, 'method': request.method}
    _headers = get_headers(user_data)
    with requests.Session() as _session:
        try:
            response = _session.post(url=_url, json=user_data, headers=_headers)
            response.raise_for_status()
            response_data = response.json()
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            raise UnresponsiveServer()
        except json.JSONDecodeError as e:
            raise ServerInternalError() from e

    if not verify_signature(response=response):
        abort(401)
    payload = response_data.get('payload', {})
    authorized = payload.get('authorized', False)
    return authorized, response_data


def verify_signature(response):
    """this is authentication for the client and gateway communication"""
    secret_key = config_instance().SECRET_KEY
    data_header = response.headers.get('X-SIGNATURE', '')
    data_str, signature_header = data_header.split('|')
    _signature = hmac.new(secret_key.encode('utf-8'), data_str.encode('utf-8'), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature_header, _signature)
