import json

import requests
from flask import Blueprint, request, jsonify

from src.config import config_instance
from src.exceptions import UnresponsiveServer, InvalidSignatureError
from src.routes.authentication.handlers import get_headers, verify_signature, auth_required

apikeys_route = Blueprint("apikeys", __name__)


@apikeys_route.route('/update-api-key', methods=['POST'])
@auth_required
def regenerate_api_key(user_data: dict[str, str]):
    """
        will recreate te api keys for user
    :return:
    """
    account_data = request.get_json()
    base_url: str = config_instance().GATEWAY_SETTINGS.BASE_URL
    apikey = account_data.get('apikey', {}).get('api_key')

    if apikey is None:
        message: str = "You do not have a valid apikey please subscribe"
        payload = dict(status=False, message=message, payload={})
        return jsonify(payload)

    endpoint: str = f"{base_url}/_admin/apikey/{apikey}"
    payload = dict(apikey=apikey)
    headers = get_headers(user_data=payload)
    with requests.Session() as session:
        try:
            response = session.post(url=endpoint, json=payload, headers=headers)
            response.raise_for_status()

            response_data = response.json()
        except requests.exceptions.ConnectionError:
            raise UnresponsiveServer('Unable to connect to server -please inform admin')
        except requests.exceptions.Timeout:
            raise UnresponsiveServer('Timeout while trying to send request - please inform admin')
        except json.JSONDecodeError:
            raise UnresponsiveServer('Unable to decode response - please inform admin')

    if not verify_signature(response=response):
        raise InvalidSignatureError("Unable to verify the identity of our remote server cannot continue - please inform admin")

    return jsonify(response_data)
