from gevent import monkey
monkey.patch_all()
from gevent.pywsgi import WSGIServer
from .app import app
import os

def run_server():
    ''' Start a http server '''
    os.chdir('/')
    #TODO: remove in prod
    app.debug = True
    http_server = WSGIServer(('', 4242), app)
    http_server.serve_forever()
