from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import uuid
from analyzer.indentation_check import check_indentation
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import mm
import io

def _safe_report_name(name):
    name = os.path.basename(str(name or ''))
    safe_name = ''.join(
        char for char in name
        if (char.isascii() and char.isalnum()) or char in '_-'
    )[:64]
    return safe_name or 'api_code'

def _report_path(name):
    reports_dir = os.path.realpath('reports')
    report_path = os.path.realpath(os.path.join(reports_dir, f'{_safe_report_name(name)}.pdf'))
    if os.path.commonpath((reports_dir, report_path)) != reports_dir:
        raise ValueError('Invalid report path')
    return report_path

_BACKEND_ANALYZER_DIR = Path(__file__).resolve().parents[2] / 'securecode-backend' / 'analyzer'


def _load_backend_checker(module_name):
    module_path = _BACKEND_ANALYZER_DIR / f'{module_name}.py'
    spec = importlib.util.spec_from_file_location(f'securecode_backend_{module_name}', module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f'Unable to load analyzer module: {module_path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check_security_vulnerabilities = _load_backend_checker('security_check').check_security_vulnerabilities
check_low_severity_issues = _load_backend_checker('low_severity_check').check_low_severity_issues

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

    story.append(section_header('SUMMARY'))
    story.append(Spacer(1, 2*mm))
    risk_level = (
        'HIGH' if any(e.get('severity', '').upper() in ('HIGH', 'CRITICAL') for e in errors or [])
        else 'MEDIUM' if errors
        else 'SECURE'
    )
    summary_data = [
        ['Metric', 'Value'],
        ['Total Issues', str(len(errors or []))],
        ['Risk Level', risk_level],
    ]
    tbl = Table(summary_data, colWidths=[W*0.6, W*0.4])
    tbl.setStyle(_table_style())
    story.append(tbl)
    story.append(Spacer(1, 6*mm))

    story.append(section_header('ISSUES OVERVIEW'))
    story.append(Spacer(1, 2*mm))
    overview_data = [['#', 'Type', 'Severity', 'Line']]
    for i, error in enumerate(errors or [], 1):
        overview_data.append([
            str(i),
            _esc(error['type']),
            _esc(error.get('severity', 'N/A')),
            str(error.get('line', 0)),
        ])
    tbl = Table(overview_data, colWidths=[W*0.06, W*0.50, W*0.24, W*0.20])
    tbl.setStyle(_table_style())
    story.append(tbl)
    story.append(Spacer(1, 6*mm))

    story.append(section_header('DETAILED FINDINGS'))
    story.append(Spacer(1, 2*mm))
    if errors:
        for i, error in enumerate(errors, 1):
            rows = [['Field', 'Detail']]
            rows.append(['Error #', str(i)])
            rows.append(['Type', _esc(error['type'])])
            if 'severity' in error:
                rows.append(['Severity', _esc(error['severity'])])
            if 'cvss' in error:
                rows.append(['CVSS Score', _esc(error['cvss'])])
            rows.append(['Line', str(error.get('line', 0))])
            rows.append(['Description', Paragraph(_esc(error.get('message', '')), normal)])
            rows.append(['Code Snippet', Paragraph(_esc(error.get('code', '')), mono)])
            rows.append(['Recommendation', Paragraph(_esc(error.get('suggestion', '')), normal)])
            tbl = Table(rows, colWidths=[W*0.25, W*0.75])
            tbl.setStyle(_table_style())
            story.append(tbl)
            story.append(Spacer(1, 4*mm))
    else:
        story.append(Paragraph('No findings detected.', normal))

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
    report.append("="*70)
    report.append("SECURECODE ANALYSIS REPORT")
    report.append("="*70)
    report.append(f"\nTotal Errors Found: {len(errors)}\n")
    report.append("="*70)
    
    for i, error in enumerate(errors, 1):
        report.append(f"\n[ERROR #{i}]")
        report.append("-"*70)
        report.append(f"Error Type      : {error['type']}")
        report.append(f"Line Number     : {error['line']}")
        report.append(f"Description     : {error['message']}")
        report.append(f"\nCode Snippet    :")
        report.append(f"  {error['code']}")
        report.append(f"\nRecommendation  : {error['suggestion']}")
        report.append("-"*70)
    
    report.append("\n" + "="*70)
    report.append("END OF REPORT")
    report.append("="*70)
    
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
            filename = _safe_report_name(os.path.splitext(uploaded_file.name)[0])
            code_content = uploaded_file.read().decode('utf-8')
        # Handle JSON body
        elif request.body:
            data = json.loads(request.body)
            code_content = data.get('code')
            filename = _safe_report_name(data.get('filename', 'api_code'))
        
        if not code_content:
            return JsonResponse({'error': 'No code provided'}, status=400)

        report_id = uuid.uuid4().hex
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code_content)
            temp_path = temp_file.name
        
        try:
            indentation_errors = check_indentation(temp_path) or []
            security_findings = check_security_vulnerabilities(temp_path) or []
            quality_findings = check_low_severity_issues(temp_path) or []

            if indentation_errors:
                quality_findings = [
                    finding for finding in quality_findings
                    if finding.get('type') not in ('Syntax Error', 'Indentation Error')
                ]

            all_issues = indentation_errors + security_findings + quality_findings
            os.makedirs('reports', exist_ok=True)
            report_path = _report_path(report_id)
            report_text = format_error_report(all_issues, filename, False)
            generate_pdf_report(report_text, report_path, errors=all_issues, filename=filename)

            has_errors = bool(all_issues)
            no_execution_message = 'No code was executed.'
            return JsonResponse({
                'status': 'error' if has_errors else 'success',
                'has_errors': has_errors,
                'error_count': len(all_issues),
                'errors': all_issues,
                'message': no_execution_message,
                'output': no_execution_message,
                'report': report_text,
                'filename': filename,
                'report_id': report_id
            })
        finally:
            os.unlink(temp_path)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_report_api(request, report_id):
    """
    API endpoint to download report as text file
    GET /api/report/<report_id>/
    Add ?download=true to download as file attachment
    """
    report_path = _report_path(report_id)
    
    if os.path.exists(report_path):
        from django.http import HttpResponse
        if request.GET.get('download') == 'true':
            with open(report_path, 'rb') as f:
                content = f.read()
            response = HttpResponse(content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{report_id}.pdf"'
            return response
        
        return JsonResponse({
            'status': 'success',
            'report_id': report_id,
            'report': f'PDF report available at /api/report/{report_id}/?download=true'
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
