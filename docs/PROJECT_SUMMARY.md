# Project Summary

SecureCode has two Django backends and two web clients:

- `securecode-api/`: indentation and syntax checks, API, and CLI.
- `securecode-backend/`: the same API and CLI plus pattern-based security and code-quality checks and a basic static UI.
- `securecode-ui/`: React client for the full backend.

Both APIs accept pasted code as JSON or a `.py` upload, return findings as JSON, and generate PDF reports in a local `reports/` directory. The full-backend CLI also checks security patterns and code quality, and scans folders recursively; the API-only CLI checks syntax and indentation only.

Start the full app with `./run-local.sh`; setup details are in [Quick Start](QUICKSTART.md). See the [API Reference](API_DOCUMENTATION.md) and [CLI Guide](CLI_DOCUMENTATION.md) for usage.

**Important:** The full backend and CLIs do not execute submitted code. The separate API-only backend still executes submissions that pass its checks; its timeout is not a sandbox. Use only trusted code with that backend.
