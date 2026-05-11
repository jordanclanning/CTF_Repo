#!/usr/bin/env python3
"""
build_pdf_image_exif.py — CTF Tier 1.5 Challenge Builder

Creates a PDF that looks like a routine security incident report,
with an embedded image whose EXIF UserComment field contains the flag.

Decoy URLs are scattered throughout the PDF body and metadata to
mislead participants who rely on `strings | grep` shortcuts.

Intended solve path:
  1. pdfid.py target.pdf            -> shows image objects present
  2. pdfimages -all target.pdf img  -> extracts embedded image
  3. exiftool img-000.jpg           -> reveals flag in UserComment

Usage:
  python3 build_pdf_image_exif.py --flag "CTF{example_flag}"
  python3 build_pdf_image_exif.py --flag "CTF{x}" --image my_pic.jpg --output custom.pdf
"""

import argparse
import io
import os
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import piexif


# -----------------------------------------------------------------------------
# Decoy URLs — plausible-looking domains, intentionally NOT real CTF infra.
# These are red herrings to punish lazy `strings | grep http` analysis.
# Hosts can edit this list to customize per-event.
# -----------------------------------------------------------------------------
DECOY_URLS = [
    "https://internal-reports.acme-corp.local/q3/incident-447",
    "https://secure-mail.acme-corp.local/portal",
    "https://threatfeed.opensecuritydaily.com/ioc/2026-05",
    "https://wiki.acme-corp.local/security/playbooks",
    "https://siem.acme-corp.local/alerts/2026/may",
    "https://kb.vendorx.com/article/CVE-2025-44782",
    "https://status.acme-corp.local",
]

# Realistic-looking but fake IOCs to bulk out the document
DECOY_IOCS = [
    "192.168.47.203",
    "10.14.88.91",
    "ac3f-b27e-9d11-44a8",
    "MD5: 7a3b1d9e44c8f201a6e9b3d5c7e1f88a",
    "SHA256: 9f2c1b3d4e5a6f7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b",
]


def generate_placeholder_image(output_path: str) -> None:
    """
    Generates a believable-looking 'evidence screenshot' image.
    Looks like a blurry screenshot of a console/log at thumbnail size.
    """
    width, height = 800, 500
    img = Image.new("RGB", (width, height), color=(28, 32, 40))
    draw = ImageDraw.Draw(img)

    # Try to use a monospace font; fall back to default if unavailable
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 14)
        title_font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 18)
    except (OSError, IOError):
        font = ImageFont.load_default()
        title_font = font

    # Fake terminal header
    draw.rectangle([0, 0, width, 30], fill=(60, 70, 85))
    draw.text((10, 7), "session-log-447.txt", fill=(220, 220, 220), font=title_font)

    # Fake log lines — looks legitimate, contains no flag
    log_lines = [
        "[2026-05-11 09:42:17] INFO   user=jsmith action=login src=10.14.88.91",
        "[2026-05-11 09:42:18] INFO   session_id=ac3f-b27e-9d11-44a8 established",
        "[2026-05-11 09:43:02] WARN   unusual user-agent detected: 'curl/7.84'",
        "[2026-05-11 09:43:11] INFO   request GET /api/v2/reports/q3",
        "[2026-05-11 09:43:14] ERROR  rate limit exceeded: 47 req/sec",
        "[2026-05-11 09:43:15] ALERT  triggering threat playbook PB-014",
        "[2026-05-11 09:43:17] INFO   notify=secops@acme-corp.local",
        "[2026-05-11 09:43:20] INFO   session terminated, source quarantined",
        "[2026-05-11 09:43:21] INFO   forensic capture initiated -> evidence/447/",
        "[2026-05-11 09:44:05] INFO   handoff to L2 analyst: ticket #IR-2026-447",
    ]

    y = 50
    for line in log_lines:
        draw.text((10, y), line, fill=(180, 200, 180), font=font)
        y += 22

    # Footer
    draw.rectangle([0, height - 25, width, height], fill=(60, 70, 85))
    draw.text((10, height - 20), "End of capture", fill=(180, 180, 180), font=font)

    img.save(output_path, "JPEG", quality=85)


def embed_flag_in_exif(image_path: str, flag: str, extra_decoys: bool = True) -> None:
    """
    Writes the flag into the image's EXIF UserComment field.
    Also writes decoy text into other EXIF fields to add noise.
    """
    # Load existing EXIF (or empty if none)
    try:
        exif_dict = piexif.load(image_path)
    except Exception:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

    # UserComment requires a specific encoding prefix
    user_comment = b"ASCII\x00\x00\x00" + flag.encode("utf-8")
    exif_dict["Exif"][piexif.ExifIFD.UserComment] = user_comment

    if extra_decoys:
        # Decoy text in other EXIF fields — looks like real photo metadata
        exif_dict["0th"][piexif.ImageIFD.Software] = b"Acme SecOps Capture v3.2"
        exif_dict["0th"][piexif.ImageIFD.Artist] = b"automated-capture-system"
        exif_dict["0th"][piexif.ImageIFD.ImageDescription] = (
            b"Forensic evidence capture - ticket IR-2026-447"
        )
        exif_dict["0th"][piexif.ImageIFD.Copyright] = (
            b"Internal use only - https://wiki.acme-corp.local/forensics"
        )

    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, image_path)


def build_pdf(flag: str, image_path: str, output_path: str) -> None:
    """
    Builds the PDF: a believable security incident report with the
    embedded image and decoy URLs scattered throughout.
    """
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # PDF metadata — decoy content, NOT the flag
    c.setTitle("Security Incident Report IR-2026-447")
    c.setAuthor("Acme Corp - Security Operations")
    c.setSubject("Quarterly Incident Review - Internal Use Only")
    c.setKeywords(
        "incident,security,quarterly,2026,"
        + random.choice(DECOY_URLS)
    )

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 80, "SECURITY INCIDENT REPORT")
    c.setFont("Helvetica", 10)
    c.drawString(72, height - 100, "Reference: IR-2026-447    Classification: Internal Use")
    c.drawString(72, height - 115, "Reporting URL: " + DECOY_URLS[0])

    # Body paragraph 1
    c.setFont("Helvetica", 11)
    y = height - 160
    body_lines_top = [
        "An anomalous session was observed on May 11, 2026 originating",
        "from internal subnet 10.14.0.0/16. Initial telemetry was captured by",
        "our SIEM (" + DECOY_URLS[4] + ") and forwarded to L2 review.",
        "",
        "Indicators of Compromise (preliminary):",
        "  - Source: " + DECOY_IOCS[0],
        "  - Session: " + DECOY_IOCS[2],
        "  - Hash: " + DECOY_IOCS[3],
        "",
        "Initial capture image is attached below for analyst review:",
    ]
    for line in body_lines_top:
        c.drawString(72, y, line)
        y -= 16

    # Embed the image
    try:
        img_reader = ImageReader(image_path)
        img_width = 400
        img_height = 250
        c.drawImage(
            img_reader,
            72,
            y - img_height - 20,
            width=img_width,
            height=img_height,
            preserveAspectRatio=True,
        )
        y = y - img_height - 40
    except Exception as e:
        print(f"WARNING: failed to embed image: {e}", file=sys.stderr)

    # Body paragraph 2 (below image)
    body_lines_bottom = [
        "Follow-up actions:",
        "  - Forensic review per playbook: " + DECOY_URLS[3],
        "  - Status dashboard: " + DECOY_URLS[6],
        "  - Vendor advisory: " + DECOY_URLS[5],
        "",
        "Report compiled by automated system. Direct questions to secops.",
    ]
    for line in body_lines_bottom:
        c.drawString(72, y, line)
        y -= 16

    c.save()


def main():
    parser = argparse.ArgumentParser(
        description="Build a CTF Tier 1.5 challenge: PDF with flag hidden in embedded image's EXIF.",
    )
    parser.add_argument(
        "--flag",
        required=True,
        help='Flag to embed, e.g. "CTF{example_flag_value}"',
    )
    parser.add_argument(
        "--output",
        default="incident_report.pdf",
        help="Output PDF path (default: incident_report.pdf)",
    )
    parser.add_argument(
        "--image",
        default=None,
        help="Optional path to a JPG to use. If omitted, one is generated.",
    )
    parser.add_argument(
        "--keep-image",
        action="store_true",
        help="Keep the intermediate image file (useful for debugging).",
    )
    args = parser.parse_args()

    # Decide on image source
    if args.image:
        if not os.path.isfile(args.image):
            print(f"ERROR: image not found: {args.image}", file=sys.stderr)
            sys.exit(1)
        # Copy host's image to a working file so we don't modify their original
        working_image = "_working_image.jpg"
        with open(args.image, "rb") as src, open(working_image, "wb") as dst:
            dst.write(src.read())
        print(f"Using host-supplied image: {args.image}")
    else:
        working_image = "_working_image.jpg"
        generate_placeholder_image(working_image)
        print(f"Generated placeholder image: {working_image}")

    # Inject flag into image EXIF
    embed_flag_in_exif(working_image, args.flag)
    print(f"Embedded flag into UserComment EXIF field")

    # Build the PDF
    build_pdf(args.flag, working_image, args.output)
    print(f"Built PDF: {args.output}")

    # Clean up unless --keep-image
    if not args.keep_image and os.path.exists(working_image):
        os.remove(working_image)

    print("\nDone. Verify the challenge:")
    print(f"  open {args.output}")
    print(f"  pdfid.py {args.output}")
    print(f"  strings {args.output} | grep -i ctf       # should find NOTHING")
    print(f"  strings {args.output} | grep -i http      # should find decoy URLs")
    print(f"  pdfimages -all {args.output} extracted")
    print(f"  exiftool extracted-000.*                 # reveals flag")


if __name__ == "__main__":
    main()
