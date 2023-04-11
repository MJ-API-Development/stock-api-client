from flask import Blueprint, render_template, send_from_directory

from src.routes.authentication.routes import user_details

home_route = Blueprint('home', __name__)


@home_route.route('/')
@user_details
def home(user_data: dict[str, str]):
    context = dict(user_data=user_data, total_exchanges=75, BASE_URL="eod-stock-api.site")
    return render_template('index.html', **context)


@home_route.route('/status')
@user_details
def status(user_data: dict[str, str]):
    context = dict(user_data=user_data, BASE_URL="eod-stock-api.site")
    return render_template('dashboard/status.html', **context)


@home_route.route('/pricing')
@user_details
def pricing(user_data: dict[str, str]):
    context = dict(user_data=user_data, BASE_URL="eod-stock-api.site")
    return render_template('index.html', **context)


@home_route.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')


@home_route.route('/Robots.txt')
def _robots():
    return send_from_directory('static', 'robots.txt')


@home_route.route('/terms')
@user_details
def terms_of_use(user_data: dict[str, str]):
    context = dict(user_data=user_data, BASE_URL="eod-stock-api.site")
    return render_template('terms.html', **context)


@home_route.route('/privacy')
@user_details
def privacy_policy(user_data: dict[str, str]):
    context = dict(user_data=user_data)
    return render_template('privacy.html', **context)

