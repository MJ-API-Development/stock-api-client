import random
import string
from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, current_app

from src.databases.models.sql import mysql_instance
from src.databases.models.sql.contact import Contacts
from src.logger import init_logger


home_logger = init_logger("home_route")


def get_api_key():
    return create_id(64)


def get_paypal_address():
    return "addrress@example.com"


def generate_key_api():
    return create_id(64)


home_route = Blueprint('home', __name__)

_char_set = string.ascii_lowercase + string.ascii_uppercase + string.digits


def create_id(size: int = 16, chars: str = _char_set) -> str:
    """
        **create_id**
            create a random unique id for use as indexes in Database Models

    :param size: size of string - leave as default if you can
    :param chars: character set to create Unique identifier from leave as default
    :return: uuid -> randomly generated id
    """
    return ''.join(random.choice(chars) for _ in range(size))


@home_route.route('/')
def home():
    return render_template('index.html', total_exchanges=73, BASE_URL="eod-stock-api.site")


@home_route.route('/account')
def account():
    api_key = get_api_key()
    paypal_address = get_paypal_address()
    return render_template('dashboard/account.html', api_key=api_key, BASE_URL="eod-stock-api.site")


@home_route.route('/regenerate_api_key')
def regenerate_api_key():
    pass


@home_route.route('/status')
def status():
    return render_template('dashboard/status.html', BASE_URL="eod-stock-api.site")


@home_route.route('/pricing')
def pricing():
    return render_template('index.html', BASE_URL="eod-stock-api.site")


@home_route.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        context = dict(BASE_URL="eod-stock-api.site")
        return render_template('dashboard/contact.html', **context)
    else:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        message = data.get("message")
        # TODO handle the issue where the user has logged in
        contact_dict = dict(name=name, email=email, message=message, contact_id=create_id())
        with mysql_instance.get_session() as _session:
            Contacts.create_if_not_exists()
            _session.add(Contacts(**{**contact_dict, "timestamp": datetime.now().timestamp()}))
            _session.commit()

        return jsonify(dict(status=True, message="We have received your message and will get back to you soon..."))
