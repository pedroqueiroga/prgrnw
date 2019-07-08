import subprocess
import sys
import re
import socket
import pickle

from datetime import datetime, date

def cmd(command):
    result = subprocess.check_output(command, shell=True) #.decode()
    ret = ''
    
    try:
        ret = result.decode()
    except:
        ret = result

    return ret

def atq_user_dates(date_wanted, user_wanted):
    "date_wanted deve estar no formato '%d/%m/%Y'"

    # True se encontrou um prgrnw.py praquele user praquele dia
    dmy = list(map(int, date_wanted.split('/')))[::-1]
    datetimedate_wanted = date(*dmy)
    print(datetimedate_wanted)

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

    print(jobs)
    print(datetime.date(jobs[0].next_run_time))
    matches = list(filter(lambda x: (datetime.date(x.next_run_time) == datetimedate_wanted and x.name == user_wanted), jobs))
    print(matches)
    for match in matches:
        print(match)
    return len(matches) > 0
        
def parse_cmd_line():
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        return ''
