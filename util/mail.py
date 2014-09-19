# coding=utf-8

from smtplib import SMTP
from smtplib import SMTPException


def send_email():
    sender = 'wangxiao_8800@qq.com'
    receivers = ['edwin.wang@pingplusplus.com']

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