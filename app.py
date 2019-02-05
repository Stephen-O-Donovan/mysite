from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flaskext.mysql import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, TextField, SubmitField
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
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=2, max=50)])
    email = StringField('Email', [validators.Length(min=3, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    print(form.validate())
    if request.method == 'POST': #and form.validate():
        print("starting request")
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        try:
            connection = create_connection()
            with connection.cursor() as cursor:
                print("checking if user exists")
                user_exists = cursor.execute('SELECT * FROM users WHERE username = %s', [username])
                if int(user_exists) == 0:
                    print("inserting username etc")
                    cursor.execute('INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)', (name, email, username , password))
                    connection.commit()
                    flash('You are now registered and can log in', 'success')
                    return redirect(url_for('login'))
                else:
                    print("username exists")
                    flash('Username already exists', 'danger')
                    return redirect(url_for('register'))
        finally:
            connection.close()
    else:
        print("Not post")



    return render_template('register.html', form=form)


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        cur = mysql.get_db().cursor()
        result = cur.execute('SELECT * FROM users WHERE username = %s', [username])
        if result > 0:
            data = cur.fetchone()
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
            cur.close()
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
