import logging
import socket

from flask import Flask, request, send_from_directory, render_template
from flask_cors import CORS

from src.config.config import config_instance
from src.main import create_app

app: Flask = create_app(config=config_instance())

CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/sw.js', methods=['GET'])
def sw():
    """
        service worker js
    :return:
    """
    print('Waiting for for service worker ')
    return send_from_directory('static', 'js/sw.js')


app.logger.setLevel(logging.INFO)

if __name__ == '__main__':
    """    
        start celery worker process 
            $ celery -A app.celery worker --loglevel=info
            Here, app.celery is the Celery instance created in your Flask application, and --loglevel=info sets the logging level to info.        
        Start a Celery beat process:
            $ celery -A app.celery beat --loglevel=info
    
            This will start the beat process, which will schedule tasks at the specified intervals.        
            Note that you need to start these processes in separate terminal windows or background them 
            using a process manager such as supervisor or systemd.            
            Once the worker and beat processes are running, you can submit tasks to the Celery queue and 
            they will be executed by the worker process.                
    """
    # TODO learn how to run celery
    # celery.run()
    # uvicorn.run("app:app", host="127.0.0.1", port=8081, reload=True, workers=1)
    if socket.gethostname() == config_instance().DEVELOPMENT_SERVER_NAME:
        app.run(debug=True, use_reloader=True, host="127.0.0.1", port=8081)
    else:
        app.run(debug=True, use_reloader=True, host="0.0.0.0", port=8081)
