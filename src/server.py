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

    try:
        mydb = database.PrgrnwDB()
    except Exception as e:
        print('meerdaaaaa no banco')
        sys.stdout.flush()
        return render_template('index.html', feedback='Algo deu errado, tente novamente mais tarde. (ERRO W1)')

    # TODO: checar se ja esta cadastrado
    creds=None
    try:
        creds = mydb.get_user(form['perg-cpf'])
    except Exception as e:
        print('o bixo n existe bro')
        print(e)
        sys.stdout.flush()

    if not creds:
        try:
            print('usuario nao localizado, inserindo...')
            mydb.insert_user(form['perg-cpf'], form['perg-passw'], form['perg-email'])
            print('ok')
            sys.stdout.flush()
        except Exception as e:
            print('deu merda aqui no insert??')
            print(e)
            sys.stdout.flush()
            return render_template('index.html', feedback='Algo deu errado, tente novamente mais tarde. (ERRO W2)')
        finally:
            mydb.close()

    # if inserted or already existed, puts popo to worker, so worker dyno will run prgrnw
    popo(form['perg-cpf'])
    
    return render_template('index.html', feedback='Cheque sua caixa de entrada/spam em breve!')

#@app.route('/oie')
def list_jobs():
    """ list scheduled jobs """
    pass

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
