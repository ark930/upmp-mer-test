# coding=utf-8

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders
import os

mailto_list = ["edwin.wang@pingplusplus.com", "489004717@qq.com"]

mail_host = 'smtp.ym.163.com'
mail_user = "robot"
mail_pass = "robot4pingpp"
mail_postfix = "pingplusplus.com"

def send_mail(to_list, sub, content):
    me = 'robot' + "<" + mail_user + "@" + mail_postfix + ">"
    msg = MIMEMultipart('alternative')
    # msg = MIMEText(content)
    # msg['Subject'] = sub  # 设置主题
    msg['From'] = me  # 发件人
    msg['To'] = ";".join(to_list)  # 收件人

    text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
    html = """\
    <html>
      <head></head>
      <body>
        <p>Hi!<br>
           How are you?<br>
           Here is the <a href="http://www.python.org">link</a> you wanted.
        </p>
      </body>
    </html>
    """

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    files = ['../data/untest_merchant.txt', '../data/template.xlsx']
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
    if send_mail(mailto_list, "subject", "content"):
        print "发送成功"
    else:
        print "发送失败"