# API-Only Backend

This Django backend provides the analysis API and a syntax-and-indentation CLI. The API runs syntax, security-pattern, and code-quality checks; it does not include a web UI.

From this directory, create an isolated environment and start the API:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Check `http://127.0.0.1:8000/api/health/`. For another device, configure `DJANGO_ALLOWED_HOSTS` and `DJANGO_CORS_ORIGINS`, then bind Django to `0.0.0.0:8000` and use `http://<server-LAN-IP>:8000/` from the client. `0.0.0.0` is a bind address, not a client URL. This API does not execute submitted code, but it has no authentication; expose it only on a trusted network.

- [Quick start](../docs/QUICKSTART.md)
- [API reference](../docs/API_DOCUMENTATION.md)
- [CLI guide](../docs/CLI_DOCUMENTATION.md)

**Security:** The API inspects source and returns `No code was executed.` Its static checks are heuristic, not a guarantee that code is secure.
