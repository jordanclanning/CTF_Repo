# PDF Challenges

This directory contains scripts that generate PDF-based CTF challenges. Each script builds a viewable PDF artifact with a flag hidden using a specific technique. Participants analyze the artifact using standard tools.

## Tiers Available

| Tier | Script | Technique | Status |
|------|--------|-----------|--------|
| 1 | `build_pdf_meta.py` | Flag in PDF metadata (Subject field) | ✅ Working |
| 1.5 | `build_pdf_image_exif.py` | Flag in EXIF UserComment of embedded image | ✅ Working |
| 3 | `build_pdf_embedded_ps.py` | Obfuscated PowerShell payload embedded as PDF attachment | ✅ Working |

Difficulty increases with tier number. Tier 2 (hidden stream) and Tier 4 (generic embedded file) are planned but not yet built.

---

## Deployment (For CTF Hosts)

### Prerequisites

- Python 3.8 or newer
- Required packages:
```bash
