import re
import ast

def check_low_severity_issues(file_path):
    """Check Python file for low-severity vulnerabilities and code quality issues."""
    issues = []
    
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            content = ''.join(lines)
        
        # Try to parse the file for syntax errors
        try:
            ast.parse(content)
        except SyntaxError as e:
            issues.append({
                'type': 'Syntax Error',
                'severity': 'LOW',
                'cvss': '3.1',
                'line': e.lineno or 1,
                'message': f'Syntax error: {e.msg}',
                'code': lines[e.lineno - 1].rstrip() if e.lineno and e.lineno <= len(lines) else '',
                'suggestion': 'Fix syntax error before deployment'
            })
        except IndentationError as e:
            issues.append({
                'type': 'Indentation Error',
                'severity': 'LOW',
                'cvss': '2.5',
                'line': e.lineno or 1,
                'message': f'Indentation error: {e.msg}',
                'code': lines[e.lineno - 1].rstrip() if e.lineno and e.lineno <= len(lines) else '',
                'suggestion': 'Ensure consistent indentation (use 4 spaces)'
            })
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Unused imports
            if re.search(r'^import\s+\w+', line_stripped) or re.search(r'^from\s+\w+\s+import', line_stripped):
                # This is a simple heuristic - in real scenario would need full AST analysis
                if 'import' in line_stripped and not any(c in content for c in ['#', '"""', "'''"]):
                    pass  # Would need more sophisticated analysis
            
            # Insecure file upload - missing validation
            if re.search(r'request\.FILES', line_stripped):
                # Check if there's size validation nearby
                context_start = max(0, line_num - 5)
                context_end = min(len(lines), line_num + 5)
                context = ''.join(lines[context_start:context_end])
                
                has_size_check = re.search(r'\.size|MAX_UPLOAD_SIZE|file.*size', context, re.IGNORECASE)
                has_type_check = re.search(r'content_type|MIME|\.name.*endswith|allowed.*extension', context, re.IGNORECASE)
                
                if not has_size_check:
                    issues.append({
                        'type': 'Insecure File Upload - Missing Size Validation',
                        'severity': 'LOW',
                        'cvss': '3.5',
                        'line': line_num,
                        'message': 'File upload without size validation can lead to DoS',
                        'code': line.rstrip(),
                        'suggestion': 'Add file size validation: if file.size > MAX_SIZE: raise ValidationError'
                    })
                
                if not has_type_check:
                    issues.append({
                        'type': 'Insecure File Upload - Missing Type Validation',
                        'severity': 'LOW',
                        'cvss': '3.2',
                        'line': line_num,
                        'message': 'File upload without type validation can accept malicious files',
                        'code': line.rstrip(),
                        'suggestion': 'Add file type validation: if not file.name.endswith(allowed_extensions): raise ValidationError'
                    })
            
            # Deprecated API usage - Python 2 style
            if re.search(r'\bprint\s+[^(]', line_stripped):
                issues.append({
                    'type': 'Deprecated API Usage',
                    'severity': 'LOW',
                    'cvss': '2.0',
                    'line': line_num,
                    'message': 'Python 2 style print statement (deprecated)',
                    'code': line.rstrip(),
                    'suggestion': 'Use Python 3 print function: print(...)'
                })
            
            # Deprecated - urllib.urlopen
            if re.search(r'urllib\.urlopen', line_stripped):
                issues.append({
                    'type': 'Deprecated API Usage',
                    'severity': 'LOW',
                    'cvss': '2.5',
                    'line': line_num,
                    'message': 'urllib.urlopen is deprecated in Python 3',
                    'code': line.rstrip(),
                    'suggestion': 'Use urllib.request.urlopen or requests library'
                })
            
            # Deprecated - assertEquals
            if re.search(r'\.assertEquals\s*\(', line_stripped):
                issues.append({
                    'type': 'Deprecated API Usage',
                    'severity': 'LOW',
                    'cvss': '2.0',
                    'line': line_num,
                    'message': 'assertEquals is deprecated, use assertEqual',
                    'code': line.rstrip(),
                    'suggestion': 'Replace assertEquals with assertEqual'
                })
            
            # Bare except clause
            if re.search(r'except\s*:', line_stripped):
                issues.append({
                    'type': 'Code Quality Issue - Bare Except',
                    'severity': 'LOW',
                    'cvss': '2.8',
                    'line': line_num,
                    'message': 'Bare except clause catches all exceptions including system exits',
                    'code': line.rstrip(),
                    'suggestion': 'Specify exception type: except Exception: or except SpecificError:'
                })
            
            # Mutable default argument
            if re.search(r'def\s+\w+\s*\([^)]*=\s*\[', line_stripped) or re.search(r'def\s+\w+\s*\([^)]*=\s*\{', line_stripped):
                issues.append({
                    'type': 'Code Quality Issue - Mutable Default Argument',
                    'severity': 'LOW',
                    'cvss': '3.0',
                    'line': line_num,
                    'message': 'Mutable default argument can cause unexpected behavior',
                    'code': line.rstrip(),
                    'suggestion': 'Use None as default and initialize inside function'
                })
            
            # TODO/FIXME/HACK comments
            if re.search(r'#\s*(TODO|FIXME|HACK|XXX|BUG)', line_stripped, re.IGNORECASE):
                issues.append({
                    'type': 'Code Quality Issue - Unresolved Comment',
                    'severity': 'LOW',
                    'cvss': '2.0',
                    'line': line_num,
                    'message': 'Unresolved TODO/FIXME/HACK comment',
                    'code': line.rstrip(),
                    'suggestion': 'Resolve pending issues before production deployment'
                })
            
            # Unused variable (simple heuristic)
            if re.search(r'^\s*\w+\s*=\s*', line_stripped) and not re.search(r'self\.|global |return ', line_stripped):
                var_match = re.match(r'^\s*(\w+)\s*=', line_stripped)
                if var_match:
                    var_name = var_match.group(1)
                    # Check if variable is used later (simple check)
                    if var_name not in content[content.find(line):]:
                        issues.append({
                            'type': 'Code Quality Issue - Unused Variable',
                            'severity': 'LOW',
                            'cvss': '2.0',
                            'line': line_num,
                            'message': f'Variable "{var_name}" appears to be unused',
                            'code': line.rstrip(),
                            'suggestion': 'Remove unused variables or prefix with underscore if intentional'
                        })
            
            # Missing docstring for functions/classes
            if re.search(r'^(def|class)\s+\w+', line_stripped):
                # Check if next non-empty line is a docstring
                next_line_idx = line_num
                while next_line_idx < len(lines) and not lines[next_line_idx].strip():
                    next_line_idx += 1
                
                if next_line_idx < len(lines):
                    next_line = lines[next_line_idx].strip()
                    if not (next_line.startswith('"""') or next_line.startswith("'''")):
                        issues.append({
                            'type': 'Code Quality Issue - Missing Docstring',
                            'severity': 'LOW',
                            'cvss': '2.0',
                            'line': line_num,
                            'message': 'Function/class missing docstring',
                            'code': line.rstrip(),
                            'suggestion': 'Add docstring to document purpose and parameters'
                        })
            
            # Long line (PEP 8)
            if len(line.rstrip()) > 120:
                issues.append({
                    'type': 'Code Quality Issue - Line Too Long',
                    'severity': 'LOW',
                    'cvss': '2.0',
                    'line': line_num,
                    'message': f'Line exceeds 120 characters ({len(line.rstrip())} chars)',
                    'code': line.rstrip()[:80] + '...',
                    'suggestion': 'Break long lines for better readability (PEP 8 recommends max 79-120 chars)'
                })
            
            # Multiple statements on one line
            if ';' in line_stripped and not line_stripped.startswith('#'):
                issues.append({
                    'type': 'Code Quality Issue - Multiple Statements',
                    'severity': 'LOW',
                    'cvss': '2.0',
                    'line': line_num,
                    'message': 'Multiple statements on one line (semicolon usage)',
                    'code': line.rstrip(),
                    'suggestion': 'Split into separate lines for better readability'
                })
            
            # Comparison to True/False
            if re.search(r'==\s*(True|False)\b', line_stripped) or re.search(r'(True|False)\s*==', line_stripped):
                issues.append({
                    'type': 'Code Quality Issue - Explicit Boolean Comparison',
                    'severity': 'LOW',
                    'cvss': '2.0',
                    'line': line_num,
                    'message': 'Explicit comparison to True/False is not Pythonic',
                    'code': line.rstrip(),
                    'suggestion': 'Use "if variable:" instead of "if variable == True:"'
                })
            
            # Type comparison with type()
            if re.search(r'type\s*\([^)]+\)\s*==', line_stripped):
                issues.append({
                    'type': 'Code Quality Issue - Type Comparison',
                    'severity': 'LOW',
                    'cvss': '2.0',
                    'line': line_num,
                    'message': 'Using type() for comparison is not recommended',
                    'code': line.rstrip(),
                    'suggestion': 'Use isinstance() instead of type() for type checking'
                })
            
            # Empty except block
            if line_stripped == 'pass' and line_num > 1:
                prev_line = lines[line_num - 2].strip()
                if prev_line.startswith('except'):
                    issues.append({
                        'type': 'Code Quality Issue - Empty Exception Handler',
                        'severity': 'LOW',
                        'cvss': '2.5',
                        'line': line_num,
                        'message': 'Empty exception handler silently ignores errors',
                        'code': line.rstrip(),
                        'suggestion': 'Add logging or proper error handling instead of pass'
                    })
    
    except FileNotFoundError:
        issues.append({
            'type': 'File Error',
            'severity': 'LOW',
            'cvss': '2.0',
            'line': 0,
            'message': f'File not found: {file_path}',
            'code': '',
            'suggestion': 'Verify file path exists'
        })
    except Exception as e:
        issues.append({
            'type': 'Analysis Error',
            'severity': 'LOW',
            'cvss': '2.0',
            'line': 0,
            'message': f'Error analyzing file: {str(e)}',
            'code': '',
            'suggestion': 'Check file format and encoding'
        })
    
    return issues if issues else None
