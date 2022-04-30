#!/usr/bin/env python

from setuptools import setup, find_packages
setup(
    name="python-relations-restful",
    version="0.1.0",
    package_dir = {'': 'lib'},
    py_modules = [
        'relations_restx',
        'relations_restx.resource',
        'relations_restx.source',
        'relations_restx.unittest'
    ],
    install_requires=[
        'requests==2.25.1',
        'flask==2.1.1',
        'flask-restx==0.5.1'
    ]
)
