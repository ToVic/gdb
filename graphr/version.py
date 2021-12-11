'''app version and resources info'''

import os

__version__ = '0.0.1'
app_name = 'repo'


def _get_build_info_items(prefixes: list):
    '''
    generate selected CI ENV iterator
    '''

    for key, value in os.environ.items():
        for prefix in prefixes:
            if key.startswith(prefix):
                yield key, value


def get_version_info():
    '''
    get application version info
    '''

    app = {
        'version': __version__,
    }
    for __, sha in _get_build_info_items(
        ['BUILD_CI_COMMIT_SHA', 'CI_COMMIT_SHA']):
        app['commit'] = sha[:8]

    return app
