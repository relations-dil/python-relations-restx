
import flask_restx

from werkzeug.utils import cached_property

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
            except Exception:
                # Log the source exception for debugging purpose
                # and return an error message
                msg = "Unable to render schema"
                flask_restx.api.log.exception(msg)  # This will provide a full traceback
                return {"error": msg}
        return self._schema


class OpenApi(flask_restx.Swagger):
    """
    Overrride Flask RestX Swagger
    """

    def relations_example(self, field):
        """
        Generates an example alues
        """

        if "default" in field:
            return field["default"]

        if field["kind"] == "str":
            return ""

        if field["kind"] == "int":
            return 0

        if field["kind"] == "bool":
            return True

        if field["kind"] == "float":
            return 0.0

    def relations_schemas(self, thy):
        """
        Generates specs from fields
        """

        schemas = {}

        record = {
            "type": "object",
            "properties": {},
        }

        required = []
        example = {

        }

        for field in thy._fields:

            property = {
                "type": field["kind"]
            }

            if field.get("readonly"):
                property["readOnly"] = True
            else:
                example[field["name"]] = self.relations_example(field)

            if field.get("required"):
                required.append(field["name"])

            record["properties"][field['name']] = property

        if required:
            record["required"] = required

        if example:
            record["example"] = example

        singular = {
            "type": "object",
            "properties": {
                thy.SINGULAR: {
                    "$ref": f"#/components/schemas/{thy._model.TITLE}"
                }
            },
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
            },
        }

        filter = {
            "type": "object",
            "properties": {
                "filter": {
                    "$ref": f"#/components/schemas/{thy._model.TITLE}"
                }
            },
        }

        return {
            thy._model.TITLE: record,
            thy.SINGULAR: singular,
            thy.PLURAL: plural,
            f"{thy.SINGULAR}_filter": filter,
        }

    def relations_create_options(self, thy):
        """
        Generates create options operation
        """

        return {
            "tags": [thy._model.TITLE],
            "operationId": f"{thy.SINGULAR}_create_options",
            "summary": f"generates and validates fields to create one {thy.SINGULAR} or many {thy.PLURAL}",
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": f"#/components/schemas/{thy.SINGULAR}"
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": f"fields to create one {thy.SINGULAR} or many {thy.PLURAL} generated and validated"
                }
            }
        }

    def relations_create_filter(self, thy):
        """
        Generates create operation
        """

        return {
            "tags": [thy._model.TITLE],
            "operationId": f"{thy.SINGULAR}_create_search",
            "summary": f"creates one {thy.SINGULAR} or many {thy.PLURAL} or a complex filter retrieve",
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "oneOf": [
                                {
                                    "$ref": f"#/components/schemas/{thy.SINGULAR}"
                                },
                                {
                                    "$ref": f"#/components/schemas/{thy.PLURAL}"
                                },
                                {
                                    "$ref": f"#/components/schemas/{thy.SINGULAR}_filter"
                                }
                            ]
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": f"many {thy.PLURAL} retrieved"
                },
                "201": {
                    "description": f"one {thy.SINGULAR} or many {thy.PLURAL} created"
                },
                "400": {
                    "description": f"unable to create due to bad request"
                }
            }
        }

    def relations_retrieve_many(self, thy):
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
                        "type": "object"
                    },
                    "style": "form",
                    "explode": True,
                        "name": "params"
                }
            ],
            "responses": {
                "200": {
                    "description": f"many {thy.PLURAL} retrieved"
                }
            }
        }

    def relations_update_many(self, thy):
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
                        "name": "params"
                }
            ],
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object"
                        }
                    }
                }
            },
            "responses": {
                "202": {
                    "description": f"many {thy.PLURAL} updated"
                },
                "400": {
                    "description": f"unable to update due to bad request"
                }
            }
        }

    def relations_delete_many(self, thy):
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
                        "name": "params"
                }
            ],
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object"
                        }
                    }
                }
            },
            "responses": {
                "202": {
                    "description": f"many {thy.PLURAL} deleted"
                }
            }
        }

    def relations_update_options(self, thy):
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
                            "type": "object"
                        }
                    }
                }
            },
            "responses": {
                "200": {
                    "description": f"fields to update one {thy.SINGULAR} generated and validated"
                },
                "404": {
                    "description": f"{thy.SINGULAR} not found"
                }
            }
        }

    def relations_retrieve_one(self, thy):
        """
        Generates reteieve one operation
        """

        return {
            "tags": [thy._model.TITLE],
            "operationId": f"{thy.SINGULAR}_retrieve_one",
            "summary": f"retrieves one {thy.SINGULAR}",
            "responses": {
                "200": {
                    "description": f"one {thy.SINGULAR} retrieved"
                },
                "404": {
                    "description": f"{thy.SINGULAR} not found"
                }
            }
        }

    def relations_update_one(self, thy):
        """
        Generates update eone operation
        """

        return {
            "tags": [thy._model.TITLE],
            "operationId": f"{thy.SINGULAR}_update_one",
            "summary": f"updates one {thy.SINGULAR}",
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object"
                        }
                    }
                }
            },
            "responses": {
                "202": {
                    "description": f"one {thy.SINGULAR} updated"
                },
                "400": {
                    "description": f"unable to update due to bad request"
                },
                "404": {
                    "description": f"{thy.SINGULAR} not found"
                }
            }
        }

    def relations_delete_one(self, thy):
        """
        Generates delete one operation
        """

        return {
            "tags": [thy._model.TITLE],
            "operationId": f"{thy.SINGULAR}_delete_one",
            "summary": f"deletes one {thy.SINGULAR}",
            "responses": {
                "202": {
                    "description": f"one {thy.SINGULAR} deleted"
                },
                "404": {
                    "description": f"{thy.SINGULAR} not found"
                }
            }
        }

    def relations_operations(self, specs, ns, urls, thy):
        """
        Generates operations for all methods
        """

        for url in self.api.ns_urls(ns, urls):

            path = flask_restx.swagger.extract_path(url)

            for method in ["options", "get", "post", "patch", "delete"]:

                if "{" not in path:
                    if method == "options":
                        specs["paths"][path][method].update(self.relations_create_options(thy))
                    elif method == "post":
                        specs["paths"][path][method].update(self.relations_create_filter(thy))
                    elif method == "get":
                        specs["paths"][path][method].update(self.relations_retrieve_many(thy))
                    elif method == "patch":
                        specs["paths"][path][method].update(self.relations_update_many(thy))
                    elif method == "delete":
                        specs["paths"][path][method].update(self.relations_delete_many(thy))
                else:
                    if method == "options":
                        specs["paths"][path][method].update(self.relations_update_options(thy))
                    elif method == "post":
                        del specs["paths"][path][method]
                        continue
                    elif method == "get":
                        specs["paths"][path][method].update(self.relations_retrieve_one(thy))
                    elif method == "patch":
                        specs["paths"][path][method].update(self.relations_update_one(thy))
                    elif method == "delete":
                        specs["paths"][path][method].update(self.relations_delete_one(thy))

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

        for ns in self.api.namespaces:
            for resource, urls, _, _ in ns.resources:
                if hasattr(resource, "thy"):
                    self.relations_resource(specs, ns, resource, urls)

        return specs
