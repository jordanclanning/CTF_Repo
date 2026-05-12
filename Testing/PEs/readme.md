# PE Challenges

Scripts that generate Windows PE (Portable Executable) CTF challenges. Each tier lives in its own subdirectory with `source.c`, `build.py`, and a per-tier readme.

## Tiers

| Tier | Directory | Technique | Tool to solve |
|------|-----------|-----------|---------------|
| 1 | `tier1_strings/` | Plain flag string in `.rdata` | `strings` |
| 2 | `tier2_stacked_strings/` | Flag constructed byte-by-byte on the stack at runtime | `floss` |

## Prerequisites

```bash
brew install mingw-w64
pip3 install pefile flare-floss
```

Make sure Python user-script directory is on your PATH for `floss`:
```bash
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
```

## Build

```bash
cd tier1_strings/
python3 build.py --flag "CTF{your_flag}"

cd ../tier2_stacked_strings/
python3 build.py --flag "CTF{your_flag}"
```

Use unique `--flag` values per team. Built `.exe` files are gitignored. Distribute as password-protected ZIP (`infected` is the standard CTF password) to bypass AV scanners.

## Verification on Mac (build host)

Mac can't run Windows PE files but can verify they're well-formed:

```bash
file output.exe                   # confirms PE32+ format
strings output.exe                # reveals plaintext strings
floss output.exe                  # reveals stack/tight/decoded strings
python3 -c "import pefile; pefile.PE('output.exe').print_info()"
```

Full runtime verification requires a Windows VM.
