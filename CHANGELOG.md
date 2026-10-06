# Changelog

All notable changes to python-relations-restx are recorded here, newest first. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [SemVer](https://semver.org/).

## [Unreleased]

Shipping as 0.6.5, with relations-dil 0.6.16.

### Added
- Tests for a parent key stored in a dict field (`child_inject` in relations-dil 0.6.16): it comes through as an optional form field that carries its `inject`, gets its parent picker, formats with no titles when there's no parent, and posts, lists, filters, patches, clears and deletes like any other key. A mass patch through it is refused.

## [0.6.4] - 2026-06-08

- Bumped the `relations-dil` requirement to 0.6.15 and installed git in the Dockerfile; tests were extended to cover searching ties through attributes.

## [0.6.3] - 2026-06-07

- Fixed relation lookups for option titles and formats in `Resource` to use the parent relation's `parent_id` instead of `parent_field`, supporting many-to-many relations.
- Bumped `relations-dil` to 0.6.14, pinned `jsonschema`, `MarkupSafe` and `click`, and changed the setup step to `pip install .`.

## [0.6.2] - 2022-12-10

- Moved the package version into a `VERSION` file, read by `setup.py` and the Makefile, with an optional `BUILD_VERSION` override for builds.
- Bumped the `relations-dil` requirement to 0.6.12.

## [0.6.1] - 2022-08-09

- Fixed the PyPI description title to use the `relations-restx` name and bumped the version.

## [0.6.0] - 2022-08-09

- Prepared the package for PyPI with a `LICENSE.txt`, a `PYPI.md` description, and `testpypi` and `pypi` Makefile targets.
- Removed the git-based installs from the Dockerfile and setup step.

## [0.5.0] - 2022-06-11

- Added `Api` and `OpenApi` classes (in `relations_restx.api`) that override the Flask-RESTX Swagger generation so the OpenAPI document and GUI describe each model's fields, examples, filters, sorting and limits.
- Added `bin/api.py` and `bin/restx_models.py` for running an example API, with Kubernetes and Tilt manifests for development.

## [0.4.0] - 2022-05-01

- Updated the `python-relations` requirement to 0.6.10 and removed the `python-relations-rest` requirement.
- Switched tests to the new shared unittest location and made small fixes to `setup.py` and the Makefile.

## [0.3.0] - 2022-04-30

- Removed the REST `Source` and the unittest helper from this package, which now only provides the Flask-RESTX server side.
- Dropped the dependency on `python-relations-rest` and updated the docstrings to say RestX.

## [0.2.0] - 2022-04-30

- Renamed the package from `python-relations-restful` to `python-relations-restx` in `setup.py`.

## [0.1.0] - 2022-04-30

- Initial release with `Resource` and `ResourceIdentity` classes that expose a Relations model as Flask-RESTX CRUD endpoints, with `ResourceError` and an `exceptions` decorator that turns errors into JSON responses with 400, 404 or 500 status codes.
- Added `resources`, `ensure` and `attach` helpers that find or generate a `Resource` for each model and register it on a RESTX API, plus a `/model` endpoint listing the available models.
- Also included a REST `Source` and a unittest helper module, with tests, Dockerfile, Jenkinsfile and Makefile.
