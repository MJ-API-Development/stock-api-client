import json

from flask import Blueprint, render_template, redirect, request, jsonify, request, abort
import requests
from src.config import config_instance
from src.exceptions import UnresponsiveServer, ServerInternalError
from src.logger import init_logger
from src.routes.authentication.routes import get_headers, verify_signature
from src.utils import create_id

plan_routes = Blueprint('plan', __name__)
plan_logger = init_logger('plan_logger')


def get_all_plans() -> list[dict[str, str]]:
    """

    :return:
    """
    base_url: str = config_instance().GATEWAY_SETTINGS.BASE_URL
    endpoint: str = f"{base_url}/_admin/plans"
    data: dict[str, str] = {'plan_id': create_id()}
    headers = get_headers(user_data=data)
    with requests.Session() as session:
        try:
            response = requests.get(endpoint, headers=headers, json=data)
            response.raise_for_status()
            json_data = response.json()
            # Check if the request was successful and return the response body as a dict
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
            plan_logger.exception(f"Error making requests to backend : {endpoint}")
            raise UnresponsiveServer() from e
        except json.JSONDecodeError as e:
            plan_logger.exception("Error decoding paypal settings")
            raise ServerInternalError() from e

    if not verify_signature(response=response):
        abort(401)

    return json_data


def get_plan_details(plan_id: str) -> dict:
    """
        **get_plan_details**
            obtain plan details using plan_id
    :param plan_id:
    :return:
    """
    base_url: str = config_instance().GATEWAY_SETTINGS.BASE_URL
    endpoint: str = f"{base_url}/_admin/plans/{plan_id}"
    data: dict[str, str] = {'plan_id': plan_id}
    headers = get_headers(user_data=data)
    with requests.Session() as session:
        try:
            # Make a GET request with plan_id in the body as a dict
            response = session.get(endpoint, headers=headers, json=data)
            response.raise_for_status()
            json_data = response.json()
            # Check if the request was successful and return the response body as a dict
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
            plan_logger.exception(f"Error making requests to backend : {endpoint}")
            raise UnresponsiveServer() from e
        except json.JSONDecodeError as e:
            plan_logger.exception("Error decoding paypal settings")
            raise ServerInternalError() from e

    if not verify_signature(response=response):
        abort(401)

    return json_data


def get_user_data(uuid: str) -> dict:
    """
        given uuid obtain user details from the gateway server
    :param uuid:
    :return:
    """
    base_url: str = config_instance().GATEWAY_SETTINGS.BASE_URL
    endpoint: str = f"{base_url}/_admin/user/{uuid}"
    data = dict(uuid=uuid)
    headers = get_headers(user_data=data)
    with requests.Session() as session:
        try:
            # Make a GET request with UUID in the endpoint URL
            response = session.get(endpoint, headers=headers)
            response.raise_for_status()
            json_data = response.json()
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
            plan_logger.exception(f"Error making requests to backend : {endpoint}")
            raise UnresponsiveServer() from e
        except json.JSONDecodeError as e:
            plan_logger.exception("Error decoding paypal settings")
            raise ServerInternalError() from e

    if not verify_signature(response=response):
        abort(401)

    return json_data


def get_paypal_settings(uuid: str) -> dict:
    """
    Given UUID obtain PayPal settings from the gateway server.
    :param uuid: UUID of the user.
    :return: PayPal settings as a dict.
    """
    base_url = config_instance().GATEWAY_SETTINGS.BASE_URL
    endpoint = f"{base_url}/_admin/paypal/settings/{uuid}"
    headers = get_headers(user_data=dict(uuid=uuid))

    with requests.Session() as session:
        try:
            response = session.get(endpoint, headers=headers)
            response.raise_for_status()
            json_data = response.json()
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
            raise UnresponsiveServer() from e
        except json.JSONDecodeError as e:
            plan_logger.exception("Error decoding paypal settings")
            raise ServerInternalError() from e

    if not verify_signature(response=response):
        abort(401)

    return json_data


@plan_routes.route('/plan-subscription/<string:plan_id>.<string:uuid>', methods=["GET", "POST"])
def plan_subscription(plan_id: str, uuid: str):
    """
        this endpoint will be called by the front page to get details
        about the subscription plan
    :param plan_id:
    :param uuid:
    :return:
    """
    if request.method.casefold() == "get":
        if not plan_id:
            return redirect('/')

        plan = get_plan_details(plan_id)
        user_data = get_user_data(uuid=uuid)
        paypal_settings = get_paypal_settings(uuid=uuid)
        context = dict(plan=plan.get('payload'), user_data=user_data.get("payload"), paypal_settings=paypal_settings)
        return render_template('dashboard/plan_subscriptions.html', **context)


# noinspection PyUnusedLocal
@plan_routes.route('/plan-details/<string:plan_id>.<string:uuid>', methods=["GET"])
def plan_details(plan_id: str, uuid: str):
    """
        this endpoint will be called by the front page to get details
        about the subscription plan
    :param plan_id:
    :param uuid:
    :return:
    """
    plan: dict[str, str] = get_plan_details(plan_id)
    return jsonify(plan)


@plan_routes.route('/plans-all', methods=["GET"])
def plans_all():
    """
        this endpoint will be called by the front page to get details
        about the subscription plan
    :return:
    """
    plan: dict[str, str] = get_all_plans()
    return jsonify(plan)


@plan_routes.route('/subscribe', methods=['POST'])
def subscribe():
    """
        **called to actually create a subscription
        this is after a person has already approved the subscription on paypal
    :return:
    """
    # subscription_data: dict[str, str] = request.get_json()
    # subscription_data = dict(uuid=uuid, plan_id=plan_id, payment_method="paypal")
    json_data = request.get_json()
    json_data.update(payment_method='paypal')

    base_url = config_instance().GATEWAY_SETTINGS.BASE_URL
    endpoint = f"{base_url}/_admin/subscriptions"
    headers = get_headers(user_data=json_data)

    with requests.Session() as session:
        try:
            response = session.post(endpoint, json=json_data, headers=headers)
            response.raise_for_status()
            json_data = response.json()
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
            raise UnresponsiveServer() from e
        except json.JSONDecodeError as e:
            plan_logger.exception("Error decoding paypal settings")
            raise ServerInternalError() from e

    if not verify_signature(response=response):
        abort(401)

    return json_data
