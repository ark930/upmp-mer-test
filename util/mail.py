# coding=utf-8

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import Encoders
import os

from email.MIMEBase import MIMEBase


mail_host = 'smtp.ym.163.com'
mail_user = "robot"
mail_pass = "robot4pingpp"
mail_postfix = "pingplusplus.com"


def send_mail(to_list, merchant, attchment_path):
    from_name = '钢铁侠'
    me = from_name + "<" + mail_user + "@" + mail_postfix + ">"
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '银联测试报告：' + merchant['name'].decode('utf-8').encode('utf-8')  # 设置主题
    msg['From'] = from_name  # 发件人
    msg['To'] = ";".join(to_list)  # 收件人

    html = """\
    <html>
      <head></head>
      <body>
        <p>商户名称：%s<p>
        <p>  商户号：%s<p>
        </p>
      </body>
    </html>
    """ % (merchant['name'].decode('utf-8').encode('utf-8'), merchant['id'].decode('utf-8').encode('utf-8'))
    msg.attach(MIMEText(html, 'html'))

    files = [attchment_path]
    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(f, "rb").read())
        Encoders.encode_base64(part)
        print(os.path.basename(f))
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)

    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        s.login(mail_user + "@" + mail_postfix, mail_pass)
        s.sendmail(me, to_list, msg.as_string())
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False


if __name__ == '__main__':
    attchment_path = '../data/template.xlsx'
    merchant = dict()
    merchant['name'] = '是的范德萨'
    merchant['id'] = '423432342323'

    mailto_list = list()
    with open('../data/maillist') as f:
        for line in f:
            mailto_list.append(line.strip())

    if send_mail(mailto_list, merchant, attchment_path):
        print "发送成功"
    else:
        print "发送失败"