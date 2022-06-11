import unittest
import unittest.mock
import relations.unittest

import flask
import flask_restx
import werkzeug.exceptions
from test.test_relations_restx.test_resource import SimpleResource, TestRestX

import opengui
import ipaddress

import relations
import relations_restx

class TestOpenApi(TestRestX):

    def test_relations_value(self):

        self.assertEqual(relations_restx.OpenApi.relations_value({"default": 1}), 1)
        self.assertEqual(relations_restx.OpenApi.relations_value({"kind": "set", "options": [1, 2, 3]}), [1])
        self.assertEqual(relations_restx.OpenApi.relations_value({"kind": "int", "options": [1, 2, 3]}), 1)
        self.assertEqual(relations_restx.OpenApi.relations_value({"kind": "str"}), "")
        self.assertEqual(relations_restx.OpenApi.relations_value({"kind": "int"}), 0)
        self.assertEqual(relations_restx.OpenApi.relations_value({"kind": "bool"}), False)
        self.assertEqual(relations_restx.OpenApi.relations_value({"kind": "float"}), 0.0)
        self.assertIsNone(relations_restx.OpenApi.relations_value({"kind": "nope"}))

    def test_relations_example(self):

        self.assertEqual(relations_restx.OpenApi.relations_example(SimpleResource.thy()), {"name": ""})
        self.assertEqual(relations_restx.OpenApi.relations_example(SimpleResource.thy(), readonly=True), {"id": 0, "name": ""})

    def test_relations_schema(self):

        schemas = relations_restx.OpenApi.relations_schemas(SimpleResource.thy())

        self.assertEqual(schemas["Simple"], {
            "type": "object",
            "properties": {
                "id": {
                    "type": "int",
                    "readOnly": True
                },
                "name": {
                    "type": "str"
                }
            },
            "required": ["name"]
        })

        self.assertEqual(schemas["simple"], {
            "type": "object",
            "properties": {
                "simple": {
                    "$ref": "#/components/schemas/Simple"
                }
            }
        })

        self.assertEqual(schemas["simples"], {
            "type": "object",
            "properties": {
                "simples": {
                    "type": "array",
                    "items": {
                        "$ref": "#/components/schemas/Simple"
                    }
                }
            }
        })

        self.assertEqual(schemas["simple_filter"], {
            "type": "object",
            "properties": {
                "filter": {
                    "$ref": "#/components/schemas/Simple"
                }
            }
        })

        self.assertEqual(schemas["simple_sort"], {
            "type": "object",
            "properties": {
                "sort": {
                    "type": "array",
                    "description": "sort by these fields, prefix with + for ascending (default), - for descending",
                    "default": ["+name"]
                }
            }
        })

        self.assertEqual(schemas["simple_limit"], {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "limit the number of simples"
                },
                "limit__start": {
                    "type": "integer",
                    "description": "limit the number of simples starting here"
                },
                "limit__per_page": {
                    "type": "integer",
                    "description": "limit the number of simples by this page size (default 2)"
                },
                "limit__page": {
                    "type": "integer",
                    "description": "limit the number of simples and retrieve this page"
                }
            }
        })

        self.assertEqual(schemas["simple_count"], {
            "type": "object",
            "properties": {
                "count": {
                    "type": "boolean",
                    "description": "return only the count of simples found"
                }
            }
        })

    def test_relations_create_options(self):

        self.assertEqual(relations_restx.OpenApi.relations_create_options(SimpleResource.thy()), {
            "tags": ["Simple"],
            "operationId": "simple_create_options",
            "summary": "generates and validates fields to create one simple or many simples",
            "description": "To generate, send nothing. To validate, send a simple.",
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/simple"
                        },
                        "examples": {
                            "generate": {
                                "value": {}
                            },
                            "validate": {
                                "value": {
                                    "simple": {"name": ""}
                                }
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "fields to create one simple or many simples generated and validated",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": '#/components/schemas/Options'
                            }
                        }
                    }
                }
            }
        })

    def test_relations_create_filter(self):

        self.assertEqual(relations_restx.OpenApi.relations_create_filter(SimpleResource.thy()), {
            "tags": ["Simple"],
            "operationId": "simple_create_search",
            "summary": "creates one simple or many simples or a complex retrieve",
            "description": "To create one, send simple. To create many, send simples. To retrieve send filter (sort, limit, count optional).",
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "oneOf": [
                                {
                                    "$ref": "#/components/schemas/simple",
                                },
                                {
                                    "$ref": "#/components/schemas/simples"
                                },
                                {
                                    "oneOf": [
                                        {
                                            "$ref": "#/components/schemas/simple_filter"
                                        }
                                    ],
                                    "anyOf": [
                                        {
                                            "$ref": "#/components/schemas/simple_sort"
                                        },
                                        {
                                            "$ref": "#/components/schemas/simple_limit"
                                        },
                                        {
                                            "$ref": "#/components/schemas/simple_count"
                                        }
                                    ]
                                }
                            ]
                        },
                        "examples": {
                            "create one": {
                                "value": {
                                    "simple": {"name": ""}
                                }
                            },
                            "create many": {
                                "value": {
                                    "simples": [{"name": ""}]
                                }
                            },
                            "complex retrieve": {
                                "value": {
                                    "filter": {"name": ""},
                                    "sort": ["+name"]
                                }
                            },
                            "limit retrieve": {
                                "value": {
                                    "filter": {"name": ""},
                                    "sort": ["+name"],
                                    "limit": {
                                        "limit": 2,
                                        "start": 0
                                    }
                                }
                            },
                            "paginate retrieve": {
                                "value": {
                                    "filter": {"name": ""},
                                    "sort": ["+name"],
                                    "limit": {
                                        "page": 1,
                                        "per_page": 2
                                    }
                                }
                            },
                            "count retrieve": {
                                "value": {
                                    "filter": {"name": ""},
                                    "count": True
                                }
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "many simples retrieved",
                    "content": {
                        "application/json": {
                            "schema": {
                                "oneOf": [
                                    {
                                        "$ref": "#/components/schemas/simples"
                                    },
                                    {
                                        "$ref": "#/components/schemas/Retrieved"
                                    },
                                ]
                            },
                            "examples": {
                                "list retrieve": {
                                    "value": {
                                        "simples": [{"id": 0, "name": ""}],
                                        "overflow": False,
                                        "formats": {}
                                    }
                                },
                                "count retrieve": {
                                    "value": {
                                        "count": 1
                                    }
                                }
                            }
                        }
                    }
                },
                "201": {
                    "description": "one simple or many simples created",
                    "content": {
                        "application/json": {
                            "schema": {
                                "oneOf": [
                                    {
                                        "$ref": "#/components/schemas/simple",
                                        "description": "lol"
                                    },
                                    {
                                        "$ref": "#/components/schemas/simples"
                                    }
                                ]
                            },
                            "examples": {
                                "create one": {
                                    "value": {
                                        "simple": {"id": 0, "name": ""}
                                    }
                                },
                                "create many": {
                                    "value": {
                                        "simples": [{"id": 0, "name": ""}]
                                    }
                                }
                            }
                        }
                    }
                },
                "400": {
                    "description": "unable to create due to bad request"
                }
            }
        })

    def test_relations_retrieve_many(self):

        self.assertEqual(relations_restx.OpenApi.relations_retrieve_many(SimpleResource.thy()), {
            "tags": ["Simple"],
            "operationId": "simple_retrieve_many",
            "summary": "retrieves many simples",
            "parameters": [
                {
                    "in": "query",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "dude": {
                                "type": "integer",
                                "example": 5,
                                "description": "lolwut"
                            }
                        },

                    },
                    "style": "form",
                    "explode": True,
                    "name": "params",
                    "examples": {
                        "retrieve": {
                            "value": {
                                **{"name": ""},
                                "sort": ",".join(["+name"])
                            }
                        },
                        "limit": {
                            "value": {
                                **{"name": ""},
                                "sort": ",".join(["+name"]),
                                "limit": 2,
                                "limit__start": 0
                            }
                        },
                        "paginate": {
                            "value": {
                                **{"name": ""},
                                "sort": ",".join(["+name"]),
                                "limit__page": 1,
                                "limit__per_page": 2
                            }
                        },
                        "count": {
                            "value": {
                                **{"name": ""},
                                "count": 1
                            }
                        }
                    }
                }
            ],
            "responses": {
                "200": {
                    "description": "many simples retrieved",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/simples"
                            },
                            "examples": {
                                "list retrieve": {
                                    "value": {
                                        "simples": [{"id": 0, "name": ""}],
                                        "overflow": False,
                                        "formats": {}
                                    }
                                },
                                "count retrieve": {
                                    "value": {
                                        "count": 1
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })

    def test_relations_update_many(self):

        self.assertEqual(relations_restx.OpenApi.relations_update_many(SimpleResource.thy()), {
            "tags": ["Simple"],
            "operationId": "simple_update_many",
            "summary": "updates many simples",
            "parameters": [
                {
                    "in": "query",
                    "schema": {
                        "type": "object"
                    },
                    "style": "form",
                    "explode": True,
                    "name": "params",
                    "examples": {
                        "filter through params": {
                            "value": {
                                **{"name": ""}
                            }
                        },
                        "filter through params limit": {
                            "value": {
                                **{"name": ""},
                                "sort": ",".join(["+name"]),
                                "limit": 2,
                                "limit__start": 0
                            }
                        },
                        "filter through params paginate": {
                            "value": {
                                **{"name": ""},
                                "sort": ",".join(["+name"]),
                                "limit__page": 1,
                                "limit__per_page": 2
                            }
                        },
                        "filter through body": {
                            "value": {}
                        }
                    }
                }
            ],
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "anyOf": [
                                {
                                    "$ref": "#/components/schemas/simple"
                                },
                                {
                                    "$ref": "#/components/schemas/simple_filter"
                                }
                            ]
                        },
                        "examples": {
                            "filter through params": {
                                "value": {
                                    "simples": {"name": ""}
                                }
                            },
                            "filter through body": {
                                "value": {
                                    "filter": {"name": ""},
                                    "simples": {"name": ""}
                                }
                            },
                            "filter through body limit": {
                                "value": {
                                    "filter": {"name": ""},
                                    "sort": ["+name"],
                                    "limit": {
                                        "limit": 2,
                                        "start": 0
                                    },
                                    "simples": {"name": ""}
                                }
                            },
                            "filter through body paginate": {
                                "value": {
                                    "filter": {"name": ""},
                                    "sort": ["+name"],
                                    "limit": {
                                        "page": 1,
                                        "per_page": 2
                                    },
                                    "simples": {"name": ""}
                                }
                            },
                            "update all": {
                                "value": {
                                    "filter": {},
                                    "simples": {"name": ""}
                                }
                            }
                        }
                    }
                }
            },
            "responses": {
                "202": {
                    "description": "many simples updated",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/Updated"
                            }
                        }
                    }
                },
                "400": {
                    "description": "unable to update due to bad request"
                }
            }
        })

    def test_relations_delete_many(self):

        self.assertEqual(relations_restx.OpenApi.relations_delete_many(SimpleResource.thy()), {
            "tags": ["Simple"],
            "operationId": "simple_delete_many",
            "summary": "deletes many simples",
            "parameters": [
                {
                    "in": "query",
                    "schema": {
                        "type": "object"
                    },
                    "style": "form",
                    "explode": True,
                    "name": "params",
                    "examples": {
                        "filter through params": {
                            "value": {
                                **{"name": ""}
                            }
                        },
                        "filter through params limit": {
                            "value": {
                                **{"name": ""},
                                "sort": ",".join(["+name"]),
                                "limit": 2,
                                "limit__start": 0
                            }
                        },
                        "filter through params paginate": {
                            "value": {
                                **{"name": ""},
                                "sort": ",".join(["+name"]),
                                "limit__page": 1,
                                "limit__per_page": 2
                            }
                        },
                        "filter through body": {
                            "value": {}
                        }
                    }
                }
            ],
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "anyOf": [
                                {
                                    "$ref": "#/components/schemas/simple_filter"
                                }
                            ]
                        },
                        "examples": {
                            "filter through params": {
                                "value": {}
                            },
                            "filter through body": {
                                "value": {
                                    "filter": {"name": ""}
                                }
                            },
                            "filter through body limit": {
                                "value": {
                                    "filter": {"name": ""},
                                    "sort": ["+name"],
                                    "limit": {
                                        "limit": 2,
                                        "start": 0
                                    }
                                }
                            },
                            "filter through body paginate": {
                                "value": {
                                    "filter": {"name": ""},
                                    "sort": ["+name"],
                                    "limit": {
                                        "page": 1,
                                        "per_page": 2
                                    }
                                }
                            },
                            "delete all": {
                                "value": {
                                    "filter": {}
                                }
                            }
                        }
                    }
                }
            },
            "responses": {
                "202": {
                    "description": "many simples deleted",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/Deleted"
                            }
                        }
                    }
                },
                "400": {
                    "description": "unable to updeletedate due to bad request"
                }
            }
        })

    def test_relations_update_options(self):

        self.assertEqual(relations_restx.OpenApi.relations_update_options(SimpleResource.thy()), {
            "tags": ["Simple"],
            "operationId": "simple_update_options",
            "summary": "generates and validates fields to update one simple",
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/simple"
                        },
                        "examples": {
                            "generate": {
                                "value": {}
                            },
                            "validate": {
                                "value": {
                                    "simple": {"name": ""}
                                }
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": "fields to update one simple generated and validated",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": '#/components/schemas/Options'
                            }
                        }
                    }
                },
                "404": {
                    "description": "simple not found"
                }
            }
        })

    def test_relations_retrieve_one(self):

        self.assertEqual(relations_restx.OpenApi.relations_retrieve_one(SimpleResource.thy()), {
            "tags": ["Simple"],
            "operationId": "simple_retrieve_one",
            "summary": "retrieves one simple",
            "responses": {
                "200": {
                    "description": "one simple retrieved",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/simple"
                            },
                            "examples": {
                                "retrieve": {
                                    "value": {
                                        "simple": {"id": 0, "name": ""},
                                        "overflow": False,
                                        "formats": {}
                                    }
                                }
                            }
                        }
                    }
                },
                "404": {
                    "description": "simple not found"
                }
            }
        })

    def test_relations_relations_update_one(self):

        self.assertEqual(relations_restx.OpenApi.relations_update_one(SimpleResource.thy()), {
            "tags": ["Simple"],
            "operationId": "simple_update_one",
            "summary": "updates one simple",
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/simple"
                        },
                        "examples": {
                            "update": {
                                "value": {
                                    "simple": {"name": ""}
                                }
                            }
                        }
                    }
                }
            },
            "responses": {
                "202": {
                    "description": "one simple updated",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/Updated"
                            }
                        }
                    }
                },
                "400": {
                    "description": "unable to update due to bad request"
                },
                "404": {
                    "description": "simple not found"
                }
            }
        })

    def test_relations_delete_one(self):

        self.assertEqual(relations_restx.OpenApi.relations_delete_one(SimpleResource.thy()), {
            "tags": ["Simple"],
            "operationId": "simple_delete_one",
            "summary": "deletes one simple",
            "responses": {
                "202": {
                    "description": "one simple deleted",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/"
                            }
                        }
                    }
                },
                "404": {
                    "description": "simple not found"
                }
            }
        })

    def test_relations_operations(self):

        specs = {
            "paths": {
                "/simple": {
                    "options": {"no": "touch"},
                    "post": {"no": "touch"},
                    "get": {"no": "touch"},
                    "patch": {"no": "touch"},
                    "delete": {"no": "touch"}
                },
                "/simple/{id}": {
                    "options": {"no": "touch"},
                    "post": {"no": "touch"},
                    "get": {"no": "touch"},
                    "patch": {"no": "touch"},
                    "delete": {"no": "touch"}
                }
            }
        }

        urls = [
            '/simple', '/simple/<id>'
        ]

        relations_restx.OpenApi(self.restx).relations_operations(specs, self.restx.namespaces[0], urls, SimpleResource.thy())

        self.assertEqual(specs["paths"]["/simple"]["options"]["operationId"], "simple_create_options")
        self.assertEqual(specs["paths"]["/simple"]["options"]["no"], "touch")

        self.assertEqual(specs["paths"]["/simple"]["post"]["operationId"], "simple_create_search")
        self.assertEqual(specs["paths"]["/simple"]["post"]["no"], "touch")

        self.assertEqual(specs["paths"]["/simple"]["get"]["operationId"], "simple_retrieve_many")
        self.assertEqual(specs["paths"]["/simple"]["get"]["no"], "touch")

        self.assertEqual(specs["paths"]["/simple"]["patch"]["operationId"], "simple_update_many")
        self.assertEqual(specs["paths"]["/simple"]["patch"]["no"], "touch")

        self.assertEqual(specs["paths"]["/simple"]["delete"]["operationId"], "simple_delete_many")
        self.assertEqual(specs["paths"]["/simple"]["delete"]["no"], "touch")

        self.assertEqual(specs["paths"]["/simple/{id}"]["options"]["operationId"], "simple_update_options")
        self.assertEqual(specs["paths"]["/simple/{id}"]["options"]["no"], "touch")

        self.assertNotIn("post", specs["paths"]["/simple/{id}"])

        self.assertEqual(specs["paths"]["/simple/{id}"]["get"]["operationId"], "simple_retrieve_one")
        self.assertEqual(specs["paths"]["/simple/{id}"]["get"]["no"], "touch")

        self.assertEqual(specs["paths"]["/simple/{id}"]["patch"]["operationId"], "simple_update_one")
        self.assertEqual(specs["paths"]["/simple/{id}"]["patch"]["no"], "touch")

        self.assertEqual(specs["paths"]["/simple/{id}"]["delete"]["operationId"], "simple_delete_one")
        self.assertEqual(specs["paths"]["/simple/{id}"]["delete"]["no"], "touch")

    def test_relations_resource(self):

        specs = {
            "paths": {
                "/simple": {
                    "options": {"no": "touch"},
                    "post": {"no": "touch"},
                    "get": {"no": "touch"},
                    "patch": {"no": "touch"},
                    "delete": {"no": "touch"}
                },
                "/simple/{id}": {
                    "options": {"no": "touch"},
                    "post": {"no": "touch"},
                    "get": {"no": "touch"},
                    "patch": {"no": "touch"},
                    "delete": {"no": "touch"}
                }
            },
            "tags": [],
            "components": {
                "schemas": {}
            }
        }

        urls = [
            '/simple', '/simple/<id>'
        ]

        relations_restx.OpenApi(self.restx).relations_resource(specs, self.restx.namespaces[0], SimpleResource, urls)

        self.assertEqual(specs["tags"], [{"name": "Simple"}])

        self.assertEqual(specs["components"]["schemas"]["Simple"], {
            "type": "object",
            "properties": {
                "id": {
                    "type": "int",
                    "readOnly": True
                },
                "name": {
                    "type": "str"
                }
            },
            "required": ["name"]
        })

        self.assertEqual(specs["paths"]["/simple"]["options"]["operationId"], "simple_create_options")
        self.assertEqual(specs["paths"]["/simple"]["options"]["no"], "touch")

    def test_as_dict(self):

        specs = self.api.get("/swagger.json").json

        self.assertNotIn("swagger", specs)
        self.assertEqual(specs["openapi"], "3.0.3")

        self.assertEqual(specs["components"]["schemas"]["Field"], {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "name of the field"
                },
                "value": {
                    "description": "the current value of the field"
                },
                "original": {
                    "description": "the original value of the field"
                },
                "default": {
                    "description": "the default value of the field"
                },
                "options": {
                    "type": "array",
                    "items": {},
                    "description": "array of options to select from"
                },
                "required": {
                    "type": "boolean",
                    "description": "whether the field is required"
                },
                "multi": {
                    "type": "boolean",
                    "description": "whether multiple options can be selected"
                },
                "trigger": {
                    "type": "boolean",
                    "description": "whether to reload when this field changes"
                },
                "readonly": {
                    "type": "boolean",
                    "description": "whether the field is readonly"
                },
                "validation": {
                    "description": "how to validate this field"
                },
                "content": {
                    "type": "object",
                    "description": "used for any other data, like titles"
                },
                "errors": {
                    "type": "array",
                    "description": "the original value of the field"
                }
            }
        })

        self.assertEqual(specs["components"]["schemas"]["Options"], {
            "type": "object",
            "properties": {
                "fields": {
                    "type": "array",
                    "items": {
                        "$ref": "#/components/schemas/Field"
                    }
                },
                "errors": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        })

        self.assertEqual(specs["components"]["schemas"]["Retrieved"], {
            "type": "object",
            "properties": {
                "overflow": {
                    "type": "boolean",
                    "description": "whether more could have been retrieved"
                },
                "format": {
                    "type": "object",
                    "description": "Formatting information for fields, like titles"
                }
            }
        })

        self.assertEqual(specs["components"]["schemas"]["Counted"], {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "description": "count of those retrieved"
                }
            }
        })

        self.assertEqual(specs["components"]["schemas"]["Updated"], {
            "type": "object",
            "properties": {
                "updated": {
                    "type": "integer",
                    "description": "count of those updated"
                }
            }
        })

        self.assertEqual(specs["components"]["schemas"]["Deleted"], {
                "type": "object",
                "properties": {
                    "deleted": {
                        "type": "integer",
                        "description": "count of those deleted"
                    }
                }
        })

        self.assertIn({"name": "Simple"}, specs["tags"])

        self.assertEqual(specs["components"]["schemas"]["Simple"], {
            "type": "object",
            "properties": {
                "id": {
                    "type": "int",
                    "readOnly": True
                },
                "name": {
                    "type": "str"
                }
            },
            "required": ["name"]
        })

        self.assertEqual(specs["paths"]["/simple"]["options"]["operationId"], "simple_create_options")
