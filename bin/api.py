#!/usr/bin/env python

import flask
import flask_restx

import relations
import relations.unittest
import relations_restx

import restx_models


def build():
    """
    Builds the Flask App
    """

    app = flask.Flask("relations-restx-api")
    api = relations_restx.Api(app)

    app.source = relations.unittest.MockSource("relations-restx")

    api.add_resource(Health, '/health')

    relations_restx.attach(api, restx_models, relations.models(restx_models, restx_models.Base))

    return app


class Health(flask_restx.Resource):
    """
    Class for Health checks
    """

    def get(self):
        """
        Just return ok
        """
        return {"message": "OK"}


build().run(host='0.0.0.0', port=80)
