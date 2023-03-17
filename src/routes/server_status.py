
import requests
from flask import Blueprint, jsonify
from requests.exceptions import ConnectionError, ConnectTimeout
from src.logger import init_logger

status_bp = Blueprint('status', __name__)
status_logger = init_logger('status_logger')


@status_bp.get('/status')
def get_status():
    """
        check if all services and server are available and list the details
    :return:
    """
    status_logger.info("are we even getting status")
    try:
        server_1 = requests.get(url="https://www.eod-stock-api.site/_ah/warmup")

    except ConnectTimeout:
        server_1 = "Server busy"
        # server busy
    except ConnectionError:
        server_1 = "Server Unavailable"
        # server not available

    try:
        server_2 = requests.get(url="https://cron.eod-stock-api.site/_ah/warmup")
    except ConnectTimeout:
        server_2 = "Server busy"
        # server busy
    except ConnectionError:
        server_2 = "Server Unavailable"
        # server not available
    try:
        gateway_status = requests.get(url="https://gateway.eod-stock-api.site/_ah/warmup")
    except ConnectTimeout:
        gateway_status = "Server busy"
        # server busy
    except ConnectionError:
        gateway_status = "Server Unavailable"
        # server not available

    server_status = dict(server_1=server_1,
                         server_2=server_2,
                         gateway=gateway_status)

    service_availability = dict()
    _payload = dict(server_status=server_status, services=service_availability)

    payload = dict(status=True, payload=_payload, message='successfully retrieved status of all the servers')

    return jsonify(payload), 200

