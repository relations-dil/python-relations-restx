# python-relations-restx

CRUD API from DB Modeling using the Flask-RESTX library

Relations overall is designed to be a simple, straight forward, flexible DIL (data interface layer).

Quite different from other DIL's, it has the singular, microservice based purpose to:
- Create models with very little code, independent of backends
- Create CRUD API with a database backend from those models with very little code
- Create microservices to use those same models but with that CRUD API as the backend

Ya, that last one is kinda new I guess.

Say we create a service, composed of microservices, which in turn is to be consumed by other services made of microservices.

You should only need to define the model once. Your conceptual structure is the same, to the DB, the API, and anything using that API. You shouldn't have say that structure over and over. You shouldn't have to define CRUD endpoints over and over. That's so boring, tedious, and unnecessary.

Furthermore, the conceptual structure is based not the backend of what you've going to use at that moment of time (scaling matters) but on the relations, how the pieces interact. If you know the structure of the data, that's all you need to interact with the data.

So with Relations, Models and Fields are defined independent of any backend, which instead is set at runtime. So the API will use a DB, everything else will use that API.

This creates the CRUD API from Resources pointing to Models.

Don't have great docs yet so I've included some of the unittests to show what's possible.

Btw, going to the root of the API generates a whole OpenAPI GUI. It's pretty!

# Example

## define

```python

import relations
import relations_pymysql

# The source is a string, the backend of which is defined at runtime

class SourceModel(relations.Model):
    SOURCE = "RestXResource"

class Simple(SourceModel):
    id = int
    name = str
    CHUNK = 2 # restrieves records 2 at a time

class Plain(SourceModel):
    ID = None # This table has no primary id field
    simple_id = int
    name = str

# This makes Simple a parent of Plain

relations.OneToMany(Simple, Plain)

class Meta(SourceModel):
    id = int
    name = str
    flag = bool
    spend = float
    people = set # JSON storage
    stuff = list # JSON stroage
    things = dict, {"extract": "for__0____1"} # Extracts things["for"][0][-1] as a virtual column
    push = str, {"inject": "stuff___1__relations.io____1"} # Injects this value into stuff[-1]["relations.io"]["1"]

def subnet_attr(values, value):

    values["address"] = str(value)
    min_ip = value[0]
    max_ip = value[-1]
    values["min_address"] = str(min_ip)
    values["min_value"] = int(min_ip)
    values["max_address"] = str(max_ip)
    values["max_value"] = int(max_ip)

class Net(SourceModel):

    id = int
    ip = ipaddress.IPv4Address, { # The field type is that of a class, with the storage being JSON
        "attr": {
            "compressed": "address", # Storge compressed attr as address key in JSON
            "__int__": "value"       # Storge int() as value key in JSON
        },
        "init": "address",           # Initilize with address from JSON
        "titles": "address",         # Use address from JSON as the how to list this field
        "extract": {
            "address": str,          # Extract address as virtual column
            "value": int             # Extra value as virtual column
        }
    }
    subnet = ipaddress.IPv4Network, {
        "attr": subnet_attr,
        "init": "address",
        "titles": "address"
    }

    TITLES = "ip__address" # When listing, use ip["address"] as display value
    INDEX = "ip__value"    # Create an index on the virtual column ip __value

# Define resources based on the models

class SimpleResource(relations_restx.Resource):
    MODEL = Simple

class PlainResource(relations_restx.Resource):
    MODEL = Plain

class MetaResource(relations_restx.Resource):
    MODEL = Meta

class NetResource(relations_restx.Resource):
    MODEL = Net

# With this statement, all the above models now have an in memory store backend

self.source = relations.unittest.MockSource("RestXResource")

# Create standard Flask and RESTX resources

self.app = flask.Flask("resource-api")
self.restx = relations_restx.Api(self.app)

# Add the Relations Resources and endpoints

self.restx.add_resource(SimpleResource, *SimpleResource.thy().endpoints())
self.restx.add_resource(PlainResource, *PlainResource.thy().endpoints())
self.restx.add_resource(MetaResource, *MetaResource.thy().endpoints())
self.restx.add_resource(NetResource, *NetResource.thy().endpoints())

# Use this as the client for all tests

self.api = self.app.test_client()
```

## options

Used with OpenGUI to dynamically build a form. So if you change fields and what not, the forms automatically adapt.

```python
response = self.api.options("/simple")
self.assertStatusFields(response, 200, [
    {
        "name": "id",
        "kind": "int",
        "readonly": True
    },
    {
        "name": "name",
        "kind": "str",
        "required": True
    }
], errors=[])

id = self.api.post("/simple", json={"simple": {"name": "ya"}}).json["simple"]["id"]

response = self.api.options(f"/simple/{id}")
self.assertStatusFields(response, 200, [
    {
        "name": "id",
        "kind": "int",
        "readonly": True,
        "original": id
    },
    {
        "name": "name",
        "kind": "str",
        "required": True,
        "original": "ya"
    }
], errors=[])

response = self.api.options(f"/simple/{id}", json={"simple": {"name": "sure"}})
self.assertStatusFields(response, 200, [
    {
        "name": "id",
        "kind": "int",
        "readonly": True,
        "original": id
    },
    {
        "name": "name",
        "kind": "str",
        "required": True,
        "original": "ya",
        "value": "sure"
    }
], errors=[])

response = self.api.options(f"/plain", json={"likes": {"simple_id": "y"}})
self.assertStatusFields(response, 200, [
    {
        "name": "simple_id",
        "kind": "int",
        "options": [1],
        "titles": {
            '1': ["ya"]
        },
        "like": "y",
        "format": [None],
        "overflow": False,
        "required": True
    },
    {
        "name": "name",
        "kind": "str",
        "required": True
    }
], errors=[])

response = self.api.options(f"/plain", json={"likes": {"simple_id": "n"}})
self.assertStatusFields(response, 200, [
    {
        "name": "simple_id",
        "kind": "int",
        "options": [],
        "titles": {},
        "like": "n",
        "format": [None],
        "overflow": False,
        "required": True
    },
    {
        "name": "name",
        "kind": "str",
        "required": True
    }
], errors=[])

id = self.api.post("/net", json={"net": {"ip": "1.2.3.4", "subnet": "1.2.3.0/24"}}).json["net"]["id"]

response = self.api.options(f"/net/{id}")
self.assertStatusFields(response, 200, [
    {
        "name": "id",
        "kind": "int",
        "readonly": True,
        "original": 1
    },
    {
        "name": "ip",
        "kind": "IPv4Address",
        "original": {
            "address": "1.2.3.4",
            "value": 16909060
        },
        "init": {"address": "address"}
    },
    {
        "name": "subnet",
        "kind": "IPv4Network",
        "original": {
            "address": "1.2.3.0/24",
            "min_address": "1.2.3.0",
            "min_value": 16909056,
            "max_address": "1.2.3.255",
            "max_value": 16909311
        },
        "init": {"address": "address"}
    }
], errors=[])

response = self.api.options("/meta")
self.assertStatusFields(response, 200, [
    {
        "name": "id",
        "kind": "int",
        "readonly": True
    },
    {
        "name": "name",
        "kind": "str",
        "required": True
    },
    {
        "name": "flag",
        "kind": "bool"
    },
    {
        "name": "spend",
        "kind": "float"
    },
    {
        "name": "people",
        "kind": "set",
        "default": []
    },
    {
        "name": "stuff",
        "kind": "list",
        "default": []
    },
    {
        "name": "things",
        "kind": "dict",
        "default": {}
    },
    {
        "name": "push",
        "kind": "str",
        "inject": "stuff__-1__relations.io___1"
    }
], errors=[])
```

## post

Used to create one or many, or perform a complex search with a JSON body.

```python
response = self.api.post("/simple")
self.assertStatusValue(response, 400, "message", "either simple or simples required")

response = self.api.post("/simple", json={"simple": {"name": "ya"}})
self.assertStatusModel(response, 201, "simple", {"name": "ya"})
simple = Simple.one(id=response.json["simple"]["id"])
self.assertEqual(simple.name, "ya")

response = self.api.post("/plain", json={"plains": [{"name": "sure"}]})
self.assertStatusModel(response, 201, "plains", [{"name": "sure"}])
self.assertEqual(Plain.one().name, "sure")

response = self.api.post("/simple", json={"filter": {"name": "ya"}})
self.assertStatusModel(response, 200, "simples", [{"id": simple.id, "name": "ya"}])

response = self.api.post("/simple", json={"filter": {"name": "ya"}, "count": True})
self.assertStatusModel(response, 200, "simples", 1)
```

## get

Used to retrieve one or many or even a count

```python
simple = Simple("ya").create()
simple.plain.add("whatevs").create()

response = self.api.get(f"/simple")
self.assertStatusModel(response, 200, "simples", [{"id": simple.id, "name": "ya"}])
self.assertStatusValue(response, 200, "formats", {})

response = self.api.get(f"/plain")
self.assertStatusModel(response, 200, "plains", [{"simple_id": simple.id, "name": "whatevs"}])
self.assertStatusValue(response, 200, "formats", {
    "simple_id": {
        "titles": {'1': ["ya"]},
        "format": [None]
    }
})

response = self.api.get(f"/simple/{simple.id}")
self.assertStatusModel(response, 200, "simple", {"id": simple.id, "name": "ya"})

response = self.api.get("/simple", json={"filter": {"name": "ya"}})
self.assertStatusModel(response, 200, "simples", [{"id": simple.id, "name": "ya"}])
self.assertStatusValue(response, 200, "overflow", False)

response = self.api.get("/simple", json={"filter": {"name": "no"}})
self.assertStatusModel(response, 200, "simples", [])
self.assertStatusValue(response, 200, "overflow", False)

Simple("sure").create()
Simple("fine").create()

response = self.api.get("/simple", json={"filter": {"like": "y"}})
self.assertStatusModels(response, 200, "simples", [{"id": simple.id, "name": "ya"}])
self.assertStatusValue(response, 200, "overflow", False)

response = self.api.get("/simple?limit=1&limit__start=1")
self.assertStatusModels(response, 200, "simples", [{"name": "sure"}])
self.assertStatusValue(response, 200, "overflow", True)

response = self.api.get("/simple?limit__per_page=1&limit__page=3")
self.assertStatusModels(response, 200, "simples", [{"name": "ya"}])
self.assertStatusValue(response, 200, "overflow", True)
self.assertStatusValue(response, 200, "formats", {})

simples = Simple.bulk()

for name in range(3):
    simples.add(name)

simples.create()

self.assertEqual(self.api.get("/simple?count=yes").json["simples"], 6)
self.assertEqual(self.api.get("/simple", json={"count": True}).json["simples"], 6)
```

## patch

Used to update one (id) or many (filter).

```python
response = self.api.patch("/simple")
self.assertStatusValue(response, 400, "message", "either simple or simples required")

response = self.api.patch(f"/simple", json={"simple": {"name": "yep"}})
self.assertStatusModel(response, 400, "message", "to confirm all, send a blank filter {}")

simple = Simple("ya").create()
response = self.api.patch(f"/simple/{simple.id}", json={"simple": {"name": "yep"}})
self.assertStatusModel(response, 202, "updated", 1)

response = self.api.patch("/simple", json={"filter": {"name": "yep"}, "simple": {"name": "sure"}})
self.assertStatusModel(response, 202, "updated", 1)

response = self.api.patch("/simple", json={"filter": {"name": "sure"}, "simples": {"name": "whatever"}})
self.assertStatusModel(response, 202, "updated", 1)

response = self.api.patch("/simple", json={"filter": {"name": "no"}, "simples": {}})
self.assertStatusModel(response, 202, "updated", 0)
```

## delete

Use to delete one (id) or many (filter).

```python
response = self.api.delete(f"/simple")
self.assertStatusModel(response, 400, "message", "to confirm all, send a blank filter {}")

simple = Simple("ya").create()
response = self.api.delete(f"/simple/{simple.id}")
self.assertStatusModel(response, 202, "deleted", 1)

simple = Simple("sure").create()
response = self.api.delete("/simple", json={"filter": {"name": "sure"}})
self.assertStatusModel(response, 202, "deleted", 1)

response = self.api.delete("/simple", json={"filter": {"name": "no"}})
self.assertStatusModel(response, 202, "deleted", 0)
```
