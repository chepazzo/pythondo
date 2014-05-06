#!/usr/bin/env python

# see http://docs.python.org/distutils/setupscript.html

from distutils.core import setup
import sys
sys.path.append('bin')

# Import version from the module. Add one if you don't have one.
from pydo import __doc__ as long_desc
from pydo import __version__

setup(
    name='pythondo',
    version=__version__,
    author='Mike Biancanello',
    author_email='mikebianc@aol.com',

    #packages = []

    #py_modules = [],

    # Used to list python scripts that will be part of the python package
    scripts=[
        'bin/pydo.py'
    ],

    # Used to list other files that need to be installed
    data_files=[
        ('/opt/lib', ['PythonDo.pm'])
    ],

    license='AOL Proprietary',
    url='https://github.com/chepazzo/pythondo',
    description='implements multi-lingual py classes',
    long_description=long_desc,

    # If you want to package scripts, put the relative path to them here.
    # e.g. scripts = [
    #          'bin/deviceupdater',
    #      ],
    #scripts=[],
)
# Assuming __version__ = '0.1'
# 'python setup.py build' will "build" the module to build/lib/dcommand.py
# 'python setup.py sdist' will tarball and create dist/python-docommand-0.1.tar.gz
# 'python setup.py bdist' will tarball and create dist/python-docommand-0.1.tar.gz
# 'python setup.py install' would install docommand.py to the same location
# within the bdist tarball:
#   ('/opt/bcs/packages/python-modules-2.0/lib/python/site-packages/')

