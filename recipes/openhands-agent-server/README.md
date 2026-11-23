# Packaging status

This is a preparatory recipe for the published PyPI release 1.63.1.

Before submitting this recipe for merge:

- Publish `openhands-sdk` and `openhands-tools` on conda-forge, including
  their dependencies. Neither was available under those names when checked
  on 2026-11-23. The sibling SDK recipe documents its known blockers.
- Verify the complete dependency solve and run the import, `pip check` and
  `agent-server --help` tests. Rendering and linting are not build tests.
- Test the server with the intended SDK/tools release combination. The
  recipe preserves the unversioned SDK/tools requirements in the upstream
  distribution rather than inventing a compatibility range.

The PyPI `docker` dependency maps to conda-forge's `docker-py` Python client;
it does not install a Docker daemon. The optional PostHog extra is not enabled.

The sdist lacks a license file. The second source supplies the MIT license
from the immutable commit behind upstream tag `v1.63.1`.

Packaging this server does not guarantee download-free execution of every
tool, container, editor or external ACP agent. Canvas launcher changes and
an audit of optional runtime downloads remain separate work.

## Local validation (2026-11-23)

- conda-smithy 2026.11.6 lint: passed.
- rattler-build 0.81.0 rendering: passed.
- Source download, checksum verification and noarch package generation on
  osx-arm64: passed.
- Tests: not executed; test environment solving failed because `openhands-sdk`
  was unavailable. This is not a passing end-to-end build.
