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

proposal_page = Blueprint('proposal_page', __name__, template_folder='templates')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You must be logged in to view this page', 'danger')
            return redirect(url_for('login'))
    return wrap

class SubmitProposalForm(Form):
    # will display proposal name, duration and applicants email as uneditable fields
    ethical_issues = TextAreaField('Ethical Issues')
    applicant_country = StringField('Country', [validators.DataRequired(), validators.Length(min=3, max=50)])
    list_of_co_applicants = StringField('List co-applicants')
    list_of_collaborators = TextAreaField('List collaborators')
    lay_abstract = TextAreaField('Lay Abstract', [validators.DataRequired(message='Please enter lay abstract'), validators.Length(min=20, max=65000)])
    program_documents = TextAreaField('Program Documents', [validators.DataRequired(message='Please enter program documents'), validators.Length(min=20, max=65000)])
    scientific_abstract = TextAreaField('Scientific Abstract', [validators.DataRequired(message='Please enter scientific abstract'), validators.Length(min=20, max=65000)])


class CreateProposalForm(Form):
    proposal_name = StringField('Proposal Name', [validators.DataRequired(message='Please enter a name'), validators.Length(min=1, max=300)])
    #email = StringField('Email', [validators.DataRequired(), validators.Length(min=3, max=50),
    #                              validators.Email(message="Invalid email")])
    nrp_area = StringField('Description', [validators.DataRequired(message='Please enter an NRP area'), validators.Length(min=1, max=1)])
    description = StringField('Description', [validators.DataRequired(message='Please enter a description'), validators.Length(min=50, max=65000)])
    report_guidelines = TextAreaField('Report Guidelines', [validators.DataRequired(message='Please enter guidelines'), validators.Length(min=20, max=65000)])
    eligibility_criteria = TextAreaField('Eligibility Criteria', [validators.DataRequired(message='Please enter criteria'),
                                                          validators.Length(min=20, max=65000)])
    duration = StringField('Grant Duration', [validators.DataRequired(message='Please enter duration'), validators.Length(min=5, max=20)])
    time_frame = StringField('Start Time Frame', [validators.DataRequired(message='Please enter start time frame'), validators.Length(min=5, max=100)])

@proposal_page.route('/adminCreateProposal', methods=['GET', 'POST'])
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
                        ' nrp_area, call_text, report_guidelines, eligibility_criteria, duration, time_frame)'
                        ' VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                        (form.proposal_name.data, target_group_filename, proposal_deadline_filename, form.nrp_area.data,
                         form.description.data, form.report_guidelines.data, form.eligibility_criteria.data,
                         form.duration.data, form.time_frame.data))
                    connection.commit()
                    flash('Your files have been uploaded', 'success')

            finally:
                connection.close()
        else:
            flash('Please select two .pdf files for upload')

    return render_template('adminCreateProposal.html', form=form)

@proposal_page.route('/pendingProposals')
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

@proposal_page.route('/activeProposals')
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

@proposal_page.route('/pressProposals')
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

@proposal_page.route('/pastProposals')
@is_logged_in
def pastProposals():
    if 'email' in session:
        email = session['email']
    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM GrantApplication WHERE email = %s AND submitted = %s', [email, '1'])
            rows = cursor.fetchall()

    finally:
        connection.close()
    return render_template('pastProposals.html', rows=rows)

@proposal_page.route('/reviewproposal')
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

@proposal_page.route('/reviewIndividualProposal')
@is_logged_in
def reviewIndividualProposal():
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
    return render_template('reviewIndividualProposal.html', rpdata2=rpdata2)
