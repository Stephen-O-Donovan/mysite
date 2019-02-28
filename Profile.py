import os
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, Blueprint
from flaskext.mysql import MySQL
from wtforms import Form, SelectField, BooleanField,StringField,IntegerField, TextAreaField, PasswordField, validators, TextField, SubmitField, DateField
from passlib.hash import sha256_crypt
from functools import wraps
from pymysql.cursors import DictCursor
#from flask_sslify import SSLify
from utilities import *
from werkzeug.utils import secure_filename
from datetime import date
from forms import *

UPLOAD_FOLDER = 'storage/proposals'
profile_page = Blueprint('profile_page', __name__, template_folder='templates')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You must be logged in to view this page', 'danger')
            return redirect(url_for('login'))
    return wrap

@profile_page.route('/adminProfile', methods=['GET', 'POST'])
@is_logged_in
def adminProfile():
    form = BasicProfileForm(request.form)
    if 'email' in session:
        email = session['email']

    try:
        connection = create_connection()
        with connection.cursor() as cursor:

            if request.method == 'POST':
                if request.form['submit'] == 'Save Personal Info':
                    cursor.execute('UPDATE Users SET first_name=%s, surname=%s, suffix=%s,'
                                   'phone=%s, phone_extension=%s'
                                   'WHERE email=%s',
                                   [form.first_name.data, form.surname.data, form.suffix.data,
                                   form.phone.data, form.phone_extension.data, email])
                    connection.commit()

            #get data from tables
            cursor.execute('SELECT * FROM Users WHERE email = %s', [email])
            p1_data = cursor.fetchone()

    finally:
        connection.close()

    return render_template('adminProfile.html', form=form, p1_data=p1_data)

@profile_page.route('/uniProfile', methods=['GET', 'POST'])
@is_logged_in
def uniProfile():
    form = BasicProfileForm(request.form)
    if 'email' in session:
        email = session['email']

    try:
        connection = create_connection()
        with connection.cursor() as cursor:

            if request.method == 'POST':
                if request.form['submit'] == 'Save Personal Info':
                    cursor.execute('UPDATE Users SET first_name=%s, surname=%s, suffix=%s,'
                                   'phone=%s, phone_extension=%s'
                                   'WHERE email=%s',
                                   [form.first_name.data, form.surname.data, form.suffix.data,
                                   form.phone.data, form.phone_extension.data, email])
                    connection.commit()

            #get data from tables
            cursor.execute('SELECT * FROM Users WHERE email = %s', [email])
            p1_data = cursor.fetchone()

    finally:
        connection.close()

    return render_template('uniProfile.html', form=form, p1_data=p1_data)
