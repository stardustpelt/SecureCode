# Security Scanner Guide

The full backend combines indentation/syntax checks with regular-expression security checks and lightweight code-quality heuristics. These checks are indicators, not a complete security audit; expect false positives and missed issues.

Checks cover hardcoded credentials, dynamic code execution, SQL and shell command construction, unsafe HTML/deserialization, path handling, Django security settings, TLS verification, and common code-quality issues. See `../analyzer/security_check.py` and `../analyzer/low_severity_check.py` for the current rules.

Use the full backend with `./run-local.sh` from the repository root. The root CLI and `securecode-backend/cli.py` run syntax, security-pattern, and code-quality checks; the API uses the same checks.

The full backend analyzes submissions without executing them. The separate `securecode-api` backend has different behavior; see the root API reference before using it.
