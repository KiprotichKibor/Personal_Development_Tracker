from datetime import datetime, date
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from flask_login import current_user
from wtforms import StringField, FileField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from waweza.models import User, GoalType, StatusType, Goal, Habit, HabitLog, MoodType, Mood

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ResendVerificationForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Resend Verification Email')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class GoalForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    type = SelectField('Type',
                       choices=[(goal_type.value, goal_type.name.capitalize()) for goal_type in GoalType],
                       validators=[DataRequired()])
    status = SelectField('Status',
                       choices=[(status_type.value, status_type.name.capitalize()) for status_type in StatusType],
                       validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_end_date(form, field):
        if field.data < form.start_date.data:
            raise ValidationError('End date must be after start date.')
        
class HabitForm(FlaskForm):
    name = StringField('Habit Name', validators=[DataRequired()])
    goal = SelectField('Associated Goal', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Habit')

class HabitLogForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    completed = BooleanField('Completed') 
    submit = SubmitField('Log Habit')

class HabitStatusForm(FlaskForm):
    status = SelectField('Status', choices=[('completed', 'Completed'), ('not_completed', 'Not Completed')], validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Update Status')

class MoodForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], default=date.today)
    mood_type = SelectField('Mood', choices=[(mood.name, mood.value) for mood in MoodType], validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Log Mood')