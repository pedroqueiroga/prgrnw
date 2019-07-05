import subprocess
import re


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


