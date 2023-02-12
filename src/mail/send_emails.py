
from flask import Flask, render_template, Blueprint
from flask_mail import Mail, Message
from src.main import mail
from src.main import celery
# Initialize Celery

send_mail_route = Blueprint('send_mail', __name__)


@celery.task
def send_email(subject, recipients, template, context):
    msg = Message(subject, recipients=recipients)
    msg.html = render_template(template, context=context)
    mail.send(msg)


def schedule_mail(subject: str, name: str, template: str,  recipient: list[str]):
    send_email.apply_async(
        args=[subject, recipient, template, {'name': name}],
        countdown=60  # send the email in 60 seconds
    )
    return 'Email scheduled for sending in 60 seconds!'
