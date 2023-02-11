from flask import Flask

from src.config.config import config_instance
from src.mail.send_emails import celery
from src.main import create_app


app: Flask = create_app(config=config_instance())


if __name__ == '__main__':
    # TODO learn how to run celery
    # celery.run()
    app.run(debug=True, use_reloader=True, host="0.0.0.0", port=8081)