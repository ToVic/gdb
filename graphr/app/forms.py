''' forms using WTForms '''
from wtforms import Form, StringField, validators, TextAreaField, SelectField
from .neo import Neo_client

Neo = Neo_client()

DEPT_CHOICES = [dept['name'] for dept in Neo.get_all_depts()]
DIR_POSITION = ['director']
DEPT_CHOICES.append(DIR_POSITION)

class NewDeptForm(Form):

    name = StringField('name', [validators.length(min=3, max=20), validators.DataRequired()])
    description = TextAreaField('description', [validators.length(min=10, max=160), 
                validators.DataRequired()], render_kw={'class': 'form-control', 'rows': 5, 'columns': 50})


class NewEmployeeForm(Form):

    surname=StringField('surname', [validators.length(min=3, max=20), validators.DataRequired()])
    name=StringField('name', [validators.length(min=3, max=20), validators.DataRequired()])
    department=SelectField('department', [validators.DataRequired()], choices = DEPT_CHOICES)
    position=StringField('position', [validators.length(min=3, max=20), validators.DataRequired()])
    skills=StringField('skills', [validators.length(min=3, max=30), validators.DataRequired()])
    note=TextAreaField('note', [validators.length(min=10, max=150), 
                validators.DataRequired()], render_kw={'class': 'form-control', 'rows': 5, 'columns': 50})
