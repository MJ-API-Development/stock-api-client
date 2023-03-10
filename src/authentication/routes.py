import requests
from flask import request, render_template, redirect, url_for, session, Blueprint, flash, abort
from functools import wraps
import hmac
import hashlib
from src.config import config_instance
from src.databases.models.schemas.account import AccountBase

auth_handler = Blueprint(__name__, "auth")

from werkzeug.exceptions import HTTPException


class InvalidSignatureError(HTTPException):
    code = 400
    description = 'The signature is invalid.'


def create_header(secret_key: str, user_data: dict) -> str:
    data_str = ','.join([str(user_data[k]) for k in sorted(user_data.keys())])
    signature = hmac.new(secret_key.encode(), data_str.encode(), hashlib.sha256).hexdigest()
    return f"{data_str},{signature}"


def get_headers(user_data: dict) -> dict[str, str]:
    secret_key = config_instance().SECRET_KEY
    signature = create_header(secret_key, user_data)
    return {'X-SECRET-KEY': signature, 'Content-Type': 'application/json'}


@auth_handler.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_data = request.json()
        account_base = AccountBase(**user_data)
        _url = "https://gateway.eod-stock-api.site/_admin/users/create"
        _headers = get_headers(user_data=account_base.dict())
        response = requests.post(url=_url, data=account_base.json(), headers=_headers)
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
        email = request.form['email']
        password = request.form['password']

        # Check user credentials using API endpoint
        _url = "https://gateway.eod-stock-api.site/_admin/users/login"
        user_data = {'email': email, 'password': password}
        _headers = get_headers(user_data)
        response = requests.post(url=_url, data=user_data, headers=_headers)
        if not verify_signature(response=response):
            raise InvalidSignatureError()

        response_data = response.json()

        if response_data and response_data.get('status', False):
            session['uuid'] = response_data['data']['uuid']
            flash('Login successful.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')


@auth_handler.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'uuid' not in session:
            return redirect('/login')

        # Call the API to check if the user is authorized to access this resource
        _url = "https://gateway.eod-stock-api.site/_admin/users/check_authorization"
        user_data = {'uuid': session['uuid'], 'path': request.path}
        _headers = get_headers(user_data)
        response = requests.post(url=_url, data=user_data, headers=_headers)

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
    signature_header = response.headers.get('X-SIGNATURE', '')
    signature = hmac.new(secret_key.encode(), response.content, hashlib.sha256).hexdigest()
    return signature_header == signature
