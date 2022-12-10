#!/usr/bin/env python

import os
from setuptools import setup

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

version = os.environ.get("BUILD_VERSION")

if version is None:
    with open("VERSION", "r") as version_file:
        version = version_file.read().strip()

setup(
    name="relations-restx",
    version=version,
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
        'relations-dil==0.6.12'
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
