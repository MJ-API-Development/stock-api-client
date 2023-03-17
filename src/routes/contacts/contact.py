import requests
from flask import Blueprint, render_template, request, abort, jsonify

from src.config import config_instance
from src.databases.models.schemas.contacts import Contacts
from src.routes.authentication.routes import get_headers, UnresponsiveServer, verify_signature
from src.utils import create_id

contact_route = Blueprint("contact", __name__)


@contact_route.route('/contact', methods=['GET', 'POST'])
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
        contact_instance = Contacts(**contact_dict)
        base_url = config_instance().GATEWAY_SETTINGS.BASE_URL
        url: str = f"{base_url}/_admin/contacts"
        _headers = get_headers(user_data=contact_instance.dict())
        response = requests.post(url=url, json=contact_instance.dict(), headers=_headers)

        if response.status_code not in [200, 201, 401]:
            raise UnresponsiveServer()

        if not verify_signature(response=response):
            abort(401)
        response_data = response.json()

        return jsonify(response_data)
