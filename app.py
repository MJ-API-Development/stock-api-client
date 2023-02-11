from flask import Flask

from src.config.config import config_instance
from src.main import create_app

app: Flask = create_app(config_class=config_instance())


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, host="0.0.0.0", port=8081)