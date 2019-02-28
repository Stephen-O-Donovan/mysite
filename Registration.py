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

registration_page = Blueprint('registration_page', __name__, template_folder='templates')

class RegistrationType(Form):
    User_Type = SelectField(u'', choices=[('R','Researcher'),('A','Admin'),('C','Consultant'),('U','University')])

class AdminRegistrationType(Form):
    User_Type = SelectField(u'', choices=[('A','Admin'),('C','Consultant'),('U','University')])

class RegisterForm(Form):
    Prefix = SelectField(u'Prefix', choices=[('mr','Mr.'),('mrs','Mrs.'),('ms','Ms.'),('dr','Dr.')])
    First_Name = StringField('First Name', [validators.DataRequired(),validators.Length(min=2, max=50)])
    SurName = StringField('Surname', [validators.DataRequired(),validators.Length(min=2, max=50)])
    Suffix = SelectField(u'Suffix',[validators.DataRequired()], choices=[('phd','PHD'),('n/a','N/A.')])
    Email = StringField('Email', [validators.DataRequired(),validators.Length(min=3, max=50),validators.Email(message="Invalid email")])
    Job_Title = StringField('Job Title', [validators.DataRequired(),validators.Length(min=2, max=50)])
    Institution = SelectField('Institution',choices=[('ucc','UCC'),('ucd','UCD'),('ul','UL'),('dcu','DCU')])
    Orcid = StringField('Orcid')
    Phone = IntegerField('Phone', [validators.DataRequired(message="Please enter a valid number")])
    Phone_Extension = SelectField(u'Phone Extension',[validators.DataRequired()], choices=[('353','+353'),('etc','etc.')])


    Password = PasswordField('Password')
    confirm = PasswordField('Confirm Password', [
        validators.DataRequired(),
        validators.EqualTo("Password", message='Passwords do not match')
    ])
class AdminRegisterForm(Form):
    Prefix = SelectField(u'Prefix', choices=[('mr','Mr.'),('mrs','Mrs.'),('ms','Ms.'),('dr','Dr.')])
    First_Name = StringField('First Name', [validators.DataRequired(),validators.Length(min=2, max=50)])
    SurName = StringField('Surname', [validators.DataRequired(),validators.Length(min=2, max=50)])
    Suffix = SelectField(u'Suffix',[validators.DataRequired()], choices=[('phd','PHD'),('n/a','N/A.')])
    Email = StringField('Email', [validators.DataRequired(),validators.Length(min=3, max=50),validators.Email(message="Invalid email")])
    Phone = IntegerField('Phone', [validators.DataRequired(message="Please enter a valid number")])
    Phone_Extension = SelectField(u'Phone Extension',[validators.DataRequired()], choices=[('353','+353'),('etc','etc.')])


    Password = PasswordField('Password')
    confirm = PasswordField('Confirm Password', [
        validators.DataRequired(),
        validators.EqualTo("Password", message='Passwords do not match')
    ])

class UniversityAdminRegisterForm(Form):
    Prefix = SelectField(u'Prefix', choices=[('mr','Mr.'),('mrs','Mrs.'),('ms','Ms.'),('dr','Dr.')])
    First_Name = StringField('First Name', [validators.DataRequired(),validators.Length(min=2, max=50)])
    SurName = StringField('Surname', [validators.DataRequired(),validators.Length(min=2, max=50)])
    Suffix = SelectField(u'Suffix',[validators.DataRequired()], choices=[('phd','PHD'),('n/a','N/A.')])
    Email = StringField('Email', [validators.DataRequired(),validators.Length(min=3, max=50),validators.Email(message="Invalid email")])
    Institution = SelectField('Institution',choices=[('ucc','UCC'),('ucd','UCD'),('ul','UL'),('dcu','DCU')])
    Phone = IntegerField('Phone', [validators.DataRequired(message="Please enter a valid number")])
    Phone_Extension = SelectField(u'Phone Extension',[validators.DataRequired()], choices=[('353','+353'),('etc','etc.')])


    Password = PasswordField('Password')
    confirm = PasswordField('Confirm Password', [
        validators.DataRequired(),
        validators.EqualTo("Password", message='Passwords do not match')
    ])
class ConsultantRegisterForm(Form):
    Prefix = SelectField(u'Prefix', choices=[('mr','Mr.'),('mrs','Mrs.'),('ms','Ms.'),('dr','Dr.')])
    First_Name = StringField('First Name', [validators.DataRequired(),validators.Length(min=2, max=50)])
    SurName = StringField('Surname', [validators.DataRequired(),validators.Length(min=2, max=50)])
    Suffix = SelectField(u'Suffix',[validators.DataRequired()], choices=[('phd','PHD'),('n/a','N/A.')])
    Email = StringField('Email', [validators.DataRequired(),validators.Length(min=3, max=50),validators.Email(message="Invalid email")])
    Phone = IntegerField('Phone', [validators.DataRequired(message="Please enter a valid number")])
    Phone_Extension = SelectField(u'Phone Extension',[validators.DataRequired()], choices=[('353','+353'),('etc','etc.')])


    Password = PasswordField('Password')
    confirm = PasswordField('Confirm Password', [
        validators.DataRequired(),
        validators.EqualTo("Password", message='Passwords do not match')
    ])

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You must be logged in to view this page', 'danger')
            return redirect(url_for('login'))
    return wrap

@registration_page.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationType(request.form)
    if request.method == 'POST':
        user_type = form.User_Type.data

        if user_type=="R":
            return redirect(url_for('registration_page.researcherRegistration'))
        if user_type == "A":
            flash('To register an administrator,university or consultant account \n you must be logged in as an administrator','danger')
        if user_type == "U":
            flash('To register an administrator,university or consultant account \n you must be logged in as an administrator','danger')
        if user_type == "C":
            flash('To register an administrator,university or consultant account \n you must be logged in as an administrator','danger')


    return render_template('register.html',form=form)

@registration_page.route('/adminRegisterUser', methods=['GET', 'POST'])
@is_logged_in
def adminRegisterUser():
    form = AdminRegistrationType(request.form)
    if request.method == 'POST':
        user_type = form.User_Type.data

        if user_type == "A":
            return redirect(url_for('registration_page.adminRegistration'))
        if user_type == "U":
            return redirect(url_for('registration_page.universityRegistration'))
        if user_type == "C":
            return redirect(url_for('registration_page.reviewerRegistration'))


    return render_template('adminRegisterUser.html',form=form)

@registration_page.route('/adminRegistration', methods=['GET', 'POST'])
@is_logged_in
def adminRegistration():
    form = AdminRegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        prefix = form.Prefix.data
        first_name = form.First_Name.data
        surname = form.SurName.data
        suffix = form.Suffix.data
        email = form.Email.data
        phone = form.Phone.data
        phone_extension = form.Phone_Extension.data
        password = sha256_crypt.encrypt(str(form.Password.data))
        user_type="A"
        is_verified=True
        institution="SFI"
        job_title="Admin"

        try:
            connection = create_connection()
            with connection.cursor() as cursor:
                #Checking if the username is in the database
                user_exists = cursor.execute('SELECT * FROM Users WHERE email = %s', [email])
                if int(user_exists) == 0:
                    cursor.execute('INSERT INTO Users(prefix,first_name,surname,suffix,email,phone,phone_extension,password,user_type,is_verified,institution,job_title) VALUES(%s, %s,%s, %s, %s, %s, %s, %s, %s,%s, %s,%s)', (prefix,first_name,surname,suffix,email,phone,phone_extension,password,user_type,is_verified,institution,job_title))
                    connection.commit()
                    flash('User registered', 'success')
                    return redirect(url_for('registration_page.adminRegisterUser'))
                else:
                    #Redirect if username is taken
                    flash('Email already in use', 'danger')
                    return redirect(url_for('registration_page.adminRegistration'))
        finally:
            connection.close()
    return render_template('/adminRegistration.html',form=form)



@registration_page.route('/reviewerRegistration', methods=['GET', 'POST'])
@is_logged_in
def reviewerRegistration():
    form = ConsultantRegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        prefix = form.Prefix.data
        first_name = form.First_Name.data
        surname = form.SurName.data
        suffix = form.Suffix.data
        email = form.Email.data
        phone = form.Phone.data
        phone_extension = form.Phone_Extension.data
        password = sha256_crypt.encrypt(str(form.Password.data))
        user_type="C"
        is_verified=True
        institution="N/A"
        job_title="Consultant"

        try:
            connection = create_connection()
            with connection.cursor() as cursor:
                #Checking if the username is in the database
                user_exists = cursor.execute('SELECT * FROM Users WHERE email = %s', [email])
                if int(user_exists) == 0:
                    cursor.execute('INSERT INTO Users(prefix,first_name,surname,suffix,email,phone,phone_extension,password,user_type,is_verified,job_title,institution) VALUES(%s, %s,%s, %s, %s, %s, %s, %s, %s,%s, %s,%s)', (prefix,first_name,surname,suffix,email,phone,phone_extension,password,user_type,is_verified,job_title,institution))
                    connection.commit()
                    flash('User registered', 'success')
                    return redirect(url_for('registration_page.adminRegisterUser'))
                else:
                    #Redirect if username is taken
                    flash('Email already in use', 'danger')
                    return redirect(url_for('registration_page.reviewerRegistration'))
        finally:
            connection.close()
    return render_template('/reviewerRegistration.html',form=form)


@registration_page.route('/universityRegistration', methods=['GET', 'POST'])
@is_logged_in
def universityRegistration():
    form = UniversityAdminRegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        prefix = form.Prefix.data
        first_name = form.First_Name.data
        surname = form.SurName.data
        suffix = form.Suffix.data
        email = form.Email.data
        job_title = "University Admin"
        institution = form.Institution.data

        phone = form.Phone.data
        phone_extension = form.Phone_Extension.data
        password = sha256_crypt.encrypt(str(form.Password.data))
        user_type="U"
        is_verified=True

        try:
            connection = create_connection()
            with connection.cursor() as cursor:
                #Checking if the username is in the database
                user_exists = cursor.execute('SELECT * FROM Users WHERE email = %s', [email])
                if int(user_exists) == 0:
                    cursor.execute('INSERT INTO Users(prefix,first_name,surname,suffix,email,job_title,institution,phone,phone_extension,password,user_type,is_verified) VALUES( %s,%s,%s, %s, %s, %s, %s, %s, %s,%s, %s,%s)', (prefix,first_name,surname,suffix,email,job_title,institution,phone,phone_extension,password,user_type,is_verified))
                    connection.commit()
                    flash('User Registered', 'success')
                    return redirect(url_for('registration_page.adminRegisterUser'))
                else:
                    #Redirect if username is taken
                    flash('Email already in use', 'danger')
                    return redirect(url_for('registration_page.universityRegistration'))
        finally:
            connection.close()

    return render_template('universityRegistration.html', form=form)

@registration_page.route('/researcherRegistration', methods=['GET', 'POST'])
def researcherRegistration():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        prefix = form.Prefix.data
        first_name = form.First_Name.data
        surname = form.SurName.data
        suffix = form.Suffix.data
        email = form.Email.data
        job_title = form.Job_Title.data
        institution = form.Institution.data
        orcid=form.Orcid.data
        phone = form.Phone.data
        phone_extension = form.Phone_Extension.data
        password = sha256_crypt.encrypt(str(form.Password.data))
        user_type="R"
        is_verified=False

        try:
            connection = create_connection()
            with connection.cursor() as cursor:
                #Checking if the username is in the database
                user_exists = cursor.execute('SELECT * FROM Users WHERE email = %s', [email])
                if int(user_exists) == 0:
                    cursor.execute('INSERT INTO Users(prefix,first_name,surname,suffix,email,job_title,institution,orcid,phone,phone_extension,password,user_type,is_verified) VALUES(%s, %s,%s,%s, %s, %s, %s, %s, %s, %s,%s, %s,%s)', (prefix,first_name,surname,suffix,email,job_title,institution,orcid,phone,phone_extension,password,user_type,is_verified))
                    connection.commit()
                    flash('You are now registered and can log in', 'success')
                    return redirect(url_for('login'))
                else:
                    #Redirect if username is taken
                    flash('Email already in use', 'danger')
                    return redirect(url_for('registration_page.researcherRegistration'))
        finally:
            connection.close()

    return render_template('researcherRegistration.html', form=form)
