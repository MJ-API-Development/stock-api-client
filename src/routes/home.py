import functools

from flask import Blueprint, render_template, Request, request, send_from_directory

from src.routes.authentication.routes import user_details

home_route = Blueprint('home', __name__)


@home_route.route('/')
@user_details
def home(user_data: dict[str, str]):
    if user_data is None:
        user_data = {}
    context = dict(user_data=user_data, total_exchanges=75, BASE_URL="client.eod-stock-api.site")
    return render_template('index.html', **context)


@home_route.route('/status')
@functools.lru_cache(maxsize=128)
@user_details
def status(user_data: dict[str, str]):
    if user_data is None:
        user_data = {}

    context = dict(user_data=user_data, BASE_URL="eod-stock-api.site")
    return render_template('dashboard/status.html', **context)


@home_route.route('/pricing')
@functools.lru_cache(maxsize=128)
@user_details
def pricing(user_data: dict[str, str]):
    if user_data is None:
        user_data = {}

    context = dict(user_data=user_data, BASE_URL="eod-stock-api.site")
    return render_template('index.html', **context)


@home_route.route('/robots.txt')
def static_from_root():
    return send_from_directory(home_route.static_folder, request.path[1:])


@home_route.route('/terms')
def terms_of_use():
    return render_template('terms.html')


@home_route.route('/privacy')
def privacy_policy():
    return render_template('privacy.html')


