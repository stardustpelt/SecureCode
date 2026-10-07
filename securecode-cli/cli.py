#!/usr/bin/env python3
"""Command-line interface for the standalone SecureCode analyzer."""

import argparse
import html
import json
from pathlib import Path
import sys

from engine import analyze_file, analyze_source, collect_python_files


def _table(findings, files_scanned):
    headers = ("SEVERITY", "FILE", "LINE", "FINDING")
    rows = [
        (
            finding.get("severity", "LOW").upper(),
            finding.get("file", ""),
            str(finding.get("line", 0)),
            finding.get("type", "Finding"),
        )
        for finding in findings
    ]
    widths = [
        max([len(headers[index]), *(len(row[index]) for row in rows)])
        for index in range(len(headers))
    ]
    separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"
    lines = [
        f"SecureCode scan: {files_scanned} file(s), {len(findings)} finding(s)",
        separator,
        "| " + " | ".join(headers[index].ljust(widths[index]) for index in range(4)) + " |",
        separator,
    ]
    if rows:
        for row in rows:
            display = tuple(value.replace("\n", " ") for value in row)
            lines.append("| " + " | ".join(
                display[index].ljust(widths[index]) for index in range(4)
            ) + " |")
    else:
        lines.append("| No findings detected.".ljust(sum(widths) + 9) + " |")
    lines.append(separator)
    return "\n".join(lines)


def _write_pdf(findings, files_scanned, output_path):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

    styles = getSampleStyleSheet()
    body = ParagraphStyle("FindingBody", parent=styles["BodyText"], fontSize=8, leading=10)
    story = [
        Paragraph("SecureCode Analysis Report", styles["Title"]),
        Paragraph(
            f"Files scanned: {files_scanned} &nbsp; | &nbsp; Findings: {len(findings)}",
            styles["BodyText"],
        ),
        Spacer(1, 5 * mm),
    ]
    if findings:
        table_data = [["Severity", "File", "Line", "Finding", "Details", "Recommendation"]]
        for finding in findings:
            table_data.append([
                str(finding.get("severity", "LOW")),
                Paragraph(html.escape(str(finding.get("file", ""))), body),
                str(finding.get("line", 0)),
                Paragraph(html.escape(str(finding.get("type", "Finding"))), body),
                Paragraph(html.escape(str(finding.get("message", ""))), body),
                Paragraph(html.escape(str(finding.get("suggestion", ""))), body),
            ])
        table = Table(
            table_data,
            repeatRows=1,
            colWidths=[20 * mm, 43 * mm, 12 * mm, 34 * mm, 55 * mm, 55 * mm],
            hAlign="LEFT",
        )
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24362d")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b7c0b8")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f4f1")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No findings detected.", styles["BodyText"]))

    SimpleDocTemplate(
        str(output_path), pagesize=landscape(A4),
        leftMargin=12 * mm, rightMargin=12 * mm,
        topMargin=12 * mm, bottomMargin=12 * mm,
    ).build(story)


def _report_format(requested_format, output_path):
    if requested_format:
        return requested_format
    suffix = Path(output_path).suffix.lower() if output_path else ""
    if suffix == ".json":
        return "json"
    if suffix == ".pdf":
        return "pdf"
    return "text"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Analyze Python files for security and code-quality issues."
    )
    parser.add_argument(
        "paths", nargs="+", help="Python files or directories; use '-' to read source from stdin"
    )
    parser.add_argument("-o", "--output", help="Save the report to this file")
    parser.add_argument(
        "--format", choices=("text", "json", "pdf"),
        help="Report format (inferred from -o extension, or text by default)",
    )
    args = parser.parse_args(argv)

    input_paths = [path for path in args.paths if path != "-"]
    files, errors = collect_python_files(input_paths)
    findings = []
    scanned_files = []

    for path in files:
        try:
            findings.extend(analyze_file(path))
            scanned_files.append(str(path))
        except OSError as error:
            errors.append(f"Could not read {path}: {error}")

    if "-" in args.paths:
        try:
            stdin_source = sys.stdin.read()
            findings.extend(analyze_source(stdin_source, "<stdin>"))
            scanned_files.append("<stdin>")
            for finding in findings:
                if "file" not in finding:
                    finding["file"] = "<stdin>"
        except OSError as error:
            errors.append(f"Could not read stdin: {error}")

    for error in errors:
        print(f"Error: {error}", file=sys.stderr)

    if not scanned_files:
        return 1

    report_format = _report_format(args.format, args.output)
    output_path = args.output
    if report_format == "pdf" and output_path is None:
        output_path = "securecode-report.pdf"

    try:
        if report_format == "pdf":
            _write_pdf(findings, scanned_files, output_path)
            print(f"PDF report saved to {output_path}")
        elif report_format == "json":
            report = json.dumps({
                "files_scanned": scanned_files,
                "file_count": len(scanned_files),
                "finding_count": len(findings),
                "findings": findings,
            }, indent=2)
            if output_path:
                Path(output_path).write_text(report + "\n", encoding="utf-8")
                print(f"JSON report saved to {output_path}")
            else:
                print(report)
        else:
            report = _table(findings, len(scanned_files))
            if output_path:
                Path(output_path).write_text(report + "\n", encoding="utf-8")
                print(f"Text report saved to {output_path}")
            else:
                print(report)
    except (OSError, ImportError) as error:
        print(f"Error: could not write report: {error}", file=sys.stderr)
        return 1

    return 1 if findings or errors else 0


if __name__ == "__main__":
    sys.exit(main())
