# PDF Challenges

This directory contains scripts that generate PDF-based CTF challenges. Each script builds a viewable PDF artifact with a flag hidden using a specific technique. Participants analyze the artifact using standard tools.

## Tiers Available

| Tier | Script | Technique | Status |
|------|--------|-----------|--------|
| 1 | `build_pdf_meta.py` | Flag in PDF metadata (Subject field) | ✅ Working |
| 1.5 | `build_pdf_image_exif.py` | Flag in EXIF UserComment of embedded image | ✅ Working |

---

## Deployment (For CTF Hosts)

### Prerequisites

- Python 3.8 or newer
- `pip3 install reportlab==3.6.12 PyPDF2 Pillow piexif`

### Build the artifacts

From this directory:

```bash
