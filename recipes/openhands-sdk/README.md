# Packaging status

This is a preparatory recipe for the published PyPI release 1.63.1, not
the changing dependency metadata on upstream `main`.

Before submitting this recipe for merge:

- Package `lmnr >=0.7.60,<0.8.0` and its missing dependencies, including
  `lmnr-claude-code-proxy`. Audit its transitive version constraints too.
- Make `litellm >=1.108.3,<1.109` available on conda-forge. The newer
  published conda builds do not satisfy this upper bound; do not loosen it
  without upstream compatibility evidence.
- Run the package import and `pip check` tests with the completed dependency
  set. Rendering and linting alone do not establish installability.

Availability was checked against the conda-forge Anaconda API on 2026-11-23.
`tree-sitter` on PyPI maps to `tree_sitter` on conda-forge. The `lua` and
`socks` extras are represented explicitly by `lupa` and `socksio`.
Optional boto3, Vertex and ToolShield extras are not enabled.

The sdist lacks a license file. The second source supplies the MIT license
from the immutable commit behind upstream tag `v1.63.1`.

This recipe does not package Canvas or change its runtime launcher. Eliminating
Canvas's `uvx`/`npx` downloads is separate work after its backend dependencies
are available.

## Local validation (2026-11-23)

- conda-smithy 2026.11.6 lint: passed.
- rattler-build 0.81.0 rendering: passed.
- Source download, checksum verification and noarch package generation on
  osx-arm64: passed.
- Tests: not executed; test environment solving failed because `litellm >=1.108.3,<1.109`
  was unavailable. This is not a passing end-to-end build.
