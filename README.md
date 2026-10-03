# SecureCode

SecureCode checks Python files for indentation and syntax issues. The full backend also runs pattern-based security and code-quality checks. The project includes a Django API, local CLI, React UI, and basic static UI.

## Run Locally

From the repository root:

```bash
./run-local.sh
```

The script creates or reuses `securecode-backend/.venv`, installs backend dependencies there, installs frontend dependencies, applies migrations, and starts both services bound to this computer's loopback interface. Open http://127.0.0.1:3000/ and press `Ctrl+C` to stop both servers. The API is at http://127.0.0.1:8000/api/.

`run-local.sh` is for local browser access only. It does not expose the UI or API to other devices on your network.
If port `3000` or `8000` is occupied, stop that process or rerun `./run-local.sh --kill-ports` to send SIGTERM to the process using the required port before startup.

The API-only backend is in `securecode-api/`. See [Quick Start](docs/QUICKSTART.md) for setup options.

**Security:** The full backend analyzes submitted code without executing it. The separate `securecode-api` backend still executes valid submissions; use only trusted code with that backend and do not expose the development server to untrusted networks.

## Documentation

- [Quick Start](docs/QUICKSTART.md): run the full app or API-only backend
- [Analysis Capabilities](docs/ANALYSIS_CAPABILITIES.md): checks, backend differences, and limitations
- [Improvement Suggestions](docs/IMPROVEMENT_SUGGESTIONS.md): prioritized safety, scanner, API, and maintenance work
- [API Reference](docs/API_DOCUMENTATION.md): endpoints and request/response formats
- [CLI Guide](docs/CLI_DOCUMENTATION.md): local file checks
- [Project Summary](docs/PROJECT_SUMMARY.md): components and backend differences
- [Security Scanner Guide](securecode-backend/docs/SECURITY_SCANNER_GUIDE.md): full-backend checks and limitations
