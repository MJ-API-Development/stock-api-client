
from flask import Blueprint
from src.routes.authentication.routes import auth_required

apikeys_route = Blueprint("apikeys", __name__)


@apikeys_route.route('/regenerate-api-key', methods=['POST'])
@auth_required
def regenerate_api_key():
    """
        will recreate te api keys for user
    :return:
    """
    pass
