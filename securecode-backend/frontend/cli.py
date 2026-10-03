#!/usr/bin/env python3
"""
SecureCode CLI - Python Indentation and Syntax Checker
"""
import argparse
import sys
import os
from analyzer.indentation_check import check_indentation

def format_errors(errors):
    """Format errors for terminal output."""
    output = []
    output.append("=" * 70)
    output.append("SECURECODE ANALYSIS REPORT")
    output.append("=" * 70)
    output.append(f"\nTotal Errors Found: {len(errors)}\n")
    output.append("=" * 70)
    
    for i, error in enumerate(errors, 1):
        output.append(f"\n[ERROR #{i}]")
        output.append("-" * 70)
        output.append(f"Error Type      : {error['type']}")
        output.append(f"Line Number     : {error['line']}")
        output.append(f"Description     : {error['message']}")
        output.append(f"\nCode Snippet    :")
        output.append(f"  {error['code']}")
        output.append(f"\nRecommendation  : {error['suggestion']}")
        output.append("-" * 70)
    
    output.append("\n" + "=" * 70)
    return "\n".join(output)

def format_success():
    """Format success message."""
    output = []
    output.append("=" * 70)
    output.append("SECURECODE ANALYSIS REPORT")
    output.append("=" * 70)
    output.append("\n✅ SUCCESS: No indentation errors detected!")
    output.append("\nYour code follows proper Python indentation standards.")
    output.append("=" * 70)
    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(
        description='SecureCode - Check Python files for indentation and syntax errors',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  securecode myfile.py              Check a single file
  securecode file1.py file2.py      Check multiple files
  securecode myfile.py -o report.txt  Save report to file
  cat myfile.py | securecode -       Read from stdin
        """
    )
    
    parser.add_argument('files', nargs='+', help='Python file(s) to check (use "-" for stdin)')
    parser.add_argument('-o', '--output', help='Save report to file')
    parser.add_argument('-q', '--quiet', action='store_true', help='Only show errors, no success messages')
    
    args = parser.parse_args()
    
    all_results = []
    exit_code = 0
    
    for file_path in args.files:
        # Handle stdin
        if file_path == '-':
            import tempfile
            code = sys.stdin.read()
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name
            try:
                errors = check_indentation(temp_path)
                file_path = '<stdin>'
            finally:
                os.unlink(temp_path)
        else:
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"Error: File '{file_path}' not found", file=sys.stderr)
                exit_code = 1
                continue
            
            errors = check_indentation(file_path)
        
        # Format output
        if errors:
            exit_code = 1
            result = f"\nFile: {file_path}\n" + format_errors(errors)
        else:
            if not args.quiet:
                result = f"\nFile: {file_path}\n" + format_success()
            else:
                result = None
        
        if result:
            all_results.append(result)
    
    # Print or save results
    if all_results:
        output_text = "\n\n".join(all_results)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_text)
            print(f"Report saved to: {args.output}")
        else:
            print(output_text)
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
