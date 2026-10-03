# Full Backend

This Django backend provides the API and CLI, plus pattern-based security and code-quality checks and a static HTML UI. The React UI lives in `../securecode-ui/`.

From the repository root, run `./run-local.sh` to install dependencies in local environments, apply migrations, and start both services bound to `127.0.0.1`. Open http://127.0.0.1:3000/; the API is at http://127.0.0.1:8000/api/. This launcher is for the same computer only; the React client is not configured for LAN access.

- [Quick start](../docs/QUICKSTART.md)
- [API reference](../docs/API_DOCUMENTATION.md)
- [CLI guide](../docs/CLI_DOCUMENTATION.md)
- [Security scanner guide](docs/SECURITY_SCANNER_GUIDE.md)

**Security:** This backend analyzes submitted code without executing it.
