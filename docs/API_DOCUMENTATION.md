# API Reference

Both backends expose the same endpoints under `/api/` and run syntax/indentation, pattern-based security, and code-quality checks. The API-only CLI remains syntax-and-indentation-only; the full-backend CLI also runs security and code-quality checks.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health/` | Health check |
| `POST` | `/api/analyze/` | Analyze JSON code or upload a `.py` file |
| `GET` | `/api/report/<report_id>/` | Get report download information (32-character UUID hex) |
| `GET` | `/api/report/<report_id>/?download=true` | Download the generated PDF |

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

The JSON response includes `status`, `has_errors`, `errors` when findings exist, `output` when checks pass, a text `report`, the display `filename`, and a random `report_id`. Findings are returned in the response and are not stored in the configured SQLite database.

## Download report

Use the response's `report_id` (not its display `filename`) to download the PDF:

```bash
curl -OJ 'http://127.0.0.1:8000/api/report/0123456789abcdef0123456789abcdef/?download=true'
```

The download is a PDF. Without `download=true`, the endpoint returns JSON with the PDF download URL. Reports are written under random UUID hex names in the backend's local `reports/` directory, so repeated requests with the same display filename do not overwrite one another.

## Security

Neither API executes submitted code; both return `No code was executed.` Scanner results are heuristic and may miss issues or report false positives. The local launcher binds to loopback by default. Both backends use explicit host and CORS environment settings; set them deliberately before exposing an unauthenticated API beyond the local machine.

## Local and network addresses

`./run-local.sh` binds the React UI and API to `127.0.0.1`, so open the UI at http://127.0.0.1:3000/ on the same computer. The API-only quick start also binds to loopback by default.

To let another device reach the API, bind Django to `0.0.0.0:8000` and connect from that device to `http://<server-LAN-IP>:8000/`. Use the server's actual LAN IP in the client; `0.0.0.0` is only the server bind address. The included React and static clients use `127.0.0.1` as their API host, so they work locally by default and are not configured for remote clients.
