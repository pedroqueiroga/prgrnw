web: gunicorn prgrnw.wsgi --log-file -
worker: python src/worker.py & python src/scheduler.py & wait -n
