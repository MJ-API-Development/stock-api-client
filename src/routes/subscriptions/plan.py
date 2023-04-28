from json import JSONDecodeError
import json
from typing import Callable

import flask
from requests.exceptions import RequestException, ConnectionError
import requests
from flask import Blueprint, render_template, redirect, jsonify, request, abort

from src.cache import cached
from src.config import config_instance
from src.databases.models.schemas.subscriptions import PayPalSubscriptionModel, PlanModels
from src.exceptions import UnresponsiveServer, ServerInternalError
from src.logger import init_logger
from src.routes.authentication.handlers import auth_required, user_details
from src.routes.authentication.routes import get_headers, verify_signature
from src.utils import create_id

plan_routes = Blueprint('plan', __name__)
plan_logger = init_logger('plan_logger')

paypal_settings_cache: dict[str, dict[str, str | int]] = {}
cache_get_paypal_settings: Callable = paypal_settings_cache.get


@cached
def get_all_plans() -> list[dict[str, str]]:
    """
        will fetch all plans from the gateway
    :return:
    """
    # Creating endpoint URL
    base_url: str = config_instance().GATEWAY_SETTINGS.BASE_URL
    endpoint: str = f"{base_url}/_admin/plans"

    # Nonce for creating Authorization Header
    data: dict[str, str] = {'nonce': create_id()}
    headers: dict[str, str | int] = get_headers(user_data=data)

    with requests.Session() as request_session:
        try:
            response: requests.Response = request_session.get(endpoint, headers=headers, json=data)
            response.raise_for_status()
            all_plan_details: list[dict[str, str | int]] = response.json()
            # Check if the request was successful and return the response body as a dict
        except (RequestException, ConnectionError) as e:
            plan_logger.exception(f"Error making requests to backend : {endpoint}")
            raise UnresponsiveServer() from e
        except JSONDecodeError as e:
            plan_logger.exception(f"Error decoding paypal settings : {response.text}")
            raise ServerInternalError() from e

    if not verify_signature(response=response):
        abort(401)

    return all_plan_details


@cached
def get_plan_details(plan_id: str) -> dict[str, str | int]:
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
    with requests.Session() as request_session:
        try:
            # Make a GET request with plan_id in the body as a dict
            response = request_session.get(endpoint, headers=headers, json=data)
            response.raise_for_status()
            _plan_details: dict[str, str | int] = response.json()
            # Check if the request was successful and return the response body as a dict
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
            plan_logger.exception(f"Error making requests to backend : {endpoint}")
            raise UnresponsiveServer() from e
        except json.JSONDecodeError as e:
            plan_logger.exception(f"Error decoding paypal settings : {response.text}")
            raise ServerInternalError() from e

    if not verify_signature(response=response):
        abort(401)

    return _plan_details


@cached
def get_user_data(uuid: str) -> dict[str, str | int]:
    """
        given uuid obtain user details from the gateway server
    :param uuid:
    :return:
    """
    base_url: str = config_instance().GATEWAY_SETTINGS.BASE_URL
    endpoint: str = f"{base_url}/_admin/user/{uuid}"
    data: dict[str, str] = dict(uuid=uuid)
    headers: dict[str, str] = get_headers(user_data=data)
    with requests.Session() as request_session:
        try:
            # Make a GET request with UUID in the endpoint URL
            response = request_session.get(endpoint, headers=headers)
            response.raise_for_status()
            user_data: dict[str, str | int] = response.json()
        except (RequestException, ConnectionError) as e:
            plan_logger.exception(f"Error making requests to backend : {endpoint}")
            raise UnresponsiveServer() from e
        except JSONDecodeError as e:
            plan_logger.exception(f"Error decoding paypal settings: {response.text}")
            raise ServerInternalError() from e

    if not verify_signature(response=response):
        abort(401)

    return user_data


@cached
def get_paypal_settings(uuid: str) -> dict[str, str | int]:
    """
    Given UUID obtain PayPal settings from the gateway server.
    :param uuid: UUID of the user.
    :return: PayPal settings as a dict.
    """
    base_url: str = config_instance().GATEWAY_SETTINGS.BASE_URL
    endpoint: str = f"{base_url}/_admin/paypal/settings/{uuid}"
    headers: dict[str, str | int] = get_headers(user_data=dict(uuid=uuid))

    with requests.Session() as request_session:
        try:
            response: requests.Response = request_session.get(url=endpoint, headers=headers)
            # plan_logger.info(f"PayPal settings : {response.headers['Content-Type']}")
            response.raise_for_status()
            paypal_settings: dict[str, str | int] = response.json()

        except (RequestException, ConnectionError) as e:
            plan_logger.exception(f"Exception - get_paypal_settings: {e}")
            raise UnresponsiveServer() from e
        except JSONDecodeError as e:
            plan_logger.exception(f"Error decoding paypal settings: {e}")
            raise ServerInternalError() from e

    if not verify_signature(response=response):
        abort(401)

    return paypal_settings


@plan_routes.route('/plan-subscription/<string:plan_id>', methods=["GET"])
@user_details
def plan_subscription(user_data: dict[str, str], plan_id: str) -> flask.Response:
    """
        this endpoint will be called by the front page to get details
        about the subscription plan
    :param user_data:
    :param plan_id:
    :return:
    """
    if user_data:
        uuid = user_data.get('uuid')
    else:
        uuid = create_id()

    if request.method.casefold() == "get":
        if not plan_id:
            return redirect('/')

        plan: dict[str, str | int] = get_plan_details(plan_id)

        _paypal_settings: dict[str, dict[str, str | int]] = cache_get_paypal_settings('settings', None)
        if _paypal_settings is None:
            _paypal_settings = get_paypal_settings(uuid=uuid)
            paypal_settings_cache['settings'] = _paypal_settings

        context: dict[str, dict[str, str]] = dict(plan=plan.get("payload", {}),
                                                  user_data=user_data,
                                                  paypal_settings=_paypal_settings)

        return render_template('dashboard/plan_subscriptions.html', **context)


# noinspection PyUnusedLocal
@plan_routes.route('/plan-details/<string:plan_id>', methods=["GET"])
@auth_required
def plan_details(user_data: dict[str, str], plan_id: str, uuid: str) -> flask.Response:
    """
        this endpoint will be called by the front page to get details
        about the subscription plan
    :param plan_id:
    :param uuid:
    :param user_data:
    :return: flask.Response
    """
    return jsonify(get_plan_details(plan_id=plan_id))


@plan_routes.route('/subscribe', methods=['POST'])
@auth_required
def subscribe(user_data: dict[str, str]) -> flask.Response:
    """
        **called to actually create a subscription
        this is after a person has already approved the subscription on paypal
    :return: flask.Response
    """
    # subscription_data: dict[str, str] = request.get_json()
    # subscription_data = dict(uuid=uuid, plan_id=plan_id, payment_method="paypal")
    paypal_data: dict[str, str | int] = request.get_json()
    paypal_subscription: PayPalSubscriptionModel = PayPalSubscriptionModel(**paypal_data)

    base_url: str = config_instance().GATEWAY_SETTINGS.BASE_URL
    endpoint: str = f"{base_url}/_admin/subscriptions"
    _headers: dict[str, str] = get_headers(user_data=paypal_subscription.dict())

    with requests.Session() as request_session:
        try:
            response = request_session.post(endpoint, json=paypal_subscription.dict(), headers=_headers)
            response.raise_for_status()
            json_data: dict[str, str | int] = response.json()

        except (RequestException, ConnectionError) as e:
            raise UnresponsiveServer() from e

        except JSONDecodeError as e:
            plan_logger.exception("Error decoding paypal settings")
            raise ServerInternalError() from e

    if not verify_signature(response=response):
        abort(401)

    return json_data


@plan_routes.route('/plans-all', methods=["GET"])
@cached
def plans_all() -> flask.Response:
    """
        this endpoint will be called by the front page to get details
        about the subscription plan
    :return:
    """
    return jsonify(get_all_plans())


def select_plan_by_name(plans_models: list[PlanModels], plan_name: str) -> str:
    for plan in plans_models:
        if plan.plan_name.casefold() == plan_name.casefold():
            return plan
    return ''


@plan_routes.route('/plan-descriptions/<string:plan_name>', methods=['GET'])
@user_details
def plan_by_name(user_data: dict[str, str], plan_name: str):

    _plans_models: dict[str, str | dict[str, str]] = get_all_plans()
    plans_models = [PlanModels.parse_obj(plan_dict) for plan_dict in _plans_models.get('payload')]

    plan: PlanModels = select_plan_by_name(plans_models=plans_models, plan_name=plan_name)

    uuid: str = user_data.get('uuid', create_id())

    _paypal_settings: dict[str, dict[str, str | int]] = cache_get_paypal_settings('settings', None)
    if _paypal_settings is None:
        _paypal_settings = get_paypal_settings(uuid=uuid)
        paypal_settings_cache['settings'] = _paypal_settings

    context: dict[str, dict[str, str]] = dict(plan=plan.dict(),
                                              user_data=user_data,
                                              paypal_settings=_paypal_settings)

    return render_template('dashboard/plan_subscriptions.html', **context)

