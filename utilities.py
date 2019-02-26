import pymysql
import sendgrid
import datetime
import threading
from sendgrid.helpers.mail import Email, Content, Mail

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

def send_email(email, subject, text):
    sg = sendgrid.SendGridAPIClient(apikey='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')
    from_email = Email("test@example.com")
    to_email = Email(email)
    subject = subject
    content = Content("text/plain", text)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)



def mail_check():
    x = datetime.datetime.now()
    subject = 'Yearly Report Reminder'
    content = "Please don't forget to submit your yearly report"
    if int(x.strftime("%d")) == 1 and int(x.strftime('%m')) % 2 == 0:
        try:
            connection = create_connection()
            with connection.cursor() as cursor:
                cursor.execute('SELECT email FROM GrantApplication WHERE admin_accepted=1 and reviewer_accepted=1 and university_accepted=1')
                for data in cursor.fetchall():
                    try:
                        send_email(data['email'], subject, content)
                    except:
                        print(data['email'])
        finally:
            connection.close()
    threading.Timer(86400, mail_check).start()

