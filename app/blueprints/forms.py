from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password')])


class HabitForm(FlaskForm):
    name = StringField('Habit Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    frequency = SelectField('Frequency', 
                           choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
                           validators=[DataRequired()])


class CompleteHabitForm(FlaskForm):
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])


class RelapseEventForm(FlaskForm):
    trigger_type = SelectField('Trigger Type',
                              choices=[
                                  ('emotional_distress', 'Emotional Distress'),
                                  ('social_situation', 'Social Situation'),
                                  ('environmental_cue', 'Environmental Cue'),
                                  ('stress', 'Stress'),
                                  ('peer_pressure', 'Peer Pressure'),
                                  ('other', 'Other')
                              ],
                              validators=[DataRequired()])
    severity = IntegerField('Severity (1-10)', 
                           validators=[DataRequired(), NumberRange(min=1, max=10)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=1000)])
    occurred_at = StringField('Occurred At', validators=[Optional()])
