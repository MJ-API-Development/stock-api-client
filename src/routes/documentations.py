import functools
import json
import os

import markdown
import requests
from flask import Blueprint, render_template, request, make_response

from src.routes.authentication.routes import user_details

docs_route = Blueprint('docs', __name__)


@docs_route.context_processor
def inject_specifications() -> dict[str, str]:
    static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    json_path = os.path.join(static_path, 'spec.json')

    with open(json_path, "r") as f:
        file_contents = f.read()
    return dict(json_data=file_contents)


# @functools.cache
def documentations_routes(params: dict[str, str]) -> dict:
    """
        will return a map of paths
    :param params:
    :return:
    """
    user_data = params.get('user_data')
    path = params.get('path')
    context = dict(user_data=user_data, BASE_URL="https://client.eod-stock-api.site")
    _index = render_template('docs/docs.html', **context)
    _routes = {
        'eod': render_template('docs/eod.html', **context),
        'exchanges': render_template('docs/exchanges.html', **context),
        'fundamentals': render_template('docs/fundamentals.html', **context),
        'financial-news': render_template('docs/financial_news.html', **context),
        'sentiment': render_template('docs/sentiment.html', **context),
        'stocks': render_template('docs/stocks.html', **context),
        'options': render_template('docs/options.html', **context),
        'playground': render_template('docs/playground.html', **context)
    }
    return _routes.get(path, _index)


@docs_route.route('/redoc', methods=['GET'])
def redoc():
    """

    :return:
    """
    # Replace "http://gateway.eod-stock-api.site" with the URL of your subdomain
    url = "https://gateway.eod-stock-api.site" + request.full_path
    response = requests.get(url)
    return response.content


@docs_route.route('/openapi.json', methods=['GET'])
def openapi_json():
    """

    :return:
    """
    # Replace "http://gateway.eod-stock-api.site" with the URL of your subdomain
    url = "https://gateway.eod-stock-api.site/open-api"
    openapi_data = requests.get(url)
    response = make_response(openapi_data.json(), 200)
    response.headers["Content-Type"] = "application/json"
    return response


@docs_route.route('/openapi', methods=['GET'])
def openapi_html():
    """

    :return:
    """
    # Replace "http://gateway.eod-stock-api.site" with the URL of your subdomain
    url = "https://gateway.eod-stock-api.site/open-api"
    openapi_data = requests.get(url)
    json_spec = json.dumps(openapi_data.json())

    context = dict(**inject_specifications(), BASE_URL="https://client.eod-stock-api.site")

    return render_template('docs/docs-openapi.html', **context)


@docs_route.route('/github-docs', methods=['GET'])
def github_docs():
    url = "https://raw.githubusercontent.com/MJ-API-Development/Intelligent-EOD-Stock-Financial-News-API/main/README.md"
    response = requests.get(url)
    html_content = markdown.markdown(response.content.decode('utf-8'))
    context = dict(document=html_content, BASE_URL="https://client.eod-stock-api.site")
    return render_template('docs/github-docs.html', **context)


@docs_route.route('/docs/<string:path>', methods=['GET', 'POST'])
@user_details
def documentations(user_data: dict[str, str], path: str):
    """

    :param user_data: user_data for the logged in user
    :param path: path to the correct documentation
    :return:
    """
    try:
        params = dict(user_data=user_data, path=path)
        return documentations_routes(params=params)
    except KeyError:
        # raise a proper HTTP Error for invalid route
        pass
