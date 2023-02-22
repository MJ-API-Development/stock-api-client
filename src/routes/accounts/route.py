import random
import string
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session, abort, current_app

from src.databases.models.sql import mysql_instance
from src.databases.models.sql.account import Account
from src.logger import init_logger
from src.mail.send_emails import schedule_mail
from secrets import token_hex

account_bp = Blueprint('account', __name__)
account_logger = init_logger("account_route")


@account_bp.route('/account/<string:uuid>', methods=["GET"])
async def get_account(uuid: str):
    """

    :param uuid:
    :return:
    """
    with mysql_instance.get_session() as session:
        account_inst = await Account.get_by_uuid(uuid=uuid, session=session)

    if not account_inst:
        message: str = "This account does not exist"
        return render_template('dashboard/account.html', message=message, account={})

    message: str = "Account found"
    return render_template('dashboard/account.html', message=message, account=account_inst.to_dict())


@account_bp.route('/auth/login', methods=["GET", "POST"])
def auth():
    """
        user authentication
    :return:
    """
    message: str = "Successfully logged in"
    account_inst = Account()
    return render_template('dashboard/account.html', message=message, account=account_inst.to_dict())

