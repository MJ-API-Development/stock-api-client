import requests
from werkzeug.exceptions import HTTPException
from flask import request, render_template, redirect, url_for, session, Blueprint, flash, abort, jsonify
from functools import wraps
import hmac
import hashlib
from src.config import config_instance
from src.databases.models.schemas.account import AccountModel, CompleteAccountResponseModel, AccountResponseSchema
from src.routes.authentication.routes import auth_required, get_headers, UnresponsiveServer, verify_signature
from src.utils import get_api_key, get_paypal_address

account_handler = Blueprint("account", __name__)


@account_handler.route('/account', methods=['GET'])
def account():
    if request.method == "GET":
        return render_template('dashboard/account.html')


@account_handler.route('/account/<string:uuid>', methods=['GET'])
def get_account(uuid: str):
    """user data must already be contained on the session so just return that data"""
    user_data = session[uuid]
    if uuid and user_data:
        payload = dict(status=True, payload=user_data, message="successfully found user data")
    else:
        _base = config_instance().GATEWAY_SETTINGS.BASE_URL
        _url = f"{_base}/_admin/user/{uuid}"
        user_data = dict(uuid=uuid)
        _header = get_headers(user_data=user_data)
        response = requests.get(url=_url, json=user_data, headers=_header)

        if response.status_code not in [200, 401]:
            raise UnresponsiveServer()

        if not verify_signature(response=response):
            abort(401)

        if response.status_code == 200:
            response_data = AccountResponseSchema(**response.json())
            session[uuid] = response_data.dict(exclude=['uuid']).get('payload', {})

            return jsonify(response_data.dict())

        session[uuid] = {}
        message: str = "Unable to update your account"
        new_response = dict(status=False, message=message, payload={})

        return jsonify(new_response)

    # sending this information to user display
    return jsonify(payload)


@account_handler.route('/account/<string:uuid>', methods=['PUT'])
@auth_required
def update_account(uuid: str):
    """check if user data is valid then update"""
    user_data = request.get_json()
    user_data.update(dict(uuid=uuid))
    account_data = AccountModel(**user_data)
    _headers = get_headers(account_data.dict())

    _base = config_instance().GATEWAY_SETTINGS.BASE_URL
    _url = f"{_base}/_admin/user"

    response = requests.put(url=_url, json=user_data, headers=_headers)

    if response.status_code not in [200, 201, 401]:
        raise UnresponsiveServer()

    if not verify_signature(response=response):
        abort(401)

    if response.status_code == 201:
        response_data = AccountResponseSchema(**response.json())
        session[uuid] = response_data.dict(exclude=['uuid']).get('payload', {})

        return jsonify(response_data.dict())

    session[uuid] = {}
    message: str = "Unable to update your account"
    new_response = dict(status=False, message=message, payload={})

    return jsonify(new_response)





