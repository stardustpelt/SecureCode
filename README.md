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

**Security:** Both Django APIs and both CLIs inspect submitted Python source without executing it. The APIs return `No code was executed.` Static analysis is heuristic and does not prove that code is secure.

## API

The local API is available at `http://127.0.0.1:8000/api/` when the app is running.

- `GET /api/health/` checks API availability.
- `POST /api/analyze/` accepts JSON containing Python source, or a `.py` file upload.
- `GET /api/report/<report_id>/?download=true` downloads the PDF report returned by an analysis.

Example request body:

```json
{
	"code": "print('Hello, world!')",
	"filename": "example"
}
```

The analysis endpoint has no user authentication. Keep it on loopback; do not expose it to a shared network or the public internet without adding and reviewing appropriate access controls.

## Documentation

- [Quick Start](docs/QUICKSTART.md): run the full app or API-only backend
- [Analysis Capabilities](docs/ANALYSIS_CAPABILITIES.md): checks, backend differences, and limitations
- [CLI Guide](docs/CLI_DOCUMENTATION.md): local file checks
