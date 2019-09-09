web: cd src; gunicorn --bind 0.0.0.0:${PORT} wsgi
worker: python src/worker.py & python src/scheduler.py & wait -n
