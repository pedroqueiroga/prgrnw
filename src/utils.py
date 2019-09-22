import subprocess
import sys
import re
import socket
import pickle

import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


def cmd(command):
    result = subprocess.check_output(command, shell=True) #.decode()
    ret = ''
    
    try:
        ret = result.decode()
    except:
        ret = result

    return ret


def get_jobs(user):
    HOST='127.0.0.1'
    PORT=65432
    BUFFSIZE=1024

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        job = {'func': 'get_jobs'}
        s.sendall(pickle.dumps(job))
        whole = b''
        while True:
            part = s.recv(BUFFSIZE)
            whole += part
            if len(part) < BUFFSIZE:
                break

    if whole:
        jobs = pickle.loads(whole)
    else:
        raise Exception("teste")

    matches = list(filter(lambda x: x.name == user, jobs))

    return matches


def get_jobs_dates(user):
    "retorna lista de datas dos proximos jobs"
    jobs = get_jobs(user)

    return [ datetime.datetime.date(i.next_run_time) for i in jobs ]


def atq_user_dates(dates_wanted, user_wanted):
    "dates_wanted deve ser [date]"

    print(dates_wanted)

    jobs = get_jobs(user_wanted)

    print('jobs', jobs)
    matches = list(filter(lambda x: datetime.datetime.date(x.next_run_time) in dates_wanted, jobs))
    print('matches', matches)
    for match in matches:
        print(match)
    return [ datetime.datetime.date(i.next_run_time) for i in matches ]
        
def parse_cmd_line():
    if len(sys.argv) > 2:
        return sys.argv[1], sys.argv[2]
    else:
        return ''


def add_job(date, uid, now=False):
    HOST='127.0.0.1'
    PORT=65432

    print('added', 'type of date:', type(date), date, uid)
    if now == False:
        dt = datetime.datetime.strptime("{}/{}/{} 07:00".format(date.day, date.month, date.year), "%d/%m/%Y %H:%M")
    else:
        dt = datetime.datetime.now() + datetime.timedelta(seconds=20)
    print(dt)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        job = {
            'func': 'popo',
            'trigger': 'date',
            'next_run_time': dt,
            'uid': uid,
            'args': uid
        }
        s.sendall(pickle.dumps(job))
    
    print(job)
    return
