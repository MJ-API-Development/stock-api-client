from celery import Celery
from flask import Flask, render_template, Blueprint
from flask_mail import Mail, Message
from src.config.config import config_instance
from src.main import mail

# Initialize Celery
celery = Celery('EOD-MAILER', broker=config_instance().CELERY_SETTINGS.CELERY_BROKER_URL)
send_mail_route = Blueprint('send_mail', __name__)

@celery.task
def send_email(subject, recipients, template, context):
    msg = Message(subject, recipients=recipients)
    msg.html = render_template(template, context=context)
    mail.send(msg)


@send_mail_route.route('/')
def index():
    send_email.apply_async(
        args=['Subject', ['recipient_email@example.com'], 'email_template.html', {'name': 'John Doe'}],
        countdown=60  # send the email in 60 seconds
    )
    return 'Email scheduled for sending in 60 seconds!'


if __name__ == '__main__':

    app.run()
