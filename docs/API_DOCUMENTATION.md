# API Reference

Both backends expose the same endpoints under `/api/`. The API-only backend checks indentation and syntax. The full backend also runs pattern-based security and code-quality checks.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health/` | Health check |
| `POST` | `/api/analyze/` | Analyze JSON code or upload a `.py` file |
| `GET` | `/api/report/<filename>/` | Get report download information |
| `GET` | `/api/report/<filename>/?download=true` | Download the generated PDF |

## Analyze code

Send JSON:

```bash
curl -X POST http://127.0.0.1:8000/api/analyze/ \
  -H 'Content-Type: application/json' \
  -d '{"code":"def hello():\n    print(\"Hello\")","filename":"example"}'
```

Or upload a Python file using multipart form data with the field name `file`:

```bash
curl -X POST http://127.0.0.1:8000/api/analyze/ -F 'file=@example.py'
```

The JSON response includes `status`, `has_errors`, `errors` when findings exist, `output` when checks pass, and a text `report`. Findings are returned in the response and are not stored in the configured SQLite database.

## Download report

Replace `example` with the response's `filename`:

```bash
curl -OJ 'http://127.0.0.1:8000/api/report/example/?download=true'
```

The download is a PDF. Without `download=true`, the endpoint returns JSON with the PDF download URL. Reports are written to the backend's local `reports/` directory.

## Security

The full `securecode-backend` API does not execute submitted code. The separate `securecode-api` backend still executes submissions when syntax and indentation checks pass, with a five-second timeout; this is not a sandbox. Use only trusted code with that backend. Development settings also allow all hosts and CORS origins; do not expose the server to untrusted networks or use these settings in production.

## Local and network addresses

`./run-local.sh` binds the React UI and API to `127.0.0.1`, so open the UI at http://127.0.0.1:3000/ on the same computer. The API-only quick start also binds to loopback by default.

To let another device reach the API, bind Django to `0.0.0.0:8000` and connect from that device to `http://<server-LAN-IP>:8000/`. Use the server's actual LAN IP in the client; `0.0.0.0` is only the server bind address. The included React and static clients use `127.0.0.1` as their API host, so they work locally by default and are not configured for remote clients.
