from flask import Flask

from src.config.config import config_instance

from src.main import create_app

app: Flask = create_app(config=config_instance())

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
    app.run(debug=True, use_reloader=True, host="0.0.0.0", port=8081)
