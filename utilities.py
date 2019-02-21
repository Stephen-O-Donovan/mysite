import pymysql
import sendgrid
from sendgrid.helpers.mail import *
import os

ALLOWED_EXTENSIONS = set(['pdf', 'odt', 'txt'])
def create_connection():
    connection = pymysql.connect(host='mysql.netsoc.co',
                                 user='stephenteam5',
                                 password='eFDhNR4lUP',
                                 db='stephenteam5_Project5',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_email(to_email, subject, content):
    sg = sendgrid.SendGridAPIClient(apikey='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')
    from_email = Email("SFI@groupproject.com")
    to_email = Email(to_email)
    subject = subject
    content = Content("text/plain", content)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)
