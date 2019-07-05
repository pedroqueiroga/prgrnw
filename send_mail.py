import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from utils import pega_credenciais


OTLK_HOST_ADDR = 'smtp-mail.outlook.com'
OTLK_PORT_NMBR = 587
EMAIL_SUBJECT = 'Pergamum Renewal Extravaganza just ran'


def send_mail(receiver, string):
    "Sends an email from receiver to receiver"

    prgrnw_email_address,prgrnw_email_password = pega_credenciais('credenciais_email')
    msg = compose_mail(prgrnw_email_address, receiver, string)
    # The actual mail send
    server = smtplib.SMTP(host=OTLK_HOST_ADDR,
                          port=OTLK_PORT_NMBR)
    server.starttls()
    server.login(prgrnw_email_address, prgrnw_email_password)
    server.send_message(msg)
    server.quit()


def compose_mail(sender, receiver, message):
    mail = MIMEMultipart()

    mail['From'] = sender
    mail['To'] = receiver
    mail['Subject'] = EMAIL_SUBJECT

    mail.attach(MIMEText(message, 'plain'))

    return mail


