import datetime
import time
import os

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

def main():

   try:
      cpf, senha = pega_credenciais('credenciais')
   except Exception as e:
      print('Cheque o arquivo das credenciais, algo não está correto.')
      return

   browser = webdriver.Firefox()
   browser.set_page_load_timeout(10)
   try:
      browser.get('http://pergamum.ufpe.br/pergamum/biblioteca/index.php')
   except TimeoutException:
      # if timeout, stop page load, should continue working just as fine
      browser.execute_script("window.stop();")

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

   books = get_MP_books(browser)

   for book in books:
      print(book_str_info(book))

   for book in books:
      if book_should_renew(book):
         new_date = renew(browser, book)
         print(new_date)
         break
      

def get_MP_books(browser):
   "gets books listed in Meu Pergamum's Pending Titles page"
   wanted_div_id = 'Accordion1'
   # wait for Accordion1 to show
   WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.ID, wanted_div_id)))
   booksTable = browser.find_elements_by_xpath("//div[@id='" + wanted_div_id + "']/div[1]/div[2]/table[1]/tbody[1]/tr[position()>1]")
   # position() > 1 to ignore header tr

   books = []

   for tr in booksTable:
      book_info = []

      for td in tr.find_elements_by_xpath("./td[position()>1 and position() < last()]"):
         # first and last td are useless to us.
         book_info.append(td)

      books.append(book_info)

   return books

def renew(browser, book):
   book_name, book_return, book_limit, book_renewal = book
   print('Vou renovar:', book_name.text)
   book_renewal.click()

   new_return_date = WebDriverWait(browser,10).until(ec.presence_of_element_located((By.XPATH, "//div[@id='meio']/table[1]/tbody[1]/tr[1]/td[2]/table[1]/tbody[1]/tr[2]/td[1]/table[1]/tbody[1]/tr[1]/td[1]/table[1]/tbody[1]/tr[1]/td[1]/table[3]/tbody[1]/tr[1]/td[3]")))

   new_rd = new_return_date.text.strip().split(' ')[0]
   print('peguei essa merda aqui ó:', new_rd)

   back = browser.find_element_by_id('btn_gravar4')
   back.click()
   
   wanted_div_id = 'Accordion1'
   # wait for Accordion1 to show
   WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.ID, wanted_div_id)))

   return new_rd

def pt_timeleft(timeleft):
   portuguese_tl = str(timeleft).replace('day', 'dia').replace(':', 'h', 1)
   portuguese_tl = portuguese_tl[:portuguese_tl.index(':')] + 'm'

   return portuguese_tl

def book_timeleft(book):
   # book_name, book_return, book_limit, book_renewal = book
   book_return = book[1]
   today = datetime.datetime.today()
   return_date = datetime.datetime.strptime(book_return.text.strip() + ' 23:59:59', '%d/%m/%Y %H:%M:%S')
   timeleft = return_date-today

   return timeleft

def book_expired(timeleft):
   return timeleft.days < 0

def book_should_renew(book):
   timeleft = book_timeleft(book)
   nreturns_left = book_returns_left(book)
   return timeleft.days == 0 and nreturns_left > 0

def book_returns_left(book):
   # book_name, book_return, book_limit, book_renewal = book
   book_limit = book[2]
   parsed_limit = book_limit.text.split(' / ')
   nreturns_left = int(parsed_limit[1]) - int(parsed_limit[0])

   return nreturns_left

def book_str_info(book):
   # book_name, book_return, book_limit, book_renewal = book
   info = ''
   book_name = book[0]

   timeleft = book_timeleft(book)
   portuguese_tl = pt_timeleft(timeleft)
   book_exp = book_expired(timeleft)

   nreturns_left = book_returns_left(book)
   
   info += '> ' + book_name.text + '\n'

   if not book_exp:
      info += '\tTempo de aluguel restante: ' +  portuguese_tl + '\n'
   else:
      info += '\tEste livro está atrasado ' + str(-(timeleft.days)) + ' dia' + ('s.' if timeleft.days < -1 else '.') + '\n'

   end = ('' if timeleft.days < 2 and timeleft.days >= 0 else '\n')
   if nreturns_left > 0 and not book_exp:
      info += '\tVocê pode renová-lo mais ' + str(nreturns_left) + ' vez' + ('es.' if nreturns_left > 2 else '.') + end
      if timeleft.days == 0:
         info += ' Renove este livro ainda hoje!!\n'
      elif timeleft.days == 1:
         info += ' Renove este livro amanhã!\n'
   else:
      info += '\tVocê não pode renová-lo.' + end
      if timeleft.days == 0:
         info += ' Retorne este livro HOJE!\n'
      elif timeleft.days == 1:
         info += ' Lembre-se de retornar este livro amanhã!\n'

   return info

def pega_credenciais(file_name):
   with open(file_name, 'r') as credf:
      lines = credf.readlines()
      if len(lines) != 2:
         raise Exception('Arquivo de credenciais não existe, ou não presta.')
      
      cpf = lines[0].strip()
      senha = lines[1].strip()

   return cpf, senha
   
main()
