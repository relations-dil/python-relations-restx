# Changelog

All notable changes to python-relations-restx are recorded here, newest first. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [SemVer](https://semver.org/).

## [Unreleased]

### Added
- Jenkins releases on a merge to `main`: a `release` stage (only on `main`) runs `make release`, which does nothing for a version that is already released and otherwise does the test release, the release and the tag. It pushes the tag with the `github` credential, as Leroy Jenkins, one build at a time, with a two hour timeout (relations-dil/python-relations#80). The package builds run in a copy with only the files they use mounted read-only, so nothing root-owned is left in the workspace, and `make tag` stops on a failure instead of ignoring it. The release scripts work with the older git on the Jenkins host.
- `make help` lists every target with what it does (each target has a `## description` after it), and is what a bare `make` runs.
- Release tooling, the same as relations-dil's (relations-dil/python-relations#77): `make new` starts a release, `make version` sets the version, `make release-check` says where a release is up to and what would stop it, `make release` does what's left (checks, TestPyPI and a clean install from it, PyPI, the tag), `make dist-check` builds and checks the distributions, and `make test-release` tests the scripts against a throwaway repo and fake indexes. The work is in `scripts/`.

### Changed
- `make release-check` and `make release` don't run `build`, `test`, `lint` and `setup` again: the Jenkins stages have just run them before the release stage, so it was the same work twice. Run them yourself before checking by hand, as `make release-check` is only the checks and `dist-check` now (relations-dil/python-relations#90).
- Every `docker run` in the `Makefile` uses `--rm`, and a replaced database container is removed with its volume (`docker rm --force -v`), so builds and test runs leave no stopped containers or volumes behind.
- `testpypi` and `pypi` run in the current `python` image with `build` and `twine` installed on the fly, so the custom `gaf3/pypi` image is no longer used.

Shipping as 0.6.5, with relations-dil 0.6.16.

### Added
- Tests for a parent key stored in a dict field (`child_inject` in relations-dil 0.6.16): it comes through as an optional form field that carries its `inject`, gets its parent picker, formats with no titles when there's no parent, and posts, lists, filters, patches, clears and deletes like any other key. A mass patch through it is refused.

## [0.6.7] - 2026-10-14

### Changed
- `exceptions` picks the status by what was raised, not by what it says: a `relations.NotFoundError` is a 404 and a `relations.UniqueError` is a 409, any other `ModelError` a 500. A plain `ModelError` that only says "none retrieved" used to be a 404 and is now a 500, every source raises `NotFoundError` for it now.
- `ResourceError` is a `relations.RelationsError`. Needs relations-dil 0.6.19 (relations-dil/python-relations#78).

## [0.6.6] - 2026-10-14

### Changed
- The form for updating a record (`OPTIONS` with an id) marks a readonly field readonly, so a string id (relations-dil 0.6.18, supplied by the caller) shows as fixed on update instead of editable. A PATCH that changed it was already ignored. The form for creating one is unchanged, the id is required there.
- Needs relations-dil 0.6.18.

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
