import requests
from flask import request, render_template, session, Blueprint, abort, jsonify
from src.config import config_instance
from src.databases.models.schemas.account import AccountModel, AccountResponseSchema
from src.logger import init_logger
from src.main import user_session
from src.routes.authentication.routes import auth_required, get_headers, UnresponsiveServer, verify_signature, \
    user_details

account_handler = Blueprint("account", __name__)
account_logger = init_logger("account_logger")


@account_handler.route('/account', methods=['GET'])
@user_details
def account(user_data: dict[str, str]):
    if user_data is None:
        user_data = {}
    context = dict(user_data=user_data)
    return render_template('dashboard/account.html', **context)


@account_handler.route('/account/<string:uuid>', methods=['GET'])
def get_account(uuid: str):
    """user data must already be contained on the
    session so just return that data"""
    user_data = user_session.get(uuid)
    if uuid and (user_data is not None):
        account_logger.info(f"User data : {user_data}")
        payload = dict(status=True, payload=user_data, message="successfully found user data")
        return jsonify(payload)
    else:
        _base: str = config_instance().GATEWAY_SETTINGS.BASE_URL
        _url = f"{_base}/_admin/user/{uuid}"
        user_data: dict[str, str] = dict(uuid=uuid)
        _header: dict[str, str] = get_headers(user_data=user_data)
        with requests.Session() as request_session:
            try:
                response = request_session.get(url=_url, json=user_data, headers=_header)
                response.raise_for_status()
            except requests.exceptions.ConnectionError:
                raise UnresponsiveServer()
            except requests.exceptions.Timeout:
                raise UnresponsiveServer()
            # TODO try catching HTTP Errors

        if response.status_code not in [200, 401]:
            raise UnresponsiveServer()

        if not verify_signature(response=response):
            abort(401)

        if response.status_code == 200:
            response_data = response.json()
            user_session.update({f"{uuid}": response_data.get('payload', {})})
            return jsonify(response_data)

        user_session.update({f"{uuid}": {}})
        message: str = "Sorry cannot load account"
        new_response = dict(status=False, message=message, payload={})
        return jsonify(new_response)


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
    with requests.Session() as request_session:
        try:
            response = request_session.put(url=_url, json=user_data, headers=_headers)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            raise UnresponsiveServer()
        except requests.exceptions.Timeout:
            raise UnresponsiveServer()

    if response.status_code not in [200, 201, 401]:
        raise UnresponsiveServer()

    if not verify_signature(response=response):
        abort(401)

    if response.status_code == 201:
        response_data = AccountResponseSchema(**response.json())
        user_session.update({f"{uuid}": response_data.dict().get('payload', {})})

        return jsonify(response_data.dict())

    user_session.update({f"{uuid}": {}})

    message: str = "Unable to update your account"
    new_response = dict(status=False, message=message, payload={})

    return jsonify(new_response)
