from datetime import datetime, timedelta
import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

import socket
import pickle
from worker_functions import popo

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

scheduler = BackgroundScheduler()
scheduler.add_jobstore(SQLAlchemyJobStore(url='sqlite:///jobs.sqlite'))

scheduler.start()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            data = conn.recv(1024)
            if not data:
                break
            
            # data deve ser uma tupla
            job = pickle.loads(data)
            print(job)
            print(type(job))
            if job['func'] == 'popo':
                scheduler.add_job(popo, trigger=job['trigger'], next_run_time=job['next_run_time'], misfire_grace_time=3600, name=job['uid'], args=job['args'])
            elif job['func'] == 'get_jobs':
                conn.sendall(pickle.dumps(scheduler.get_jobs()))
