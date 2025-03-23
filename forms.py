from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField, TextAreaField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('staff', 'Staff'), ('admin', 'Admin')])
    submit = SubmitField('Register')

class StudentForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    phone_no = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField('Register Student')

class FeeTypeForm(FlaskForm):
    name = StringField('Fee Name', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Description')
    amount = FloatField('Amount', validators=[DataRequired()])
    frequency = SelectField('Frequency', choices=[
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
        ('one-time', 'One Time')
    ])
    submit = SubmitField('Add Fee Type')

class PaymentForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    fee_type_id = SelectField('Fee Type', coerce=int, validators=[DataRequired()])
    amount = FloatField('Amount (leave blank to use default)', validators=[Optional()])
    payment_method = SelectField('Payment Method', choices=[
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer')
    ])
    reference_no = StringField('Reference Number', validators=[Optional(), Length(max=50)])
    month = SelectField('Month', choices=[
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
        ('NA', 'Not Applicable')
    ])
    year = IntegerField('Year', validators=[DataRequired()])
    submit = SubmitField('Record Payment')