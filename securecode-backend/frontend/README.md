# Static UI

This folder contains the basic HTML/JavaScript client. Start the API and static UI from separate terminals:

```bash
cd securecode-backend
python3 manage.py runserver 127.0.0.1:8000
```

```bash
cd securecode-backend
python3 serve_frontend.py
```

Open http://127.0.0.1:3000/ on the same computer. The static page sends API requests to `127.0.0.1:8000`, so it is not configured for remote-device access. The React UI and API are documented in the [main README](../../README.md) and [API reference](../../docs/API_DOCUMENTATION.md).

The full backend analyzes submitted code without executing it.
