import random
import string

from flask import Blueprint, render_template

from src.logger import init_logger
from src.utils import get_api_key, get_paypal_address

home_logger = init_logger("home_route")

home_route = Blueprint('home', __name__)


@home_route.route('/')
def home():
    return render_template('index.html', total_exchanges=73, BASE_URL="eod-stock-api.site")


@home_route.route('/regenerate_api_key')
def regenerate_api_key():
    pass


@home_route.route('/status')
def status():
    return render_template('dashboard/status.html', BASE_URL="eod-stock-api.site")


@home_route.route('/pricing')
def pricing():
    return render_template('index.html', BASE_URL="eod-stock-api.site")
