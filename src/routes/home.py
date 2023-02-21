import random
import string
from flask import Blueprint, render_template, request, jsonify, session, abort, current_app

from src.mail.send_emails import schedule_mail
from secrets import token_hex


class CSRFProtect:
    def __init__(self, app=current_app):
        self.app = app
        self.session = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self.check_csrf_token)

    def generate_csrf_token(self):
        csrf_token = token_hex(32)
        self.session['csrf_token'] = csrf_token
        print(f"Created CRF TOKEN : {csrf_token}")
        return csrf_token

    def check_csrf_token(self):
        if request.method == 'POST':
            csrf_token = self.session.get('csrf_token', None)
            print(f"Checking CRF TOKEN : {csrf_token}")
            print(f"Token from form {request.get_json().get('csrf_token')}")
            if not csrf_token or (csrf_token != request.get_json().get("csrf_token")):
                abort(400, 'Invalid CSRF token')


home_route = Blueprint('home', __name__)

_char_set = string.ascii_lowercase + string.ascii_uppercase + string.digits

csrf = CSRFProtect(current_app)


def create_id(size: int = 16, chars: str = _char_set) -> str:
    """
        **create_id**
            create a random unique id for use as indexes in Database Models

    :param size: size of string - leave as default if you can
    :param chars: character set to create Unique identifier from leave as default
    :return: uuid -> randomly generated id
    """
    return ''.join(random.choice(chars) for _ in range(size))


@home_route.route('/')
def home():
    return render_template('index.html', total_exchanges=73, BASE_URL="eod-stock-api.site")


@home_route.route('/login')
def login():
    return render_template('login.html', BASE_URL="eod-stock-api.site")


@home_route.route('/account')
def account():
    return render_template('dashboard/account.html', BASE_URL="eod-stock-api.site")


@home_route.route('/status')
def status():
    return render_template('dashboard/status.html', BASE_URL="eod-stock-api.site")


@home_route.route('/pricing')
def pricing():
    return render_template('index.html', BASE_URL="eod-stock-api.site")


@home_route.route('/contact', methods=['GET', 'POST'])
def contact():

    if request.method == 'GET':
        context = dict(csrf_token=csrf.generate_csrf_token(), BASE_URL="eod-stock-api.site")
        return render_template('dashboard/contact.html', **context)
    else:
        data = request.get_json()
        print(data)

        return jsonify(request.get_json())


@home_route.route('/feedback', methods=['GET', 'POST'])
def form_handler():
    """
        def schedule_mail(subject: str, name: str, template: str,  recipient: list[str]):
    :return:
    """
    response = schedule_mail(subject="EOD-Stock-API Activation Email", name=request.get_json().get('name'),
                             template='emails/mailing_list.html', recipient=[request.get_json().get('email')])
    print(f"form submitted : {request.get_json()} , {response}")

    return jsonify(dict(status="Successfully submitted your subscription request",
                        message="We sent you an activation email please activate your subscription by clicking on the activate link "))
