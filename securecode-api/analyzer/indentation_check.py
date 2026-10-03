import ast

def get_suggestion(error_type, message):
    """Get suggestion based on error type and message."""
    if "expected an indented block" in message:
        return "Ensure the function body is properly indented."
    elif "unexpected indent" in message:
        return "Check the indentation level on this line."
    elif "invalid syntax" in message:
        return "Check for missing colons, parentheses, or quotes."
    else:
        return "Review the syntax and indentation on this line."

def check_indentation(file_path):
    """Check Python file for indentation and syntax errors."""
    errors = []
    
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # Try parsing the entire file to catch all errors
        try:
            with open(file_path, 'r') as file:
                ast.parse(file.read())
        except (SyntaxError, IndentationError) as e:
            error_type = type(e).__name__
            line_num = e.lineno or 1
            code_line = lines[line_num - 1].rstrip() if line_num <= len(lines) else "(line not found)"
            suggestion = get_suggestion(error_type, e.msg)
            
            errors.append({
                'type': error_type,
                'line': line_num,
                'message': e.msg,
                'code': code_line,
                'suggestion': suggestion
            })
                
    except FileNotFoundError:
        errors.append({
            'type': 'FileNotFoundError',
            'line': 0,
            'message': f"File not found: {file_path}",
            'code': '',
            'suggestion': 'Check the file path and ensure the file exists.'
        })
    except Exception as e:
        errors.append({
            'type': type(e).__name__,
            'line': 0,
            'message': str(e),
            'code': '',
            'suggestion': 'Review the file for unexpected issues.'
        })
    
    return errors if errors else None
