from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, FieldList, FormField
from wtforms import DateField, SelectField, SelectMultipleField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import ValidationError, DataRequired
from app.models import Users, Problems

class TestCaseForm(FlaskForm):
    input = TextAreaField("Input", validators=[DataRequired()])

class ExamplesForm(FlaskForm):
    input = TextAreaField("Input", validators=[DataRequired()])
    output = TextAreaField("Output", validators=[DataRequired()])

class QuestionForm(FlaskForm):
    title = StringField("Question title", validators=[DataRequired()])
    question = TextAreaField("Question content", validators=[DataRequired()])
    version = IntegerField("Version number")
    solution = TextAreaField("Solution", validators=[DataRequired()])
    examples = FieldList(FormField(ExamplesForm), min_entries=1)
    testcases = FieldList(FormField(TestCaseForm), min_entries=2)
    submit = SubmitField('Submit')

class CourseForm(FlaskForm):
    title = StringField("Course title", validators=[DataRequired()])
    startdate = DateField("Start date (mm/dd/yyyy)", format='%m/%d/%Y')
    enddate = DateField("End date (mm/dd/yyyy)", format='%m/%d/%Y')
    semester = StringField("Semester (Fall 2018)")
    submit = SubmitField('Submit')

class AssignmentForm(FlaskForm):
    problem = SelectMultipleField("Problems")
    startdate = DateField("Start date (mm/dd/yyyy)", format='%m/%d/%Y')
    enddate = DateField("End date (mm/dd/yyyy)", format='%m/%d/%Y')
    submit = SubmitField('Submit')
