# Packaging status

This is a preparatory recipe for the published PyPI release 1.63.1, not
the changing dependency metadata on upstream `main`.

The LiteLLM dependency blocker is resolved. The conda-forge
[v1.108.x backfill PR](https://github.com/conda-forge/litellm-feedstock/pull/489)
was merged, and the public channel supplies releases satisfying
`litellm >=1.108.3,<1.109`. Validation below used public LiteLLM 1.108.20.

This SDK recipe is ready for review of the downstream optional-tracing patch.
Submit the SDK separately from Agent Server, whose `openhands-tools`
dependency still needs packaging.

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

## Local validation (2026-11-28)

- conda-smithy 2026.11.6 lint: passed.
- rattler-build 0.81.0 full build on osx-arm64: passed, including source
  checksum verification, patch application and noarch package generation.
- All build and runtime dependencies came from the public conda-forge channel;
  only the SDK under test was built locally. No locally built LiteLLM or
  PyPI-installed runtime dependencies were used.
- The solver selected LiteLLM 1.108.20. Import tests and `pip check`
  passed with Python 3.12 and Python 3.14 (the `"*"` test variant).
- `test_no_lmnr.py` passed in the conda Python 3.12 environment:
  SDK/ACP imports, a local conversation with a mocked model response,
  tracing-disabled sync/async helpers, actionable errors for each tracing
  environment variable, optional dependency metadata and mocked Laminar
  initialization. Neither Laminar nor its proxy was installed.
- Linux and Windows builds, live model calls and the real Laminar service
  were not tested locally.

Reproduction (the output directory must not contain a local LiteLLM package):

```sh
rattler-build build -r recipes/openhands-sdk/recipe.yaml   -c conda-forge --output-dir sdk-public-validation
```
