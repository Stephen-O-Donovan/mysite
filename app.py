# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flaskext.mysql import MySQL
from wtforms import Form, SelectField, BooleanField,StringField, TextAreaField, PasswordField, validators, TextField, SubmitField
from passlib.hash import sha256_crypt
from functools import wraps
from pymysql.cursors import DictCursor
#from flask_sslify import SSLify
from utilities import *
from werkzeug.utils import secure_filename



UPLOAD_FOLDER = 'storage/proposals'

app = Flask(__name__)
#sslify = SSLify(app)
app.secret_key = 'alphaHodder'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# Initialise MySQL
mysql = MySQL(cursorclass=DictCursor)
mysql.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

class RegistrationType(Form):
    User_Type = SelectField(u'Register as', choices=[('R','Researcher'),('A','Admin'),('C','Consultant'),('U','University')])

class RegisterForm(Form):
    Prefix = SelectField(u'Prefix', choices=[('mr','Mr.'),('mrs','Mrs.'),('ms','Ms.'),('dr','Dr.')])
    First_Name = StringField('First Name', [validators.DataRequired()])
    SurName = StringField('Surname', [validators.DataRequired(),validators.Length(min=2, max=50)])
    Suffix = SelectField(u'Suffix',[validators.DataRequired()], choices=[('phd','PHD'),('n/a','N/A.')])
    Email = StringField('Email', [validators.DataRequired(),validators.Length(min=3, max=50),validators.Email(message="Invalid email")])
    Job_Title = StringField('Job Title', [validators.DataRequired(),validators.Length(min=2, max=50)])
    Institution = StringField('Institution', [validators.DataRequired(),validators.Length(min=2, max=50)])
    Phone = StringField('Phone', [validators.DataRequired(),validators.Length(min=2, max=50)])
    Phone_Extension = SelectField(u'Phone Extension',[validators.DataRequired()], choices=[('353','+353'),('etc','etc.')])
    Administrator = BooleanField()

    Password = PasswordField('Password')
    confirm = PasswordField('Confirm Password', [
        validators.DataRequired(),
        validators.EqualTo("Password", message='Passwords do not match')
    ])



class CreateProposalForm(Form):
    proposal_name = StringField('Proposal Name', [validators.Length(min=1, max=300)])

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationType(request.form)
    if request.method == 'POST':
        user_type = form.User_Type.data
        
        if user_type=="R":
            return redirect(url_for('researcherRegistration'))
        if user_type == "A":
            return redirect(url_for('adminRegistration'))

    return render_template('register.html',form=form)




@app.route('/researcherRegistration', methods=['GET', 'POST'])
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
        phone = form.Phone.data
        phone_extension = form.Phone_Extension.data
        password = sha256_crypt.encrypt(str(form.Password.data))

        try:
            connection = create_connection()
            with connection.cursor() as cursor:
                #Checking if the username is in the database
                user_exists = cursor.execute('SELECT * FROM Users WHERE email = %s', [email])
                if int(user_exists) == 0:
                    cursor.execute('INSERT INTO Users(prefix,first_name,surname,suffix,email,job_title,institution,phone,phone_extension,password) VALUES( %s,%s, %s, %s, %s, %s, %s, %s,%s, %s)', (prefix,first_name,surname,suffix,email,job_title,institution,phone,phone_extension,password))
                    connection.commit()
                    flash('You are now registered and can log in', 'success')
                    return redirect(url_for('login'))
                else:
                    #Redirect if username is taken
                    flash('Email already in use', 'danger')
                    return redirect(url_for('researcherRegistration'))
        finally:
            connection.close()

    return render_template('researcherRegistration.html', form=form)


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_candidate = request.form['password']
        cursor = create_connection().cursor()
        result = cursor.execute('SELECT * FROM Users WHERE email = %s', [email])
        form = RegistrationType(request.form)
        user_type = form.User_Type.data
        if result > 0:
            data = cursor.fetchone()
            password = data['password']
            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['email'] = email
                #Admin or not
                if user_type == "A":
                    flash('log in as admin', 'success')
                    return redirect(url_for('admindashboard'))
                else:
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

@app.route('/admindashboard')
@is_logged_in
def admindashboard():
    return render_template('admindashboard.html')


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

@app.route('/proposalcreation', methods=['GET', 'POST'])
def create_proposal():
    form = CreateProposalForm(request.form)
    if request.method == 'POST':
        if 'DescriptionOfTargetGroup' not in request.files or 'DescriptionOfProposalDeadlines' not in request.files:
            flash('Please include all files')
            return redirect(request.url)

        description_of_target_group = request.files['DescriptionOfTargetGroup']
        description_of_proposal_deadlines = request.files['DescriptionOfProposalDeadlines']

        if description_of_target_group.filename == '' or description_of_proposal_deadlines.filename == '':
            flash('Please include all files')
            return redirect(request.url)

        if (description_of_target_group and allowed_file(description_of_target_group.filename)) and (description_of_proposal_deadlines and allowed_file(description_of_proposal_deadlines.filename)):
            target_group_filename = secure_filename(description_of_target_group.filename)
            description_of_target_group.save(os.path.join(app.config['UPLOAD_FOLDER'], target_group_filename))
            proposal_deadline_filename = secure_filename(description_of_proposal_deadlines.filename)
            description_of_proposal_deadlines.save(os.path.join(app.config['UPLOAD_FOLDER'], proposal_deadline_filename))

            try:
                connection = create_connection()

                with connection.cursor() as cursor:
                    cursor.execute(
                        'INSERT INTO CFP(proposal_name, description_of_target_group, description_of_proposal_deadlines) VALUES( %s, %s, %s)',
                        (form.proposal_name.data, target_group_filename, proposal_deadline_filename))
                    connection.commit()
                    flash('Your files have been uploaded', 'success')

            finally:
                connection.close()
        else:
            flash('Please select two .pdf files for upload')

    return render_template('admin_create_proposal.html', form=form)


if __name__ == '__main__':
    app.run(ssl_context='adhoc')
