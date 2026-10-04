#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/.venv"
LOCAL_HOST="127.0.0.1"
KILL_PORTS=false

usage() {
    printf 'Usage: %s [--kill-ports]\n' "${0##*/}"
    printf '  --kill-ports  Stop processes using TCP ports 3000 and 8000 before startup.\n'
}

for argument in "$@"; do
    case "$argument" in
        --kill-ports)
            KILL_PORTS=true
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            printf 'Error: unknown option: %s\n' "$argument" >&2
            usage >&2
            exit 2
            ;;
    esac
done

if ! command -v fuser >/dev/null 2>&1; then
    printf 'Error: fuser is required to check ports 3000 and 8000.\n' >&2
    exit 1
fi

for port in 3000 8000; do
    port_users="$(fuser -n tcp "$port" 2>/dev/null || true)"
    if [[ -n "$port_users" ]]; then
        if [[ "$KILL_PORTS" != true ]]; then
            printf 'Error: TCP port %s is already in use (PID(s):%s).\n' "$port" "$port_users" >&2
            printf 'To stop only the process using port %s and restart:\n' "$port" >&2
            printf '  fuser -k -TERM -n tcp %s\n' "$port" >&2
            printf '  ./run-local.sh\n' >&2
            printf 'Or stop processes on both required ports and restart in one step:\n' >&2
            printf '  ./run-local.sh --kill-ports\n' >&2
            exit 1
        fi

        printf 'Stopping process(es) using TCP port %s (PID(s):%s)...\n' "$port" "$port_users"
        fuser -k -TERM -n tcp "$port" >/dev/null 2>&1 || true
        for attempt in {1..25}; do
            if ! fuser -n tcp "$port" >/dev/null 2>&1; then
                break
            fi
            sleep 0.2
        done
        if fuser -n tcp "$port" >/dev/null 2>&1; then
            printf 'Error: TCP port %s is still in use. Stop its process manually and retry.\n' "$port" >&2
            exit 1
        fi
    fi
done

if ! command -v python3 >/dev/null 2>&1; then
    printf 'Error: python3 is required but was not found in PATH.\n' >&2
    exit 1
fi

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    python3 -m venv "$VENV_DIR"
fi

PYTHON="$VENV_DIR/bin/python"
printf 'Using Python environment: %s\n' "$VENV_DIR"

export DJANGO_DEBUG=1
export DJANGO_SECRET_KEY="$("$PYTHON" -c 'import secrets; print(secrets.token_urlsafe(50))')"

"$PYTHON" -m pip install -r "$BACKEND_DIR/requirements.txt"

if ! command -v npm >/dev/null 2>&1; then
    printf 'Error: npm is required but was not found in PATH.\n' >&2
    exit 1
fi

if [[ ! -x "$FRONTEND_DIR/node_modules/.bin/react-scripts" ]]; then
    npm install --prefix "$FRONTEND_DIR"
fi

"$PYTHON" "$BACKEND_DIR/manage.py" migrate --noinput

cleanup() {
    if [[ -n "${BACKEND_PID:-}" ]]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [[ -n "${FRONTEND_PID:-}" ]]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    wait 2>/dev/null || true
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

(
    cd "$BACKEND_DIR"
    exec "$PYTHON" manage.py runserver "$LOCAL_HOST:8000"
) &
BACKEND_PID=$!

(
    cd "$FRONTEND_DIR"
    exec env REACT_APP_API_BASE_URL="http://$LOCAL_HOST:8000" BROWSER=none HOST="$LOCAL_HOST" PORT=3000 ./node_modules/.bin/react-scripts start
) &
FRONTEND_PID=$!

printf '\nSecureCode is starting for this computer only.\nFrontend: http://%s:3000/\nAPI:      http://%s:8000/api/\nPress Ctrl+C to stop both servers.\n\n' "$LOCAL_HOST" "$LOCAL_HOST"

wait -n "$BACKEND_PID" "$FRONTEND_PID"