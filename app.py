import logging

from flask import Flask, send_from_directory
from flask_cors import CORS

from src.config.config import config_instance, is_development
from src.main import create_app

app: Flask = create_app(config=config_instance())

app.config['MIME_TYPES'] = {
    'js': 'application/javascript',
    'css': 'text/css',
    'woff': 'font/woff',
    'woff2': 'font/woff2'
}

_origin: str = config_instance().SERVER_NAME
CORS(app, resources={r"/*": {"origins": _origin}})


@app.route('/sw.js', methods=['GET'])
def sw():
    """
        service worker js
    :return:
    """
    print('Waiting for for service worker ')
    return send_from_directory('static', 'js/sw.js')


@app.route('/sitemap_index.xml', methods=['GET'])
def sitemap_index():
    """
        sitemap index
    :return:
    """
    return send_from_directory('static', 'sitemap_index.xml')


app.logger.setLevel(logging.INFO)

if __name__ == '__main__':
    if is_development():
        app.run(debug=True, use_reloader=True, host="127.0.0.1", port=8081)
    else:
        app.run(debug=True, use_reloader=True, host="0.0.0.0", port=8081)
