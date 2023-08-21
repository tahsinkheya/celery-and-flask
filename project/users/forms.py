from flask_wtf import FlaskForm
from wtforms import  StringField, validators,IntegerField

class YourForm(FlaskForm):
    username=StringField('Username', [validators.Length(min=4, max=25)])
    # email=StringField('Email', [validators.Length(min=6, max=35)])
    # username=IntegerField('Username')
    email=IntegerField('Email')
