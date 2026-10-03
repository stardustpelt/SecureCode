# API-Only Backend

This Django backend provides indentation and syntax checks, an API, and a local CLI. It does not include a web UI.

From this directory, create an isolated environment and start the API:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Check `http://127.0.0.1:8000/api/health/`. For another device, bind Django to `0.0.0.0:8000` and use `http://<server-LAN-IP>:8000/` from the client. `0.0.0.0` is a bind address, not a client URL. This exposes an API that executes submitted code; only do it on a trusted network and with trusted input.

- [Quick start](../docs/QUICKSTART.md)
- [API reference](../docs/API_DOCUMENTATION.md)
- [CLI guide](../docs/CLI_DOCUMENTATION.md)

**Security:** The API executes submitted code when checks pass. This is not a sandbox; analyze only trusted code.
