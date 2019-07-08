import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config


EMAIL_SUBJECT = 'Pergamum Renewal Extravaganza just ran'

def send_mail(receiver, string):
    "Sends an email from receiver to receiver"

    msg = compose_mail(config.PRGRNW_EMAIL_ADDR, receiver, string)
    # The actual mail send
    server = smtplib.SMTP(host=config.PRGRNW_HOST_ADDR,
                          port=config.PRGRNW_PORT_NMBR)
    server.starttls()
    server.login(config.PRGRNW_EMAIL_ADDR, config.PRGRNW_EMAIL_PWD)
    server.send_message(msg)
    server.quit()


def compose_mail(sender, receiver, message):
    mail = MIMEMultipart()

    mail['From'] = sender
    mail['To'] = receiver
    mail['Subject'] = EMAIL_SUBJECT

    mail.attach(MIMEText(message, 'plain'))

    return mail


