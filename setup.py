#!/usr/bin/python
from setuptools import setup, find_packages

setup(
    name="pyparsing_helper",
    version="0.1.0",
    py_modules=["pyparsing_helper","command_seq_reader"],
    
    # metadata for upload to PyPI
    author = 'Catherine Devlin',
    author_email = 'catherine.devlin@gmail.com',
    description = "GUI assistant for pyparsing",
    license = 'MIT',
    keywords = 'pyparsing GUI grammar troubleshooting',
    url = 'http://pypi.python.org/pypi/pyparsing_helper',
    packages = find_packages(),
    include_package_data = True,
    install_requires=['pyparsing'],
    platforms = ['any'],
    entry_points = """
                   [console_scripts]
                   pyparsing_helper = pyparsing_helper:main""",
    
    long_description = """A GUI for getting immediate feedback while constructing
and troubleshooting pyparsing grammars.  Analogous to tools like Kodos 
for regular expressions.

Mercurial repository and issue tracking
at http://www.assembla.com/spaces/pyparsing_helper/""",

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Filters',        
    ],
    )