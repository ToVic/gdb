''' custom logger '''

import logging
import urllib3


class ConfLogger():
    '''
    set a logger with configured handlers and filters
    '''
    def __init__(self, name, log_level=logging.DEBUG, log_verbose=False):

        handlers = [
            logging.StreamHandler(),
        ]

        logging.basicConfig(
            format='%(asctime)s: GRAPHR %(funcName)s, %(levelname)s:'
            ' %(message)s',
            level=log_level,
            handlers=handlers,
            datefmt='%m/%d/%Y %I:%M:%S %p')

        if not log_verbose:
            logging.getLogger('urllib3').setLevel(logging.CRITICAL)
            urllib3.disable_warnings()

        self.logger = logging.getLogger(name)

    def get_logger(self):
        ''' getter '''
        return self.logger


cl = ConfLogger(__name__, log_level='DEBUG', log_verbose=False)
logger = cl.get_logger()
