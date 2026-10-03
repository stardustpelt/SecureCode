#!/usr/bin/env python3
"""Scan Python files for syntax, security, and code-quality findings."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
from xml.sax.saxutils import escape

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
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle('FindingBody', parent=styles['BodyText'], fontSize=9, leading=12, alignment=TA_LEFT)
    code_style = ParagraphStyle('FindingCode', parent=styles['Code'], fontSize=8, leading=10, wordWrap='CJK')
    story = [
        Paragraph('SecureCode Analysis Report', styles['Title']),
        Paragraph(f'Files scanned: {len(scanned_files)} &nbsp; | &nbsp; Total findings: {len(findings)}', body_style),
        Spacer(1, 5 * mm),
    ]
    if findings:
        for number, finding in enumerate(findings, 1):
            story.append(Paragraph(
                f"{number}. {escape(str(finding['type']))} [{escape(str(finding['severity']))}]",
                styles['Heading2'],
            ))
            details = [
                ['File', Paragraph(escape(str(finding['file'])), body_style)],
                ['Line', str(finding.get('line', 0))],
                ['Description', Paragraph(escape(str(finding.get('message', ''))), body_style)],
                ['Code', Preformatted(escape(str(finding.get('code', ''))), code_style)],
                ['Recommendation', Paragraph(escape(str(finding.get('suggestion', ''))), body_style)],
            ]
            table = Table(details, colWidths=[28 * mm, 150 * mm], hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eeeeee')),
                ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#b8b8b8')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.extend([table, Spacer(1, 4 * mm)])
    else:
        story.append(Paragraph('No findings detected.', body_style))

    SimpleDocTemplate(str(output_path), pagesize=A4).build(story)


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
