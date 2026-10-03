# SecureCode Philosophy Alignment Audit

**Audit snapshot:** `main` at `56a7316` (`feat(dev): add occupied-port recovery option`), reviewed 2026-10-03. This is a source/documentation audit, not a penetration test or dependency-license review.

## Executive Summary

SecureCode is aligned with its strongest safety promise in the checked runtime paths: the APIs and CLIs statically inspect source and do not execute submitted code. The normal launcher binds the React UI and full API to loopback, and no analyzer code was found sending submitted source to an external analysis service.

The broader philosophy is only **partially aligned**. Local-only behavior is a launcher default rather than a backend-enforced boundary; both Django settings allow all hosts and CORS origins. The UI makes external requests for fonts and a CLI download, though the requests found do not transmit analyzed source. The scanners are readable, but there is no tracked project license, so the UI's open-source/free-use promise is not legally established. Some documentation still incorrectly says the API-only backend executes submitted code.

## 1. Code Execution Safety

**✅ PASS for the current analyzer and CLI paths**

Both API handlers write submitted source to a temporary `.py` file, call syntax/indentation, security, and quality checkers, build a report, then remove the temporary file. The API-only view returns “No code was executed” ([securecode-api view](../securecode-api/code_analyzer/views.py#L224), [checker and response path](../securecode-api/code_analyzer/views.py#L229)). The full-backend view similarly runs all three checkers and substitutes a no-execution message on clean submissions ([securecode-backend view](../securecode-backend/code_analyzer/views.py#L250), [no-execution response](../securecode-backend/code_analyzer/views.py#L285)). The root/full-backend CLI invokes those same analysis functions ([CLI scan function](../securecode-backend/cli.py#L44)). No actual `subprocess.run`, `Popen`, `os.system`, `eval`, or user-source `exec` call was found in these request handlers or CLI scan paths.

The scanner contains strings and regular expressions that *detect* `eval()`, `exec()`, and `compile()` in submitted source ([security rules](../securecode-backend/analyzer/security_check.py#L29)); these are detection rules, not calls that execute the submitted file.

## 2. Local-First Architecture

**⚠️ PARTIAL**

The documented launcher binds the React dev server and full Django API to `127.0.0.1` ([run-local host](../run-local.sh#L8), [server binds](../run-local.sh#L105)). Both browser clients send analysis requests to `127.0.0.1:8000` ([React API base](../securecode-ui/src/App.js#L13), [static API base](../securecode-backend/frontend/index.html#L339)). The API stores temporary source and PDF reports locally; no external analysis API or source-upload destination was found in the application code.

However, the React CSS requests fonts from Google Fonts ([stylesheet import](../securecode-ui/src/index.css#L1)), and the React Docs page fetches the downloadable CLI from GitHub when clicked ([CLI download URL](../securecode-ui/src/Documentation.js#L80)). These requests do not appear to include submitted code, but the UI is not fully offline or free of third-party network requests.

Loopback is not enforced by Django settings. Both backends set `ALLOWED_HOSTS = ['*']`, `DEBUG = True`, and `CORS_ALLOW_ALL_ORIGINS = True` ([full-backend settings](../securecode-backend/securecode_web/settings.py#L26), [allowed hosts](../securecode-backend/securecode_web/settings.py#L28), [CORS](../securecode-backend/securecode_web/settings.py#L123); same defaults exist in [API-only settings](../securecode-api/securecode_web/settings.py#L26)). The quick start explicitly documents binding to `0.0.0.0` for LAN access ([Quick Start](QUICKSTART.md#L24)). If started that way, the service is no longer local-machine-only; the APIs also have CSRF-exempt analysis handlers and no authentication ([full-backend view](../securecode-backend/code_analyzer/views.py#L207)).

## 3. Educational Clarity

**⚠️ PARTIAL**

The UI explains the local-first/no-execution intent and intended audience ([About philosophy](../securecode-ui/src/About.js#L55), [principles](../securecode-ui/src/About.js#L61)). Scanner rules provide descriptions and recommendations, for example hardcoded-secret guidance ([security checker](../securecode-backend/analyzer/security_check.py#L65)) and syntax recommendations ([quality checker](../securecode-backend/analyzer/low_severity_check.py#L19)). The API response includes findings and a text report ([API response](../securecode-api/code_analyzer/views.py#L245)). The React UI shows severity, line, type, and message for up to eight findings, and also displays the full report ([issue summary](../securecode-ui/src/App.js#L350), [full report](../securecode-ui/src/App.js#L378)).

Some user-facing guidance is stale: the API-only README and project summary still claim that API-only requests execute source ([API-only README](../securecode-api/README.md#L21), [project summary](PROJECT_SUMMARY.md#L13)), although the current view no longer executes it. This contradiction weakens the safety message and can confuse users.

## 4. Transparency

**⚠️ PARTIAL**

The scanner is ordinary, readable Python using AST parsing and explicit regular-expression/text rules ([security checker](../securecode-backend/analyzer/security_check.py#L1), [quality checker](../securecode-backend/analyzer/low_severity_check.py#L1)). No ML model, SaaS scanner endpoint, telemetry SDK, or obfuscated analyzer was found. The direct Python and React dependencies are named in their manifest files ([Python dependencies](../securecode-backend/requirements.txt#L1), [React dependencies](../securecode-ui/package.json#L5)).

No project `LICENSE` or `COPYING` file is tracked. Public source visibility alone does not grant reuse rights, so “open-source” and “free for all” cannot be verified as licensing claims until a license is added. Also, the UI comparison with “typical enterprise tools” is broad and unsourced ([comparison table](../securecode-ui/src/About.js#L74)); keep it clearly framed as a general contrast, not a product-by-product factual assessment.

## 5. Accessibility and Free Access

**⚠️ PARTIAL**

No login, subscription, payment, or premium feature gate was found in the web UI or API paths reviewed. The React package is marked private for package publishing ([package manifest](../securecode-ui/package.json#L2)); that is not itself a paid feature gate. Beginner-facing quick starts and CLI examples exist.

The missing project license means the legal terms for free use, modification, and redistribution are unclear. In addition, stale execution guidance and scanner limitations can mislead beginners. The report should not promise unrestricted free/open-source use until licensing is explicit.

## Issues Found

| Issue | Severity | File | Description |
|---|---|---|---|
| Permissive development settings and embedded secret | High | [securecode-backend settings](../securecode-backend/securecode_web/settings.py#L23) | A development secret is committed, `DEBUG` is enabled, all hosts are accepted, and CORS is open to all origins. These are unsafe if the API is exposed beyond a trusted local environment. The API-only settings have the same defaults. |
| User-controlled report path | High | [securecode-api view](../securecode-api/code_analyzer/views.py#L219) | The request `filename` is interpolated directly into `reports/{filename}.pdf` ([write path](../securecode-api/code_analyzer/views.py#L241)); the report-download route also uses the supplied filename to build a path ([download path](../securecode-api/code_analyzer/views.py#L272)). Validate or replace it with a server-generated identifier and constrain resolved paths to the reports directory. The full backend has the same pattern. |
| Local-only is not enforced by settings | High | [run-local.sh](../run-local.sh#L105) | The standard launcher binds to loopback, but Django accepts all hosts and CORS origins; alternate/manual binds can expose the unauthenticated, CSRF-exempt analyzer to a network. |
| Project license absent | Medium | [repository license inventory](../README.md) | No tracked `LICENSE`/`COPYING` file was found. The project cannot clearly establish reuse or redistribution permissions despite “open-source” and “free” UI claims. |
| Third-party browser requests | Medium | [React CSS](../securecode-ui/src/index.css#L1), [React Docs](../securecode-ui/src/Documentation.js#L80) | Google Fonts is loaded remotely, and the CLI download is fetched from GitHub. No submitted source was observed in those requests, but these dependencies prevent a strict offline/no-third-party-request claim. |
| Execution documentation is stale | Medium | [API-only README](../securecode-api/README.md#L21), [project summary](PROJECT_SUMMARY.md#L13) | Both still say the API-only backend executes accepted submissions, but the current API view reports that no code was executed. |
| Automated tests are placeholders | Medium | [API-only tests](../securecode-api/code_analyzer/tests.py#L1), [full-backend tests](../securecode-backend/code_analyzer/tests.py#L1) | Both Django test modules contain only the generated placeholder. The no-execution guarantee and scanner rules are not protected by automated tests. |

## Recommendations

1. Move Django secrets into environment variables; default to `DEBUG = False`, explicit allowed hosts, and restricted CORS outside local development.
2. Sanitize report filenames or generate opaque server-side IDs; resolve and verify report paths stay inside the reports directory.
3. Keep local loopback as the default and make network exposure an explicit, guarded configuration; add authentication or other access controls before LAN use.
4. Add a project `LICENSE` and align “free/open-source” claims with the chosen license.
5. Bundle fonts locally or document the Google Fonts request; host the downloadable CLI locally if offline operation is a goal.
6. Correct API-only execution statements in its README and the project summary.
7. Add tests that submit source with filesystem side effects and assert neither API nor CLI runs it; add regression tests for checker findings and false-positive examples.
8. Keep scanner coverage described as heuristic. The UI already signals limited coverage, but findings should remain review suggestions rather than assurance that code is secure.

## Overall Alignment Score

**1/5 principles fully aligned.** Code-execution safety is aligned in current analyzers/CLIs. Local-first is the default workflow but is not fully enforced by backend settings and includes external UI requests; education is undermined by stale docs; transparency and free-use rights are incomplete without an explicit license.

**Readiness:** Suitable as a local educational/final-year project demo when run with `./run-local.sh`. Not production-ready as configured: permissive development settings, report-path handling, missing license, and lack of automated tests need attention first.
