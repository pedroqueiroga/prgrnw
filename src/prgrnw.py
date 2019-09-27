import datetime
import time
import os
import sys
import traceback
import textwrap

from send_mail import send_mail
from utils import atq_user_dates, parse_cmd_line, add_job, get_jobs_dates
import database
import exceptions

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
#from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options

def prgrnw(user, test_mode=False):

   print('running prgrnw for', user)
   sys.stdout.flush()

   big_email_string = ''
   if test_mode:
      creds = user[0], user[1], 'prgrnw@outlook.com'
   else:
      try:
         mydb = database.PrgrnwDB()
      except Exception as e:
         print(e)
         # these catches should actually log
         string = 'Cheque o arquivo das credenciais, algo não está correto.'
         print(string)
         return

      try:
         creds = mydb.get_user(user)
         print(creds)
         sys.stdout.flush()
      except Exception as e:
         print(e)
         string = 'Usuario \'{}\' não consta na base de dados'.format(user)
         print(string)
         sys.stdout.flush()
         return
      finally:
         mydb.close()

   cpf, senha, email = creds
   
   options = Options()
   options.headless = True
   browser = webdriver.Chrome(options=options)

   timeout=10 # seconds
   browser.set_page_load_timeout(timeout)
   n_tries = 10 # try to connect 10 times before giving up.

   div_login = None
   for i in range(n_tries):
      try:
         browser.get('http://pergamum.ufpe.br/pergamum/biblioteca/index.php')
         div_login = browser.find_element_by_id('div_login')
         break
      except TimeoutException:
         # if timeout, stop page load, should continue working just as fine
         try:
            browser.execute_script("window.stop();")
            div_login = browser.find_element_by_id('div_login')
            break;
         except:
            # if something goes wrong, try again.
            time.sleep(15) # try again in 15 seconds perhaps
            continue
      except NoSuchElementException:
         time.sleep(15)
         continue

   if div_login:
      div_login.click()
   else:
      # too many tries and nothing, send mail to user to check
      # pergamum manually
      string = textwrap.fill(('Não foi possível acessar o Pergamum. Cheque se'
                              'ele está fora do ar e solicite uma nova'
                              'execução se/quando não estiver.'), width=80)
      big_email_string += string + '\n'
      print(string)
      browser.quit()
      send_mail(email, big_email_string)
      return
      
      

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
      string ='Não foi possível fazer o login no Pergamum. Cheque seu CPF e senha.'
      big_email_string += string + '\n'
      print(string)
      print(e)
      browser.quit()
      send_mail(email, big_email_string)
      return

   meu_pergamum = browser.find_element_by_link_text('Meu Pergamum')
   meu_pergamum.click()

   # wait for new window (meu pergamum)
   # 2 because before this one opened, there was only 1 window handler!
   try:
      wait.until(lambda _: len(browser.window_handles) == 2)
   except Exception as e:
      string = textwrap.fill(('Algum erro aconteceu durante a execução do'
                              'Pergamum Renewal Extravaganza. Não foi possível'
                              'checar seus livros, tente solicitar uma nova'
                              'execução.'), width=80)
      big_email_string += string + '\n'
      print(string)
      print(e)
      browser.quit()
      send_mail(email, big_email_string)
      return

   # switch to meu pergamum's window
   for handle in browser.window_handles:
      browser.switch_to_window(handle)

   up_dates = set()

   renovados = []

   # check if there is a late book
   none_late=get_MP_books(browser, late_exit=True)

   max_broken_tries = 0
   
   while none_late:
      try:
         new_date,book_name = renew_MP_books(browser)
      except Exception as e:
         print('Erro durante a execucao do renew_MP_books(browser), linha 151')
         traceback.print_exc()
         max_broken_tries += 1
         if broken_tries == 10:
            string = '\n' + textwrap.fill(
               ('Algum erro aconteceu durante a execução'
                'do Pergamum Renewal Extravaganza. Não foi'
                'possível checar todos os seus livros, '
                'tente solicitar uma nova execução.'), width=80) + '\n'
            big_email_string += string + '\n'
            print(string)
         break
         
      if new_date == None or book_name == None: # in reality, can't be just one, but this is looser, so it is better
         break

      renovados.append((book_name, new_date))
      
   if len(renovados) > 0:
      string = 'RENOVADO' + ('S' if len(renovados) > 1 else '') + ':'
      big_email_string += string + '\n'
      print(string)

   for renovado in renovados:
      book_name, new_date = renovado
      string = '\n\t'.join(textwrap.wrap(('\t' + book_name), width=80))
      big_email_string += string + '\n'
      print(string)

      string = '\tNova data: ' + new_date + '\n'
      big_email_string += string + '\n'
      print(string)
         
   books = get_MP_books(browser)

   string = ' Estado atual dos livros '.center(80, '*')
   big_email_string += string + '\n'
   print(string)

   if len(books) == 0:
      string = '*' + ('Zero livros. Isto significa que minha recursão '
                      'chegou ao fim.').center(78) + '*\n'
      string += ('*' * 80)
      big_email_string += string + '\n'
      print(string)
      browser.quit()
      send_mail(email, big_email_string)
      return
      
   if (not none_late) and len(books) > 0:
      string = '\nVOCÊ NÃO PODE RENOVAR LIVROS POR CAUSA DE DÉBITO!\n'
      big_email_string += string + '\n'
      print(string)

   late = []
   cant_renew = []
   possible_return_dates = set()
   possible_return_names = []
   
   for book in books:

      string=book_str_info(book, (not none_late))
      big_email_string += string + '\n'

      return_date = book[1].text.strip()
      book_name = book[0].text

      if book_expired(book_timeleft(book)):
         late.append(book_name)
      elif book_returns_left(book) == 0:
         cant_renew.append(book_name)
      else:
         dmy = list(map(int, return_date.split('/')))[::-1]
         

         possible_return_dates.add((datetime.date(*dmy) -
                                    datetime.timedelta(days=1)))
         possible_return_names.append(book_name)

      print(string)

   if len(possible_return_dates) > 0:
      contemplated_dates = atq_user_dates(possible_return_dates, cpf)
      new_dates = []
      today = datetime.date.today()
      for i in possible_return_dates:
         if (i not in contemplated_dates) and (i != today):
            up_dates.add(i)
      
   n_days = len(up_dates)
   print('up_dates', up_dates)

   for d in up_dates:
      string = '\t' + d.strftime("%d/%m/%Y")
      print(string)

      # add job
      print('adding job!!!')
      print(d,cpf)
      add_job(d, cpf)

   if len(late) > 0 or len(cant_renew) > 0:
      string = '-' * 80
      big_email_string += string + '\n'
      print(string)
      
   if len(late) > 0:
      string = 'ATRASADO' + ('S' if len(late) > 1 else '') + ':'
      big_email_string += string + '\n'
      print(string)
      for b in late:
         string = '\n\t'.join(textwrap.wrap('\t' + b, width=80)) + '\n'
         big_email_string += string + '\n'
         print(string)

   if len(cant_renew) > 0:
      string = 'ZERO RENOVAÇÕES DISPONÍVEIS:'
      big_email_string += string + '\n'
      print(string)
      for b in cant_renew:
         string = '\n\t'.join(textwrap.wrap('\t' + b, width=80)) + '\n'
         big_email_string += string + '\n'
         print(string)

   job_dates = get_jobs_dates(cpf)

   if len(job_dates) > 0:
      string = '\nPróximas execuções:'
      big_email_string += string + '\n'
      print(string)
      for d in job_dates:
         string = '\t' + d.strftime("%d/%m/%Y")
         big_email_string += string + '\n'
         print(string)
      
   print('*'*80)
   big_email_string += ('*' * 80) + '\n'
   browser.quit()
   send_mail(email, big_email_string)
   
def stupid_format_date(date):
   splitted = date.split('/')
   if len(splitted) != 3:
      return None
   return splitted[1] + '/' + splitted[0] + '/' +  splitted[2]

def renew_MP_books(browser):
   # like get_MP_books, but with less queries, since won't create 10 DOM references, when I only need one, because all the others get stale.
   wanted_div_id = 'Accordion1'
   # wait for Accordion1 to show
   WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.ID, wanted_div_id)))
   booksTable = browser.find_elements_by_xpath("//div[@id='" + wanted_div_id + "']/div[1]/div[2]/table[1]/tbody[1]/tr[position()>1]")
   # position() > 1 to ignore header tr

   new_date = None
   book_name = None

   for tr in booksTable:
      book = []

      for td in tr.find_elements_by_xpath("./td[position()>1 and position() < last()]"):
         # first and last td are useless to us.
         book.append(td)

      if book_should_renew(book):
         book_name = book[0].text
         try:
            new_date = renew(browser, book)
         except:
            raise
         break

   return new_date, book_name
         
def get_MP_books(browser, late_exit=False):
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

      if late_exit:
         timeleft = book_timeleft(book_info)
         book_exp = book_expired(timeleft)
         if book_exp:
            return False

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

   if new_rd == "Renovação Cancelada. Este exemplar se encontra em atraso.":
      new_rd = False

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
   return timeleft.days >= 0 and timeleft.days <= 1 and nreturns_left > 0

def book_returns_left(book):
   # book_name, book_return, book_limit, book_renewal = book
   book_limit = book[2]
   parsed_limit = book_limit.text.split(' / ')
   nreturns_left = int(parsed_limit[1]) - int(parsed_limit[0])

   return nreturns_left

def book_str_info(book, some_late):
   # book_name, book_return, book_limit, book_renewal = book
   info = ''
   book_name = book[0]

   timeleft = book_timeleft(book)
   portuguese_tl = pt_timeleft(timeleft)
   book_exp = book_expired(timeleft)

   nreturns_left = book_returns_left(book)
   
   info += '\n  '.join(textwrap.wrap('> ' + book_name.text, width=80)) + '\n'

   if not book_exp:
      info += '\tTempo de aluguel restante: ' +  portuguese_tl + '\n'
   else:
      info += '\tEste livro está atrasado ' + str(-(timeleft.days)) + ' dia' + ('s.' if timeleft.days < -1 else '.') + '\n'

   end = ('' if timeleft.days < 2 and timeleft.days >= 0 else '\n')
   if nreturns_left > 0 and (not book_exp) and (not some_late):
      info += '\tVocê pode renová-lo mais ' + str(nreturns_left) + ' vez' + ('es.' if nreturns_left > 1 else '.') + end
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
   

if __name__ == '__main__':
   prgrnw(parse_cmd_line(), test_mode=True)
