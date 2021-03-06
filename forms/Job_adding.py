from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, IntegerField, BooleanField
from wtforms.validators import DataRequired


class JobAddingForm(FlaskForm):
    job = StringField('Job', validators=[DataRequired()])
    work_hours = IntegerField('Work Hours', validators=[DataRequired()])
    team_leader = IntegerField('Team Leader id', validators=[DataRequired()])
    collaborators = StringField('Collaborators', validators=[DataRequired()])
    category = IntegerField('Hazard category(1-3)', validators=[DataRequired()])
    is_finished = BooleanField('Is job finished?')
    submit = SubmitField('Submit')
