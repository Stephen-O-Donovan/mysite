import os
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flaskext.mysql import MySQL
from wtforms import Form, SelectField, BooleanField,StringField,IntegerField, TextAreaField, PasswordField, validators, TextField, SubmitField, DateField
from passlib.hash import sha256_crypt
from functools import wraps
from pymysql.cursors import DictCursor
#from flask_sslify import SSLify
from utilities import *
from werkzeug.utils import secure_filename
from datetime import date

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
