# this file was stolen/copied from https://github.com/hynek/pem

import codecs
import os
import re

from setuptools import setup


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding
    """
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), 'rb', 'utf-8') as f:
        return f.read()


def find_version(*file_paths):
    """
    Build a path from *file_paths* and search for a ``__version__``
    string inside.
    """
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
        version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='rswt',
    version=find_version("rswt.py"),
    description='Control RobertSonics WavTrigger through serial port.',
    long_description=(read('README.rst') + '\n\n' ),
    url='https://github.com/wayoda/rswt/',
    license="MIT",
    author="Eberhard Fahle",
    author_email='e.fahle@wayoda.org',
    py_modules=['rswt'],
    install_requires=['pyserial'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Multimedia :: Sound/Audio :: Players'
    ],
)
