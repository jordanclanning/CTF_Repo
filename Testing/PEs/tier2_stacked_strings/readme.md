# Tier 2 — Stacked Strings in PE

**Cover:** `SystemDiagnostic.exe` — fake system diagnostic utility for "Acme Corp."

**Technique:** Flag is constructed byte-by-byte on the stack at runtime. The bytes appear as immediate values inside compiled instructions in `.text`, never as a contiguous string in any data section. `strings` cannot find it.

**Build:**
```bash
python3 build.py --flag "CTF{your_flag}"
# Produces: SystemDiagnostic.exe
```

**Build flags:** Compiled with `-O0` (no optimization). Required — at `-Os`, GCC constant-folds the byte writes away, defeating the challenge.

**Solve:**
```bash
strings SystemDiagnostic.exe | grep CTF   # finds nothing
floss SystemDiagnostic.exe | grep CTF     # reveals the flag
```

FLOSS classifies the find as a "tight string" or "decoded string" rather than a strict "stack string" (FLOSS's stack-string detection looks for specific byte-write patterns that GCC doesn't always emit). The flag is still recovered via FLOSS's other strategies.

**Skills taught:**
- The limits of `strings` — not all string data lives in data sections
- Recognizing runtime-constructed string obfuscation (a real malware technique)
- Using FLOSS to recover strings invisible to `strings`
- Understanding that some analyses require function emulation, not just static parsing
