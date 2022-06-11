#!/usr/bin/env python

from setuptools import setup, find_packages
setup(
    name="python-relations-restx",
    version="0.5.0",
    package_dir = {'': 'lib'},
    py_modules = [
        'relations_restx',
        'relations_restx.resource',
        'relations_restx.api'
    ],
    install_requires=[
        'flask==2.1.1',
        'flask-restx==0.5.1'
    ]
)
