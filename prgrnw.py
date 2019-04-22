import datetime
import time
import os

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def main():

   try:
      cpf, senha = pega_credenciais('credenciais')
   except Exception as e:
      print('Cheque o arquivo das credenciais, algo não está correto.')
      return

   browser = webdriver.Firefox()
   browser.get('http://pergamum.ufpe.br/pergamum/biblioteca/index.php')

   div_login = browser.find_element_by_id('div_login')
   div_login.click()

   wait = WebDriverWait(browser, 10)
   # waiting for the login text box to show
   # should this be a presence of all elements, and find both login and senha?
   wait.until(ec.presence_of_element_located((By.ID, 'login_acesso')))

   login_box = browser.find_element_by_id('login_acesso')
   passw_box = browser.find_element_by_id('senha_acesso')

   try:
      login_box.send_keys(cpf)
      passw_box.send_keys(senha)
      passw_box.send_keys(Keys.RETURN)

      # wait for logout to show, which means meu pergamum will now do what I want
      wait.until(ec.presence_of_element_located((By.ID, 'div_logout')))
   except Exception as e:
      print('Não foi possível fazer o login no Pergamum. Cheque seu CPF e senha.')
      return

   meu_pergamum = browser.find_element_by_link_text('Meu Pergamum')
   meu_pergamum.click()

   # wait for new window (meu pergamum)
   wait.until(lambda _: len(browser.window_handles) == 2)

   # switch to meu pergamum's window
   for handle in browser.window_handles:
      browser.switch_to_window(handle)

   process_meu_pergamum(browser)
   
def process_meu_pergamum(browser):
   wanted_div_id = 'Accordion1'
   # wait for Accordion1 to show
   WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.ID, wanted_div_id)))
   booksTable = browser.find_elements_by_xpath("//div[@id='" + wanted_div_id + "']/div[1]/div[2]/table[1]/tbody[1]/tr[position()>1]")
   # position() > 1 to ignore header tr
   for tr in booksTable:
      book_info = []

      for td in tr.find_elements_by_xpath("./td[position()>1 and position() < last()]"):
         # first and last td are useless to us.
         book_info.append(td)

      print_book_info(*book_info)
      print()

def print_book_info(book_name, book_return, book_limit, book_renewal):
   today = datetime.datetime.today()
   return_date = datetime.datetime.strptime(book_return.text.strip() + ' 23:59:59', '%d/%m/%Y %H:%M:%S')
   timedelta = return_date-today
   parsed_limit = book_limit.text.split(' / ')
   nreturns_left = int(parsed_limit[1]) - int(parsed_limit[0])

   portuguese_td = str(timedelta).replace('day', 'dia').replace(':', 'h', 1)
   portuguese_td = portuguese_td[:portuguese_td.index(':')] + 'm'
   
   print('>',book_name.text)
   if timedelta.days >= 0:
      print('\tTempo de aluguel restante:', portuguese_td)
   else:
      print('\tEste livro está atrasado', -(timedelta.days), 'dia' + ('s.' if timedelta.days < -1 else '.'))

   end = ('' if timedelta.days < 2 and timedelta.days >= 0 else '\n')
   if nreturns_left > 0 and timedelta.days >= 0:
      print('\tVocê pode renová-lo mais', nreturns_left, 'vez' + ('es.' if nreturns_left > 2 else '.'), end=end)
      if timedelta.days == 0:
         print(' Renove este livro ainda hoje!!')
      elif timedelta.days == 1:
         print(' Renove este livro amanhã!')
   else:
      print('\tVocê não pode renová-lo.', end=end)
      if timedelta.days == 0:
         print(' Retorne este livro HOJE!')
      elif timedelta.days == 1:
         print(' Lembre-se de retornar este livro amanhã!')

def pega_credenciais(file_name):
   with open(file_name, 'r') as credf:
      lines = credf.readlines()
      if len(lines) != 2:
         raise Exception('Arquivo de credenciais não existe, ou não presta.')
      
      cpf = lines[0].strip()
      senha = lines[1].strip()

   return cpf, senha
   
main()
