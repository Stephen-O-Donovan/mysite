# encoding: utf-8
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flaskext.mysql import MySQL
from wtforms import Form, SelectField, BooleanField,StringField, TextAreaField, PasswordField, validators, TextField, SubmitField
from passlib.hash import sha256_crypt
from functools import wraps
from pymysql.cursors import DictCursor
from flask_sslify import SSLify
from utilities import *


app = Flask(__name__)
sslify = SSLify(app)
app.secret_key = 'alphaHodder'
#Config MySQL - below is remote host
#app.config['MYSQL_DATABASE_HOST'] = 'team5ucc.cloudaccess.host'
#app.config['MYSQL_DATABASE_USER'] = 'vjvpukus'
#app.config['MYSQL_DATABASE_PASSWORD'] = 'gv4+Bez9B9[FB9'
#app.config['MYSQL_DATABASE_DB'] = 'vjvpukus'
#app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#this is working, cannot be accessed remotely
app.config['MYSQL_DATABASE_HOST'] = 'team5ucc.mysql.pythonanywhere-services.com'
app.config['MYSQL_DATABASE_USER'] = 'team5ucc'
app.config['MYSQL_DATABASE_PASSWORD'] = 'alphaVase'
app.config['MYSQL_DATABASE_DB'] = 'team5ucc$users'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


# Initialise MySQL
mysql = MySQL(cursorclass=DictCursor)
mysql.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')


class RegisterForm(Form):
    Prefix = SelectField(u'Prefix', choices=[('mr','Mr.'),('mrs','Mrs.'),('ms','Ms.'),('dr','Dr.')])
    First_Name = StringField('First Name', [validators.Length(min=1, max=50)])
    SurName = StringField('SurName', [validators.Length(min=1, max=50)])
    Suffix = SelectField(u'Suffix', choices=[('phd','PHD'),('n/a','N/A.')])
    Email = StringField('Email', [validators.Length(min=3, max=50)])
    Job_Title = StringField('Job Title', [validators.Length(min=2, max=50)])
    Phone = StringField('Phone', [validators.Length(min=2, max=50)])
    Phone_Extension = StringField('Phone Extension', [validators.Length(min=2, max=50)])
    Administrator = BooleanField()

    Password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST': #and form.validate():
        Prefix = form.Prefix.data
        First_Name = form.First_Name.data
        SurName = form.SurName.data
        Suffix = form.Suffix.data
        Email = form.Email.data
        Job_Title = form.Job_Title.data
        Phone = form.Phone.data
        Phone_Extension = form.Phone_Extension.data
        Administrator = form.Administrator.data
        Password = sha256_crypt.encrypt(str(form.Password.data))

        try:
            connection = create_connection()
            with connection.cursor() as cursor:
                #Checking if the username is in the database
                user_exists = cursor.execute('SELECT * FROM Registration WHERE Email = %s', [Email])
                if int(user_exists) == 0:
                    cursor.execute('INSERT INTO Registration(Prefix,First_Name,SurName,Suffix,Email,Job_Title,Phone,Phone_Extension,Administrator,Password) VALUES( %s,%s, %s, %s, %s, %s, %s, %s, %s, %s)', (Prefix,First_Name,SurName,Suffix,Email,Job_Title,Phone,Phone_Extension,Administrator,Password))
                    connection.commit()
                    flash('You are now registered and can log in', 'success')
                    return redirect(url_for('login'))
                else:
                    #Redirect if username is taken
                    flash('Email already in use', 'danger')
                    return redirect(url_for('register'))
        finally:
            connection.close()

    return render_template('register.html', form=form)


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        cursor = create_connection().cursor()
        result = cursor.execute('SELECT * FROM users WHERE username = %s', [username])
        if result > 0:
            data = cursor.fetchone()
            password = data['password']
            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            cursor.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check for user auth
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You must be logged in to view this page', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(ssl_context='adhoc')
