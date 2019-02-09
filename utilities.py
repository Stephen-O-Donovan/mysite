import pymysql

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