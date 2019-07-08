from rq import Queue
from worker import conn
from prgrnw import prgrnw

def popo(uid):
    q = Queue('workinson', connection=conn)
    q.enqueue(prgrnw, uid)

