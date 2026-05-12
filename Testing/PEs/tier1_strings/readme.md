# Tier 1 — Plain String in PE

**Cover:** `LicenseValidator.exe` — fake license validation utility for "Acme Corp."

**Technique:** Flag stored as a plain `static const char[]` in the binary's `.rdata` section. No encoding, no obfuscation.

**Build:**
```bash
python3 build.py --flag "CTF{your_flag}"
# Produces: LicenseValidator.exe
```

**Solve:**
```bash
strings LicenseValidator.exe | grep CTF
```

**Skills taught:**
- `strings` as the universal first move on any unknown binary
- Recognizing PE files (`file` output)
- That hardcoded credentials in binaries are real (malware authors do this all the time)
