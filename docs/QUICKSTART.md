# Quick Start

## Full App

From the repository root, run:

```bash
./run-local.sh
```

On first run, this creates `securecode-backend/.venv`, installs backend and React dependencies, applies migrations, and starts both servers bound to `127.0.0.1`. Open http://127.0.0.1:3000/; the API is at http://127.0.0.1:8000/api/. Press `Ctrl+C` to stop both servers. This launcher is local-machine-only.

## API Only

```bash
cd securecode-api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Check the API with `curl http://127.0.0.1:8000/api/health/`. For API access from another device, run Django with `python manage.py runserver 0.0.0.0:8000`, then connect to `http://<server-LAN-IP>:8000/` using the server computer's actual LAN IP. `0.0.0.0` is a bind address, not a URL to open. The bundled React UI still targets `127.0.0.1`, so it is not configured for remote-device access.

## CLI

Run the CLI from either backend directory:

```bash
python3 cli.py path/to/file.py
```

See [CLI Documentation](CLI_DOCUMENTATION.md) for full-backend CLI options. The full backend does not execute submitted code. The separate `securecode-api` backend still executes valid submissions and should only be used with trusted code.
