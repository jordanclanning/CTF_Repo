# Reverse Engineering — Linux / May 2026

These are Linux-based ELF binary challenges. All can be solved using 1) a debugger, 2) a decompiler, or 3) generative AI. They are relatively approachable for anyone familiar with tools like GDB, Ghidra, or strings analysis.

---

## Challenges

### Wheres_The_Flag
- **Description:** The flag is not stored statically in the binary — it only exists in memory at runtime.
- **How to Solve:** Run the binary under a debugger (GDB/pwndbg) and inspect memory at runtime to find the flag.
- **Flag:** `Summit{runtime_memory_only}`

---

### challenge_split
- **Description:** The flag has been split across the binary using logic that must be traced to reconstruct it.
- **How to Solve:** Decompile the binary and trace the split logic to reassemble the full flag string.
- **Flag:** `Summit{split_logic_rocks}`

---

### malicious_calculator
- **Description:** A calculator application with malicious behavior hidden inside — analyze it to find the flag.
- **How to Solve:** Load the binary into Ghidra or a similar decompiler and analyze the hidden functionality.
- **Flag:** `SummitCTF{GhidraMaster}`

---

### ransomware
- **Description:** A simulated ransomware binary — reverse the encryption or logic to retrieve the flag.
- **How to Solve:** Decompile and trace the ransomware logic, identifying where the flag is embedded or derived.
- **Flag:** `Summit{Overflow4tw}`

---

## Recommended Tools
- **GDB / pwndbg** — runtime debugging
- **Ghidra** — static decompilation
- **strings / objdump** — quick static analysis
- **ltrace / strace** — library and syscall tracing
