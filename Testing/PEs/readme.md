# PE Challenges

Scripts that generate Windows PE (Portable Executable) CTF challenges. Each tier lives in its own subdirectory with `source.c`, `build.py`, and a per-tier readme.

## Tiers

| Tier | Directory | Technique | Status |
|------|-----------|-----------|--------|
| 1 | `tier1_strings/` | Plain flag string in `.rdata` | ✅ Working |

## Prerequisites

```bash
brew install mingw-w64
pip3 install pefile
```

## Build

```bash
cd tier1_strings/
python3 build.py --flag "CTF{your_flag}"
```

Built `.exe` files are gitignored. Distribute as password-protected ZIP (`infected` is the standard CTF password) to bypass AV scanners.

## Verification on Mac (build host)

Mac can't *run* Windows PE files but can verify they're well-formed:
```bash
file output.exe                   # confirms PE32+ format
strings output.exe                # reveals plaintext strings
python3 -c "import pefile; pefile.PE('output.exe').print_info()"
```

Full runtime verification requires a Windows VM.
