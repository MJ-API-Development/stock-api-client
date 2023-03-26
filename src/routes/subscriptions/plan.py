from flask import Blueprint, render_template, redirect, request, jsonify, request
import requests
from src.config import config_instance
from src.routes.authentication.routes import get_headers

plan_routes = Blueprint('plan', __name__)


def get_plan_details(plan_id: str) -> dict:
    """
        **get_plan_details**
            obtain plan details using plan_id
    :param plan_id:
    :return:
    """
    base_url: str = config_instance().GATEWAY_SETTINGS.BASE_URL
    endpoint: str = f"{base_url}/_admin/plan/{plan_id}"
    data: dict[str, str] = {'plan_id': plan_id}
    headers = get_headers(user_data=data)

    # Make a GET request with plan_id in the body as a dict
    response = requests.get(endpoint, headers=headers, json=data)

    # Check if the request was successful and return the response body as a dict
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        # Handle errors
        response.raise_for_status()


def get_user_data(uuid: str) -> dict:
    """
        given uuid obtain user details from the gateway server
    :param uuid:
    :return:
    """
    base_url: str = config_instance().GATEWAY_SETTINGS.BASE_URL
    endpoint: str = f"{base_url}/user/{uuid}"
    data = dict(uuid=uuid)
    headers = get_headers(user_data=data)

    # Make a GET request with UUID in the endpoint URL
    response = requests.get(endpoint, headers=headers)

    # Check if the request was successful and return the response body as a dict
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        # Handle errors
        response.raise_for_status()


def get_paypal_settings(uuid: str) -> dict:
    """
    Given UUID obtain PayPal settings from the gateway server.
    :param uuid: UUID of the user.
    :return: PayPal settings as a dict.
    """
    # Get gateway server endpoint URL and headers
    base_url = config_instance().GATEWAY_SETTINGS.BASE_URL
    endpoint = f"{base_url}/paypal/settings/{uuid}"
    data = dict(uuid=uuid)
    headers = get_headers(user_data=data)

    # Make a GET request to the endpoint with the headers
    response = requests.get(endpoint, headers=headers)

    # Check if the request was successful and return the response body as a dict
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        # Handle errors
        response.raise_for_status()


@plan_routes.route('/plan-subscription/<string:plan_id>.<string:uuid>', methods=["GET"])
def plan_subscription(plan_id: str, uuid: str):
    """
        this endpoint will be called by the front page to get details
        about the subscription plan
    :param plan_id:
    :param uuid:
    :return:
    """
    if not plan_id:
        return redirect('/')

    plan = get_plan_details(plan_id)
    user_data = get_user_data(uuid=uuid)
    paypal_settings = get_paypal_settings(uuid=uuid)

    context = dict(plan=plan, user_data=user_data, paypal_settings=paypal_settings)
    return render_template('dashboard/plan_subscriptions.html', context=context)


@plan_routes.route('/subscribe', methods=['POST'])
def subscribe():
    subscription_data: dict[str, str] = request.get_json()

    # Handle subscription process using PayPal API
    return jsonify({'success': True})
