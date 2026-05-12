# Tier 2 — Stacked Strings in PE

**Cover:** `SystemDiagnostic.exe` — fake system diagnostic utility for "Acme Corp."

**Technique:** Flag is constructed byte-by-byte on the stack at runtime. The bytes appear as immediate values inside compiled instructions in `.text`, never as a contiguous string in any data section. `strings` cannot find it.

**Build:**
```bash
python3 build.py --flag "CTF{your_flag}"
# Produces: SystemDiagnostic.exe
```

**Solve:**
```bash
strings SystemDiagnostic.exe | grep CTF   # finds nothing
floss SystemDiagnostic.exe                # reveals stack strings, including the flag
```

**Skills taught:**
- The limits of `strings` — not all string data is in data sections
- Recognizing stacked-string obfuscation (a real malware technique)
- Using FLOSS to recover stack-constructed strings
- Understanding that some analyses require function emulation, not just static parsing
