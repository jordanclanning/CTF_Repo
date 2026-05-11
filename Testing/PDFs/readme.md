# PDF Challenges

Scripts that generate PDF-based CTF challenges. Each produces a viewable PDF with a flag hidden via a specific technique.

## Tiers

| Tier | Script | Technique |
|------|--------|-----------|
| 1 | `build_pdf_meta.py` | Flag in PDF metadata (Subject field) |
| 1.5 | `build_pdf_image_exif.py` | Flag in EXIF of embedded image |
| 3 | `build_pdf_embedded_ps.py` | Obfuscated PowerShell embedded as PDF attachment |
| 4 | `build_pdf_appended.py` | ZIP appended after `%%EOF`, recovered via carving |

## Prerequisites

```bash
pip3 install reportlab==3.6.12 PyPDF2 Pillow piexif pikepdf
```

Analysis tools: `exiftool`, `pdfimages` (poppler), `pdfid.py`/`pdf-parser.py` (Didier Stevens), `binwalk`.

## Build

```bash
python3 build_pdf_meta.py
python3 build_pdf_image_exif.py --flag "CTF{your_flag}"
python3 build_pdf_embedded_ps.py --flag "CTF{your_flag}"
python3 build_pdf_appended.py --flag "CTF{your_flag}"
```

Use unique `--flag` values per team. Built PDFs are gitignored — distribute separately.

## Solve Paths (Organizer Reference)

| Tier | Solve |
|------|-------|
| 1 | `exiftool file.pdf` → flag in Subject |
| 1.5 | `pdfimages -all file.pdf out` → `exiftool out-000.jpg` → flag in UserComment |
| 3 | `pdfid.py` shows `/EmbeddedFile` → `pdf-parser.py -o N -d out.ps1` → reverse + base64 decode (UTF-16LE) → flag in deobfuscated URL |
| 4 | `binwalk --extract file.pdf` → flag in `extractions/.../flag.txt`. Manual: find `PK\x03\x04` offset, carve with `dd` or Python |

## Notes

- Scripts are the host toolkit; built PDFs are the participant-facing artifacts
- Customize decoy content at the top of each script per event
- Tier 2 (hidden FlateDecode stream) — planned, not yet built
