""" 
Pergamum Renewal Extravaganza server
"""


import os
import logging
import redis
import gevent
from flask import Flask, render_template, request
from flask_sockets import Sockets

import database

from worker_functions import popo

import sys

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)


app = Flask(__name__)
app.debug = 'DEBUG' in os.environ

sockets = Sockets(app)


@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/dale', methods=['GET', 'POST'])
def dale():
    """This function makes the worker dyno WORK"""
    form = request.form

    for i in form:
        print(i,'=',form[i])

    sys.stdout.flush()

    # return render_template('index.html')
    try:
        mydb = database.PrgrnwDB()
    except Exception as e:
        print('meerdaaaaa no banco')
        sys.stdout.flush()
        return render_template('index.html')

    # TODO: checar se ja esta cadastrado
    creds=None
    try:
        creds = mydb.get_user(form['perg-cpf'])
    except Exception as e:
        print('o bixo n existe bro')
        print(e)
        sys.stdout.flush()

    # TODO: se nao for cadastrado, cadastrar
    try:
        mydb.insert_user(form['perg-cpf'], form['perg-passw'], form['perg-email'])
    except Exception as e:
        print('deu merda aqui no insert??')
        print(e)
        sys.stdout.flush()
        return render_template('index.html')
    finally:
        mydb.close()

    # if valid user, puts popo to worker, so worker dyno will run prgrnw
    popo(form['perg-cpf'])
        
    return render_template('index.html')

#@app.route('/oie')
def list_jobs():
    """ list scheduled jobs """
    pass

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
