from flask import Blueprint, render_template, request, jsonify

from src.mail.send_emails import schedule_mail

home_route = Blueprint('home', __name__)


@home_route.route('/')
def home():
    return render_template('index.html', BASE_URL="eod-stock-api.site")


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
