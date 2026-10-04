# React UI

The React client sends code to the Django analysis API and downloads generated PDF reports. Its default API base is `https://secure-code-5m4t.onrender.com`; set `REACT_APP_API_BASE_URL` to override it.

## Run the full app

From the repository root:

```bash
./run-local.sh
```

Open http://127.0.0.1:3000/. The script installs dependencies and starts the API and UI together, bound to this computer only. The UI sends API requests to `http://127.0.0.1:8000/api/`.

## Run the UI separately

Start the backend using the [Quick Start](../docs/QUICKSTART.md), then run:

```bash
cd frontend
npm install
PORT=3001 npm start
```

The production bundle can be built with `npm run build`.

`./run-local.sh` overrides the API base to the local backend at `http://127.0.0.1:8000`. For Vercel, set `REACT_APP_API_BASE_URL` to the Render backend URL in the project environment settings, then redeploy. The backend must allow the exact Vercel origin in `DJANGO_CORS_ORIGINS`.

**Security:** The Django API inspects submitted code without executing it and returns `No code was executed.` Static checks are heuristic and do not prove that code is secure.
