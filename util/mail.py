# coding=utf-8

from smtplib import SMTP
from smtplib import SMTPException


def send_email():
    sender = 'from'
    receivers = ['to']

    message = """
    Subject: UPMP merchant test report

    Contratulations! Upmp test finished
    """

    try:
        smtp = SMTP('localhost')
        smtp.sendmail(sender, receivers, message)
        print "Successfully sent email"
    except SMTPException:
        print "Error: unable to send email"