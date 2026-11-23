# Packaging status

This is a preparatory recipe for the published PyPI release 1.63.1, not
the changing dependency metadata on upstream `main`.

Before submitting this recipe for merge:

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

## Downstream optional tracing patch

The patch moves `lmnr >=0.7.60,<0.8.0` from mandatory dependencies to the
`observability` extra. This conda package does not include Laminar or its
Claude Code proxy. Optionalizing Laminar is discussed in
[upstream issue #5693](https://github.com/OpenHands/software-agent-sdk/issues/5693);
this patch is not an upstream-accepted change.

The Laminar dependency chain includes `lmnr-claude-code-proxy`. Release 0.1.22
does not supply a license file or declared license; release 0.2.0 declares
`LicenseRef-Proprietary` and its terms require written redistribution permission.
Do not add the proxy to conda-forge without resolving redistribution rights.

With no tracing configuration, SDK operations use the existing no-op tracing
paths. If any supported Laminar/OpenTelemetry endpoint or API-key variable is
set while `lmnr` is absent, the patch raises an actionable error instead of
silently disabling requested tracing. It does not download optional packages.
Users must clear these variables or separately provide the optional integration.
Installing extras through pip is not part of the conda recipe.

The regression script checks SDK/ACP imports, sync/async tracing wrappers,
a local conversation with a mocked model response and real finish tool,
each tracing environment variable, optional-dependency metadata, and the
initialization path with a mocked Laminar module. It does not validate the
real Laminar service.

## Local validation (2026-11-23)

- conda-smithy 2026.11.6 lint: passed.
- rattler-build 0.81.0 rendering: passed.
- Source download, checksum verification and noarch package generation on
  osx-arm64: passed.
- Conda package tests: not executed; test environment solving failed because `litellm >=1.108.3,<1.109`
  was unavailable. This is not a passing end-to-end build.
- Separate Python 3.12 environment using the patched release source and PyPI
  dependencies: `test_no_lmnr.py` passed with neither `lmnr` nor its proxy
  installed; `uv pip check` passed for all 114 installed packages.
  This validates the patch behavior, not conda-forge dependency availability.
- The generated conda artifact metadata was inspected: `lmnr` is absent
  from conda runtime dependencies and is optional in Python distribution metadata.
  The same regression script also passed against its extracted Python files using
  the separate PyPI dependency environment (not a conda installation test).
