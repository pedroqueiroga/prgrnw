from rq import Queue
from worker import conn
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

import socket
import pickle

HOST='127.0.0.1'
PORT=65432

def popo(uid):
    q = Queue('workinson', connection=conn)
    q.enqueue(do_it, uid)

def do_it(uid):
    print(uid)
    for i in range(50):
        print(i, ', ', end='')

    print()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        date = datetime.datetime.now() + datetime.timedelta(minutes=20)
        job = {
            'func': 'popo',
            'trigger': 'date',
            'next_run_time': date,
            'uid': uid,
            'args': uid
        }
        print(job)
        s.sendall(pickle.dumps(job))
    
    return

if __name__ == '__main__':
    do_it('3')
