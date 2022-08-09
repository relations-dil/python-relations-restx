#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setup(
    name="relations-restx",
    version="0.6.0",
    package_dir = {'': 'lib'},
    py_modules = [
        'relations_restx',
        'relations_restx.resource',
        'relations_restx.api'
    ],
    install_requires=[
        'Werkzeug==2.1.2',
        'flask==2.1.2',
        'flask-restx==0.5.1',
        'opengui==0.8.8',
        'relations-dil==0.6.11'
    ],
    url="https://github.com/relations-dil/python-relations-restx",
    author="Gaffer Fitch",
    author_email="relations@gaf3.com",
    description="CRUD API from DB Modeling using the Flask-RESTX library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license_files=('LICENSE.txt',),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ]
)
