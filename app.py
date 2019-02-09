# -*- coding: utf-8 -*-
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
        prefix = form.Prefix.data
        first_name = form.First_Name.data
        surname = form.SurName.data
        suffix = form.Suffix.data
        email = form.Email.data
        job_title = form.Job_Title.data
        phone = form.Phone.data
        phone_extension = form.Phone_Extension.data
        password = sha256_crypt.encrypt(str(form.Password.data))

        try:
            connection = create_connection()
            with connection.cursor() as cursor:
                #Checking if the username is in the database
                user_exists = cursor.execute('SELECT * FROM Users WHERE email = %s', [email])
                if int(user_exists) == 0:
                    cursor.execute('INSERT INTO Users(prefix,first_name,surname,suffix,email,job_title,phone,phone_extension,password) VALUES( %s,%s, %s, %s, %s, %s, %s, %s, %s)', (prefix,first_name,surname,suffix,email,job_title,phone,phone_extension,password))
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
        email = request.form['email']
        password_candidate = request.form['password']
        cursor = create_connection().cursor()
        result = cursor.execute('SELECT * FROM Users WHERE email = %s', [email])
        if result > 0:
            data = cursor.fetchone()
            password = data['password']
            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['email'] = email

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


@app.route('/profile')
@is_logged_in
def show_profile():
    if 'email' in session:
        email = session['email']
    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            #get data from tables
            cursor.execute('SELECT * FROM Users WHERE email = %s', [email])
            p1_data = cursor.fetchone()

            cursor.execute('SELECT * FROM Profile_Education_Info WHERE email = %s', [email])
            p2_data = cursor.fetchall()

            cursor.execute('SELECT * FROM Profile_Employment WHERE email = %s', [email])
            p3_data = cursor.fetchall()

            cursor.execute('SELECT * FROM Profile_Profess_soc WHERE email = %s', [email])
            p4_data = cursor.fetchall()
            
            cursor.execute('SELECT * FROM Profile_DandA WHERE email = %s', [email])
            p5_data = cursor.fetchall()
            
            cursor.execute('SELECT * FROM Profile_Funding WHERE email = %s', [email])
            p6_data = cursor.fetchall()
            
            cursor.execute('SELECT * FROM Profile_Teamate WHERE email = %s', [email])
            p7_data = cursor.fetchall()
            
            cursor.execute('SELECT * FROM Profile_Impact WHERE email = %s', [email])
            p8_data = cursor.fetchall()
            
            cursor.execute('SELECT * FROM Profile_IandC WHERE email = %s', [email])
            p9_data = cursor.fetchall()
            
            cursor.execute('SELECT * FROM Profile_Publications WHERE email = %s', [email])
            p10_data = cursor.fetchall()
            
            cursor.execute('SELECT * FROM Profile_Presentation WHERE email = %s', [email])
            p11_data = cursor.fetchall()
            
            cursor.execute('SELECT * FROM Profile_Academic_Col WHERE email = %s', [email])
            p12_data = cursor.fetchall()
            
            cursor.execute('SELECT * FROM Profile_None_Academic_Col WHERE email = %s', [email])
            p13_data = cursor.fetchall()
            
            cursor.execute('SELECT * FROM Profile_Workshop WHERE email = %s', [email])
            p14_data = cursor.fetchall()
            
            cursor.execute('SELECT * FROM Profile_Communication WHERE email = %s', [email])
            p15_data = cursor.fetchall()
            
            cursor.execute('SELECT * FROM Profile_SFI_Fund_Ratio WHERE email = %s', [email])
            p16_data = cursor.fetchall()
            
            cursor.execute('SELECT * FROM Profile_Public_Engagement WHERE email = %s', [email])
            p17_data = cursor.fetchall()
    finally:
        connection.close()
    return render_template('show_profile.html', p1_data=p1_data,p2_data=p2_data,p3_data=p3_data,p4_data=p4_data,p5_data=p5_data,p6_data=p6_data,p7_data=p7_data,p8_data=p8_data,p9_data=p9_data,p10_data=p10_data,p11_data=p11_data,p12_data=p12_data,p13_data=p13_data,p14_data=p14_data,p15_data=p15_data,p16_data=p16_data,p17_data=p17_data)

if __name__ == '__main__':
    app.run(ssl_context='adhoc')
