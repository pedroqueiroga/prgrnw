web: gunicorn  prgrnw.wsgi --log-file -
worker: python worker.py &
        python scheduler.py
