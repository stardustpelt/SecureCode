#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if (( $# > 1 )); then
    printf 'Usage: %s [file-or-directory]\n' "$0" >&2
    exit 2
fi

target="${1:-}"
if [[ -z "$target" ]]; then
    read -r -p 'Path to scan [samples]: ' target
    target="${target:-samples}"
fi

if [[ ! -e "$target" ]]; then
    printf 'Error: path does not exist: %s\n' "$target" >&2
    exit 2
fi

if [[ "$target" != /* ]]; then
    target="$PWD/$target"
fi

printf 'Choose report format:\n'
printf '  1) Text Report (printed directly to the terminal)\n'
printf '  2) JSON Report (saved to file)\n'
printf '  3) PDF Report (saved to file)\n'
read -r -p 'Enter choice [1-3]: ' choice

case "$choice" in
    1)
        python3 "$SCRIPT_DIR/cli.py" "$target"
        exit_code=$?
        ;;
    2|3)
        mkdir -p -- "$SCRIPT_DIR/reports" || {
            printf 'Error: could not create reports directory.\n' >&2
            exit 1
        }
        timestamp="$(date '+%Y%m%d_%H%M%S')"
        if [[ "$choice" == 2 ]]; then
            format='json'
            extension='json'
        else
            format='pdf'
            extension='pdf'
        fi
        output="$SCRIPT_DIR/reports/report_${timestamp}.${extension}"
        python3 "$SCRIPT_DIR/cli.py" "$target" --format "$format" -o "$output"
        exit_code=$?
        ;;
    *)
        printf 'Error: choose 1, 2, or 3.\n' >&2
        exit 2
        ;;
esac

if (( exit_code != 0 )); then
    printf 'Scan finished with exit status %d.\n' "$exit_code" >&2
fi
exit "$exit_code"