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

UPLOAD_FOLDER = 'storage/proposals'
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
    sfi_legal_remit = TextAreaField('SFI Legal Remit')
    ethical_issues = TextAreaField('Ethical Issues')
    applicant_country = StringField('Country', [validators.DataRequired(), validators.Length(min=3, max=50)])
    list_of_co_applicants = StringField('List co-applicants')
    list_of_collaborators = TextAreaField('List collaborators')
    lay_abstract = TextAreaField('Lay Abstract', [validators.DataRequired(message='Please enter lay abstract'), validators.Length(min=20, max=65000)])
    #program_documents = TextAreaField('Program Documents', [validators.DataRequired(message='Please enter program documents'), validators.Length(min=20, max=65000)])
    scientific_abstract = TextAreaField('Scientific Abstract', [validators.DataRequired(message='Please enter scientific abstract'), validators.Length(min=20, max=65000)])
    declaration_acceptance = BooleanField("I agree", [validators.DataRequired(message='Please declare')])

class CreateProposalForm(Form):
    proposal_name = StringField('Proposal Name', [validators.DataRequired(message='Please enter a name'), validators.Length(min=1, max=300)])
    #email = StringField('Email', [validators.DataRequired(), validators.Length(min=3, max=50),
    #                              validators.Email(message="Invalid email")])
    nrp_area = SelectField('NRP Area', [validators.DataRequired(message='Please enter an NRP area')], choices=[('a', 'A'), ('n', 'N'), ('s', 'S')])
    description = StringField('Description', [validators.DataRequired(message='Please enter a description'), validators.Length(min=50, max=65000)])
    report_guidelines = TextAreaField('Report Guidelines', [validators.DataRequired(message='Please enter guidelines'), validators.Length(min=20, max=65000)])
    description_of_target_group = TextAreaField('Description of Target Group', [validators.DataRequired(message='Please enter description'), validators.Length(min=10, max=65000)])

    eligibility_criteria = TextAreaField('Eligibility Criteria', [validators.DataRequired(message='Please enter criteria'),
                                                          validators.Length(min=20, max=65000)])
    duration = StringField('Grant Duration', [validators.DataRequired(message='Please enter duration'), validators.Length(min=5, max=20)])
    time_frame = StringField('Start Time Frame', [validators.DataRequired(message='Please enter start time frame'), validators.Length(min=5, max=100)])


@proposal_page.route('/adminCreateProposal', methods=['GET', 'POST'])
@is_logged_in
def create_proposal():
    form = CreateProposalForm(request.form)
    if request.method == 'POST' and form.validate():
        if 'AdditionalInfo' not in request.files:
            flash('Please include all files')
            return redirect(request.url)

        additional_info_pdf = request.files['AdditionalInfo']

        if additional_info_pdf.filename == '':
            flash('Please include all files')
            return redirect(request.url)

        if (additional_info_pdf and allowed_file(additional_info_pdf.filename)):
            additional_info = secure_filename(additional_info_pdf.filename)
            additional_info_pdf.save(os.path.join(UPLOAD_FOLDER, additional_info))

            try:
                connection = create_connection()

                with connection.cursor() as cursor:
                    cursor.execute(
                        'INSERT INTO CFP(proposal_name, description_of_target_group, additional_info,'
                        ' nrp_area, call_text, report_guidelines, eligibility_criteria, duration, time_frame)'
                        ' VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                        (form.proposal_name.data, form.description_of_target_group.data, additional_info, form.nrp_area.data,
                         form.description.data, form.report_guidelines.data, form.eligibility_criteria.data,
                         form.duration.data, form.time_frame.data))
                    connection.commit()
                    flash('Your files have been uploaded', 'success')

            finally:
                connection.close()
        else:
            flash('Please select a .pdf file for upload')

    return render_template('adminCreateProposal.html', form=form)

@proposal_page.route('/proposalSubmission', methods=['GET', 'POST'])
@is_logged_in
def proposalSubmission():

    form = SubmitProposalForm(request.form)
    proposal_name = request.args.get('proposal_name', '')
    duration = request.args.get('duration', '')
    nrp_area = request.args.get('nrp_area', '')
    ro_approval = 0
    submitted = 1
    application_successful = 0
    program_documents = ""

    if 'email' in session:
        email = session['email']
    if request.method == 'POST' and request.form.get('save'):
        submitted = 0
        proposal_name = request.args.get('proposal_name', '')
        duration = request.args.get('duration', '')
        nrp_area = request.args.get('nrp_area', '')
        try:
            connection = create_connection()
            with connection.cursor() as cursor:
                cursor.execute('SELECT proposal_name FROM GrantApplication WHERE email = %s', [email])
                existing_edit = cursor.fetchone()

                if existing_edit:
                    cursor.execute(
                        'UPDATE GrantApplication'
                        ' SET '
                        ' sfi_legal_remit=%s, ethical_issues=%s, applicant_country=%s, '
                        ' list_of_co_applicants=%s, list_of_collaborators=%s, lay_abstract=%s,'
                        ' program_documents=%s, scientific_abstract=%s'
                        ' WHERE email=%s',
                        (
                            form.sfi_legal_remit.data, form.ethical_issues.data, form.applicant_country.data,
                            form.list_of_co_applicants.data, form.list_of_collaborators.data, form.lay_abstract.data,
                            program_documents, form.scientific_abstract.data, email
                            )
                            )
                    connection.commit()
                    flash('Application saved', 'success')
                    return render_template('proposalSubmission.html', form=form, email=email, proposal_name=proposal_name, duration=duration, nrp_area=nrp_area)

                else:
                    cursor.execute(
                        'INSERT INTO GrantApplication'
                        '(proposal_name, duration_of_award_in_months, nrp_area,'
                        ' sfi_legal_remit, ethical_issues, applicant_country, '
                        ' list_of_co_applicants, list_of_collaborators, lay_abstract,'
                        ' declaration_acceptance, ro_approval, submitted,'
                        ' application_successful, email, '
                        ' program_documents, scientific_abstract)'
                        ' VALUES( '
                        ' %s, %s, %s, '
                        ' %s, %s, %s, '
                        ' %s, %s, %s, '
                        ' %s, %s, %s, '
                        ' %s, %s,'
                        ' %s, %s)',
                        (proposal_name, duration, nrp_area,
                            form.sfi_legal_remit.data, form.ethical_issues.data, form.applicant_country.data,
                            form.list_of_co_applicants.data, form.list_of_collaborators.data, form.lay_abstract.data,
                            1, ro_approval, 0,
                            application_successful, email,
                            program_documents, form.scientific_abstract.data))
                    connection.commit()
                    flash('Application saved', 'success')
                    return render_template('proposalSubmission.html', form=form, email=email, proposal_name=proposal_name, duration=duration, nrp_area=nrp_area)
        finally:
            connection.close()

    if request.method == 'POST' and form.validate():
        if 'ProgramDocuments' not in request.files:
            flash('Please include all files')
            return redirect(request.url)

        program_documents_pdf = request.files['ProgramDocuments']

        if program_documents_pdf.filename == '':
           flash('Please include all files')
           return redirect(request.url)

        if (program_documents_pdf and allowed_file(program_documents_pdf.filename)):
            program_documents = secure_filename(program_documents_pdf.filename)
            program_documents_pdf.save(os.path.join(UPLOAD_FOLDER, program_documents))

            try:
                connection = create_connection()
                with connection.cursor() as cursor:

                    cursor.execute(
                        'INSERT INTO GrantApplication'
                        '(proposal_name, duration_of_award_in_months, nrp_area,'
                        ' sfi_legal_remit, ethical_issues, applicant_country, '
                        ' list_of_co_applicants, list_of_collaborators, lay_abstract,'
                        ' declaration_acceptance, ro_approval, submitted,'
                        ' application_successful, email, '
                        ' program_documents, scientific_abstract)'
                        ' VALUES( '
                        ' %s, %s, %s, '
                        ' %s, %s, %s, '
                        ' %s, %s, %s, '
                        ' %s, %s, %s, '
                        ' %s, %s,'
                        ' %s, %s)',
                        (proposal_name, duration, nrp_area,
                            form.sfi_legal_remit.data, form.ethical_issues.data, form.applicant_country.data,
                            form.list_of_co_applicants.data, form.list_of_collaborators.data, form.lay_abstract.data,
                            1, ro_approval, submitted,
                            application_successful, email,
                            program_documents, form.scientific_abstract.data))
                    connection.commit()
                    #flash('Application sent', 'success')
                    try:
                        cursor.execute('SELECT emails FROM University_Users WHERE university_name = "ucc"')
                        print(cursor.fetchone()['emails'])
                        send_email("joeydelarago@gmail.com", 'Proposal Submitted', 'A member of your institution has made a proposal please review this on your account')
                    except Exception as e:
                        print('Please inter emails for universitys in database')
                        print(e)
                    return render_template('dashboard.html')
            finally:
                connection.close()
        else:
            flash('Please complete all fields')
            return render_template('proposalSubmission.html', form=form, email=email, proposal_name=proposal_name, duration=duration, nrp_area=nrp_area)

    return render_template('proposalSubmission.html', form=form, email=email, proposal_name=proposal_name, duration=duration, nrp_area=nrp_area)

@proposal_page.route('/callForProposals')
@is_logged_in
def callForProposals():
    if 'email' in session:
        email = session['email']
    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            #need to not show cfp that have been submitted
            cursor.execute('SELECT * FROM CFP')
            rows = cursor.fetchall()

    finally:
        connection.close()
    return render_template('callForProposals.html', rows=rows, email=email)


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

@proposal_page.route('/savedProposals')
@is_logged_in
def savedProposals():

    proposal_name = request.args.get('proposal_name', '')
    nrp_area = request.args.get('nrp_area', '')
    duration = request.args.get('duration', '')

    if 'email' in session:
        email = session['email']

    edit = request.args.get('edit', '')
    delete = request.args.get('delete', '')

    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM GrantApplication WHERE email = %s', [email])
            rows = cursor.fetchall()
            if edit:
                #return render_template('proposalEditSubmission.html', proposal_name=proposal_name, duration=duration, nrp_area=nrp_area)
                return proposalEditSubmission(proposal_name, duration, nrp_area)

            if delete:
                cursor.execute('DELETE FROM GrantApplication WHERE email=%s AND proposal_name=%s', [email, proposal_name])
                connection.commit()
                return render_template('savedProposals.html', rows=rows, proposal_name=proposal_name)

    finally:
        connection.close()
    return render_template('savedProposals.html', rows=rows, proposal_name=proposal_name)

@proposal_page.route('/proposalEditSubmission')
@is_logged_in
def proposalEditSubmission(proposal_name, duration, nrp_area):

    form = SubmitProposalForm(request.form)
    #proposal_name = request.args.get('proposal_name', '')
    #duration = request.args.get('duration', '')
    #nrp_area = request.args.get('nrp_area', '')
    proposal_name = proposal_name
    duration = duration
    nrp_area = nrp_area


    ro_approval = 0
    submitted = 1
    application_successful = 0
    program_documents = ""

    if 'email' in session:
        email = session['email']

    try:
        connection = create_connection()
        with connection.cursor() as cursor:

            cursor.execute('SELECT * FROM GrantApplication WHERE email = %s and proposal_name = %s', [email, proposal_name])
            g_data = cursor.fetchall()

            if request.method == 'POST' and request.form['save'] == 'Save':
                submitted = 0
                proposal_name = request.args.get('proposal_name', '')
                duration = request.args.get('duration', '')
                nrp_area = request.args.get('nrp_area', '')
                cursor.execute('SELECT proposal_name FROM GrantApplication WHERE email = %s', [email])
                existing_edit = cursor.fetchone()

                if existing_edit:
                    cursor.execute(
                        'UPDATE GrantApplication'
                        ' SET '
                        ' sfi_legal_remit=%s, ethical_issues=%s, applicant_country=%s, '
                        ' list_of_co_applicants=%s, list_of_collaborators=%s, lay_abstract=%s,'
                        ' program_documents=%s, scientific_abstract=%s'
                        ' WHERE email=%s',
                        (
                            form.sfi_legal_remit.data, form.ethical_issues.data, form.applicant_country.data,
                            form.list_of_co_applicants.data, form.list_of_collaborators.data, form.lay_abstract.data,
                            program_documents, form.scientific_abstract.data, email
                            )
                            )
                    connection.commit()
                    flash('Application saved', 'success')
                    return render_template('proposalEditSubmission.html', form=form, email=email, proposal_name=proposal_name, duration=duration, nrp_area=nrp_area)

                else:
                    cursor.execute(
                        'INSERT INTO GrantApplication'
                        '(proposal_name, duration_of_award_in_months, nrp_area,'
                        ' sfi_legal_remit, ethical_issues, applicant_country, '
                        ' list_of_co_applicants, list_of_collaborators, lay_abstract,'
                        ' declaration_acceptance, ro_approval, submitted,'
                        ' application_successful, email, '
                        ' program_documents, scientific_abstract)'
                        ' VALUES( '
                        ' %s, %s, %s, '
                        ' %s, %s, %s, '
                        ' %s, %s, %s, '
                        ' %s, %s, %s, '
                        ' %s, %s,'
                        ' %s, %s)',
                        (proposal_name, duration, nrp_area,
                            form.sfi_legal_remit.data, form.ethical_issues.data, form.applicant_country.data,
                            form.list_of_co_applicants.data, form.list_of_collaborators.data, form.lay_abstract.data,
                            1, ro_approval, 0,
                            application_successful, email,
                            program_documents, form.scientific_abstract.data))
                    connection.commit()
                    flash('Application saved', 'success')
                    return render_template('proposalEditSubmission.html', form=form, email=email, proposal_name=proposal_name, duration=duration, nrp_area=nrp_area)

            if request.method == 'POST' and form.validate():
                if 'ProgramDocuments' not in request.files:
                    flash('Please include all files')
                    return redirect(request.url)

                program_documents_pdf = request.files['ProgramDocuments']

                if program_documents_pdf.filename == '':
                   flash('Please include all files')
                   return redirect(request.url)

                if (program_documents_pdf and allowed_file(program_documents_pdf.filename)):
                    program_documents = secure_filename(program_documents_pdf.filename)
                    program_documents_pdf.save(os.path.join(UPLOAD_FOLDER, program_documents))

                    cursor.execute(
                        'INSERT INTO GrantApplication'
                        '(proposal_name, duration_of_award_in_months, nrp_area,'
                        ' sfi_legal_remit, ethical_issues, applicant_country, '
                        ' list_of_co_applicants, list_of_collaborators, lay_abstract,'
                        ' declaration_acceptance, ro_approval, submitted,'
                        ' application_successful, email, '
                        ' program_documents, scientific_abstract)'
                        ' VALUES( '
                        ' %s, %s, %s, '
                        ' %s, %s, %s, '
                        ' %s, %s, %s, '
                        ' %s, %s, %s, '
                        ' %s, %s,'
                        ' %s, %s)',
                        (proposal_name, duration, nrp_area,
                            form.sfi_legal_remit.data, form.ethical_issues.data, form.applicant_country.data,
                            form.list_of_co_applicants.data, form.list_of_collaborators.data, form.lay_abstract.data,
                            1, ro_approval, submitted,
                            application_successful, email,
                            program_documents, form.scientific_abstract.data))
                    connection.commit()
                    #flash('Application sent', 'success')
                    return render_template('dashboard.html')
                else:
                    flash('Please complete all fields')
                    return redirect(request.url)
    finally:
        connection.close()

    return render_template('proposalEditSubmission.html', form=form, g_data=g_data, email=email, proposal_name=proposal_name, duration=duration, nrp_area=nrp_area)

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
            cursor.execute('SELECT * FROM GrantApplication WHERE submitted = 1 AND declaration_acceptance = 1 AND university_accepted = 1 AND reviewer_accepted = 1 AND admin_accepted = 1')
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
    finally:
        connection.close()
    return render_template('reviewIndividualProposal.html', rpdata2=rpdata2)


@proposal_page.route('/universityReviewListProposal')
@is_logged_in
def universityReviewListProposal():
    if 'email' not in session:
        return redirect(url_for('login'))

    accept = request.args.get('accept',None)
    pn = request.args.get('pn',None)
    email = request.args.get('email',None)

    if accept !=None:
        try:
            connection = create_connection()
            with connection.cursor() as cursor:
            #1 is accepted
                if accept == '1':
                    cursor.execute('UPDATE GrantApplication SET university_accepted = 1 WHERE proposal_name = %s AND email = %s',[pn,email])
                    connection.commit()
                    display = 'Proposal', pn, 'from researcher',email,'has been accepted.'
                    flash(display,'success')
                else:
                    cursor.execute('DELETE FROM GrantApplication WHERE proposal_name = %s AND email = %s',[pn,email])
                    connection.commit()
                    display='Proposal', pn, 'from researcher',email,'has been rejected.'
                    print('Proposal "%s" from researcher %s has been rejected.',[pn, email])
                    flash(display,'success')
                    try:
                        send_email(email, 'Proposal Rejected', 'Your proposal has been rejected by: Your institution')
                    except:
                        print('Please enter valid emails for users')
                cursor.execute('SELECT * FROM GrantApplication WHERE submitted = 1 AND declaration_acceptance = 1 AND university_accepted = 0 AND reviewer_accepted = 0 AND admin_accepted = 0')
                urpdata = cursor.fetchall()
                return render_template('universityReviewListProposal.html', urpdata=urpdata)
        finally:
            connection.close()

    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM GrantApplication WHERE submitted = 1 AND declaration_acceptance = 1 AND university_accepted = 0 AND reviewer_accepted = 0 AND admin_accepted = 0')
            urpdata = cursor.fetchall()
    finally:
        connection.close()
    return render_template('universityReviewListProposal.html', urpdata=urpdata)

@proposal_page.route('/universityReviewIndividualProDetail')
@is_logged_in
def universityReviewIndividualProDetail():
    if 'email' not in session:
        return redirect(url_for('login'))

    try:
        e = request.args.get('e',None)
        proposal_name = request.args.get('proposal_name',None)
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM GrantApplication WHERE submitted=1 AND email = %s AND proposal_name = %s',(e,proposal_name))
            urpdata2 = cursor.fetchone()
    finally:
        connection.close()
    return render_template('universityReviewIndividualProDetail.html', urpdata2=urpdata2)


@proposal_page.route('/reviewerReviewListProposal')
@is_logged_in
def reviewerReviewListProposal():
    if 'email' not in session:
        return redirect(url_for('login'))

    accept = request.args.get('accept',None)
    pn = request.args.get('pn',None)
    email = request.args.get('email',None)

    if accept !=None:
        try:
            connection = create_connection()
            with connection.cursor() as cursor:
            #1 is accepted
                if accept == '1':
                    cursor.execute('UPDATE GrantApplication SET reviewer_accepted = 1 WHERE proposal_name = %s AND email = %s',[pn,email])
                    connection.commit()
                    display = 'Proposal', pn, 'from researcher',email,'has been accepted.'
                    flash(display,'success')
                else:
                    cursor.execute('DELETE FROM GrantApplication WHERE proposal_name = %s AND email = %s',[pn,email])
                    connection.commit()
                    display='Proposal', pn, 'from researcher',email,'has been rejected.'
                    try:
                        send_email(email, 'Proposal Rejected', 'Your proposal has been rejected by: A reviewer')
                    except:
                        print('Please enter valid emails for users')
                    flash(display,'success')
                cursor.execute('SELECT * FROM GrantApplication WHERE submitted = 1 AND declaration_acceptance = 1 AND university_accepted = 1 AND reviewer_accepted = 0 AND admin_accepted = 0')
                urpdata = cursor.fetchall()
                return render_template('reviewerReviewListProposal.html', urpdata=urpdata)
        finally:
            connection.close()

    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM GrantApplication WHERE submitted = 1 AND declaration_acceptance = 1 AND university_accepted = 1 AND reviewer_accepted = 0 AND admin_accepted = 0')
            urpdata = cursor.fetchall()
    finally:
        connection.close()
    return render_template('reviewerReviewListProposal.html', urpdata=urpdata)

@proposal_page.route('/reviewerReviewIndividualProDetail')
@is_logged_in
def reviewerReviewIndividualProDetail():
    if 'email' not in session:
        return redirect(url_for('login'))

    try:
        e = request.args.get('e',None)
        proposal_name = request.args.get('proposal_name',None)
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM GrantApplication WHERE submitted=1 AND email = %s AND proposal_name = %s',(e,proposal_name))
            urpdata2 = cursor.fetchone()
    finally:
        connection.close()
    return render_template('reviewerReviewIndividualProDetail.html', urpdata2=urpdata2)


@proposal_page.route('/adminReviewListProposal')
@is_logged_in
def adminReviewListProposal():
    if 'email' not in session:
        return redirect(url_for('login'))

    accept = request.args.get('accept',None)
    pn = request.args.get('pn',None)
    email = request.args.get('email',None)

    if accept !=None:
        try:
            connection = create_connection()
            with connection.cursor() as cursor:
            #1 is accepted
                if accept == '1':
                    cursor.execute('UPDATE GrantApplication SET admin_accepted = 1 WHERE proposal_name = %s AND email = %s',[pn,email])
                    connection.commit()
                    display = 'Proposal', pn, 'from researcher',email,'has been accepted.'
                    flash(display,'success')
                else:
                    cursor.execute('DELETE FROM GrantApplication WHERE proposal_name = %s AND email = %s',[pn,email])
                    connection.commit()
                    display='Proposal', pn, 'from researcher',email,'has been rejected.'
                    try:
                        send_email(email, 'Proposal Rejected', 'Your proposal has been rejected by: An SFI Admin')
                    except:
                        print('Please enter valid emails for users')
                    flash(display,'success')
                cursor.execute('SELECT * FROM GrantApplication WHERE submitted = 1 AND declaration_acceptance = 1 AND admin_accepted = 0')
                urpdata = cursor.fetchall()
                return render_template('adminReviewListProposal.html', urpdata=urpdata)
        finally:
            connection.close()

    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM GrantApplication WHERE submitted = 1 AND declaration_acceptance = 1 AND admin_accepted = 0')
            urpdata = cursor.fetchall()
    finally:
        connection.close()
    return render_template('adminReviewListProposal.html', urpdata=urpdata)

@proposal_page.route('/adminReviewIndividualProDetail')
@is_logged_in
def adminReviewIndividualProDetail():
    if 'email' not in session:
        return redirect(url_for('login'))

    try:
        e = request.args.get('e',None)
        proposal_name = request.args.get('proposal_name',None)
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM GrantApplication WHERE submitted=1 AND email = %s AND proposal_name = %s',(e,proposal_name))
            urpdata2 = cursor.fetchone()
    finally:
        connection.close()
    return render_template('adminReviewIndividualProDetail.html', urpdata2=urpdata2)
