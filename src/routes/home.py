from flask import Blueprint, render_template, request, jsonify

home_route = Blueprint('home', __name__)


@home_route.route('/')
def home():
    return render_template('index.html', BASE_URL="eod-stock-api.site")


@home_route.route('/feedback', methods=['GET', 'POST'])
def form_handler():
    print(f"form submitted : {request.get_json()}")
    return jsonify(dict(status="Successfully submitted your subscription request",
                        message="We sent you an activation email please activate your subscription by clicking on the activate link "))

