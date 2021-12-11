''' main app routes '''
from flask import Flask
from flask import render_template, request, session, redirect, url_for


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
# max age of the cached static files in seconds
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 60
app.static_folder = './static'
app.secret_key = 'dumb_secret_key'


@app.context_processor
def inject_routes():
    """
    Registers the routes for the navbar into the app context
    This is needed because the parent template does not have
    its own route and can't be passed arguments
    """
    navbar_items = ['employees', 'departments', 'structure overview']
    links = [(item, item.capitalize()) for item in navbar_items]
    return(dict(links=links))

@app.route("/")
def home():
    return render_template('home.html')
