from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
import tempfile
from analyzer.indentation_check import check_indentation
from analyzer.security_check import check_security_vulnerabilities
from analyzer.low_severity_check import check_low_severity_issues
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import mm
import io

def _esc(text):
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def _table_style(header_bg=colors.HexColor('#2d2d2d')):
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), header_bg),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, 0), 9),
        ('FONTNAME',   (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',   (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f5f5f5'), colors.white]),
        ('GRID',       (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('VALIGN',     (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING',  (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ])

def generate_pdf_report(report_text, report_path, errors=None, filename='', code_output=None):
    """Build a structured PDF report with real tables."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=15*mm, rightMargin=15*mm,
                            topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    W = A4[0] - 30*mm

    title_style = ParagraphStyle('title', parent=styles['Normal'],
                                 fontName='Helvetica-Bold', fontSize=16,
                                 textColor=colors.HexColor('#1a1a2e'), spaceAfter=4)
    heading_style = ParagraphStyle('heading', parent=styles['Normal'],
                                   fontName='Helvetica-Bold', fontSize=11,
                                   textColor=colors.white, spaceAfter=2)
    normal = ParagraphStyle('normal', parent=styles['Normal'],
                            fontName='Helvetica', fontSize=9, leading=13)
    mono = ParagraphStyle('mono', parent=styles['Normal'],
                          fontName='Courier', fontSize=8, leading=11,
                          backColor=colors.HexColor('#f0f0f0'))
    footer_style = ParagraphStyle('footer', parent=styles['Normal'],
                                  fontName='Helvetica', fontSize=8,
                                  textColor=colors.grey, alignment=1)

    def section_header(text):
        tbl = Table([[Paragraph(text, heading_style)]], colWidths=[W])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#2d2d2d')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        return tbl

    story = []
    story.append(Paragraph('🛡 SecureCode Analysis Report', title_style))
    story.append(Paragraph(f'File: <b>{_esc(filename)}.py</b>', normal))
    story.append(Spacer(1, 6*mm))

    if errors:
        # Summary table
        story.append(section_header('SUMMARY'))
        story.append(Spacer(1, 2*mm))
        summary_data = [
            ['Metric', 'Value'],
            ['Total Issues', str(len(errors))],
            ['Risk Level', 'HIGH' if any(e.get('severity','').upper() in ('HIGH','CRITICAL') for e in errors) else 'MEDIUM'],
        ]
        tbl = Table(summary_data, colWidths=[W*0.6, W*0.4])
        tbl.setStyle(_table_style())
        story.append(tbl)
        story.append(Spacer(1, 6*mm))

        # Issues overview table
        story.append(section_header('ISSUES OVERVIEW'))
        story.append(Spacer(1, 2*mm))
        overview_data = [['#', 'Type', 'Severity', 'Line']]
        for i, e in enumerate(errors, 1):
            overview_data.append([
                str(i),
                _esc(e['type']),
                _esc(e.get('severity', 'N/A')),
                str(e['line']),
            ])
        tbl = Table(overview_data, colWidths=[W*0.06, W*0.50, W*0.24, W*0.20])
        tbl.setStyle(_table_style())
        story.append(tbl)
        story.append(Spacer(1, 6*mm))

        # Detailed findings — one table per error
        story.append(section_header('DETAILED FINDINGS'))
        story.append(Spacer(1, 2*mm))
        for i, e in enumerate(errors, 1):
            rows = [['Field', 'Detail']]
            rows.append(['Error #', str(i)])
            rows.append(['Type', _esc(e['type'])])
            if 'severity' in e:
                rows.append(['Severity', _esc(e['severity'])])
            if 'cvss' in e:
                rows.append(['CVSS Score', _esc(e['cvss'])])
            rows.append(['Line', str(e['line'])])
            rows.append(['Description', Paragraph(_esc(e['message']), normal)])
            rows.append(['Code Snippet', Paragraph(_esc(e['code']), mono)])
            rows.append(['Recommendation', Paragraph(_esc(e['suggestion']), normal)])
            tbl = Table(rows, colWidths=[W*0.25, W*0.75])
            tbl.setStyle(_table_style())
            story.append(tbl)
            story.append(Spacer(1, 4*mm))
    else:
        # Success — summary table
        story.append(section_header('SUMMARY'))
        story.append(Spacer(1, 2*mm))
        summary_data = [
            ['Metric', 'Value'],
            ['Total Issues', '0'],
            ['Risk Level', 'SECURE'],
        ]
        tbl = Table(summary_data, colWidths=[W*0.6, W*0.4])
        tbl.setStyle(_table_style())
        story.append(tbl)
        story.append(Spacer(1, 6*mm))

        if code_output:
            story.append(section_header('CODE OUTPUT'))
            story.append(Spacer(1, 2*mm))
            story.append(Paragraph(_esc(code_output), mono))
            story.append(Spacer(1, 4*mm))

    story.append(Spacer(1, 4*mm))
    story.append(Paragraph('SecureCode — Python Security &amp; Code Quality Analyzer', footer_style))
    story.append(Paragraph('Copyright © 2025 noob_sandip.', footer_style))

    doc.build(story)
    with open(report_path, 'wb') as f:
        f.write(buf.getvalue())

def format_error_report(errors, filename, show_filename=True):
    """Format errors into a structured report."""
    report = []
    if show_filename:
        report.append(f"File: {filename}.py\n")
    report.append("="*80)
    report.append("SECURECODE ANALYSIS REPORT")
    report.append("="*80)
    report.append(f"\nTotal Errors Found: {len(errors)}\n")
    report.append("="*80)
    
    # Issues table
    report.append("\n" + "-" * 80)
    report.append(f"{'#':<4} | {'Type':<25} | {'Severity':<10} | {'Line':<6}")
    report.append("-" * 80)
    
    for i, error in enumerate(errors, 1):
        error_type = error['type'][:24] if len(error['type']) > 24 else error['type']
        severity = error.get('severity', 'N/A')[:9] if error.get('severity') else 'N/A'
        line = str(error['line'])
        report.append(f"{i:<4} | {error_type:<25} | {severity:<10} | {line:<6}")
    
    report.append("-" * 80)
    
    # Detailed findings
    report.append("\n" + "="*80)
    report.append("DETAILED FINDINGS")
    report.append("="*80)
    
    for i, error in enumerate(errors, 1):
        report.append(f"\n[ERROR #{i}]")
        report.append("-"*80)
        report.append(f"Error Type      : {error['type']}")
        if 'severity' in error:
            report.append(f"Severity        : {error['severity']}")
        if 'cvss' in error:
            report.append(f"CVSS Score      : {error['cvss']}")
        report.append(f"Line Number     : {error['line']}")
        report.append(f"Description     : {error['message']}")
        report.append(f"\nCode Snippet    :")
        report.append(f"  {error['code']}")
        report.append(f"\nRecommendation  : {error['suggestion']}")
        report.append("-"*80)
    
    report.append("\n" + "="*80)
    report.append("END OF REPORT")
    report.append("="*80)
    report.append("\n" + "-" * 80)
    report.append("SecureCode - Python Security & Code Quality Analyzer")
    report.append("Copyright © 2025 noob_sandip.")
    report.append("-" * 80)
    
    return "\n".join(report)

@csrf_exempt
def analyze_code_api(request):
    """
    API endpoint to analyze Python code
    POST /api/analyze/
    Body: {"code": "python code string", "filename": "optional_name"}
    OR
    Form-data: file upload with 'file' field
    """
    if request.method == 'GET':
        return JsonResponse({
            'message': 'SecureCode Analyze Endpoint',
            'method': 'POST',
            'content_type': 'application/json OR multipart/form-data',
            'json_body': {
                'code': 'Python code as string (required)',
                'filename': 'Optional filename (default: api_code)'
            },
            'file_upload': 'Send file with key "file" in form-data',
            'example': {
                'code': 'def hello():\n    print("Hello World")',
                'filename': 'test'
            }
        })
    
    try:
        code_content = None
        filename = 'api_code'
        
        # Handle file upload
        if request.FILES.get('file'):
            uploaded_file = request.FILES['file']
            filename = os.path.splitext(uploaded_file.name)[0]
            code_content = uploaded_file.read().decode('utf-8')
        # Handle JSON body
        elif request.body:
            data = json.loads(request.body)
            code_content = data.get('code')
            filename = data.get('filename', 'api_code')
        
        if not code_content:
            return JsonResponse({'error': 'No code provided'}, status=400)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code_content)
            temp_path = temp_file.name
        
        try:
            # Check for indentation, security, and low-severity issues
            indentation_errors = check_indentation(temp_path)
            security_vulnerabilities = check_security_vulnerabilities(temp_path)
            low_severity_issues = check_low_severity_issues(temp_path)
            
            # Combine all issues
            all_issues = []
            if indentation_errors:
                all_issues.extend(indentation_errors)
            if security_vulnerabilities:
                all_issues.extend(security_vulnerabilities)
            if low_severity_issues:
                all_issues.extend(low_severity_issues)
            
            os.makedirs('reports', exist_ok=True)
            report_path = f'reports/{filename}.pdf'
            
            if all_issues:
                report_text = format_error_report(all_issues, filename, False)
                generate_pdf_report(report_text, report_path, errors=all_issues, filename=filename)
                
                return JsonResponse({
                    'status': 'error',
                    'has_errors': True,
                    'error_count': len(all_issues),
                    'errors': all_issues,
                    'report': report_text,
                    'filename': filename
                })
            else:
                code_output = "(Code execution disabled; submitted code was not run.)"
                
                report_text = "="*80 + "\n" + "SECURECODE ANALYSIS REPORT\n" + "="*80 + "\n\n✅ SUCCESS: No issues detected!\n\n" + "="*80 + "\nSUMMARY\n" + "="*80 + "\n" + "-"*80 + "\n" + f"{'Metric':<30} | {'Value':<10}\n" + "-"*80 + "\n" + f"{'Total Issues':<30} | {0:<10}\n" + f"{'Risk Level':<30} | {'SECURE':<10}\n" + "-"*80 + "\n\n" + "="*80 + "\nCODE OUTPUT:\n" + "="*80 + "\n" + code_output + "\n" + "="*80 + "\n\n" + "-"*80 + "\nSecureCode - Python Security & Code Quality Analyzer\nCopyright © 2025 noob_sandip.\n" + "-"*80
                generate_pdf_report(report_text, report_path, errors=None, filename=filename, code_output=code_output)
                
                return JsonResponse({
                    'status': 'success',
                    'has_errors': False,
                    'message': 'No issues detected',
                    'output': code_output,
                    'report': report_text,
                    'filename': filename
                })
        finally:
            os.unlink(temp_path)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_report_api(request, filename):
    """
    API endpoint to download report as text file
    GET /api/report/<filename>/
    Add ?download=true to download as file attachment
    """
    report_path = f'reports/{filename}.pdf'
    
    if os.path.exists(report_path):
        from django.http import HttpResponse
        if request.GET.get('download') == 'true':
            with open(report_path, 'rb') as f:
                content = f.read()
            response = HttpResponse(content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
            return response
        
        return JsonResponse({
            'status': 'success',
            'filename': filename,
            'report': f'PDF report available at /api/report/{filename}/?download=true'
        })
    
    return JsonResponse({'error': 'Report not found'}, status=404)

@require_http_methods(["GET"])
def health_check_api(request):
    """
    API endpoint for health check
    GET /api/health/
    """
    return JsonResponse({
        'status': 'ok',
        'service': 'SecureCode API',
        'version': '1.0'
    })

@require_http_methods(["GET"])
def download_cli(request):
    """
    API endpoint to download cli.py
    GET /api/download/cli/
    """
    from django.http import HttpResponse
    from django.conf import settings
    import os
    
    # Get the base directory (where manage.py is)
    base_dir = settings.BASE_DIR
    cli_path = os.path.join(base_dir, 'cli_standalone.py')
    
    if os.path.exists(cli_path):
        with open(cli_path, 'r') as f:
            content = f.read()
        response = HttpResponse(content, content_type='text/x-python')
        response['Content-Disposition'] = 'attachment; filename="cli.py"'
        return response
    
    return JsonResponse({'error': 'CLI file not found'}, status=404)

