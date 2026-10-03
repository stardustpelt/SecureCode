# Improvement Suggestions

A prioritized backlog of practical improvements for SecureCode. Start with safety and correctness before expanding scanner coverage.

## Priority 0: Safety and data handling

### Keep analysis non-executing — implemented

Both Django APIs and both CLIs now inspect Python source without executing it. The APIs return `No code was executed.` Regression tests should continue to protect this contract.

- If execution is ever required, make it a separate, explicit opt-in and run it in a real isolation boundary with restricted filesystem, network, privileges, CPU, and memory. A subprocess timeout alone is not a sandbox.

**Completion check:** both API test suites verify the no-execution response; retain a side-effect regression test if execution paths are added.

### Validate report filenames and paths — implemented

Report display names are sanitized, report files use random UUID IDs, and resolved report paths are constrained to the reports directory. Reports older than 24 hours are removed when analysis is requested.

**Completion check:** regression tests cover traversal-like names, UUID downloads, and repeated display names.

**Completion check:** tests cover path traversal strings, separators, empty names, unusual Unicode, and repeated or concurrent names; no file is created outside the report directory.

### Limit upload and request resource use

- Set request-body and upload-size limits.
- Handle invalid UTF-8 and malformed multipart/JSON input with clear `400` responses.
- Avoid loading arbitrarily large uploads fully into memory.

**Completion check:** tests cover oversized bodies, invalid encoding, missing code/file, and malformed requests without returning a traceback or `500` for client errors.

## Priority 1: Reliable findings

### Build automated tests for scanner rules

The current Django `tests.py` files are placeholders. Add focused tests for each implemented rule and important non-matching examples.

- Cover severity, line number, finding type, and recommendation.
- Include negative examples to measure false positives.
- Test the API response and generated report behavior separately from the detection functions.

**Completion check:** the test suite runs in CI and covers every documented rule in `ANALYSIS_CAPABILITIES.md`.

### Improve detection beyond line-based patterns

Many checks inspect individual lines with regular expressions. This misses multiline expressions, aliases, formatting variations, and whether a value is actually attacker-controlled.

- Use Python's `ast` module for syntax-aware checks such as calls to dangerous functions and mutable defaults.
- Consider Bandit or another maintained analyzer for standard security rules instead of reimplementing them.
- Clearly separate high-confidence findings from heuristic suggestions.

**Completion check:** regression fixtures cover multiline code and common syntax variations; documented detections match tests and limitations.

### Make rule definitions and severity consistent

- Keep the capability guide synchronized with executable scanner tests.
- Avoid duplicate findings for one issue where checkers overlap.
- Define how syntax errors, quality issues, and security findings affect `has_errors` and response status.

**Completion check:** API response semantics are documented and tested for clean code, one finding, multiple severities, malformed code, and analyzer failure.

## Priority 2: API and project maintenance

### Consolidate the two backends

`securecode-api` and `securecode-backend` duplicate much of the Django API, report generation, and CLI. Duplicated fixes can drift.

- Decide whether the API-only variant is still needed.
- If both are needed, extract shared analysis and API behavior into a common package or maintain explicit parity tests.

**Completion check:** shared behavior has one implementation or automated tests demonstrate intentional differences.

### Configure development and production settings separately

- Keep permissive CORS, wildcard hosts, and debug behavior confined to local development.
- Read secrets and allowed origins from environment variables.
- Document deployment requirements and do not use Django's development server for production.

**Completion check:** production configuration fails closed when required settings are absent; development setup remains one command.

### Pin and audit dependencies

- Add compatible version bounds or lock files for Python and Node dependencies.
- Remove packages that are not actually used, or document their intended use.
- Run dependency vulnerability checks in CI.

**Completion check:** a clean install and build work reproducibly from documented lock/requirements files.

## Priority 3: Usability and release quality

### Improve API and UI error handling

- Return consistent JSON error shapes and appropriate HTTP status codes.
- In the React UI, distinguish network errors, invalid responses, and analysis findings.
- Keep errors inline and provide a retry path without losing the entered code.

**Completion check:** manual or automated UI tests cover API unavailable, validation failure, findings, and successful analysis.

### Make the CLI and web scanner scope clear

The CLI currently checks syntax and indentation only; it does not use the full backend security and quality checks.

- Either add the broader checks to the CLI or label the scope prominently in CLI help and docs.
- Keep examples and exit codes consistent across both backend copies.

**Completion check:** CLI tests and help output match the documented behavior.

### Add CI and release checks

- Run Python tests and Django system checks.
- Run the React production build and lint checks.
- Check documentation links and verify the local launcher syntax.

**Completion check:** pull requests fail when any required check fails, and a clean checkout can follow the documented local setup.
