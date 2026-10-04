"""Standalone AST and source-pattern analysis for SecureCode."""

import ast
import os
import re
from pathlib import Path

_SECRET_NAME = re.compile(
    r"(?:password|passwd|pwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token|aws_(?:access_key_id|secret_access_key))",
    re.IGNORECASE,
)
_PLACEHOLDERS = {"", "changeme", "change_me", "example", "placeholder", "your_secret"}
_SKIPPED_DIRECTORIES = {".venv", "venv", "env", "node_modules", "__pycache__", ".git"}


def _finding(kind, severity, line, message, code, suggestion):
    return {
        "type": kind,
        "severity": severity,
        "line": line,
        "message": message,
        "code": code,
        "suggestion": suggestion,
    }


def _constant_string(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        values = [_constant_string(value) for value in node.elts]
        if all(value is not None for value in values):
            return " ".join(values)
    return None


def _is_dynamic_string(node):
    return isinstance(node, (ast.BinOp, ast.JoinedStr)) or (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "format"
    )


def _assigned_names(target):
    if isinstance(target, ast.Name):
        yield target.id
    elif isinstance(target, (ast.Tuple, ast.List)):
        for element in target.elts:
            yield from _assigned_names(element)


def _target_code(lines, line_number):
    if 1 <= line_number <= len(lines):
        return lines[line_number - 1].rstrip()
    return ""


def _analyze_tree(tree, lines):
    findings = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = [name for target in node.targets for name in _assigned_names(target)]
            value = _constant_string(node.value)
            if value is not None and any(_SECRET_NAME.search(name) for name in targets):
                if value.strip().lower() not in _PLACEHOLDERS:
                    findings.append(_finding(
                        "Hardcoded Secret", "HIGH", node.lineno,
                        "A credential-like value is assigned directly in source.",
                        _target_code(lines, node.lineno),
                        "Load secrets from an environment variable or a secret manager.",
                    ))

        elif isinstance(node, ast.AnnAssign):
            value = _constant_string(node.value) if node.value is not None else None
            if (isinstance(node.target, ast.Name) and value is not None
                    and _SECRET_NAME.search(node.target.id)
                    and value.strip().lower() not in _PLACEHOLDERS):
                findings.append(_finding(
                    "Hardcoded Secret", "HIGH", node.lineno,
                    "A credential-like value is assigned directly in source.",
                    _target_code(lines, node.lineno),
                    "Load secrets from an environment variable or a secret manager.",
                ))

        elif isinstance(node, ast.Call):
            function = node.func
            name = function.id if isinstance(function, ast.Name) else (
                function.attr if isinstance(function, ast.Attribute) else ""
            )
            qualified = ""
            if isinstance(function, ast.Attribute) and isinstance(function.value, ast.Name):
                qualified = f"{function.value.id}.{function.attr}"

            if name in {"execute", "executemany"} and node.args:
                query = node.args[0]
                if _is_dynamic_string(query):
                    findings.append(_finding(
                        "Possible SQL Injection", "HIGH", node.lineno,
                        "SQL passed to execute() is constructed with interpolation or concatenation.",
                        _target_code(lines, node.lineno),
                        "Use parameterized SQL and pass values separately to execute().",
                    ))

            if qualified in {"os.system", "os.popen"}:
                findings.append(_finding(
                    "Possible Command Injection", "HIGH", node.lineno,
                    f"{qualified}() executes a shell command string.",
                    _target_code(lines, node.lineno),
                    "Prefer subprocess.run() with an argument list and shell=False.",
                ))
            elif name in {"run", "Popen", "call", "check_call", "check_output"}:
                shell_enabled = any(
                    keyword.arg == "shell"
                    and isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is True
                    for keyword in node.keywords
                )
                if shell_enabled:
                    findings.append(_finding(
                        "Possible Command Injection", "HIGH", node.lineno,
                        "A subprocess call enables shell=True.",
                        _target_code(lines, node.lineno),
                        "Pass an argument list with shell=False, especially for untrusted input.",
                    ))

        elif isinstance(node, ast.ExceptHandler) and node.type is None:
            findings.append(_finding(
                "Bare Except", "LOW", node.lineno,
                "A bare except clause catches unexpected exceptions, including system exits.",
                _target_code(lines, node.lineno),
                "Catch a specific exception or use except Exception.",
            ))

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            positional_arguments = node.args.posonlyargs + node.args.args
            first_default = len(positional_arguments) - len(node.args.defaults)
            defaults = list(zip(positional_arguments[first_default:], node.args.defaults))
            defaults.extend(
                (argument, default)
                for argument, default in zip(node.args.kwonlyargs, node.args.kw_defaults)
                if default is not None
            )
            for argument, default in defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    findings.append(_finding(
                        "Mutable Default Argument", "LOW", default.lineno,
                        f"Argument '{argument.arg}' uses a mutable default value.",
                        _target_code(lines, default.lineno),
                        "Use None as the default and create the mutable value inside the function.",
                    ))
            if not ast.get_docstring(node):
                findings.append(_finding(
                    "Missing Docstring", "LOW", node.lineno,
                    f"Function '{node.name}' has no docstring.",
                    _target_code(lines, node.lineno),
                    "Add a short docstring describing the function's purpose and arguments.",
                ))

        elif isinstance(node, ast.ClassDef) and not ast.get_docstring(node):
            findings.append(_finding(
                "Missing Docstring", "LOW", node.lineno,
                f"Class '{node.name}' has no docstring.",
                _target_code(lines, node.lineno),
                "Add a short class docstring describing its purpose.",
            ))

    for line_number, line in enumerate(lines, 1):
        if re.search(r"#\s*(TODO|FIXME|HACK|XXX)\b", line, re.IGNORECASE):
            findings.append(_finding(
                "Unresolved TODO", "LOW", line_number,
                "A TODO/FIXME/HACK comment remains in the source.", line.rstrip(),
                "Resolve the comment or track it in the project issue system.",
            ))
        if len(line.rstrip("\r\n")) > 120:
            findings.append(_finding(
                "Long Line", "LOW", line_number,
                f"Line is {len(line.rstrip())} characters long (limit: 120).",
                line.rstrip()[:120] + "...",
                "Split the line into shorter expressions for readability.",
            ))

    return sorted(findings, key=lambda item: (item["line"], item["type"]))


def analyze_source(source, filename="<string>"):
    """Analyze Python source text and return normalized findings."""
    lines = source.splitlines()
    try:
        tree = ast.parse(source, filename=filename)
    except (SyntaxError, IndentationError) as error:
        line_number = error.lineno or 1
        kind = "Indentation Error" if isinstance(error, IndentationError) else "Syntax Error"
        return [_finding(
            kind, "LOW", line_number, error.msg,
            _target_code(lines, line_number),
            "Fix the reported syntax or indentation error before scanning again.",
        )]
    return _analyze_tree(tree, lines)


def analyze_file(path):
    """Read and analyze one Python file."""
    path = Path(path)
    source = path.read_text(encoding="utf-8", errors="replace")
    findings = analyze_source(source, str(path))
    for finding in findings:
        finding["file"] = str(path)
    return findings


def collect_python_files(paths):
    """Return Python files, skipping common virtualenv and generated directories."""
    files = []
    errors = []
    seen = set()

    for raw_path in paths:
        if str(raw_path) == "-":
            continue
        path = Path(raw_path)
        if not path.exists():
            errors.append(f"Path not found: {path}")
            continue
        if path.is_file():
            if path.suffix.lower() != ".py":
                errors.append(f"Not a Python file or directory: {path}")
                continue
            candidates = [path]
        elif path.is_dir():
            candidates = []
            for current, directories, filenames in os.walk(path):
                directories[:] = sorted(
                    name for name in directories
                    if name not in _SKIPPED_DIRECTORIES
                )
                candidates.extend(
                    Path(current) / name for name in sorted(filenames)
                    if name.lower().endswith(".py")
                )
            if not candidates:
                errors.append(f"No Python files found in: {path}")
        else:
            errors.append(f"Not a Python file or directory: {path}")
            continue

        for candidate in candidates:
            resolved = candidate.resolve()
            if resolved not in seen:
                seen.add(resolved)
                files.append(candidate)

    return files, errors
