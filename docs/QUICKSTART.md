# Quick Start

## Requirements

The local launcher requires Python 3 with `venv`, Node.js/npm, Bash, and `fuser` available on `PATH`.

## Full App

From the repository root, run:

```bash
./run-local.sh
```

On first run, this creates `securecode-backend/.venv`, installs backend and React dependencies, applies migrations, and starts both servers bound to `127.0.0.1`. Open http://127.0.0.1:3000/; the API is at http://127.0.0.1:8000/api/. Press `Ctrl+C` to stop both servers. This launcher is local-machine-only.

The launcher enables Django debug mode only for this local run and generates a fresh random secret key in memory for that process. It does not write the key to disk. Both settings files default to `DEBUG=False`; outside the launcher, set `DJANGO_SECRET_KEY` before starting Django or startup will fail. See the root `.env.example` for the supported environment variables. Django does not load that file automatically; source your local `.env` or export the values in your shell.

Use `./run-local.sh --help` to see launcher options. If a required port is occupied, `./run-local.sh --kill-ports` stops the process using ports 3000 and 8000 before startup.

## API Only

Configure the required settings before starting the API. For example, from `securecode-api`:

```bash
export DJANGO_SECRET_KEY='replace-with-a-fresh-random-secret'
export DJANGO_DEBUG=0
```

Set `DJANGO_ALLOWED_HOSTS` and `DJANGO_CORS_ORIGINS` as needed for your deployment. Their local defaults are `127.0.0.1,localhost` and `http://127.0.0.1:3000,http://localhost:3000` respectively. Do not use debug mode or the example placeholder secret in production.

```bash
cd securecode-api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Check the API with `curl http://127.0.0.1:8000/api/health/`. The API-only setup is intended for local use. Keep it bound to `127.0.0.1`; do not bind it to a network interface or expose it to other devices because the analysis endpoint has no user authentication.

The analysis endpoint is `POST /api/analyze/`; it accepts JSON with a `code` string and optional `filename`, or a `.py` file upload. Reports can be downloaded with `GET /api/report/<report_id>/?download=true`. The endpoint has no user authentication and is CSRF-exempt. Keep it bound to loopback; do not expose it to a shared network or the public internet without adding and reviewing access controls.

Submitted code is inspected, never executed. Requests are limited by Django's request-size setting and by a 200,000-character source limit. Report PDFs are stored locally and reports older than 24 hours are removed during a later analysis request.

## CLI

Run the full scanner from the repository root:

```bash
python3 cli.py path/to/file.py
python3 cli.py path/to/project
```

The full scanner CLI also accepts JSON/PDF output, multiple paths, and standard input. See [CLI Documentation](CLI_DOCUMENTATION.md) for options. The separate `securecode-api/cli.py` checks syntax and indentation only; the root CLI and `securecode-backend/cli.py` also run security-pattern and code-quality checks.
