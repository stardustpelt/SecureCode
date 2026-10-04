# Analysis Capabilities

This page describes the current scanner and its entry points.

## Entry points

| Entry point | Checks | Output | Executes submitted code? |
| --- | --- | --- | --- |
| `backend` API | Syntax/indentation, security patterns, and code-quality heuristics | JSON response, text report, and PDF report | No |
| Root `python3 cli.py PATH` | Full-backend syntax, security-pattern, and code-quality checks | Text by default; JSON or PDF with `--format` or matching output extension | No |
| `backend/cli.py PATH` | Same checks and formats as the root CLI | Text, JSON, or PDF | No |

The API accepts Python source as JSON or as a `.py` file upload and does not execute submitted code. Responses include a status, report text, filename, and generated `report_id`, plus `has_errors`, `error_count`, and `errors` for clean and flagged submissions. A PDF report is generated for each accepted analysis. Reports are stored locally; PDFs older than 24 hours are removed when a later analysis request triggers cleanup.

The analysis endpoint limits source to 200,000 characters, in addition to Django's request-body size limit. The local launcher binds the API to `127.0.0.1`. The API endpoint has no user authentication and is CSRF-exempt, so do not expose it to a shared network or the public internet without adding and reviewing access controls.

The root and backend CLIs accept one or more `.py` files, directories scanned recursively, or `-` for standard input. Findings from selected files are combined into one report. CLI exit status is `1` when findings or path errors exist and `0` when the scan completes without findings. The `--quiet` option suppresses the report only when there are no findings.

Example:

```bash
python3 cli.py ./samples
python3 cli.py ./samples -o findings.json
python3 cli.py ./samples -o findings.pdf
```

## Full scanner checks

The API and CLIs combine AST-based syntax/indentation parsing with the security and quality rules maintained under `backend/analyzer/`.

| Severity | Current security checks |
| --- | --- |
| Critical | Hardcoded password assignments; AWS access/secret credential identifiers; calls to `eval()`, `exec()`, and `compile()` |
| High | Hardcoded Django `SECRET_KEY`, names matching `API_KEY`, and token assignments; SQL formatting/concatenation patterns; `os.system()`, `os.popen()`, and subprocess calls containing `shell=True`; selected XSS patterns (`render_template_string()`, `mark_safe()`, and HTML literals passed to `HttpResponse()`); `pickle` deserialization and `yaml.load()` without a loader; constructed paths passed directly to `open()`; commented-out `@login_required` and selected commented staff/superuser checks; MD5 and SHA-1 calls |
| Medium | `DEBUG = True`; wildcard Django `ALLOWED_HOSTS`; `@csrf_exempt`; `verify=False` |
| Low | TODO/FIXME/HACK/XXX comments; syntax and indentation findings; several code-quality checks listed below |

Code-quality checks include bare `except:`, empty exception handlers, mutable list/dictionary defaults, old Python/deprecated APIs (`print` statement, `urllib.urlopen`, `assertEquals`), apparent unused variables, missing function/class docstrings, lines over 120 characters, semicolon-separated statements, explicit comparisons with `True`/`False`, direct `type()` comparisons, and upload-handling heuristics for missing nearby size/type validation around `request.FILES`.

## Limitations

Most security checks inspect individual lines with regular expressions; quality checks use nearby-text or simple source-text heuristics. They do not perform general data-flow analysis, and can miss variants or report safe code. A syntax error can also limit what AST-based checks can analyze. Treat findings as review prompts, not proof that code is safe.

Examples the current rules do not reliably detect:

- SQL built in one variable and later passed to `cursor.execute(query)`.
- Reflected text concatenated into an `HttpResponse` when the response string has no literal HTML tag.
- `SESSION_COOKIE_SECURE = False` or other cookie flags not listed above.
- Upload validation implemented without a nearby `request.FILES` reference.
- An unescaped template interpolation such as `{{ username }}` by itself.

The API and CLI use the full scanner.
