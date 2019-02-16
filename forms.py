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

class ProfileEducationForm(Form):
    degree = StringField('Degree', [validators.DataRequired(),validators.Length(min=2, max=20)])
    field_of_study = StringField('Field Of Study', [validators.DataRequired(), validators.Length(min=2, max=50)])
    institution = StringField('Institution', [validators.DataRequired(), validators.Length(min=2, max=50)])
    location = StringField('Location', [validators.DataRequired(), validators.Length(min=2, max=20)])
    degree_year = IntegerField('Degree Year', [validators.DataRequired(), validators.number_range(min=1900, max=date.today().year)])
