"""
Module for overriding the base RestX API
"""

import collections
import flask_restx

from werkzeug.utils import cached_property


class OpenApi(flask_restx.Swagger):
    """
    Overrride Flask RestX Swagger
    """

    @staticmethod
    def relations_value(field): # pylint: disable=too-many-return-statements
        """
        Generates an example alues
        """

        if "default" in field:
            return field["default"]

        if field.get("options"):
            if field["kind"] == "set":
                return [field["options"][0]]
            return field["options"][0]

        if field["kind"] == "str":
            return ""

        if field["kind"] == "int":
            return 0

        if field["kind"] == "bool":
            return False

        if field["kind"] == "float":
            return 0.0

        return None

    @classmethod
    def relations_example(cls, thy, readonly=False):
        """
        Generates an example for a single record
        """

        example = {}

        for field in thy._fields:
            if readonly or not field.get("readonly"):
                example[field["name"]] = cls.relations_value(field)

        return example

    @staticmethod
    def relations_schemas(thy):
        """
        Generates specs from fields
        """

        record = {
            "type": "object",
            "properties": {},
        }

        required = []

        for field in thy._fields:

            property = {
                "type": field["kind"]
            }

            if field.get("readonly"):
                property["readOnly"] = True

            if field.get("required"):
                required.append(field["name"])

            record["properties"][field['name']] = property

        if required:
            record["required"] = required

        singular = {
            "type": "object",
            "properties": {
                thy.SINGULAR: {
                    "$ref": f"#/components/schemas/{thy._model.TITLE}"
                }
            }
        }

        plural = {
            "type": "object",
            "properties": {
                thy.PLURAL: {
                    "type": "array",
                    "items": {
                        "$ref": f"#/components/schemas/{thy._model.TITLE}"
                    }
                }
            }
        }

        filter = {
            "type": "object",
            "properties": {
                "filter": {
                    "$ref": f"#/components/schemas/{thy._model.TITLE}"
                }
            },
        }

        sort = {
            "type": "object",
            "properties": {
                "sort": {
                    "type": "array",
                    "description": "sort by these fields, prefix with + for ascending (default), - for descending",
                    "default": thy._model._order
                }
            }
        }

        limit = {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": f"limit the number of {thy.PLURAL}"
                },
                "limit__start": {
                    "type": "integer",
                    "description": f"limit the number of {thy.PLURAL} starting here"
                },
                "limit__per_page": {
                    "type": "integer",
                    "description": f"limit the number of {thy.PLURAL} by this page size (default {thy._model.CHUNK})"
                },
                "limit__page": {
                    "type": "integer",
                    "description": f"limit the number of {thy.PLURAL} and retrieve this page"
                }
            }
        }

        count = {
            "type": "object",
            "properties": {
                "count": {
                    "type": "boolean",
                    "description": f"return only the count of {thy.PLURAL} found"
                }
            }
        }

        return {
            thy._model.TITLE: record,
            thy.SINGULAR: singular,
            thy.PLURAL: plural,
            f"{thy.SINGULAR}_filter": filter,
            f"{thy.SINGULAR}_sort": sort,
            f"{thy.SINGULAR}_limit": limit,
            f"{thy.SINGULAR}_count": count
        }

    @classmethod
    def relations_create_options(cls, thy):
        """
        Generates create options operation
        """

        return {
            "tags": [thy._model.TITLE],
            "operationId": f"{thy.SINGULAR}_create_options",
            "summary": f"generates and validates fields to create one {thy.SINGULAR} or many {thy.PLURAL}",
            "description": f"To generate, send nothing. To validate, send a {thy.SINGULAR}.",
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": f"#/components/schemas/{thy.SINGULAR}"
                        },
                        "examples": {
                            "generate": {
                                "value": {}
                            },
                            "validate": {
                                "value": {
                                    thy.SINGULAR: cls.relations_example(thy)
                                }
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": f"fields to create one {thy.SINGULAR} or many {thy.PLURAL} generated and validated",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": '#/components/schemas/Options'
                            }
                        }
                    }
                }
            }
        }

    @classmethod
    def relations_create_filter(cls, thy):
        """
        Generates create operation
        """

        return {
            "tags": [thy._model.TITLE],
            "operationId": f"{thy.SINGULAR}_create_search",
            "summary": f"creates one {thy.SINGULAR} or many {thy.PLURAL} or a complex retrieve",
            "description": f"To create one, send {thy.SINGULAR}. To create many, send {thy.PLURAL}. To retrieve send filter (sort, limit, count optional).",
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "oneOf": [
                                {
                                    "$ref": f"#/components/schemas/{thy.SINGULAR}",
                                },
                                {
                                    "$ref": f"#/components/schemas/{thy.PLURAL}"
                                },
                                {
                                    "oneOf": [
                                        {
                                            "$ref": f"#/components/schemas/{thy.SINGULAR}_filter"
                                        }
                                    ],
                                    "anyOf": [
                                        {
                                            "$ref": f"#/components/schemas/{thy.SINGULAR}_sort"
                                        },
                                        {
                                            "$ref": f"#/components/schemas/{thy.SINGULAR}_limit"
                                        },
                                        {
                                            "$ref": f"#/components/schemas/{thy.SINGULAR}_count"
                                        }
                                    ]
                                }
                            ]
                        },
                        "examples": {
                            "create one": {
                                "value": {
                                    thy.SINGULAR: cls.relations_example(thy)
                                }
                            },
                            "create many": {
                                "value": {
                                    thy.PLURAL: [cls.relations_example(thy)]
                                }
                            },
                            "complex retrieve": {
                                "value": {
                                    "filter": cls.relations_example(thy),
                                    "sort": thy._model._order
                                }
                            },
                            "limit retrieve": {
                                "value": {
                                    "filter": cls.relations_example(thy),
                                    "sort": thy._model._order,
                                    "limit": {
                                        "limit": thy._model.CHUNK,
                                        "start": 0
                                    }
                                }
                            },
                            "paginate retrieve": {
                                "value": {
                                    "filter": cls.relations_example(thy),
                                    "sort": thy._model._order,
                                    "limit": {
                                        "page": 1,
                                        "per_page": thy._model.CHUNK
                                    }
                                }
                            },
                            "count retrieve": {
                                "value": {
                                    "filter": cls.relations_example(thy),
                                    "count": True
                                }
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": f"many {thy.PLURAL} retrieved",
                    "content": {
                        "application/json": {
                            "schema": {
                                "oneOf": [
                                    {
                                        "$ref": f"#/components/schemas/{thy.PLURAL}"
                                    },
                                    {
                                        "$ref": "#/components/schemas/Retrieved"
                                    },
                                ]
                            },
                            "examples": {
                                "list retrieve": {
                                    "value": {
                                        thy.PLURAL: [cls.relations_example(thy, readonly=True)],
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
                    "description": f"one {thy.SINGULAR} or many {thy.PLURAL} created",
                    "content": {
                        "application/json": {
                            "schema": {
                                "oneOf": [
                                    {
                                        "$ref": f"#/components/schemas/{thy.SINGULAR}",
                                        "description": "lol"
                                    },
                                    {
                                        "$ref": f"#/components/schemas/{thy.PLURAL}"
                                    }
                                ]
                            },
                            "examples": {
                                "create one": {
                                    "value": {
                                        thy.SINGULAR: cls.relations_example(thy, readonly=True)
                                    }
                                },
                                "create many": {
                                    "value": {
                                        thy.PLURAL: [cls.relations_example(thy, readonly=True)]
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
        }

    @classmethod
    def relations_retrieve_many(cls, thy):
        """
        Generates reteieve many operation
        """

        return {
            "tags": [thy._model.TITLE],
            "operationId": f"{thy.SINGULAR}_retrieve_many",
            "summary": f"retrieves many {thy.PLURAL}",
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
                                **cls.relations_example(thy),
                                "sort": ",".join(thy._model._order)
                            }
                        },
                        "limit": {
                            "value": {
                                **cls.relations_example(thy),
                                "sort": ",".join(thy._model._order),
                                "limit": thy._model.CHUNK,
                                "limit__start": 0
                            }
                        },
                        "paginate": {
                            "value": {
                                **cls.relations_example(thy),
                                "sort": ",".join(thy._model._order),
                                "limit__page": 1,
                                "limit__per_page": thy._model.CHUNK
                            }
                        },
                        "count": {
                            "value": {
                                **cls.relations_example(thy),
                                "count": 1
                            }
                        }
                    }
                }
            ],
            "responses": {
                "200": {
                    "description": f"many {thy.PLURAL} retrieved",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{thy.PLURAL}"
                            },
                            "examples": {
                                "list retrieve": {
                                    "value": {
                                        thy.PLURAL: [cls.relations_example(thy, readonly=True)],
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
        }

    @classmethod
    def relations_update_many(cls, thy):
        """
        Generates update emany operation
        """

        return {
            "tags": [thy._model.TITLE],
            "operationId": f"{thy.SINGULAR}_update_many",
            "summary": f"updates many {thy.PLURAL}",
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
                                **cls.relations_example(thy)
                            }
                        },
                        "filter through params limit": {
                            "value": {
                                **cls.relations_example(thy),
                                "sort": ",".join(thy._model._order),
                                "limit": thy._model.CHUNK,
                                "limit__start": 0
                            }
                        },
                        "filter through params paginate": {
                            "value": {
                                **cls.relations_example(thy),
                                "sort": ",".join(thy._model._order),
                                "limit__page": 1,
                                "limit__per_page": thy._model.CHUNK
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
                                    "$ref": f"#/components/schemas/{thy.SINGULAR}"
                                },
                                {
                                    "$ref": f"#/components/schemas/{thy.SINGULAR}_filter"
                                }
                            ]
                        },
                        "examples": {
                            "filter through params": {
                                "value": {
                                    thy.PLURAL: cls.relations_example(thy)
                                }
                            },
                            "filter through body": {
                                "value": {
                                    "filter": cls.relations_example(thy),
                                    thy.PLURAL: cls.relations_example(thy)
                                }
                            },
                            "filter through body limit": {
                                "value": {
                                    "filter": cls.relations_example(thy),
                                    "sort": thy._model._order,
                                    "limit": {
                                        "limit": thy._model.CHUNK,
                                        "start": 0
                                    },
                                    thy.PLURAL: cls.relations_example(thy)
                                }
                            },
                            "filter through body paginate": {
                                "value": {
                                    "filter": cls.relations_example(thy),
                                    "sort": thy._model._order,
                                    "limit": {
                                        "page": 1,
                                        "per_page": thy._model.CHUNK
                                    },
                                    thy.PLURAL: cls.relations_example(thy)
                                }
                            },
                            "update all": {
                                "value": {
                                    "filter": {},
                                    thy.PLURAL: cls.relations_example(thy)
                                }
                            }
                        }
                    }
                }
            },
            "responses": {
                "202": {
                    "description": f"many {thy.PLURAL} updated",
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
        }

    @classmethod
    def relations_delete_many(cls, thy):
        """
        Generates delete many operation
        """

        return {
            "tags": [thy._model.TITLE],
            "operationId": f"{thy.SINGULAR}_delete_many",
            "summary": f"deletes many {thy.PLURAL}",
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
                                **cls.relations_example(thy)
                            }
                        },
                        "filter through params limit": {
                            "value": {
                                **cls.relations_example(thy),
                                "sort": ",".join(thy._model._order),
                                "limit": thy._model.CHUNK,
                                "limit__start": 0
                            }
                        },
                        "filter through params paginate": {
                            "value": {
                                **cls.relations_example(thy),
                                "sort": ",".join(thy._model._order),
                                "limit__page": 1,
                                "limit__per_page": thy._model.CHUNK
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
                                    "$ref": f"#/components/schemas/{thy.SINGULAR}_filter"
                                }
                            ]
                        },
                        "examples": {
                            "filter through params": {
                                "value": {}
                            },
                            "filter through body": {
                                "value": {
                                    "filter": cls.relations_example(thy)
                                }
                            },
                            "filter through body limit": {
                                "value": {
                                    "filter": cls.relations_example(thy),
                                    "sort": thy._model._order,
                                    "limit": {
                                        "limit": thy._model.CHUNK,
                                        "start": 0
                                    }
                                }
                            },
                            "filter through body paginate": {
                                "value": {
                                    "filter": cls.relations_example(thy),
                                    "sort": thy._model._order,
                                    "limit": {
                                        "page": 1,
                                        "per_page": thy._model.CHUNK
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
                    "description": f"many {thy.PLURAL} deleted",
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
        }

    @classmethod
    def relations_update_options(cls, thy):
        """
        Generates update options operation
        """

        return {
            "tags": [thy._model.TITLE],
            "operationId": f"{thy.SINGULAR}_update_options",
            "summary": f"generates and validates fields to update one {thy.SINGULAR}",
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": f"#/components/schemas/{thy.SINGULAR}"
                        },
                        "examples": {
                            "generate": {
                                "value": {}
                            },
                            "validate": {
                                "value": {
                                    thy.SINGULAR: cls.relations_example(thy)
                                }
                            }
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": f"fields to update one {thy.SINGULAR} generated and validated",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": '#/components/schemas/Options'
                            }
                        }
                    }
                },
                "404": {
                    "description": f"{thy.SINGULAR} not found"
                }
            }
        }

    @classmethod
    def relations_retrieve_one(cls, thy):
        """
        Generates retrieve one operation
        """

        return {
            "tags": [thy._model.TITLE],
            "operationId": f"{thy.SINGULAR}_retrieve_one",
            "summary": f"retrieves one {thy.SINGULAR}",
            "responses": {
                "200": {
                    "description": f"one {thy.SINGULAR} retrieved",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{thy.SINGULAR}"
                            },
                            "examples": {
                                "retrieve": {
                                    "value": {
                                        thy.SINGULAR: cls.relations_example(thy, readonly=True),
                                        "overflow": False,
                                        "formats": {}
                                    }
                                }
                            }
                        }
                    }
                },
                "404": {
                    "description": f"{thy.SINGULAR} not found"
                }
            }
        }

    @classmethod
    def relations_update_one(cls, thy):
        """
        Generates update one operation
        """

        return {
            "tags": [thy._model.TITLE],
            "operationId": f"{thy.SINGULAR}_update_one",
            "summary": f"updates one {thy.SINGULAR}",
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": f"#/components/schemas/{thy.SINGULAR}"
                        },
                        "examples": {
                            "update": {
                                "value": {
                                    thy.SINGULAR: cls.relations_example(thy)
                                }
                            }
                        }
                    }
                }
            },
            "responses": {
                "202": {
                    "description": f"one {thy.SINGULAR} updated",
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
                    "description": f"{thy.SINGULAR} not found"
                }
            }
        }

    @classmethod
    def relations_delete_one(cls, thy):
        """
        Generates delete one operation
        """

        return {
            "tags": [thy._model.TITLE],
            "operationId": f"{thy.SINGULAR}_delete_one",
            "summary": f"deletes one {thy.SINGULAR}",
            "responses": {
                "202": {
                    "description": f"one {thy.SINGULAR} deleted",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/"
                            }
                        }
                    }
                },
                "404": {
                    "description": f"{thy.SINGULAR} not found"
                }
            }
        }

    def relations_operations(self, specs, ns, urls, thy): # pylint: disable=too-many-branches
        """
        Generates operations for all methods
        """

        for url in self.api.ns_urls(ns, urls):

            path = flask_restx.swagger.extract_path(url)

            methods = specs["paths"][path]
            specs["paths"][path] = collections.OrderedDict()

            for method in ["options", "post", "get", "patch", "delete"]:

                if "{" not in path:
                    if method == "options":
                        specs["paths"][path][method] = {**methods[method], **self.relations_create_options(thy)}
                    elif method == "post":
                        specs["paths"][path][method] = {**methods[method], **self.relations_create_filter(thy)}
                    elif method == "get":
                        specs["paths"][path][method] = {**methods[method], **self.relations_retrieve_many(thy)}
                    elif method == "patch":
                        specs["paths"][path][method] = {**methods[method], **self.relations_update_many(thy)}
                    elif method == "delete":
                        specs["paths"][path][method] = {**methods[method], **self.relations_delete_many(thy)}
                else:
                    if method == "options":
                        specs["paths"][path][method] = {**methods[method], **self.relations_update_options(thy)}
                    elif method == "post":
                        continue
                    elif method == "get":
                        specs["paths"][path][method] = {**methods[method], **self.relations_retrieve_one(thy)}
                    elif method == "patch":
                        specs["paths"][path][method] = {**methods[method], **self.relations_update_one(thy)}
                    elif method == "delete":
                        specs["paths"][path][method] = {**methods[method], **self.relations_delete_one(thy)}

    def relations_resource(self, specs, ns, resource, urls):
        """
        Overrides OpenApi specs for a Relations Resource
        """

        thy = resource.thy()

        specs["tags"].append({
            "name": thy._model.TITLE
        })

        specs["components"]["schemas"].update(self.relations_schemas(thy))

        self.relations_operations(specs, ns, urls, thy)

    def as_dict(self):
        """
        Overides swagger dict to make it OpenAPI
        """

        specs = super().as_dict()

        del specs["swagger"]
        specs["openapi"] = "3.0.3"

        specs.setdefault("components", {})
        specs["components"].setdefault("schemas", {})

        specs["components"]["schemas"].update({
            "Field": {
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
            },
            "Options": {
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
            },
            "Retrieved": {
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
            },
            "Counted": {
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "description": "count of those retrieved"
                    }
                }
            },
            "Updated": {
                "type": "object",
                "properties": {
                    "updated": {
                        "type": "integer",
                        "description": "count of those updated"
                    }
                }
            },
            "Deleted": {
                "type": "object",
                "properties": {
                    "deleted": {
                        "type": "integer",
                        "description": "count of those deleted"
                    }
                }
            }
        })

        for ns in self.api.namespaces:
            for resource, urls, _, _ in ns.resources:
                if hasattr(resource, "thy"):
                    self.relations_resource(specs, ns, resource, urls)

        return specs


class Api(flask_restx.Api):
    """
    Overrride Flask RestX API
    """

    @cached_property
    def __schema__(self):
        """
        The Swagger specifications/schema for this API

        :returns dict: the schema as a serializable dict
        """
        if not self._schema:
            try:
                self._schema = OpenApi(self).as_dict()
            except Exception: # pragma: no cover
                # Log the source exception for debugging purpose
                # and return an error message
                msg = "Unable to render schema"
                flask_restx.api.log.exception(msg)  # This will provide a full traceback
                return {"error": msg}
        return self._schema
