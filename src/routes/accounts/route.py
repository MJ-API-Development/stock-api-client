import json

from flask import Blueprint, render_template, request, session, redirect, url_for

from src.databases.models.sql import mysql_instance
from src.databases.models.sql.account import Account
from src.logger import init_logger

account_bp = Blueprint('account', __name__)
account_logger = init_logger("account_route")


@account_bp.route('/login', methods=['GET'])
def login():
    context = dict(BASE_URL="eod-stock-api.site")
    return render_template('login.html', **context)


@account_bp.route('/account/<string:uuid>', methods=["GET"])
async def get_account(uuid: str):
    """

    :param uuid:
    :return:
    """
    with mysql_instance.get_session() as _session:
        account_inst = await Account.get_by_uuid(uuid=uuid, session=_session)

    if not account_inst:
        message: str = "This account does not exist"
        return render_template('dashboard/account.html', message=message, account={})

    message: str = "Account found"
    context = dict(
        account=account_inst.to_dict(),
        message=message,
        BASE_URL="eod-stock-api.site")

    return render_template('dashboard/account.html', **context)


@account_bp.route('/auth/login', methods=["POST"])
async def auth():
    """
        user authentication
    :return:
    """
    data = request.get_data(parse_form_data=True)
    data = json.loads(data)
    Account.create_if_not_exists()
    with mysql_instance.get_session() as _session:
        username = data.get('username')
        password = data.get('password')
        logged_in_user = await Account.login(username=username, password=password, session=_session)
        account_logger.info(f"Logged in User {logged_in_user}")

    if logged_in_user:
        session["user"] = logged_in_user.to_dict()
        return redirect(url_for('account.get_account'))

    message: str = "Successfully logged in"
    account_inst = Account()
    context = dict(account=account_inst.to_dict(),
                   message=message,
                   BASE_URL="eod-stock-api.site")
    return render_template('dashboard/account.html', **context)
