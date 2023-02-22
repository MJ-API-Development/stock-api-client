
import random
import string
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session, abort, current_app

from src.databases.models.sql import mysql_instance
from src.databases.models.sql.contact import Contacts
from src.logger import init_logger
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
            print(f"Checking CRF TOKEN FROM SESSION : {self.session.get('csrf_token')}")
            print(f"Token from form {request.get_json().get('csrf_token')}")
            if not csrf_token or (csrf_token != request.get_json().get("csrf_token")):
                abort(400, 'Invalid CSRF token')


csrf_instance = CSRFProtect(current_app)