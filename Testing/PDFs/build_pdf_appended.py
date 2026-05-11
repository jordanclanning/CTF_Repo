#!/usr/bin/env python3
"""
build_pdf_appended.py — CTF Tier 4 Challenge Builder

Creates a PDF that looks like a compliance audit cover sheet.
A ZIP file containing the flag is APPENDED after the PDF's %%EOF
marker. PDF readers ignore data past EOF, so the file opens normally
and PDF-specific tools (pdfid, pdf-parser) report nothing suspicious.

The hidden ZIP is found via file carving: binwalk, strings -a, or
manual hex inspection.

Intended solve path:
  1. pdfid.py target.pdf            -> looks completely clean
  2. pdf-parser.py target.pdf       -> also clean
  3. Participant notices file size feels large, OR follows a subtle hint
  4. binwalk target.pdf             -> detects appended ZIP
  5. binwalk --dd='.*' target.pdf   -> extracts the ZIP
  6. unzip the carved ZIP           -> flag.txt inside

Usage:
  python3 build_pdf_appended.py --flag "CTF{example}"
  python3 build_pdf_appended.py --flag "CTF{x}" --output audit.pdf
"""

import argparse
import io
import os
import sys
import zipfile

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


# ----------------------------------------------------------------------------
# Decoy content
# ----------------------------------------------------------------------------

DECOY_URLS = [
    "https://compliance.acme-corp.local/audits/2026-q2",
    "https://wiki.acme-corp.local/policy/SOX-controls",
    "https://internal-portal.acme-corp.local/audits",
    "https://soc2.acme-corp.local/evidence",
    "https://kb.acme-corp.local/audit-procedures",
    "https://findings.acme-corp.local/2026",
    "https://reports.acme-corp.local/quarterly",
    "https://escalations.acme-corp.local/submit",
]

TEAL = HexColor("#D6EBE9")
ORANGE = HexColor("#E8804A")
DARK_BLUE = HexColor("#0F3556")
ORANGE_BAR = HexColor("#E8804A")
LIGHT_GRAY = HexColor("#EFEFEF")
GRAY_TEXT = HexColor("#333333")


# ----------------------------------------------------------------------------
# Build the visible PDF (a "compliance audit cover sheet")
# ----------------------------------------------------------------------------

def build_pdf_bytes():
    """Generate the visible PDF content and return as bytes."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    # Metadata — no flag, just decoys
    c.setTitle("Compliance Audit Cover Sheet - Q2 2026")
    c.setAuthor("Acme Corp Internal Audit")
    c.setSubject("Quarterly compliance audit transmittal - Internal Use")
    c.setKeywords("compliance,audit,SOX,2026," + DECOY_URLS[0])

    # ---- Header band ----
    c.setFillColor(TEAL)
    c.rect(0, height - 2.2 * inch, width, 2.2 * inch, fill=1, stroke=0)

    c.setFillColor(ORANGE)
    c.circle(width - 1.0 * inch, height - 1.1 * inch, 0.55 * inch, fill=1, stroke=0)

    c.setFillColor(DARK_BLUE)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(0.6 * inch, height - 1.0 * inch, "Compliance Audit")
    c.drawString(0.6 * inch, height - 1.4 * inch, "Cover Sheet")

    c.setFillColor(GRAY_TEXT)
    c.setFont("Helvetica", 11)
    c.drawString(0.6 * inch, height - 1.75 * inch,
                 "Quarterly transmittal of audit evidence and supporting documentation.")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.6 * inch, height - 1.95 * inch,
                 "Reference: AUDIT-2026-Q2-447")

    # ---- Section 1: Audit overview ----
    y = height - 2.7 * inch
    c.setFillColor(ORANGE_BAR)
    c.rect(0.6 * inch, y + 0.05 * inch, 0.5 * inch, 0.05 * inch, fill=1, stroke=0)
    c.setFillColor(DARK_BLUE)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.6 * inch, y - 0.18 * inch, "Audit overview")

    y -= 0.55 * inch
    c.setFillColor(GRAY_TEXT)
    c.setFont("Helvetica", 10)
    body = [
        "This document transmits the Q2 2026 compliance audit evidence",
        "package to the Internal Audit committee. The complete evidence",
        "set is appended below the signature block for offline review.",
        "",
        "Audit scope:",
        "  - Access controls (SOX 404)",
        "  - Change management procedures",
        "  - Incident response readiness",
        "  - Vendor risk assessments",
        "",
        "Distribution portal: " + DECOY_URLS[2],
        "Findings dashboard:  " + DECOY_URLS[5],
    ]
    for line in body:
        c.drawString(0.6 * inch, y, line)
        y -= 14

    # ---- Section 2: Evidence inventory ----
    y -= 0.2 * inch
    c.setFillColor(ORANGE_BAR)
    c.rect(0.6 * inch, y + 0.05 * inch, 0.5 * inch, 0.05 * inch, fill=1, stroke=0)
    c.setFillColor(DARK_BLUE)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.6 * inch, y - 0.18 * inch, "Evidence inventory")

    y -= 0.55 * inch
    c.setFillColor(GRAY_TEXT)
    c.setFont("Helvetica", 10)
    body = [
        "The following artifacts are referenced by this audit package:",
        "",
        "  1. Access review attestations (Q2)",
        "  2. Change tickets sample (47 records)",
        "  3. Incident drill after-action reports",
        "  4. Third-party SOC2 attestations",
        "",
        "Supporting policies: " + DECOY_URLS[1],
        "Procedure library:   " + DECOY_URLS[4],
    ]
    for line in body:
        c.drawString(0.6 * inch, y, line)
        y -= 14

    # ---- Footer "evidence appended" notice ----
    y -= 0.4 * inch
    c.setFillColor(LIGHT_GRAY)
    c.rect(0.6 * inch, y - 0.7 * inch, 7.3 * inch, 0.7 * inch, fill=1, stroke=0)

    c.setFillColor(DARK_BLUE)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.75 * inch, y - 0.25 * inch, "Notice")

    c.setFillColor(GRAY_TEXT)
    c.setFont("Helvetica", 9)
    c.drawString(0.75 * inch, y - 0.42 * inch,
                 "Evidence archive is transmitted appended to this transmittal for")
    c.drawString(0.75 * inch, y - 0.55 * inch,
                 "offline review. Auditors should refer to the trailing archive section.")

    # ---- Signature block ----
    y -= 1.2 * inch
    c.setFillColor(DARK_BLUE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.6 * inch, y, "Submitted by:")
    c.setFillColor(GRAY_TEXT)
    c.setFont("Helvetica", 10)
    c.drawString(2.0 * inch, y, "J. Lanning, Internal Audit")
    c.drawString(0.6 * inch, y - 0.25 * inch, "Date:")
    c.drawString(2.0 * inch, y - 0.25 * inch, "May 11, 2026")
    c.drawString(0.6 * inch, y - 0.5 * inch, "Escalations:")
    c.drawString(2.0 * inch, y - 0.5 * inch, DECOY_URLS[7])

    # Page footer
    c.setFillColor(ORANGE)
    c.rect(0, 0, 0.5 * inch, 0.05 * inch, fill=1, stroke=0)
    c.setFillColor(GRAY_TEXT)
    c.setFont("Helvetica", 9)
    c.drawString(width - 0.6 * inch, 0.3 * inch, "1")

    c.save()
    return buf.getvalue()


# ----------------------------------------------------------------------------
# Build the hidden ZIP payload
# ----------------------------------------------------------------------------

def build_zip_payload(flag):
    """Build a small ZIP containing a flag.txt with the flag inside."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        # The actual flag file
        z.writestr("evidence/flag.txt",
                   "Audit evidence package - confidential\n"
                   "Flag: " + flag + "\n")
        # A few decoy files to make the ZIP look like a real archive
        z.writestr("evidence/access_review_q2.csv",
                   "user,role,last_review,status\n"
                   "jsmith,admin,2026-04-15,approved\n"
                   "alee,analyst,2026-04-15,approved\n"
                   "bwong,manager,2026-04-15,approved\n")
        z.writestr("evidence/README.txt",
                   "Q2 2026 audit evidence package.\n"
                   "Contact internal-audit@acme-corp.local with questions.\n")
    return buf.getvalue()


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Build a CTF Tier 4 challenge: PDF with a ZIP appended after %%EOF."
    )
    parser.add_argument("--flag", required=True, help='Flag, e.g. "CTF{example}"')
    parser.add_argument("--output", default="compliance_audit.pdf",
                        help="Output PDF path")
    args = parser.parse_args()

    # 1. Build the visible PDF
    pdf_bytes = build_pdf_bytes()
    print("Generated PDF body (" + str(len(pdf_bytes)) + " bytes)")

    # 2. Build the hidden ZIP
    zip_bytes = build_zip_payload(args.flag)
    print("Generated hidden ZIP payload (" + str(len(zip_bytes)) + " bytes)")

    # 3. Concatenate: PDF body + ZIP appended after %%EOF
    with open(args.output, "wb") as f:
        f.write(pdf_bytes)
        # Optional separator newline for cleaner hex view (doesn't affect either format)
        f.write(b"\n")
        f.write(zip_bytes)

    total_size = os.path.getsize(args.output)
    print("Built PDF with appended payload: " + args.output)
    print("Total file size: " + str(total_size) + " bytes")

    print("")
    print("Verify the challenge:")
    print("  open " + args.output)
    print("    -> opens as a normal compliance audit document")
    print("  python3 ~/tools/pdfid.py " + args.output)
    print("    -> reports CLEAN (no /EmbeddedFile, no /JavaScript)")
    print("  python3 ~/tools/pdf-parser.py " + args.output)
    print("    -> reports CLEAN")
    print("  strings " + args.output + " | grep -i ctf")
    print("    -> should find NOTHING")
    print("  binwalk " + args.output)
    print("    -> detects the appended ZIP signature")
    print("  binwalk --dd='zip:zip' " + args.output)
    print("    -> extracts the ZIP into _" + args.output + ".extracted/")
    print("  unzip <extracted_zip>     # reveals flag.txt")


if __name__ == "__main__":
    main()
