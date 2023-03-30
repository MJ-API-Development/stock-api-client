
from flask import Blueprint

from src.routes.authentication.routes import auth_required

apikeys_route = Blueprint("apikeys", __name__)


@apikeys_route.route('/regenerate_api_key')
@auth_required
def regenerate_api_key():
    pass
