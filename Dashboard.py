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

dashboard_page = Blueprint('dashboard_page', __name__, template_folder='templates')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You must be logged in to view this page', 'danger')
            return redirect(url_for('login'))
    return wrap

@dashboard_page.route('/dashboard')
@is_logged_in
def dashboard():
    if 'email' in session:
        email = session['email']
    try:
        connection = create_connection()
        with connection.cursor() as cursor:


            #redirect if not researcher
            cursor.execute('SELECT user_type FROM Users WHERE email = %s', [email])
            user_type = cursor.fetchone()
            if user_type["user_type"] == "A":
                return adminDashboard()
            if user_type["user_type"] == "U":
                return universityDashboard()
            if user_type["user_type"] == "C":
                return reviewerDashboard()


            #redirect to limited dashboard if not yet verified
            cursor.execute('SELECT is_verified FROM Users WHERE email = %s', [email])
            verified = cursor.fetchone()
            if verified['is_verified'] == 0:
                return render_template('basicDashboard.html')


            cursor.execute('SELECT * FROM Profile_Publications WHERE email = %s AND pub_status = %s', [email, 'Pending'])
            pendingProposalsData = cursor.rowcount

            cursor.execute('SELECT * FROM Profile_Publications WHERE email = %s AND pub_status = %s', [email, 'Published'])
            publishedProposalsData = cursor.rowcount

            cursor.execute('SELECT * FROM Profile_Publications WHERE email = %s AND pub_status = %s', [email, 'In press'])
            pressProposalsData = cursor.rowcount

            cursor.execute('SELECT * FROM Profile_Funding WHERE email = %s', [email])
            rows = cursor.fetchall()

    finally:
        connection.close()
    return render_template('dashboard.html', pendingProposalsData=pendingProposalsData, pressProposalsData=pressProposalsData,publishedProposalsData=publishedProposalsData, rows=rows)

@dashboard_page.route('/adminDashboard')
@is_logged_in
def adminDashboard():
    return render_template('adminDashboard.html')

@dashboard_page.route('/universityDashboard', methods=['GET', 'POST'])
@is_logged_in
def universityDashboard():

    if 'email' in session:
        email = session['email']

    try:
        connection = create_connection()
        with connection.cursor() as cursor:

            #if request.method == 'POST':
            #verify = request.args.get('verify', None)
            if request.method == 'GET':
                verify = request.args.get('verify', '')
                cursor.execute('UPDATE Users SET is_verified = 1 WHERE email = %s', [verify])
                connection.commit()

            cursor.execute('SELECT institution FROM Users WHERE email = %s', [email])
            row = cursor.fetchone()
            institution = row['institution']

            cursor.execute('SELECT * FROM Users WHERE institution = %s AND is_verified = 1 AND user_type = "R" ', [institution])
            verifiedResearchers = cursor.fetchall()

            cursor.execute('SELECT * FROM Users WHERE institution = %s AND is_verified = 0', [institution])
            unVerifiedResearchers = cursor.fetchall()

    finally:
        connection.close()
    return render_template('universityDashboard.html', verifiedResearchers=verifiedResearchers, unVerifiedResearchers=unVerifiedResearchers)

@dashboard_page.route('/reviewerDashboard')
@is_logged_in
def reviewerDashboard():
    return render_template('reviewerDashboard.html')
