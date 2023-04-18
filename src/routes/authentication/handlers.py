import datetime
import hashlib
import hmac
import json
from functools import wraps

import flask
import jwt
import requests
from flask import request, redirect, abort, Request, make_response, jsonify, session

from src.cache import cached
from src.config import config_instance
from src.exceptions import UnAuthenticatedError, UnresponsiveServer, ServerInternalError, InvalidSignatureError
from src.logger import init_logger
from src.main import user_session

auth_logger = init_logger('auth_logger')


def create_header(secret_key: str, user_data: dict) -> str:
    data_str = ','.join([str(user_data[k]) for k in sorted(user_data.keys())])
    signature = hmac.new(secret_key.encode('utf-8'), data_str.encode('utf-8'), hashlib.sha256).hexdigest()
    return f"{data_str}|{signature}"


def get_headers(user_data: dict) -> dict[str, str]:
    secret_key = config_instance().SECRET_KEY
    signature = create_header(secret_key, user_data)
    return {'X-SIGNATURE': signature, 'Content-Type': 'application/json'}


def create_authentication_token(user_data: dict[str, str]):
    # Create a token payload with the user ID and expiration date
    payload = {
        'uuid': user_data.get('uuid'),
        'email': user_data.get('email'),
        'password': user_data.get('password_hash'),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    # TODO consider checking if user exist with the gateway before creating the token
    # Encode the payload using a secret key
    token = jwt.encode(payload=payload, key=config_instance().SECRET_KEY, algorithm='HS256')
    auth_logger.info(f"CREATED Token : {token}")
    return token


def verify_authentication_token(token: str):
    """
        :param token:
        :return:
    """
    if not token or token is None:
        raise UnAuthenticatedError()
    try:
        # Decode the token using the secret key

        payload = jwt.decode(jwt=token, key=config_instance().SECRET_KEY, algorithms=['HS256'],
                             do_time_check=True, verify=True)

        # Check if the token has expired
        if datetime.datetime.utcnow() > datetime.datetime.fromtimestamp(payload['exp']):
            raise UnAuthenticatedError()

        # Return the protected resource
        auth_logger.info(f"Verified Token : {payload}")
        return payload

    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        raise UnAuthenticatedError()


@cached
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
    auth_logger.info(f"user data: {user_data}")
    with requests.Session() as _session:
        try:
            response = _session.post(url=_url, json=user_data, headers=_headers)
            auth_logger.info(f"authorizing request : {response.text} status code : {response.status_code} ")
            response.raise_for_status()
            response_data = response.json()
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            raise UnresponsiveServer()
        except json.JSONDecodeError as e:
            raise ServerInternalError() from e

    if not verify_signature(response=response):
        abort(401)
    payload = response_data.get('payload', {})
    authorized = payload.get('is_authorized', False)
    return authorized, response_data


def verify_signature(response):
    """this is authentication for the client and gateway communication"""
    secret_key = config_instance().SECRET_KEY
    data_header = response.headers.get('X-SIGNATURE', '')
    auth_logger.info(f'Verifying Signature : {data_header}')
    data_str, signature_header = data_header.split('|')
    _signature = hmac.new(secret_key.encode('utf-8'), data_str.encode('utf-8'), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature_header, _signature)


def get_uuid_cookie(_request: Request):
    """will obtain a secure cookie from request"""
    # Get the "Cookie" header from the request headers
    cookie = _request.cookies.get('uuid', None)
    try:
        return json.loads(cookie) if cookie is not None else None
    except json.JSONDecodeError:
        return None


def user_details(func):
    """
        Returns the user details if the user is logged in and authorized to access this route
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('X-Auth-Token', None)
        auth_logger.info(f"Request Header : {request.headers}")
        # Just Obtain user details no need to verify the token
        if token is None:
            user_data = get_uuid_cookie(_request=request)
            if user_data is None:
                user_data = {}

            token = create_authentication_token(user_data=user_data)
            user_session[user_data.get('uuid')] = user_data

        auth_logger.info(f"Token Issued from backend : {token}")
        payload = jwt.decode(jwt=token, key=config_instance().SECRET_KEY, algorithms=['HS256'])

        _uuid = payload.get('uuid', None)

        if _uuid and user_session.get(_uuid, False):
            kwargs['user_data'] = user_session.get(_uuid, {})
            response = func(*args, **kwargs)
            return response

        else:
            kwargs['user_data'] = {}
            response = func(*args, **kwargs)
            return response

    return wrapper


def auth_required(func):
    """will not allow the user to access the route if the user is not logged in and not authorized for the route"""

    @wraps(func)
    def wrapper(*args, **kwargs):

        # if request.headers.get('Content-Type')  == 'application/json':
        #     request_data = request.get_json()

        # uuid = request_data.get('uuid', kwargs.get('uuid'))
        # if uuid is None:
        token = request.headers.get('X-Auth-Token', None)
        if token is None:
            # Token not found lets try a cookie
            user_data = get_uuid_cookie(_request=request)
            if user_data is None:
                raise UnAuthenticatedError()

            token = create_authentication_token(user_data=user_data)
            user_session[user_data['uuid']] = user_data
        # verify token authenticity
        if token and token is not None:
            payload = verify_authentication_token(token=token)
        else:
            raise UnAuthenticatedError()

        _uuid = payload.get('uuid', None)

        # TODO Have to make this work ASAP
        if 'google_token' in session:
            _uuid = session['google_token']

        if _uuid is None or _uuid not in user_session:
            return redirect('/login')

        authorized, response_data = is_authorized(_uuid)

        if response_data and response_data.get('status', False) and authorized:
            kwargs['user_data'] = user_session[_uuid]
            response = func(*args, **kwargs)
            # Add X-Auth-Token header to response
            return response
        else:
            abort(401)

    return wrapper


def do_login(email: str, password: str):
    """

    :param email:
    :param password:
    :return:
    """
    user_data = {'email': email, 'password': password}
    _headers = get_headers(user_data)
    _path = config_instance().GATEWAY_SETTINGS.LOGIN_URL
    _base = config_instance().GATEWAY_SETTINGS.BASE_URL
    _url = f"{_base}{_path}"
    with requests.Session() as request_session:
        try:
            response = request_session.post(url=_url, json=user_data, headers=_headers)

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


def do_login_auth(email: str, password: str) -> flask.Response:
    """

    :param email:
    :param password:
    :return:
    """
    user_data = {'email': email, 'password': password}
    _headers = get_headers(user_data)
    _path = config_instance().GATEWAY_SETTINGS.LOGIN_URL
    _base = config_instance().GATEWAY_SETTINGS.BASE_URL
    _url = f"{_base}{_path}"
    with requests.Session() as request_session:
        try:
            response = request_session.post(url=_url, json=user_data, headers=_headers)

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
    else:
        return do_create_account(email=email, password=password)

    response = make_response(jsonify(response_data), 200)
    # Adding Authentication Token to the response
    response.headers['X-Auth-Token'] = create_authentication_token(user_data=response_data.get('payload', {}))
    return response


def do_create_account(email: str, password: str) -> flask.Response:
    """

    :param email:
    :param password:
    :return: flask.Response
    """
    user_data = {
        'email': email,
        'password': password}

    _headers = get_headers(user_data)
    _path = config_instance().GATEWAY_SETTINGS.CREATE_USER_URL
    _base = config_instance().GATEWAY_SETTINGS.BASE_URL
    _url = f"{_base}{_path}"
    with requests.Session() as request_session:
        try:
            response = request_session.post(url=_url, json=user_data, headers=_headers)

        except requests.exceptions.ConnectionError:
            raise UnresponsiveServer("Cannot connect to server try again later")
        except requests.exceptions.Timeout:
            raise UnresponsiveServer("Server is not responding")

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
