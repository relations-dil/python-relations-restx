"""
Utilities for Relations RestX
"""

import inspect

import flask_restx

from relations_restx.resource import ResourceError, ResourceIdentity, Resource, exceptions
from relations_restx.api import Api, OpenApi

def resources(module):
    """
    List all the resources in a module
    """

    return [
        cls[1]
        for cls in inspect.getmembers(
            module,
            lambda model: inspect.isclass(model)
            and issubclass(model, Resource)
        )
    ]

def ensure(module, models):
    """
    Creates the Resources for all models
    """

    exists = [resource.MODEL for resource in resources(module)]

    return [
        type(model.__name__, (Resource, ), {'MODEL': model})
        for model in models if model not in exists
    ]

def attach(restx, module, models):
    """
    Attach all Reources to a RestX
    """

    class Model(flask_restx.Resource):
        """
        Custom class for each call
        """

        MODELS = []

        def get(self):
            """
            List all models
            """
            return {"models": self.MODELS}

    restx.add_resource(Model, "/model")

    for resource in resources(module) + ensure(module, models):

        thy = resource.thy()

        Model.MODELS.append({
            "id": thy._model._id,
            "titles": thy._model._titles,
            "title": thy._model.TITLE,
            "singular": thy.SINGULAR,
            "plural": thy.PLURAL,
            "list": thy.LIST
        })

        if resource.__name__.lower() not in restx.endpoints:
            restx.add_resource(resource, *thy.endpoints())
