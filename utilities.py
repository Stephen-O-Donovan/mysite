import pymysql
import sendgrid
import datetime
import threading

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
    from_email = sendgrid.helpers.mailEmail("SFI@groupproject.com")
    to_email = sendgrid.helpers.mailEmail(to_email)
    subject = subject
    content = sendgrid.helpers.mailContent("text/plain", content)
    mail = sendgrid.helpers.mailMail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)



def mail_check():
    x = datetime.datetime.now()

    subject = 'Yearly Report Reminder'
    content = "Please don't forget to submit your yearly report"
    if x.strftime("%d") == 1 and x.strftime('%m') % 2 == 0:
        try:
            connection = create_connection()
            with connection.cursor() as cursor:
                cursor.execute('SELECT email FROM GrantApplications WHERE admin_accepted=1 and reviewer_accepted=1 and university_accepted=1')
                for email in cursor.fetchall():
                    send_email(email, subject, content)
        finally:
            connection.close()
    threading.Timer(86400, mail_check).start()

