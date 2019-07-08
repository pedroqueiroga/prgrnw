import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os

EMAIL_SUBJECT = 'Pergamum Renewal Extravaganza just ran'

def send_mail(receiver, string):
    "Sends an email from receiver to receiver"
    prgrnw_email_addr = os.getenv('PRGRNW_EMAIL_ADDR')
    prgrnw_email_pwd = os.getenv('PRGRNW_EMAIL_PWD')
    prgrnw_host_addr = 'smtp-mail.outlook.com'
    prgrnw_port_nmbr = 587
    msg = compose_mail(prgrnw_email_addr, receiver, string)
    # The actual mail send
    server = smtplib.SMTP(host=prgrnw_host_addr,
                          port=prgrnw_port_nmbr)
    server.starttls()
    server.login(prgrnw_email_addr, prgrnw_email_pwd)
    server.send_message(msg)
    server.quit()


def compose_mail(sender, receiver, message):
    mail = MIMEMultipart()

    mail['From'] = sender
    mail['To'] = receiver
    mail['Subject'] = EMAIL_SUBJECT

    mail.attach(MIMEText(message, 'plain'))

    return mail


