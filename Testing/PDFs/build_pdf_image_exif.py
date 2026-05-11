#!/usr/bin/env python3
"""
build_pdf_image_exif.py — CTF challenge builder (Tier 1.5)

Generates a PDF containing an embedded JPEG image whose EXIF UserComment
field hides the flag. Decoy URLs are scattered through the PDF body text,
PDF metadata, and the image's EXIF to mislead grep-based analysis.

Intended solve path:
    pdfid.py challenge.pdf                  # see image objects present
    pdfimages -all challenge.pdf extracted  # extract the embedded image
    exiftool extracted-000.jpg              # find UserComment with flag

Defeats:
    cat / strings | grep CTF      (flag is inside JPEG binary)
    exiftool on the PDF itself    (PDF metadata only — not embedded image)
    grep -i http                  (only finds decoy URLs)

Dependencies: reportlab, Pillow, piexif
    pip3 install reportlab==3.6.12 Pillow piexif
"""

import argparse
import io
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont
import piexif

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader


# ----------------------------------------------------------------------
# Decoy URLs — none of these are real malicious sites. They exist purely
# to clutter the file so participants can't just `grep http`.
# ----------------------------------------------------------------------
DECOY_URLS = [
    "https://securityreports-internal.com/incident/4471",
    "https://cdn-assets.threatfeeds.net/q3-2025/log.json",
    "https://reporting.corp-intranet.local/upload",
    "https://mirror.advisory-portal.org/CVE-2024-31337",
    "https://download.archive-vault.io/snapshots/oct.tar.gz",
    "https://api.telemetry-collector.dev/v2/events",
    "https://share.evidence-locker.com/case/8821-A",
]


def generate_fake_screenshot(width=600, height=400):
    """
    Create a JPEG that looks vaguely like a screenshot of a security
    dashboard. Returns raw JPEG bytes (no EXIF yet).
    """
    img = Image.new("RGB", (width, height), color=(245, 245, 247))
    draw = ImageDraw.Draw(img)

    # Try to load a system font; fall back to default if not found
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
        font_body = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except (OSError, IOError):
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()

    # Fake "header bar"
    draw.rectangle([(0, 0), (width, 50)], fill=(30, 50, 90))
    draw.text((15, 14), "Security Operations Console", fill="white", font=font_title)

    # Fake table rows
    rows = [
        ("Alert ID", "Severity", "Source", "Status"),
        ("4471", "HIGH", "10.4.18.221", "Investigating"),
        ("4470", "MEDIUM", "10.4.18.207", "Triaged"),
        ("4469", "LOW", "10.4.18.105", "Closed"),
        ("4468", "HIGH", "10.4.18.221", "Investigating"),
    ]
    y = 80
    for i, row in enumerate(rows):
        bg = (255, 255, 255) if i % 2 == 0 else (235, 235, 240)
        draw.rectangle([(20, y), (width - 20, y + 40)], fill=bg)
        x = 35
        for cell in row:
            draw.text((x, y + 12), cell, fill=(20, 20, 30), font=font_body)
            x += 140
        y += 40

    # Save to bytes as JPEG
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def inject_exif(jpeg_bytes, flag, decoys):
    """
    Take raw JPEG bytes, write the flag into EXIF UserComment, and stuff
    decoy URLs into other EXIF text fields. Returns new JPEG bytes.
    """
    # Load existing (likely empty) EXIF from the JPEG
    try:
        exif_dict = piexif.load(jpeg_bytes)
    except Exception:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

    # UserComment per EXIF spec: 8-byte charset header + payload
    user_comment = b"ASCII\x00\x00\x00" + flag.encode("utf-8")
    exif_dict["Exif"][piexif.ExifIFD.UserComment] = user_comment

    # Decoys in other text fields — Artist, Copyright
