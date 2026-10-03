# CLI Guide

The repository-root CLI and `securecode-backend/cli.py` run the full backend's syntax, security-pattern, and code-quality checks. They do not call the API or execute checked code. The separate `securecode-api/cli.py` remains syntax/indentation-only.

Run from the repository root to scan a file or recursively scan a folder:

```bash
python3 cli.py myfile.py
python3 cli.py ./test-project
```

## Options

```bash
python3 cli.py file1.py file2.py               # Check multiple files
python3 cli.py ./test-project -o report.txt
python3 cli.py ./test-project -o report.json   # JSON inferred from extension
python3 cli.py ./test-project -o report.pdf    # PDF inferred from extension
python3 cli.py ./test-project --format json
python3 cli.py --help
```

Reports combine findings from all scanned files and include file, severity, line, description, code snippet, and recommendation. Exit status is `0` when no findings are found and `1` when findings or path errors are found. Run the script directly; this repository does not provide package metadata for installing a global `securecode` command.
