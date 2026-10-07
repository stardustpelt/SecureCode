from django.http import JsonResponse
from django.core.exceptions import RequestDataTooBig
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
import os
import tempfile
import time
import uuid
from analyzer.indentation_check import check_indentation
from analyzer.security_check import check_security_vulnerabilities
from analyzer.low_severity_check import check_low_severity_issues
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
from reportlab.lib.units import mm
import io

logger = logging.getLogger(__name__)

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

def _cleanup_old_reports():
    cutoff = time.time() - 24 * 60 * 60
    try:
        with os.scandir('reports') as entries:
            for entry in entries:
                try:
                    if (entry.name.endswith('.pdf') and entry.is_file(follow_symlinks=False)
                            and entry.stat(follow_symlinks=False).st_mtime < cutoff):
                        os.unlink(entry.path)
                except OSError:
                    continue
    except OSError:
        return

def _esc(text):
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def generate_pdf_report(report_text, report_path, errors=None, filename='', code_output=None):
    """Build a professional cybersecurity case file PDF report with structured threat cards."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=15*mm, rightMargin=15*mm,
                            topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    W = A4[0] - 30*mm

    title_style = ParagraphStyle('DocTitle', parent=styles['Normal'],
                                 fontName='Helvetica-Bold', fontSize=18,
                                 textColor=colors.HexColor('#0f172a'), spaceAfter=2)
    meta_style = ParagraphStyle('MetaText', parent=styles['Normal'],
                                fontName='Helvetica', fontSize=9, leading=13,
                                textColor=colors.HexColor('#64748b'))
    section_title = ParagraphStyle('SectionHeading', parent=styles['Normal'],
                                   fontName='Helvetica-Bold', fontSize=12,
                                   textColor=colors.HexColor('#1e293b'), spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'],
                                fontName='Helvetica', fontSize=9.5, leading=14,
                                textColor=colors.HexColor('#334155'))
    code_style = ParagraphStyle('CodeSnippet', parent=styles['Normal'],
                                fontName='Courier', fontSize=8.5, leading=11,
                                textColor=colors.HexColor('#e11d48'))
    fix_style = ParagraphStyle('FixText', parent=styles['Normal'],
                                fontName='Helvetica-Bold', fontSize=9, leading=13,
                                textColor=colors.HexColor('#059669'))

    story = []

    # 1. Executive Header Banner
    story.append(Paragraph('🛡 SECURECODE VULNERABILITY ASSESSMENT', title_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph(f'<b>Target File:</b> {_esc(filename)}.py &nbsp;&bull;&nbsp; <b>Engine:</b> AST Static Analysis', meta_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#cbd5e1'), spaceAfter=12))

    # 2. Executive Summary Metrics Table
    has_high = errors and any(e.get('severity','').upper() in ('HIGH','CRITICAL') for e in errors)
    risk_level = 'HIGH' if has_high else ('MEDIUM' if errors else 'SECURE')
    
    summary_data = [
        [
            Paragraph("<b>Total Issues</b>", body_style),
            Paragraph("<b>Assessment Risk Level</b>", body_style),
            Paragraph("<b>Analysis Status</b>", body_style)
        ],
        [
            Paragraph(str(len(errors) if errors else 0), body_style),
            Paragraph(f"<b>{risk_level}</b>", body_style),
            Paragraph("Completed Successfully", body_style)
        ]
    ]
    summary_table = Table(summary_data, colWidths=[W*0.3, W*0.35, W*0.35])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    # 3. Detailed Findings / Threat Cards
    if errors:
        story.append(Paragraph('Detailed Findings & Remediation Case Files', section_title))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0'), spaceAfter=8))

        for i, e in enumerate(errors, 1):
            severity = e.get('severity', 'WARNING').upper()
            sev_color = '#e11d48' if severity in ['HIGH', 'CRITICAL'] else ('#d97706' if severity == 'MEDIUM' else '#059669')
            
            card_content = []
            
            # Card header line
            header_html = f"<b>#{i} // {_esc(e.get('type', 'Violation'))}</b> &nbsp;&bull;&nbsp; Line {e.get('line', 'N/A')} &nbsp;&bull;&nbsp; <font color='{sev_color}'><b>[{severity}]</b></font>"
            if 'cvss' in e:
                header_html += f" &nbsp;&bull;&nbsp; CVSS: {_esc(e['cvss'])}"
            card_content.append(Paragraph(header_html, body_style))
            card_content.append(Spacer(1, 4))
            
            # Description
            card_content.append(Paragraph(_esc(e.get('message', '')), body_style))
            
            # Code snippet box
            if e.get('code'):
                card_content.append(Spacer(1, 4))
                snippet_html = f"<b>Snippet:</b> <code>{_esc(e.get('code'))}</code>"
                card_content.append(Paragraph(snippet_html, code_style))

            # Recommendation / Fix
            if e.get('suggestion'):
                card_content.append(Spacer(1, 4))
                fix_html = f"<b>Remediation:</b> {_esc(e.get('suggestion'))}"
                card_content.append(Paragraph(fix_html, fix_style))

            # Wrap each finding into a distinct card table
            finding_table = Table([[card_content]], colWidths=[W])
            finding_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ffffff')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            story.append(KeepTogether([finding_table, Spacer(1, 8)]))
    else:
        story.append(Paragraph('Assessment Outcome', section_title))
        story.append(Spacer(1, 4))
        story.append(Paragraph('✅ <b>No security vulnerabilities, injection vectors, or quality issues detected!</b> The target source code passed all AST checks cleanly.', body_style))
        story.append(Spacer(1, 8))

        if code_output:
            story.append(Paragraph('Execution Output', section_title))
            story.append(Spacer(1, 4))
            output_table = Table([[Paragraph(_esc(code_output), code_style)]], colWidths=[W])
            output_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(output_table)

    # Footer
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=6))
    footer_style = ParagraphStyle('FooterText', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=colors.HexColor('#64748b'), alignment=1)
    story.append(Paragraph('SecureCode — Python Security &amp; Code Quality Analyzer | Copyright © 2025 noob_sandip.', footer_style))

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

    _cleanup_old_reports()
    
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
            if 'code' in data and not isinstance(code_content, str):
                return JsonResponse({'error': 'Code must be a string.'}, status=400)
            filename = _safe_report_name(data.get('filename', 'api_code'))
        
        if code_content is not None and not isinstance(code_content, str):
            return JsonResponse({'error': 'Code must be a string.'}, status=400)
        if not code_content:
            return JsonResponse({'error': 'No code provided'}, status=400)
        if len(code_content) > 200_000:
            return JsonResponse({'error': 'Code exceeds the 200000 character limit.'}, status=413)

        report_id = uuid.uuid4().hex
        
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
            report_path = _report_path(report_id)
            
            if all_issues:
                report_text = format_error_report(all_issues, filename, False)
                generate_pdf_report(report_text, report_path, errors=all_issues, filename=filename)
                
                return JsonResponse({
                    'status': 'error',
                    'has_errors': True,
                    'error_count': len(all_issues),
                    'errors': all_issues,
                    'report': report_text,
                    'filename': filename,
                    'report_id': report_id
                })
            else:
                code_output = 'No code was executed.'
                
                report_text = "="*80 + "\n" + "SECURECODE ANALYSIS REPORT\n" + "="*80 + "\n\n✅ SUCCESS: No issues detected!\n\n" + "="*80 + "\nSUMMARY\n" + "="*80 + "\n" + "-"*80 + "\n" + f"{'Metric':<30} | {'Value':<10}\n" + "-"*80 + "\n" + f"{'Total Issues':<30} | {0:<10}\n" + f"{'Risk Level':<30} | {'SECURE':<10}\n" + "-"*80 + "\n\n" + "="*80 + "\nCODE OUTPUT:\n" + "="*80 + "\n" + code_output + "\n" + "="*80 + "\n\n" + "-"*80 + "\nSecureCode - Python Security & Code Quality Analyzer\nCopyright © 2025 noob_sandip.\n" + "-"*80
                generate_pdf_report(report_text, report_path, errors=None, filename=filename, code_output=code_output)
                
                return JsonResponse({
                    'status': 'success',
                    'has_errors': False,
                    'message': 'No issues detected',
                    'output': code_output,
                    'report': report_text,
                    'filename': filename,
                    'report_id': report_id
                })
        finally:
            os.unlink(temp_path)
            
    except RequestDataTooBig:
        return JsonResponse({'error': 'Request body exceeds the configured size limit.'}, status=413)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except (RecursionError, MemoryError, ValueError):
        return JsonResponse({'error': 'Input could not be analyzed safely.'}, status=400)
    except Exception:
        logger.exception('Unexpected error while analyzing Python code')
        return JsonResponse({'error': 'Internal server error'}, status=500)

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