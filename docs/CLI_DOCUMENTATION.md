# CLI Guide

The repository-root CLI and `securecode-backend/cli.py` run the full backend's syntax, security-pattern, and code-quality checks. They do not call the API or execute checked code. The separate `securecode-api/cli.py` remains syntax/indentation-only.

Run from the repository root to scan a file or recursively scan a folder:

```bash
python3 cli.py myfile.py
python3 cli.py ./test-project
```

Directories are scanned recursively for Python files. Multiple paths can be passed in one invocation. To scan source from standard input:

```bash
cat myfile.py | python3 cli.py -
```

## Options

```bash
python3 cli.py file1.py file2.py               # Check multiple files
python3 cli.py ./test-project -o report.txt
python3 cli.py ./test-project -o report.json   # JSON inferred from extension
python3 cli.py ./test-project -o report.pdf    # PDF inferred from extension
python3 cli.py ./test-project --format json
python3 cli.py ./test-project --format pdf -o report.pdf
python3 cli.py ./test-project --quiet
python3 cli.py --help
```

Text is the default output format. If `--format` is omitted, JSON and PDF are inferred from an output filename ending in `.json` or `.pdf`; other filenames use text. If PDF is selected without `-o`, the report is written to `securecode-report.pdf` in the current directory. JSON and text are printed to standard output unless `-o` is provided.

Reports combine findings from all scanned files and include file, severity, line, description, code snippet, and recommendation. Exit status is `0` when no findings are found and `1` when any finding or path error is found, so the CLI can be used in CI but currently treats every finding as a failing result. `--quiet` suppresses output only for a clean scan. Run the script directly; this repository does not provide package metadata for installing a global `securecode` command.
