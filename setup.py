from setuptools import setup, find_packages
from graphr.version import __version__


try: 
    with open("README.md", "r") as fh:
        long_description = fh.read()
        fh.close()
except FileNotFoundError:
    long_description = "README.md not found"

try:
    with open('requirements.txt') as fh:
        required = fh.read().splitlines()
except FileNotFoundError:
    required = []

setup(
    name="graphr",
    version=__version__,
    author="Dominik Hartinger",
    author_email="hard07@vse.cz",
    description="Demo app with graph db backend",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ToVic/gdb",
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    package_data={"graphr": ['app/templates/*.html','app/static/styles/*.css', \
        'app/static/bootstrap/css/*.css','app/static/bootstrap/js/*.js','app/static/fonts/*.ttf'\
        'app/static/fonts/*.woff','app/static/fonts/*.woff2', 'app/static/fonts/*.svg',\
        'app/static/fonts/*.eot','app/static/icons/*.png']},
    install_requires=required,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': ['graphr=graphr.server:main'],
    })
