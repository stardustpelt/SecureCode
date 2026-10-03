import re
import ast

_DANGEROUS_BUILTINS = {
    'eval': ('Code Injection - eval()', 'Use of eval() can execute arbitrary code',
             'Avoid eval(). Use ast.literal_eval() for safe evaluation or refactor code'),
    'exec': ('Code Injection - exec()', 'Use of exec() can execute arbitrary code',
             'Avoid exec(). Refactor to use safer alternatives'),
    'compile': ('Code Injection - compile()', 'Use of compile() can execute executable code',
                'Avoid compile() with untrusted input'),
}
_SUBPROCESS_CALLS = {'Popen', 'call', 'check_call', 'check_output', 'run'}


def _is_placeholder_secret(value):
    value = value.strip()
    lowered = value.lower()
    return not value or lowered == 'changeme' or (value.startswith('<') and value.endswith('>'))


def _has_hardcoded_secret(line, variable_pattern):
    match = re.search(
        rf'\b(?:{variable_pattern})\s*=\s*(["\'])(.*?)\1',
        line,
        re.IGNORECASE,
    )
    return bool(match and not _is_placeholder_secret(match.group(2)))


def _find_dangerous_calls(source, lines):
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    os_modules = set()
    subprocess_modules = set()
    builtin_modules = set()
    builtin_aliases = {}
    os_function_aliases = set()
    subprocess_function_aliases = set()
    shadowed_builtins = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_name = alias.name.split('.')[0]
                bound_name = alias.asname or root_name
                if root_name == 'os':
                    os_modules.add(bound_name)
                elif root_name == 'subprocess':
                    subprocess_modules.add(bound_name)
                elif root_name == 'builtins':
                    builtin_modules.add(bound_name)
                if bound_name in _DANGEROUS_BUILTINS:
                    shadowed_builtins.add(bound_name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                bound_name = alias.asname or alias.name
                if node.module == 'builtins' and alias.name in _DANGEROUS_BUILTINS:
                    builtin_aliases[bound_name] = alias.name
                elif node.module == 'os' and alias.name == 'system':
                    os_function_aliases.add(bound_name)
                elif node.module == 'subprocess' and alias.name in _SUBPROCESS_CALLS:
                    subprocess_function_aliases.add(bound_name)
                elif alias.name in _DANGEROUS_BUILTINS:
                    shadowed_builtins.add(bound_name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id in _DANGEROUS_BUILTINS:
                shadowed_builtins.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name in _DANGEROUS_BUILTINS:
                shadowed_builtins.add(node.name)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                arguments = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
                if node.args.vararg:
                    arguments.append(node.args.vararg)
                if node.args.kwarg:
                    arguments.append(node.args.kwarg)
                shadowed_builtins.update(
                    argument.arg for argument in arguments
                    if argument.arg in _DANGEROUS_BUILTINS
                )

    findings = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        finding_type = None
        function = node.func
        if isinstance(function, ast.Name):
            if function.id in builtin_aliases:
                finding_type = _DANGEROUS_BUILTINS[builtin_aliases[function.id]][0]
            elif function.id in os_function_aliases:
                finding_type = 'Command Injection - os.system()'
            elif function.id in subprocess_function_aliases and _uses_shell_true(node):
                finding_type = 'Command Injection - shell=True'
            elif function.id in _DANGEROUS_BUILTINS and function.id not in shadowed_builtins:
                finding_type = _DANGEROUS_BUILTINS[function.id][0]
        elif isinstance(function, ast.Attribute) and isinstance(function.value, ast.Name):
            module_name = function.value.id
            if module_name in builtin_modules and function.attr in _DANGEROUS_BUILTINS:
                finding_type = _DANGEROUS_BUILTINS[function.attr][0]
            elif module_name in os_modules and function.attr == 'system':
                finding_type = 'Command Injection - os.system()'
            elif (module_name in subprocess_modules and function.attr in _SUBPROCESS_CALLS
                  and _uses_shell_true(node)):
                finding_type = 'Command Injection - shell=True'

        if finding_type is None:
            continue

        if finding_type.startswith('Code Injection - '):
            detail = next(value for value in _DANGEROUS_BUILTINS.values() if value[0] == finding_type)
            severity = 'CRITICAL'
            message, suggestion = detail[1], detail[2]
        elif finding_type == 'Command Injection - os.system()':
            severity = 'HIGH'
            message = 'os.system() with user input can lead to command injection'
            suggestion = 'Use subprocess with shell=False and pass command as list'
        else:
            severity = 'HIGH'
            message = 'Using shell=True can lead to command injection'
            suggestion = 'Use shell=False and pass command as list: subprocess.run(["cmd", arg1, arg2])'

        line_num = node.lineno
        findings.append({
            'type': finding_type,
            'severity': severity,
            'line': line_num,
            'message': message,
            'code': lines[line_num - 1].rstrip() if 0 < line_num <= len(lines) else '',
            'suggestion': suggestion,
        })

    return findings


def _uses_shell_true(call):
    return any(
        keyword.arg == 'shell'
        and isinstance(keyword.value, ast.Constant)
        and keyword.value.value is True
        for keyword in call.keywords
    )


def check_security_vulnerabilities(file_path):
    """Check Python file for security vulnerabilities."""
    vulnerabilities = []
    
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            content = ''.join(lines)

        vulnerabilities.extend(_find_dangerous_calls(content, lines))
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # ========== CRITICAL SEVERITY ==========
            
            # Check for hardcoded passwords
            if _has_hardcoded_secret(line_stripped, r'[A-Z0-9_]*(?:PASSWORD|PWD)'):
                vulnerabilities.append({
                    'type': 'Hardcoded Password',
                    'severity': 'CRITICAL',
                    'line': line_num,
                    'message': 'Password is hardcoded in source code',
                    'code': line.rstrip(),
                    'suggestion': 'Use environment variables or secure credential management'
                })
            
            # ========== HIGH SEVERITY ==========
            
            # Check for hardcoded SECRET_KEY
            if _has_hardcoded_secret(line_stripped, r'[A-Z0-9_]*SECRET_KEY'):
                vulnerabilities.append({
                    'type': 'Hardcoded Secret Key',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'Django SECRET_KEY is hardcoded in source code',
                    'code': line.rstrip(),
                    'suggestion': 'Use environment variables: SECRET_KEY = os.environ.get("SECRET_KEY")'
                })
            
            # Check for API keys
            if _has_hardcoded_secret(line_stripped, r'[A-Z0-9_]*API_KEY'):
                vulnerabilities.append({
                    'type': 'Hardcoded API Key',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'API key is hardcoded in source code',
                    'code': line.rstrip(),
                    'suggestion': 'Use environment variables: API_KEY = os.environ.get("API_KEY")'
                })
            
            # Check for AWS keys
            if _has_hardcoded_secret(
                    line_stripped, r'AWS_(?:ACCESS_KEY(?:_ID)?|SECRET(?:_ACCESS_KEY)?)'):
                vulnerabilities.append({
                    'type': 'AWS Credentials',
                    'severity': 'CRITICAL',
                    'line': line_num,
                    'message': 'AWS credentials detected in source code',
                    'code': line.rstrip(),
                    'suggestion': 'Use AWS IAM roles or environment variables'
                })
            
            # Check for tokens
            if _has_hardcoded_secret(line_stripped, r'[A-Z0-9_]*TOKEN'):
                vulnerabilities.append({
                    'type': 'Hardcoded Token',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'Authentication token is hardcoded',
                    'code': line.rstrip(),
                    'suggestion': 'Use environment variables or secure token storage'
                })
            
            # SQL Injection - raw SQL with string formatting
            if re.search(r'execute\s*\([^)]*[%+]', line_stripped) or re.search(r'execute\s*\([^)]*\.format', line_stripped):
                vulnerabilities.append({
                    'type': 'SQL Injection',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'SQL query uses string formatting/concatenation - vulnerable to SQL injection',
                    'code': line.rstrip(),
                    'suggestion': 'Use parameterized queries: cursor.execute("SELECT * FROM table WHERE id = ?", (user_id,))'
                })
            
            # SQL Injection - raw SQL concatenation
            if re.search(r'(SELECT|INSERT|UPDATE|DELETE).*[+%].*FROM', line_stripped, re.IGNORECASE):
                vulnerabilities.append({
                    'type': 'SQL Injection',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'SQL query built with string concatenation - vulnerable to SQL injection',
                    'code': line.rstrip(),
                    'suggestion': 'Use ORM or parameterized queries instead of string concatenation'
                })
            
            # Command Injection - os.popen
            if re.search(r'os\.popen\s*\(', line_stripped):
                vulnerabilities.append({
                    'type': 'Command Injection - os.popen()',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'os.popen() is deprecated and vulnerable to command injection',
                    'code': line.rstrip(),
                    'suggestion': 'Use subprocess.run() with shell=False'
                })
            
            # XSS - render_template_string with user input
            if re.search(r'render_template_string\s*\(', line_stripped):
                vulnerabilities.append({
                    'type': 'Cross-Site Scripting (XSS)',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'render_template_string with user input can lead to XSS',
                    'code': line.rstrip(),
                    'suggestion': 'Use render_template() with proper escaping or sanitize user input'
                })
            
            # XSS - mark_safe with user input
            if re.search(r'mark_safe\s*\(', line_stripped):
                vulnerabilities.append({
                    'type': 'Cross-Site Scripting (XSS)',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'mark_safe() bypasses XSS protection - dangerous with user input',
                    'code': line.rstrip(),
                    'suggestion': 'Avoid mark_safe() with user-provided content. Use proper escaping'
                })
            
            # XSS - HttpResponse with HTML and user input
            if re.search(r'HttpResponse\s*\([^)]*<[^>]*>', line_stripped):
                vulnerabilities.append({
                    'type': 'Cross-Site Scripting (XSS)',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'HttpResponse with HTML content may be vulnerable to XSS',
                    'code': line.rstrip(),
                    'suggestion': 'Use Django templates with auto-escaping or escape user input'
                })
            
            # Insecure Deserialization - pickle
            if re.search(r'pickle\.loads?\s*\(', line_stripped):
                vulnerabilities.append({
                    'type': 'Insecure Deserialization',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'Pickle can execute arbitrary code during deserialization',
                    'code': line.rstrip(),
                    'suggestion': 'Use JSON or other safe serialization formats'
                })
            
            # Insecure Deserialization - yaml.load
            if re.search(r'yaml\.load\s*\([^)]*\)', line_stripped) and 'Loader' not in line_stripped:
                vulnerabilities.append({
                    'type': 'Insecure Deserialization',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'yaml.load() without SafeLoader can execute arbitrary code',
                    'code': line.rstrip(),
                    'suggestion': 'Use yaml.safe_load() instead of yaml.load()'
                })
            
            # Path Traversal
            if re.search(r'open\s*\([^)]*\+[^)]*\)', line_stripped) or re.search(r'open\s*\([^)]*%[^)]*\)', line_stripped):
                vulnerabilities.append({
                    'type': 'Path Traversal',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'File path constructed with user input - vulnerable to path traversal',
                    'code': line.rstrip(),
                    'suggestion': 'Validate and sanitize file paths. Use os.path.basename() and check against whitelist'
                })
            
            # Authentication Bypass - @login_required commented out
            if re.search(r'#\s*@login_required', line_stripped):
                vulnerabilities.append({
                    'type': 'Authentication Bypass',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'Authentication decorator is commented out',
                    'code': line.rstrip(),
                    'suggestion': 'Uncomment @login_required or implement proper authentication'
                })
            
            # Authorization Bypass - is_superuser check commented
            if re.search(r'#.*is_superuser|#.*is_staff', line_stripped):
                vulnerabilities.append({
                    'type': 'Authorization Bypass',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'Authorization check is commented out',
                    'code': line.rstrip(),
                    'suggestion': 'Uncomment authorization checks or implement proper access control'
                })
            
            # Weak Cryptography - MD5
            if re.search(r'hashlib\.md5\s*\(', line_stripped):
                vulnerabilities.append({
                    'type': 'Weak Cryptography',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'MD5 is cryptographically broken and should not be used',
                    'code': line.rstrip(),
                    'suggestion': 'Use SHA-256 or bcrypt for password hashing'
                })
            
            # Weak Cryptography - SHA1
            if re.search(r'hashlib\.sha1\s*\(', line_stripped):
                vulnerabilities.append({
                    'type': 'Weak Cryptography',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'SHA1 is cryptographically weak and should not be used',
                    'code': line.rstrip(),
                    'suggestion': 'Use SHA-256 or bcrypt for password hashing'
                })
            
            # ========== MEDIUM SEVERITY ==========
            
            # Check for DEBUG = True
            if re.search(r'DEBUG\s*=\s*True', line_stripped):
                vulnerabilities.append({
                    'type': 'Debug Mode Enabled',
                    'severity': 'MEDIUM',
                    'line': line_num,
                    'message': 'DEBUG mode is enabled, should be False in production',
                    'code': line.rstrip(),
                    'suggestion': 'Set DEBUG = False in production or use DEBUG = os.environ.get("DEBUG", "False") == "True"'
                })
            
            # Check for ALLOWED_HOSTS = ["*"]
            if re.search(r'ALLOWED_HOSTS\s*=\s*\[\s*["\*\']+\s*\]', line_stripped):
                vulnerabilities.append({
                    'type': 'Wildcard ALLOWED_HOSTS',
                    'severity': 'MEDIUM',
                    'line': line_num,
                    'message': 'ALLOWED_HOSTS accepts all hosts, vulnerable to Host header attacks',
                    'code': line.rstrip(),
                    'suggestion': 'Specify exact allowed hosts: ALLOWED_HOSTS = ["yourdomain.com"]'
                })
            
            # CSRF exempt
            if re.search(r'@csrf_exempt', line_stripped):
                vulnerabilities.append({
                    'type': 'CSRF Protection Disabled',
                    'severity': 'MEDIUM',
                    'line': line_num,
                    'message': 'CSRF protection is disabled for this view',
                    'code': line.rstrip(),
                    'suggestion': 'Remove @csrf_exempt and implement proper CSRF protection'
                })
            
            # Insecure SSL/TLS
            if re.search(r'verify\s*=\s*False', line_stripped):
                vulnerabilities.append({
                    'type': 'Insecure SSL/TLS',
                    'severity': 'MEDIUM',
                    'line': line_num,
                    'message': 'SSL certificate verification is disabled',
                    'code': line.rstrip(),
                    'suggestion': 'Enable SSL verification: verify=True'
                })
            
            # ========== LOW SEVERITY ==========
            
            # Check for TODO/FIXME comments
            if re.search(r'#\s*(TODO|FIXME|HACK|XXX)', line_stripped, re.IGNORECASE):
                vulnerabilities.append({
                    'type': 'Code Quality Issue',
                    'severity': 'LOW',
                    'line': line_num,
                    'message': 'Unresolved TODO/FIXME comment found',
                    'code': line.rstrip(),
                    'suggestion': 'Address pending issues before production deployment'
                })
    
    except Exception as e:
        vulnerabilities.append({
            'type': 'Error',
            'severity': 'LOW',
            'line': 0,
            'message': f'Error scanning file: {str(e)}',
            'code': '',
            'suggestion': 'Check file permissions and format'
        })
    
    return vulnerabilities if vulnerabilities else None
