# React UI

The React client sends code to the full Django backend at `http://127.0.0.1:8000/api/` and downloads generated PDF reports.

## Run the full app

From the repository root:

```bash
./run-local.sh
```

Open http://127.0.0.1:3000/. The script installs dependencies and starts the API and UI together, bound to this computer only. The UI sends API requests to `http://127.0.0.1:8000/api/`.

## Run the UI separately

Start the backend using the [Quick Start](../docs/QUICKSTART.md), then run:

```bash
cd securecode-ui
npm install
PORT=3001 npm start
```

The production bundle can be built with `npm run build`.

The UI is not configured for access from other devices: its API address points to loopback on the browser's own computer. Binding Django to `0.0.0.0` alone does not change that.

**Security:** Both Django APIs inspect submitted code without executing it and return `No code was executed.` Static checks are heuristic and do not prove that code is secure.
