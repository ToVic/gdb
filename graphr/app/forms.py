''' forms using WTForms '''
from wtforms import Form, StringField, validators, TextAreaField

class NewDeptForm(Form):

    name = StringField('name', [validators.length(min=3, max=20), validators.DataRequired()])
    description = TextAreaField('description', [validators.length(min=10, max=100), 
                validators.DataRequired()], render_kw={'class': 'form-control', 'rows': 5, 'columns': 50})
