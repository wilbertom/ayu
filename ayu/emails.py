import smtplib
from email.mime.text import MIMEText

G_MAIL_HOST = 'smtp.gmail.com:587'


def new_email(fr, to, subject, content):
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['To'] = to
    msg['From'] = fr

    return msg


def g_mail(email, password):
    server = smtplib.SMTP(G_MAIL_HOST)
    server.ehlo()
    server.starttls()
    server.login(email, password)

    return server


class EmailSubscriber(object):

    def __init__(self, email_address, smtp):
        self.email_address = email_address
        self.s = smtp

    def send(self, fr, subject, content):
        msg = new_email(fr, self.email_address, subject, content)
        self.s.send_message(msg)

        return self


