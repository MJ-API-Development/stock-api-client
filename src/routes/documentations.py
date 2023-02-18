import functools

from flask import Blueprint, render_template, request, jsonify

from src.mail.send_emails import schedule_mail

docs_route = Blueprint('docs', __name__)


@functools.cache
def documentations_routes(path: str) -> dict:
    """
        will return a map of paths
    :param path:
    :return:
    """
    _routes = {
        'eod': render_template('docs/eod.html', BASE_URL="eod-stock-api.site"),
        'exchanges': render_template('docs/exchanges.html', BASE_URL="eod-stock-api.site"),
        'fundamentals': render_template('docs/fundamentals.html', BASE_URL="eod-stock-api.site"),
        'financial-news': render_template('docs/financial_news.html', BASE_URL="eod-stock-api.site"),
        'sentiment': render_template('docs/sentiment.html', BASE_URL="eod-stock-api.site"),
        'stocks': render_template('docs/stocks.html', BASE_URL="eod-stock-api.site"),
        'options': render_template('docs/options.html', BASE_URL="eod-stock-api.site"),
        'playground': render_template('docs/playground.html', BASE_URL="eod-stock-api.site")
    }
    return _routes[path]


@docs_route.route('/docs/<string:path>', methods=['GET', 'POST'])
def documentations(path: str):
    """

    :param path:
    :return:
    """
    try:
        return documentations_routes(path=path)
    except KeyError:
        # raise a proper HTTP Error for invalid route
        pass

