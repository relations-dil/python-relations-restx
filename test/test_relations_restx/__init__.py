import unittest
import unittest.mock
import relations.unittest
import relations_rest.unittest

import sys
import flask
import flask_restx

import relations
import relations_restx

class ResourceModel(relations.Model):
    SOURCE = "TestRestX"

class PeanutButter(ResourceModel):
    id = int
    name = str

class Jelly(ResourceModel):
    PLURAL = "jellies"
    ID = None
    name = str

class Time(ResourceModel):
    id = int
    name = str

class JellyResource(relations_restx.Resource):
    MODEL = Jelly

class TimeResource(relations_restx.Resource):
    MODEL = Time

class TestRestX(relations_rest.unittest.TestCase):

    maxDiff = None

    def test_resources(self):

        self.assertEqual(relations_restx.resources(sys.modules[__name__]), [
            JellyResource,
            TimeResource
        ])

    def test_ensure(self):

        common = relations_restx.ensure(sys.modules[__name__], relations.models(sys.modules[__name__], ResourceModel))

        self.assertEqual(common[0].MODEL, PeanutButter)
        self.assertTrue(issubclass(common[0], relations_restx.Resource))

    def test_attach(self):

        relations.unittest.MockSource("TestRestX")

        app = flask.Flask("restx-api")
        restx = flask_restx.Api(app)

        restx.add_resource(TimeResource, '/time')

        relations_restx.attach(restx, sys.modules[__name__], relations.models(sys.modules[__name__], ResourceModel))

        api = app.test_client()

        response = api.get("/model")

        self.assertStatusValue(response, 200, "models", [
            {
                "id": None,
                "title": "Jelly",
                "singular": "jelly",
                "plural": "jellies",
                "titles": ["name"],
                "list": ["name"]
            },
            {
                "id": "id",
                "title": "Time",
                "singular": "time",
                "plural": "times",
                "titles": ["name"],
                "list": ["id", "name"]
            },
            {
                "id": "id",
                "title": "PeanutButter",
                "singular": "peanut_butter",
                "plural": "peanut_butters",
                "titles": ["name"],
                "list": ["id", "name"]
            }
        ])

        response = api.post("/peanut_butter", json={"peanut_butter": {"name": "chunky"}})

        self.assertStatusModel(response, 201, "peanut_butter", {
            "name": "chunky"
        })

        id = response.json["peanut_butter"]["id"]

        response = api.get(f"/peanut_butter/{id}")

        self.assertStatusModel(response, 200, "peanut_butter", {
            "name": "chunky"
        })

        response = api.get(f"/peanut_butter/0")

        self.assertStatusModel(response, 404, "message", 'peanut_butter: none retrieved')

        response = api.get(f"/jelly")

        self.assertStatusValue(response, 200, "jellies", [])

        response = api.get(f"/jelly/0")

        self.assertIsNone(response.json)
        self.assertEqual(response.status_code, 404)
