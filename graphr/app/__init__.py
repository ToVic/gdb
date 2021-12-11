''' main app routes '''
from flask import Flask
from flask import render_template, request, session, redirect, url_for, flash
from .neo import Neo_client
from .forms import NewDeptForm


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
# max age of the cached static files in seconds
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 60
app.static_folder = './static'
app.secret_key = 'dumb_secret_key'

NAVBAR_ITEMS = ['employees', 'departments', 'structure']

Neo = Neo_client()


@app.context_processor
def inject_routes():
    """
    Registers the routes for the navbar into the app context
    This is needed because the parent template does not have
    its own route and can't be passed arguments
    """
    links = [(item, item.capitalize()) for item in NAVBAR_ITEMS]
    return(dict(links=links))

@app.route("/")
def home():
    ''' this will be an initial overview '''
    return render_template('home.html')


##### EMPLOYEES

@app.route('/employees', methods=['POST', 'GET'])
def employees():
    return render_template('employees.html')


##### DEPARTMENTS

@app.route('/departments', methods=['POST', 'GET'])
def departments():
    page_data = {}
    page_data['table_header'] = ['name','description','Chief officer']
    page_data['depts'] = Neo.get_all_depts()

    return render_template('departments.html', page_data=page_data)


@app.route('/departments/new', methods=['POST', "GET"])
def new_dept():
    ''' department creation '''

    form = NewDeptForm(request.form)
    if request.method == 'POST' and form.validate():
        dept = {
            'name': form.name.data,
            'description': form.description.data,
        }
        r = Neo.create_dept(dept)
        if not r:
            flash('An unexpected error occured while processing your request', 'error')
        else:
            flash('Department successfully added')
            redirect('/departments')

    return render_template('new_dept.html', form=form)


##### STRUCTURE

@app.route('/structure', methods=['POST', 'GET'])
def structure():
    return render_template('structure.html')