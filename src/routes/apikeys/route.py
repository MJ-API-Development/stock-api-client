
from flask import Blueprint

apikeys_route = Blueprint("apikeys", __name__)


@apikeys_route.route('/regenerate_api_key')
def regenerate_api_key():
    pass
