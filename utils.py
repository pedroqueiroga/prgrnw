import subprocess
import re
from datetime import datetime

def cmd(command):
    result = subprocess.check_output(command, shell=True) #.decode()
    ret = ''
    
    try:
        ret = result.decode()
    except:
        ret = result

    return ret


def pega_credenciais(file_name):
   with open(file_name, 'r') as credf:
      lines = credf.readlines()
      if len(lines) != 2:
         raise Exception('Arquivo de credenciais não existe, ou não presta.')
      
      usr = lines[0].strip()
      pwd = lines[1].strip()

   return usr, pwd


def atq_user_dates(date_wanted, user_wanted):
    "date_wanted deve estar no formato '%d/%m/%Y'"

    # True se encontrou um prgrnw.py praquele user praquele dia
    
    datetime_wanted = datetime.strptime(date_wanted, '%d/%m/%Y')
    jobs_number = re.compile("\d+").findall(cmd('atq | cut -f 1'))
    dates_preprocessed = re.compile("\w{3} +(\w{3}) +(\d+) +\d\d:\d\d:\d\d +(\d\d\d\d)").findall(cmd('atq | cut -f 2'))
    dates = [ datetime.strptime(' '.join(t), '%b %d %Y') for t in dates_preprocessed ]

    jobs = zip(jobs_number, dates)
    for job in jobs:
        if datetime_wanted == job[1]:
            match = re.compile('python3 prgrnw\.py ?(.*)').search(cmd('at -c ' + job[0] + ' | tail -n 3'))
            if match:
                user = match.group(1)
                if user_wanted == user:
                    return True

    return False
        
        
        
