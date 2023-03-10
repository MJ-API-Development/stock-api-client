import requests
from werkzeug.exceptions import HTTPException
from flask import request, render_template, redirect, url_for, session, Blueprint, flash, abort
from functools import wraps
import hmac
import hashlib
from src.config import config_instance
from src.databases.models.schemas.account import AccountBase

auth_handler = Blueprint("auth", __name__)


class InvalidSignatureError(HTTPException):
    code = 400
    description = 'The signature is invalid.'


class ServerInternalError(HTTPException):
    code = 500
    description = 'An internal server error occurred.'


class UnresponsiveServer(HTTPException):
    code = 503
    description = 'The server is currently unavailable and cannot process requests.'


def create_header(secret_key: str, user_data: dict) -> str:
    data_str = ','.join([str(user_data[k]) for k in sorted(user_data.keys())])
    signature = hmac.new(secret_key.encode(), data_str.encode(), hashlib.sha256).hexdigest()
    return f"{data_str}|{signature}"


def get_headers(user_data: dict) -> dict[str, str]:
    secret_key = config_instance().SECRET_KEY
    signature = create_header(secret_key, user_data)
    return {'X-SIGNATURE': signature, 'Content-Type': 'application/json'}


@auth_handler.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_data = request.json()
        account_base = AccountBase(**user_data)
        _url = config_instance().GATEWAY_SETTINGS.CREATE_USER_URL
        _headers = get_headers(user_data=account_base.dict())
        response = requests.post(url=_url, data=account_base.json(), headers=_headers)

        if response.status_code not in [200, 201]:
            raise UnresponsiveServer()

        if not verify_signature(response=response):
            raise InvalidSignatureError()

        response_data = response.json()
        if response_data and response_data.get('status', False):
            flash('Account created successfully. Please log in.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth_handler.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        request_data = request.get_json()
        print(request_data)
        email = request_data['username']
        password = request_data['password']

        # Check user credentials using API endpoint
        user_data = {'email': email, 'password': password}
        _headers = get_headers(user_data)
        _url = config_instance().GATEWAY_SETTINGS.LOGIN_URL
        response = requests.post(url=_url, data=user_data, headers=_headers)

        if response.status_code not in [200, 201]:
            raise UnresponsiveServer()

        if not verify_signature(response=response):
            raise InvalidSignatureError()

        response_data = response.json()

        if response_data and response_data.get('status', False):
            uuid = response_data.get('payload', {}).get('uuid')
            if uuid:
                session['uuid'] = uuid
                flash('Login successful.', 'success')
                return redirect(url_for('dashboard'))
            raise ServerInternalError()
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')


@auth_handler.route('/logout')
def logout():
    session.clear()
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
        if 'uuid' not in session:
            return redirect('/login')

        # Call the API to check if the user is authorized to access this resource
        _url = config_instance().GATEWAY_SETTINGS.AUTHORIZE_URL
        user_data = {'uuid': session['uuid'], 'path': request.path, 'method': request.method}
        _headers = get_headers(user_data)
        response = requests.post(url=_url, data=user_data, headers=_headers)

        if response.status_code not in [200, 201]:
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
    _signature = hmac.new(secret_key.encode(), data_str, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature_header, _signature)
