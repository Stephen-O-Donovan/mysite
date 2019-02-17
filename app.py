# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flaskext.mysql import MySQL
from wtforms import Form, SelectField, BooleanField,StringField,IntegerField, TextAreaField, PasswordField, validators, TextField, SubmitField
from passlib.hash import sha256_crypt
from functools import wraps
from pymysql.cursors import DictCursor
#from flask_sslify import SSLify
from utilities import *
from werkzeug.utils import secure_filename
from forms import *



UPLOAD_FOLDER = 'storage/proposals'

app = Flask(__name__)
#sslify = SSLify(app)
app.secret_key = 'alphaHodder'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# Initialise MySQL
mysql = MySQL(cursorclass=DictCursor)
mysql.init_app(app)
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

@app.route('/')
def index():
    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            #get data from tables
            cursor.execute('SELECT * FROM CFP')
            cfp_data = cursor.fetchall()
    finally:
        connection.close()
    return render_template('index.html',cfp_data=cfp_data)

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




class CreateProposalForm(Form):
    proposal_name = StringField('Proposal Name', [validators.DataRequired(message='Please enter a name'), validators.Length(min=1, max=300)])
    email = StringField('Email', [validators.DataRequired(), validators.Length(min=3, max=50),
                                  validators.Email(message="Invalid email")])
    description = StringField('Description', [validators.DataRequired(message='Please enter a description'), validators.Length(min=50, max=65000)])
    report_guidelines = TextAreaField('Report Guidelines', [validators.DataRequired(message='Please enter guidelines'), validators.Length(min=20, max=65000)])
    eligibility_criteria = TextAreaField('Eligibility Criteria', [validators.DataRequired(message='Please enter criteria'),
                                                          validators.Length(min=20, max=65000)])
    duration = StringField('Grant Duration', [validators.DataRequired(message='Please enter duration'), validators.Length(min=5, max=20)])
    time_frame = StringField('Start Time Frame', [validators.DataRequired(message='Please enter start time frame'), validators.Length(min=5, max=100)])



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationType(request.form)
    if request.method == 'POST':
        user_type = form.User_Type.data

        if user_type=="R":
            return redirect(url_for('researcherRegistration'))
        if user_type == "A":
            flash('To register an administrator,university or consultant account \n you must be logged in as an administrator','danger')
        if user_type == "U":
            flash('To register an administrator,university or consultant account \n you must be logged in as an administrator','danger')
        if user_type == "C":
            flash('To register an administrator,university or consultant account \n you must be logged in as an administrator','danger')


    return render_template('register.html',form=form)

@app.route('/adminRegisterUser', methods=['GET', 'POST'])
@is_logged_in
def adminRegisterUser():
    form = AdminRegistrationType(request.form)
    if request.method == 'POST':
        user_type = form.User_Type.data

        if user_type == "A":
            return redirect(url_for('adminRegistration'))
        if user_type == "U":
            return redirect(url_for('universityRegistration'))
        if user_type == "C":
            return redirect(url_for('consultantRegistration'))


    return render_template('adminRegisterUser.html',form=form)

@app.route('/adminRegistration', methods=['GET', 'POST'])
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
                    return redirect(url_for('adminRegisterUser'))
                else:
                    #Redirect if username is taken
                    flash('Email already in use', 'danger')
                    return redirect(url_for('adminRegistration'))
        finally:
            connection.close()
    return render_template('/adminRegistration.html',form=form)



@app.route('/consultantRegistration', methods=['GET', 'POST'])
@is_logged_in
def consultantRegistration():
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
                    return redirect(url_for('adminRegisterUser'))
                else:
                    #Redirect if username is taken
                    flash('Email already in use', 'danger')
                    return redirect(url_for('consultantRegistration'))
        finally:
            connection.close()
    return render_template('/consultantRegistration.html',form=form)


@app.route('/universityRegistration', methods=['GET', 'POST'])
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
                    return redirect(url_for('adminRegisterUser'))
                else:
                    #Redirect if username is taken
                    flash('Email already in use', 'danger')
                    return redirect(url_for('universityRegistration'))
        finally:
            connection.close()

    return render_template('universityRegistration.html', form=form)

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
        #user_type = cursor.execute('SELECT user_type FROM Users WHERE email = %s', [email])
        form = RegistrationType(request.form)
        #user_type = form.User_Type.data
        if result > 0:
            data = cursor.fetchone()
            password = data['password']
            user_type = data['user_type']
            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['email'] = email
                #Admin or not
                if user_type == "A":
                    flash('logged in as admin', 'success')
                    return redirect(url_for('adminDashboard'))
                elif user_type == "C":
                    flash('logged in as consultant', 'success')
                    return redirect(url_for('consultantDashboard'))
                elif user_type == "U":
                    flash('logged in as university admin', 'success')
                    return redirect(url_for('universityDashboard'))
                else:
                    flash('logged in as researcher', 'success')
                    return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            cursor.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')



@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    if 'email' in session:
        email = session['email']
    try:
        connection = create_connection()
        with connection.cursor() as cursor:

            #redirect to limited dashboard if not yet verified
            cursor.execute('SELECT is_verified FROM Users WHERE email = %s', [email])
            verified = cursor.fetchone()
            if not verified:
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

@app.route('/adminDashboard')
@is_logged_in
def adminDashboard():
    return render_template('adminDashboard.html')

@app.route('/universityDashboard')
@is_logged_in
def universityDashboard():
    return render_template('universityDashboard.html')


@app.route('/consultantDashboard')
@is_logged_in
def consultantDashboard():
    return render_template('consultantDashboard.html')


@app.route('/profile', methods=['GET', 'POST'])
@is_logged_in
def show_profile():
    form1 = BasicProfileForm(request.form)
    form2 = ProfileEducationForm(request.form)
    form3 = ProfileEmploymentForm(request.form)
    if 'email' in session:
        email = session['email']
    if request.method == 'POST':
        connection = create_connection()
        with connection.cursor() as cursor:
            if request.form['submit'] == 'Save Personal Info':
                cursor.execute('UPDATE Users SET first_name=%s, surname=%s, suffix=%s, job_title=%s, institution=%s,'
                               'orcid=%s, phone=%s, phone_extension=%s'
                               'WHERE email=%s',
                               [form1.first_name.data, form1.surname.data, form1.suffix.data, form1.job_title.data,
                                form1.institution.data, form1.orcid.data, form1.phone.data, form1.phone_extension.data,
                                email])
                connection.commit()

            elif request.form['submit'] == 'Add Education Info':
                cursor.execute('INSERT INTO Profile_Education_Info (email, degree, field_of_study, institution, location, degree_year)'
                               ' VALUES (%s, %s, %s, %s, %s, %s)',
                               [email, form2.degree.data, form2.field_of_study.data, form2.institution.data, form2.location.data, form2.degree_year.data])
                connection.commit()
                pass
            elif request.form['submit'] == 'Remove Education Info':
                cursor.execute('DELETE FROM Profile_Education_Info WHERE degree=%s AND email=%s', [request.form['degree'], email])
                connection.commit()

            elif request.form['submit'] == 'Add Employment Info':
                cursor.execute(
                    'INSERT INTO Profile_Employment (email, institution, location, emp_years)'
                    ' VALUES (%s, %s, %s, %s)',
                    [email, form3.institution.data, form3.location.data, form3.emp_years.data])
                connection.commit()
            elif request.form['submit'] == 'Remove Employment Info':
                cursor.execute('DELETE FROM Profile_Employment WHERE institution=%s AND email=%s',
                               [request.form['institution'], email])
                connection.commit()

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
    return render_template('new_show_profile.html', form1=form1, form2=form2, form3=form3, p1_data=p1_data, p2_data=p2_data, p3_data=p3_data, p4_data=p4_data, p5_data=p5_data, p6_data=p6_data, p7_data=p7_data, p8_data=p8_data, p9_data=p9_data, p10_data=p10_data, p11_data=p11_data, p13_data=p13_data, p14_data=p14_data, p16_data=p16_data, p17_data=p17_data)

@app.route('/proposalcreation', methods=['GET', 'POST'])
@is_logged_in
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
                        'INSERT INTO CFP(proposal_name, description_of_target_group, description_of_proposal_deadlines,'
                        ' email, call_text, report_guidelines, eligibility_criteria, duration, time_frame)'
                        ' VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                        (form.proposal_name.data, target_group_filename, proposal_deadline_filename, form.email.data,
                         form.description.data, form.report_guidelines.data, form.eligibility_criteria.data,
                         form.duration.data, form.time_frame.data))
                    connection.commit()
                    flash('Your files have been uploaded', 'success')

            finally:
                connection.close()
        else:
            flash('Please select two .pdf files for upload')

    return render_template('admin_create_proposal.html', form=form)

@app.route('/pendingProposals')
@is_logged_in
def pendingProposals():
    if 'email' in session:
        email = session['email']
    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM Profile_Publications WHERE email = %s AND pub_status = %s', [email, 'Pending'])
            rows = cursor.fetchall()

    finally:
        connection.close()
    return render_template('pendingProposals.html', rows=rows)

@app.route('/activeProposals')
@is_logged_in
def activeProposals():
    if 'email' in session:
        email = session['email']
    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM Profile_Publications WHERE email = %s AND pub_status = %s', [email, 'Active'])
            rows = cursor.fetchall()

    finally:
        connection.close()
    return render_template('activeProposals.html', rows=rows)

@app.route('/activeProjects')
@is_logged_in
# def activeProjects():
#     if 'email' in session:
#         email = session['email']
#     try:
#         connection = create_connection()
#         with connection.cursor() as cursor:
#             cursor.execute('SELECT * FROM Project WHERE email = %s AND active = %s', [email, 'y'])
#             rows = cursor.fetchall()

    finally:
        connection.close()
    return render_template('activeProjects.html', rows=rows)

@app.route('/pressProposals')
@is_logged_in
def pressProposals():
    if 'email' in session:
        email = session['email']
    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM Profile_Publications WHERE email = %s AND pub_status = %s', [email, 'In press'])
            rows = cursor.fetchall()

    finally:
        connection.close()
    return render_template('pressProposals.html', rows=rows)

@app.route('/fundingstatus')
@is_logged_in
def fundingstatus():
    if 'email' in session:
        email = session['email']
    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM Profile_Funding WHERE email = %s', [email])
            fdata = cursor.fetchall()

    finally:
        connection.close()
    return render_template('fundingStatus.html', fdata=fdata)

@app.route('/reviewproposal')
@is_logged_in
def reviewproposal():
    if 'email' not in session:
        return redirect(url_for('login'))
    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM GrantApplication WHERE submitted = 1 AND declaration_acceptance = 1')
            rpdata = cursor.fetchall()
    finally:
        connection.close()
    return render_template('reviewproposal.html', rpdata=rpdata)

@app.route('/reviewproposa2')
@is_logged_in
def reviewproposal2():
    if 'email' not in session:
        return redirect(url_for('login'))

    try:
        e = request.args.get('e',None)
        proposal_name = request.args.get('proposal_name',None)
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM GrantApplication WHERE submitted=1 AND email = %s AND proposal_name = %s',(e,proposal_name))
            rpdata2 = cursor.fetchone()
            print(rpdata2)
    finally:
        connection.close()
    return render_template('reviewproposal2.html', rpdata2=rpdata2)


if __name__ == '__main__':
    #app.run(ssl_context='adhoc')
    app.run(debug=True)
