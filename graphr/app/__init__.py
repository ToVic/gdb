''' main app routes '''
from flask import Flask
from flask import render_template, request, session, redirect, url_for, flash
from .neo import Neo_client
from .forms import NewDeptForm
from ..logger import logger


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
    ''' 
    this will be an initial overview 
    once it gets designed
    '''

    return render_template('home.html')


##### EMPLOYEES

@app.route('/employees', methods=['POST', 'GET'])
def employees():
    page_data = {}
    page_data['table_header'] = ['name','department','position']
    page_data['employees'] = Neo.get_all_employees()

    return render_template('employees.html', page_data=page_data)


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
            flash('Department successfully added', 'success')
            return redirect('/departments')

    return render_template('new_dept.html', form=form)


@app.route('/departments/<string:name>', methods=['GET'])
def dept_detail(name):
    ''' dept detail '''

    page_data = {}
    page_data = Neo.get_dept(name)
    if not page_data:
        flash('An unexpected error occured while processing your request', 'error')
    
    return render_template('dept[name].html', page_data=page_data)


@app.route('/departments/<string:name>/edit', methods=['GET','POST'])
def edit_dept(name):
    ''' dept edit '''

    dept_data = Neo.get_dept(name)
    if not dept_data:
        flash('An unexpected error occured while processing your request', 'error')
    form = NewDeptForm(request.form)
    form.name.data = dept_data['name']
    #form.description.data = dept_data['description']
    if request.method == 'POST' and form.validate():
        dept = {
            'name': form.name.data,
            'description': form.description.data,
        }
        if not Neo.edit_dept(dept, dept_data['name']):
            flash('An unexpected error occured while processing your request', 'error')
            return

        flash('Edit successful', 'success')
        return redirect(f'/departments/{name}')

    return render_template('edit_dept.html', form=form)


@app.route('/departments/<string:name>/delete', methods=['POST'])
def delete_dept(name):
    ''' dept delete '''
    if request.method == 'POST':
        if Neo.delete_dept(name):
            flash(f'Successfully deleted department {name}')
            return redirect('/departments')

        flash('An unexpected error occured while processing your request', 'error')
        return


##### STRUCTURE

@app.route('/structure', methods=['POST', 'GET'])
def structure():
    return render_template('structure.html')