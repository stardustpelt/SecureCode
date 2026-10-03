import re
import ast

def check_security_vulnerabilities(file_path):
    """Check Python file for security vulnerabilities."""
    vulnerabilities = []
    
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            content = ''.join(lines)
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # ========== CRITICAL SEVERITY ==========
            
            # Check for hardcoded passwords
            if re.search(r'(PASSWORD|password|pwd)\s*=\s*["\'][^"\']+["\']', line_stripped):
                vulnerabilities.append({
                    'type': 'Hardcoded Password',
                    'severity': 'CRITICAL',
                    'line': line_num,
                    'message': 'Password is hardcoded in source code',
                    'code': line.rstrip(),
                    'suggestion': 'Use environment variables or secure credential management'
                })
            
            # Check for eval() usage
            if re.search(r'\beval\s*\(', line_stripped):
                vulnerabilities.append({
                    'type': 'Code Injection - eval()',
                    'severity': 'CRITICAL',
                    'line': line_num,
                    'message': 'Use of eval() can execute arbitrary code',
                    'code': line.rstrip(),
                    'suggestion': 'Avoid eval(). Use ast.literal_eval() for safe evaluation or refactor code'
                })
            
            # Check for exec() usage
            if re.search(r'\bexec\s*\(', line_stripped):
                vulnerabilities.append({
                    'type': 'Code Injection - exec()',
                    'severity': 'CRITICAL',
                    'line': line_num,
                    'message': 'Use of exec() can execute arbitrary code',
                    'code': line.rstrip(),
                    'suggestion': 'Avoid exec(). Refactor to use safer alternatives'
                })
            
            # Check for compile() with user input
            if re.search(r'\bcompile\s*\(', line_stripped):
                vulnerabilities.append({
                    'type': 'Code Injection - compile()',
                    'severity': 'CRITICAL',
                    'line': line_num,
                    'message': 'Use of compile() can execute arbitrary code',
                    'code': line.rstrip(),
                    'suggestion': 'Avoid compile() with untrusted input'
                })
            
            # ========== HIGH SEVERITY ==========
            
            # Check for hardcoded SECRET_KEY
            if re.search(r'SECRET_KEY\s*=\s*["\']', line_stripped):
                vulnerabilities.append({
                    'type': 'Hardcoded Secret Key',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'Django SECRET_KEY is hardcoded in source code',
                    'code': line.rstrip(),
                    'suggestion': 'Use environment variables: SECRET_KEY = os.environ.get("SECRET_KEY")'
                })
            
            # Check for API keys
            if re.search(r'API_KEY\s*=\s*["\']', line_stripped):
                vulnerabilities.append({
                    'type': 'Hardcoded API Key',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'API key is hardcoded in source code',
                    'code': line.rstrip(),
                    'suggestion': 'Use environment variables: API_KEY = os.environ.get("API_KEY")'
                })
            
            # Check for AWS keys
            if re.search(r'(AWS_ACCESS_KEY|AWS_SECRET)', line_stripped):
                vulnerabilities.append({
                    'type': 'AWS Credentials',
                    'severity': 'CRITICAL',
                    'line': line_num,
                    'message': 'AWS credentials detected in source code',
                    'code': line.rstrip(),
                    'suggestion': 'Use AWS IAM roles or environment variables'
                })
            
            # Check for tokens
            if re.search(r'(TOKEN|token|auth_token)\s*=\s*["\'][^"\']+["\']', line_stripped):
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
            
            # Command Injection - os.system
            if re.search(r'os\.system\s*\(', line_stripped):
                vulnerabilities.append({
                    'type': 'Command Injection - os.system()',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'os.system() with user input can lead to command injection',
                    'code': line.rstrip(),
                    'suggestion': 'Use subprocess with shell=False and pass command as list'
                })
            
            # Command Injection - shell=True in subprocess
            if re.search(r'subprocess\.[^(]*\([^)]*shell\s*=\s*True', line_stripped):
                vulnerabilities.append({
                    'type': 'Command Injection - shell=True',
                    'severity': 'HIGH',
                    'line': line_num,
                    'message': 'Using shell=True can lead to command injection',
                    'code': line.rstrip(),
                    'suggestion': 'Use shell=False and pass command as list: subprocess.run(["cmd", arg1, arg2])'
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
