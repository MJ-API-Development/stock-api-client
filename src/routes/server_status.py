
import requests
from flask import Blueprint, jsonify
from requests.exceptions import ConnectionError, ConnectTimeout
from src.logger import init_logger
from src.routes.authentication.routes import user_details

status_bp = Blueprint('status', __name__)
status_logger = init_logger('status_logger')


@status_bp.get('/status')
def get_status():
    """
    Public access point no need for authentication
        check if all services and server are available and list the details
    :return:
    """
    status_logger.info("are we even getting status")
    response = requests.get(url="https://gateway.eod-stock-api.site/_ah/warmup")
    server_status = dict(Gateway='offline',
                         API_Master='offline',
                         API_Slave='offline')

    if response.status_code == 200 and response.headers.get('Content-Type') == 'application/json':
        payload = response.json()['payload']
        server_status = dict(Gateway=payload.get('Gateway'),
                             API_Master=payload.get('API_Master'),
                             API_Slave=payload.get('API_Slave'))

    payload = dict(status=True, payload=server_status, message='successfully retrieved status of all the servers')

    return jsonify(payload), 200

