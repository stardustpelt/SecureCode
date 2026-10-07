#!/usr/bin/env python3
"""Scan Python files for syntax, security, and code-quality findings."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
from html import escape

from analyzer.indentation_check import check_indentation
from analyzer.low_severity_check import check_low_severity_issues
from analyzer.security_check import check_security_vulnerabilities


def collect_python_files(paths):
    files = []
    errors = []
    seen = set()

    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            errors.append(f"Path not found: {path}")
            continue
        if path.is_dir():
            candidates = sorted(path.rglob('*.py'))
            if not candidates:
                errors.append(f"No Python files found in: {path}")
        elif path.is_file() and path.suffix == '.py':
            candidates = [path]
        else:
            errors.append(f"Not a Python file or directory: {path}")
            continue

        for candidate in candidates:
            resolved = candidate.resolve()
            if resolved not in seen:
                seen.add(resolved)
                files.append(candidate)

    return files, errors


def scan_file(path):
    indentation_findings = check_indentation(str(path)) or []
    security_findings = check_security_vulnerabilities(str(path)) or []
    quality_findings = check_low_severity_issues(str(path)) or []

    if indentation_findings:
        quality_findings = [
            finding for finding in quality_findings
            if finding.get('type') not in ('Syntax Error', 'Indentation Error')
        ]

    security_todo_lines = {
        (finding.get('line'), finding.get('code'))
        for finding in security_findings
        if finding.get('type') == 'Code Quality Issue'
    }
    quality_findings = [
        finding for finding in quality_findings
        if not (
            finding.get('type') == 'Code Quality Issue - Unresolved Comment'
            and (finding.get('line'), finding.get('code')) in security_todo_lines
        )
    ]

    findings = []
    for finding in indentation_findings + security_findings + quality_findings:
        normalized = dict(finding)
        normalized.setdefault('severity', 'LOW')
        normalized['file'] = str(path)
        findings.append(normalized)
    return findings


def format_text(findings, scanned_files):
    lines = [
        '=' * 80,
        'SECURECODE ANALYSIS REPORT',
        '=' * 80,
        f'Files scanned: {len(scanned_files)}',
        f'Total findings: {len(findings)}',
        '=' * 80,
    ]
    for number, finding in enumerate(findings, 1):
        lines.extend([
            '',
            f"[FINDING #{number}] {finding['type']} [{finding['severity']}]",
            '-' * 80,
            f"File            : {finding['file']}",
            f"Severity        : {finding['severity']}",
            f"Line Number     : {finding.get('line', 0)}",
            f"Description     : {finding.get('message', '')}",
            'Code Snippet    :',
            f"  {finding.get('code', '')}",
            f"Recommendation  : {finding.get('suggestion', '')}",
        ])
    if not findings:
        lines.extend(['', 'No findings detected.'])
    lines.append('=' * 80)
    return '\n'.join(lines)


def write_pdf(findings, scanned_files, output_path):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=15*mm, leftMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm
    )
    W = A4[0] - 30*mm
    styles = getSampleStyleSheet()

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
    story.append(Paragraph('🛡 SECURECODE CLI ASSESSMENT REPORT', title_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph(f'<b>Files Scanned:</b> {len(scanned_files)} &nbsp;&bull;&nbsp; <b>Total Findings:</b> {len(findings)}', meta_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#cbd5e1'), spaceAfter=12))

    # 2. Detailed Findings / Threat Cards
    if findings:
        story.append(Paragraph('Detailed Findings & Remediation Case Files', section_title))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0'), spaceAfter=8))

        for number, finding in enumerate(findings, 1):
            severity = str(finding.get('severity', 'LOW')).upper()
            sev_color = '#e11d48' if severity in ['HIGH', 'CRITICAL'] else ('#d97706' if severity == 'MEDIUM' else '#059669')
            
            card_content = []
            
            # Header line
            header_html = f"<b>#{number} // {escape(str(finding.get('type', 'Violation')))}</b> &nbsp;&bull;&nbsp; Line {escape(str(finding.get('line', 0)))} &nbsp;&bull;&nbsp; <font color='{sev_color}'><b>[{severity}]</b></font>"
            card_content.append(Paragraph(header_html, body_style))
            card_content.append(Spacer(1, 4))
            
            # File and Description
            card_content.append(Paragraph(f"<b>File:</b> {escape(str(finding.get('file', '')))}", body_style))
            card_content.append(Spacer(1, 2))
            card_content.append(Paragraph(escape(str(finding.get('message', ''))), body_style))
            
            # Code snippet box
            if finding.get('code'):
                card_content.append(Spacer(1, 4))
                snippet_html = f"<b>Snippet:</b> <code>{escape(str(finding.get('code')))}</code>"
                card_content.append(Paragraph(snippet_html, code_style))

            # Recommendation / Fix
            if finding.get('suggestion'):
                card_content.append(Spacer(1, 4))
                fix_html = f"<b>Remediation:</b> {escape(str(finding.get('suggestion')))}"
                card_content.append(Paragraph(fix_html, fix_style))

            # Wrap into individual styled threat card table
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
        story.append(Paragraph('✅ <b>No security vulnerabilities or code quality issues detected.</b>', body_style))

    # Footer
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=6))
    footer_style = ParagraphStyle('FooterText', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=colors.HexColor('#64748b'), alignment=1)
    story.append(Paragraph('SecureCode — Python Security &amp; Code Quality Analyzer | Copyright © 2025 noob_sandip.', footer_style))

    doc.build(story)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Scan Python files and folders for syntax, security, and code-quality findings.'
    )
    parser.add_argument('paths', nargs='+', help='Python files or folders to scan recursively')
    parser.add_argument('-o', '--output', help='Write the report to a file')
    parser.add_argument('--format', choices=('text', 'json', 'pdf'), default=None,
                        help='Report format (default: text, or inferred from --output extension)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Suppress the report when no findings are found')
    args = parser.parse_args(argv)

    paths = []
    stdin_path = None
    for raw_path in args.paths:
        if raw_path == '-':
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as source:
                source.write(sys.stdin.read())
                stdin_path = Path(source.name)
            paths.append(stdin_path)
        else:
            paths.append(Path(raw_path))

    try:
        files, path_errors = collect_python_files(paths)
        if path_errors:
            for error in path_errors:
                print(error, file=sys.stderr)
        if not files:
            return 1

        findings = []
        for path in files:
            file_findings = scan_file(path)
            if stdin_path and path.resolve() == stdin_path.resolve():
                for finding in file_findings:
                    finding['file'] = '<stdin>'
            findings.extend(file_findings)

        report_format = args.format
        if report_format is None:
            suffix = Path(args.output).suffix.lower() if args.output else ''
            report_format = 'json' if suffix == '.json' else 'pdf' if suffix == '.pdf' else 'text'

        if args.quiet and not findings:
            return 1 if path_errors else 0

        output_path = args.output
        if report_format == 'pdf':
            output_path = output_path or 'securecode-report.pdf'
            write_pdf(findings, files, output_path)
            print(f'Report saved to: {output_path}')
        elif report_format == 'json':
            report = json.dumps({
                'files_scanned': ['<stdin>' if stdin_path and path.resolve() == stdin_path.resolve() else str(path) for path in files],
                'file_count': len(files),
                'finding_count': len(findings),
                'findings': findings,
            }, indent=2)
            if output_path:
                Path(output_path).write_text(report + '\n', encoding='utf-8')
                print(f'Report saved to: {output_path}')
            else:
                print(report)
        else:
            report = format_text(findings, files)
            if output_path:
                Path(output_path).write_text(report + '\n', encoding='utf-8')
                print(f'Report saved to: {output_path}')
            else:
                print(report)

        return 1 if findings or path_errors else 0
    finally:
        if stdin_path:
            stdin_path.unlink(missing_ok=True)


if __name__ == '__main__':
    sys.exit(main())