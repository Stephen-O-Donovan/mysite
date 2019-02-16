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

class BasicProfileForm(Form):
    prefix = SelectField(u'Prefix', choices=[('mr','Mr.'),('mrs','Mrs.'),('ms','Ms.'),('dr','Dr.')])
    first_name = StringField('First Name', [validators.DataRequired(),validators.Length(min=2, max=20)])
    surname = StringField('Surname', [validators.DataRequired(),validators.Length(min=2, max=50)])
    suffix = SelectField(u'Suffix',[validators.DataRequired()], choices=[('phd','PHD'),('n/a','N/A.')])
    # email = StringField('Email', [validators.DataRequired(),validators.Length(min=3, max=50),validators.Email(message="Invalid email")])
    job_title = StringField('Job Title', [validators.DataRequired(),validators.Length(min=2, max=20)])
    institution = SelectField('Institution',choices=[('ucc','UCC'),('ucd','UCD'),('ul','UL'),('dcu','DCU')])
    orcid = StringField('Orcid')
    phone = IntegerField('Phone', [validators.DataRequired(message="Please enter a valid number")])
    phone_extension = SelectField(u'Phone Extension',[validators.DataRequired()], choices=[('353','+353'),('etc','etc.')])


    # password = PasswordField('Password')
    # confirm = PasswordField('Confirm Password', [
    #     validators.EqualTo("Password", message='Passwords do not match')
    # ])


class ProfileAcademicColForm(Form):
    start_date = DateField('Start Date', [validators.DataRequired()])
    end_date = DateField('End Date', [validators.DataRequired()])
    institution_name = StringField('Name of Institution', [validators.DataRequired(), validators.Length(min=2, max=30)])
    department_in_institution = StringField('Department within Institution', [validators.DataRequired(), validators.Length(min=2, max=30)])
    location = StringField('Location', [validators.DataRequired(), validators.Length(min=2, max=50)])
    collaborator_name = StringField('Name of Collaborator', [validators.DataRequired(), validators.Length(min=2, max=30)])
    primary_goal = StringField('Primary Goal of Collaboration', [validators.DataRequired(), validators.Length(min=2, max=60)])
    frequency_of_interaction = IntegerField('Frequency Of Interaction', [validators.DataRequired(message="Please enter a valid number")])
    grant_no = StringField('Primary Attribution', [validators.DataRequired(), validators.Length(min=1, max=18)])

class ProfileCommunicationForm(Form):
    comm_year = IntegerField('Year', [validators.DataRequired(), validators.number_range(min=1900, max=date.today().year)])
    public_lecture_no = IntegerField('Number of Public lectures/Demonstrations', [validators.DataRequired(message="Please enter a valid number")])
    visits_no = IntegerField('Number of Visits', [validators.DataRequired(message="Please enter a valid number")])
    media_interaction_no = IntegerField('Number of Media Interactions', [validators.DataRequired(message="Please enter a valid number")])

class ProfileDandAForm(Form):
    DandA_year = IntegerField('Year', [validators.DataRequired(), validators.number_range(min=1900, max=date.today().year)])
    award_body = StringField('Awarding Body', [validators.DataRequired(), validators.Length(min=2, max=50)])
    detail = StringField('Details of Award', [validators.DataRequired(), validators.Length(min=2, max=500)])
    teamate_name = StringField('Team Member Name', [validators.DataRequired(), validators.Length(min=2, max=50)])

class ProfileEducationForm(Form):
    degree = StringField('Degree', [validators.DataRequired(),validators.Length(min=2, max=50)])
    field_of_study = StringField('Field Of Study', [validators.DataRequired(), validators.Length(min=2, max=20)])
    institution = StringField('Institution', [validators.DataRequired(), validators.Length(min=2, max=50)])
    location = StringField('Location', [validators.DataRequired(), validators.Length(min=2, max=50)])
    degree_year = IntegerField('Degree Year', [validators.DataRequired(), validators.number_range(min=1900, max=date.today().year)])

class ProfileEmploymentForm(Form):
    institution = StringField('Institution', [validators.DataRequired(), validators.Length(min=2, max=50)])
    location = StringField('Location', [validators.DataRequired(), validators.Length(min=2, max=50)])
    emp_years = IntegerField('Years', [validators.DataRequired(message="Please enter a valid number")])

class ProfileFundingForm(Form):
    start_date = DateField('Start Date', [validators.DataRequired()])
    end_date = DateField('End Date', [validators.DataRequired()])
    amount_fund = StringField('Amount of Funding', [validators.DataRequired(), validators.Length(min=2, max=50)])
    fund_body = StringField('Funding Body', [validators.DataRequired(), validators.Length(min=2, max=30)])
    fund_program = StringField('Funding Program', [validators.DataRequired(), validators.Length(min=2, max=30)])
    status = StringField('Status', [validators.DataRequired(), validators.Length(min=1, max=10)])
    grant_no = StringField('Primary Attribution', [validators.DataRequired(), validators.Length(min=1, max=18)])

class ProfileIandCForm(Form):
    year = IntegerField('Year', [validators.DataRequired(), validators.number_range(min=1900, max=date.today().year)])
    type = StringField('Type', [validators.DataRequired(), validators.Length(min=2, max=10)])
    title = StringField('Title', [validators.DataRequired(), validators.Length(min=2, max=20)])
    grant_no = StringField('Primary Attribution', [validators.DataRequired(), validators.Length(min=1, max=18)])

class ProfileImpactForm(Form):
    impact_title = StringField('Impact Title', [validators.DataRequired(), validators.Length(min=2, max=20)])
    impact_category = StringField('Impact Category', [validators.DataRequired(), validators.Length(min=2, max=20)])
    primary_beneficiary = StringField('Primary Beneficiary', [validators.DataRequired(), validators.Length(min=2, max=20)])
    grant_no = StringField('Primary Attribution', [validators.DataRequired(), validators.Length(min=1, max=18)])

class ProfileNonAcademicColForm(Form):
    start_date = DateField('Start Date', [validators.DataRequired()])
    end_date = DateField('End Date', [validators.DataRequired()])
    institution_name = StringField('Name of Institution', [validators.DataRequired(), validators.Length(min=2, max=30)])
    department_in_institution = StringField('Department within Institution', [validators.DataRequired(), validators.Length(min=2, max=30)])
    location = StringField('Location', [validators.DataRequired(), validators.Length(min=2, max=50)])
    collaborator_name = StringField('Name of Collaborator', [validators.DataRequired(), validators.Length(min=2, max=30)])
    primary_goal = StringField('Primary Goal of Collaboration', [validators.DataRequired(), validators.Length(min=2, max=60)])
    frequency_of_interaction = IntegerField('Frequency Of Interaction', [validators.DataRequired(message="Please enter a valid number")])
    grant_no = StringField('Primary Attribution', [validators.DataRequired(), validators.Length(min=1, max=18)])

class ProfilePresentationForm(Form):
    presentation_year = IntegerField('Year', [validators.DataRequired(), validators.number_range(min=1900, max=date.today().year)])
    title = StringField('Title of Presentation', [validators.DataRequired(), validators.Length(min=2, max=20)])
    evt_type = StringField('Event Type', [validators.DataRequired(), validators.Length(min=2, max=20)])
    org_body = StringField('Organising Body', [validators.DataRequired(), validators.Length(min=2, max=30)])
    location = StringField('Location', [validators.DataRequired(), validators.Length(min=2, max=50)])
    grant_no = StringField('Primary Attribution', [validators.DataRequired(), validators.Length(min=1, max=18)])

class ProfileProfessSocForm(Form):
    start_date = DateField('Start Date', [validators.DataRequired()])
    end_date = DateField('End Date', [validators.DataRequired()])
    name_of_soc = StringField('Name Of Society', [validators.DataRequired(), validators.Length(min=2, max=50)])
    type_of_membership = StringField('Type of Membership', [validators.DataRequired(), validators.Length(min=2, max=30)])
    status = StringField('Status', [validators.DataRequired(), validators.Length(min=2, max=10)])

class ProfilePublicEngagementForm(Form):
    project_name = StringField('Name of project', [validators.DataRequired(), validators.Length(min=2, max=20)])
    start_date = DateField('Start Date', [validators.DataRequired()])
    end_date = DateField('End Date', [validators.DataRequired()])
    activity_type = StringField('Activity Type', [validators.DataRequired(), validators.Length(min=2, max=30)])
    project_topic = StringField('Project Topic', [validators.DataRequired(), validators.Length(min=2, max=20)])
    target_area = StringField('Target Geographical Area', [validators.DataRequired(), validators.Length(min=2, max=50)])
    grant_no = StringField('Primary Attribution', [validators.DataRequired(), validators.Length(min=1, max=18)])

class ProfilePublicationsForm(Form):
    pub_yr = IntegerField('Publication Year', [validators.DataRequired(), validators.number_range(min=1900, max=date.today().year)])
    pub_type = StringField('Publication Type', [validators.DataRequired(), validators.Length(min=2, max=26)])
    title = StringField('Title', [validators.DataRequired(), validators.Length(min=2, max=20)])
    journal_name = StringField('Journal/Conference Name', [validators.DataRequired(), validators.Length(min=2, max=30)])
    pub_status = StringField('Publication Status', [validators.DataRequired(), validators.Length(min=2, max=9)])
    DOI = StringField('DOI', [validators.DataRequired(), validators.Length(min=2, max=20)])
    grant_no = StringField('Primary Attribution', [validators.DataRequired(), validators.Length(min=1, max=18)])

class ProfileSFIFundRatioForm(Form):
    fund_year = IntegerField('Year', [validators.DataRequired(), validators.number_range(min=1900, max=date.today().year)])
    percentage = StringField('Percentage of Annual Spend From SFI', [validators.DataRequired(), validators.Length(min=1, max=6)])

class ProfileTeamateForm(Form):
    start_date = DateField('Start Date with Team', [validators.DataRequired()])
    depart_date = DateField('Departure date', [validators.DataRequired()])
    name = StringField('Name', [validators.DataRequired(), validators.Length(min=2, max=20)])
    position = StringField('Position within the Team', [validators.DataRequired(), validators.Length(min=2, max=20)])
    grant_no = StringField('Primary Attribution', [validators.DataRequired(), validators.Length(min=1, max=18)])

class ProfileWorkshopForm(Form):
    start_date = DateField('Start Date', [validators.DataRequired()])
    depart_date = DateField('End Date', [validators.DataRequired()])
    title = StringField('Title', [validators.DataRequired(), validators.Length(min=2, max=20)])
    evt_type = StringField('Event Type', [validators.DataRequired(), validators.Length(min=2, max=10)])
    evt_role = StringField('Role', [validators.DataRequired(), validators.Length(min=2, max=20)])
    evt_location = StringField('Location of Event', [validators.DataRequired(), validators.Length(min=2, max=50)])
    grant_no = StringField('Primary Attribution', [validators.DataRequired(), validators.Length(min=1, max=18)])
