from gevent import monkey
monkey.patch_all()

import logging
from gevent.pywsgi import WSGIServer, LoggingLogAdapter
from .app import app
from graphr.argparser import Pars
from graphr.logger import logger


def main():
    '''start a http server'''

    logger.info("HTTP server listen %s:%s", Pars.app_listen_addr,
                Pars.app_port)
    dlog = LoggingLogAdapter(logger, level=logging.DEBUG)
    errlog = LoggingLogAdapter(logger, level=logging.ERROR)
    http_server = WSGIServer((Pars.app_listen_addr, Pars.app_port),
                             app,
                             log=dlog,
                             error_log=errlog)
    http_server.serve_forever()
