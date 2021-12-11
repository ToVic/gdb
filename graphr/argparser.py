''' argument parsing for graphr app '''

import os
import logging
from argparse import ArgumentParser, ArgumentTypeError
from graphr.version import __version__

LOG_LEVEL_STRINGS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
LOG_LEVEL_DEFAULT = 'DEBUG'
LOG_VERBOSE_DEFAULT = False
API_LISTEN_ADDR_DEFAULT = '0.0.0.0'
API_PORT_DEFAULT = 4242

def log_level_string_to_int(arg_string: str) -> int:
    '''get log level int from string'''

    log_level_string = arg_string.upper()
    if log_level_string not in LOG_LEVEL_STRINGS:
        message = (f"invalid choice: {log_level_string} "
                   f"(choose from {LOG_LEVEL_STRINGS})")
        raise ArgumentTypeError(message)

    log_level_int = getattr(logging, log_level_string, logging.INFO)
    # check the log_level_choices have not changed from our expected values
    assert isinstance(log_level_int, int)

    return log_level_int


def get_pars():
    '''
    get parameters from from command line arguments
    defaults overriden by ENVs
    '''

    env_vars = {
        'NEO_LOGIN': {
            'default': LOG_LEVEL_DEFAULT
        },
        'NEO_PASSWORD': {
            'default': LOG_VERBOSE_DEFAULT
        },
        'NEO_URI': {
            'required': True,
        },
    }

    for env_var, env_pars in env_vars.items():
        if env_var in os.environ:
            default = os.environ[env_var]
            if 'default' in env_pars:
                if isinstance(env_pars['default'], bool):
                    default = bool(os.environ[env_var])
                elif isinstance(env_pars['default', int]):
                    default = int(os.environ[env_var])
            env_pars['default'] = default
            env_pars['required'] = False
    
    Parser = ArgumentParser(description=f"graphr {__version__}")

    Parser.add_argument('-l',
                        '--log-level',
                        action='store',
                        dest='log_level',
                        help=("set the logging output level. "
                              f"{LOG_LEVEL_STRINGS} "
                              f"(default {LOG_LEVEL_DEFAULT})"),
                        type=log_level_string_to_int,
                        **env_vars['LOG_LEVEL'])

    Parser.add_argument('-v',
                        '--log-verbose',
                        action='store_true',
                        dest='log_verbose',
                        help='most verbose debug level '
                        '(console only; useful for a bug hunt :)',
                        **env_vars['LOG_VERBOSE'])
    
    Parser.add_argument('-n',
                        '--neo-login',
                        action='store',
                        dest='neo_login',
                        help='neo4j database login username (usually just "neo4j")',
                        **env_vars['NEO_LOGIN'])

    Parser.add_argument('-p',
                        '--neo-password',
                        action='store',
                        dest='neo_password',
                        help='neo4j database password (generated upon graph setup)',
                        **env_vars['NEO_PASSWORD'])

    Parser.add_argument('-u',
                        '--neo-uri',
                        action='store',
                        dest='neo_uri',
                        help='neo4j database connection URI',
                        **env_vars['NEO_URI'])

    return Parser.parse_args()

Pars = get_pars() 