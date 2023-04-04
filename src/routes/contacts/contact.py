import json
import time

import flask
import requests
from flask import Blueprint, render_template, request, abort, jsonify
from src.config import config_instance
from src.databases.models.schemas.contacts import Contacts
from src.exceptions import BadResponseError
from src.routes.authentication.routes import get_headers, UnresponsiveServer, verify_signature, user_details
from src.utils import create_id

contact_route = Blueprint("contact", __name__)

bouncer = {}


def get_bouncer_key(headers: dict[str, str, tuple[str, str]]) -> str:
    ip = headers.get('cf-connecting-ip') or headers.get('x-forwarded-for')
    return ip.split(',')[0] if ip else request.remote_addr


def debounce_requests() -> None:
    """simply debounce too many requests being made from the same ip addresses"""
    key = get_bouncer_key(headers=request.headers)
    request_time = time.monotonic()
    if bouncer.get(key) is not None:
        remainder = request_time - bouncer.get(key)
        if remainder < 1:
            abort(429)
        bouncer[key] = request_time


# noinspection PyShadowingNames
@contact_route.route('/contact', methods=['GET'])
@user_details
def contact(user_data: dict[str, str]) -> flask.Response:
    """
    TODO - convert to a Ticket System
    :return: flask.Response
    """
    context = dict(BASE_URL="eod-stock-api.site", user_data=user_data)
    return render_template('dashboard/contact.html', **context)


@contact_route.route('/contact', methods=['POST'])
@user_details
def create_contact(user_data: dict[str, str]) -> flask.Response:
    # TODO Catch click bouncing here
    debounce_requests()
    contact_instance: Contacts = Contacts(**request.get_json())
    contact_instance.contact_id = create_id()

    if contact_instance.uuid is None:
        contact_instance.uuid = user_data.get('uuid', create_id())

    if (contact_instance.email is None) and user_data.get('email'):
        contact_instance.email = user_data.get('email')
    else:
        return jsonify(dict(message='Email is required, or Login'))

    if (contact_instance.name is None) and user_data.get('first_name'):
        contact_instance.name = user_data.get('first_name')
    else:
        return jsonify(dict(message='Name is required, or Login'))

    contact_instance.contact_id = create_id()

    base_url: str = config_instance().GATEWAY_SETTINGS.BASE_URL
    url: str = f"{base_url}/_admin/contacts"
    _headers: dict[str, str] = get_headers(user_data=contact_instance.dict())

    with requests.Session() as request_session:
        try:
            response: requests.Response = request_session.post(url=url, json=contact_instance.dict(),
                                                               headers=_headers)
            response.raise_for_status()
            response_data = response.json()
        except requests.exceptions.ConnectionError:
            raise UnresponsiveServer()
        except requests.exceptions.Timeout:
            raise UnresponsiveServer()
        except json.JSONDecodeError:
            raise BadResponseError()

    if response.status_code not in [200, 201]:
        raise UnresponsiveServer()

    if not verify_signature(response=response):
        abort(401)

    return jsonify(response_data)

