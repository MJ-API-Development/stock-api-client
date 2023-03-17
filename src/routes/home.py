from flask import Blueprint, render_template

home_route = Blueprint('home', __name__)


@home_route.route('/')
def home():
    return render_template('index.html', total_exchanges=73, BASE_URL="eod-stock-api.site")


@home_route.route('/status')
def status():
    return render_template('dashboard/status.html', BASE_URL="eod-stock-api.site")


@home_route.route('/pricing')
def pricing():
    return render_template('index.html', BASE_URL="eod-stock-api.site")
