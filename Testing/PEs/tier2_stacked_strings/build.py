#!/usr/bin/env python3
"""
build.py - Tier 2 PE Challenge Builder (Stacked Strings)

Compiles source.c into a Windows PE executable (SystemDiagnostic.exe)
with the flag constructed byte-by-byte on the stack at runtime.

The flag NEVER appears contiguously in any data section. `strings`
will not find it. Intended solving tool: FLOSS (flare-floss).

NOTE: Built with -O0 (no optimization). GCC's optimizer is aggressive
enough at -Os to constant-fold the stack-string construction away,
defeating the entire challenge. -O0 guarantees the byte writes appear
as real instructions in .text where FLOSS can emulate them.

Usage:
  python3 build.py --flag "CTF{example_flag}"
  python3 build.py --flag "CTF{x}" --output MyDiagnostic.exe
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

COMPILER = "x86_64-w64-mingw32-gcc"
SOURCE_FILE = "source.c"


def check_compiler():
    if shutil.which(COMPILER) is None:
        print("ERROR: " + COMPILER + " not found.", file=sys.stderr)
        print("Install with: brew install mingw-w64", file=sys.stderr)
        sys.exit(1)


def generate_stacked_string_c(flag):
    """
    Produce C statements like:
      sig[0] = 0x43; sig[1] = 0x54; ... sig[N] = 0x00;
    Using hex for each byte so the bytes appear as immediates inside
    the compiled .text section, not as a plaintext literal anywhere.
    """
    lines = []
    flag_bytes = flag.encode("utf-8")
    for i, b in enumerate(flag_bytes):
        lines.append("    sig[" + str(i) + "] = 0x" + format(b, "02x") + ";")
    lines.append("    sig[" + str(len(flag_bytes)) + "] = 0x00;")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Build Tier 2 PE challenge (stacked strings, FLOSS-solvable)."
    )
    parser.add_argument("--flag", required=True, help='Flag, e.g. "CTF{example}"')
    parser.add_argument("--output", default="SystemDiagnostic.exe", help="Output .exe path")
    args = parser.parse_args()

    check_compiler()

    if not os.path.isfile(SOURCE_FILE):
        print("ERROR: " + SOURCE_FILE + " not found in current directory.", file=sys.stderr)
        sys.exit(1)

    if len(args.flag) >= 250:
        print("ERROR: flag too long (must be < 250 chars).", file=sys.stderr)
        sys.exit(1)

    with open(SOURCE_FILE, "r") as f:
        source = f.read()

    if "{{FLAG_BYTES}}" not in source:
        print("ERROR: source.c missing {{FLAG_BYTES}} placeholder.", file=sys.stderr)
        sys.exit(1)

    flag_bytes_c = generate_stacked_string_c(args.flag)
    patched_source = source.replace("{{FLAG_BYTES}}", flag_bytes_c)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".c", delete=False, dir="."
    ) as tmp:
        tmp.write(patched_source)
        tmp_path = tmp.name

    try:
        print("Compiling " + tmp_path + " -> " + args.output)
        result = subprocess.run(
            [
                COMPILER,
                tmp_path,
                "-o", args.output,
                "-O0",            # NO optimization — required for stacked strings
                "-static",        # static link
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("ERROR: Compilation failed.", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            sys.exit(1)

        print("Build successful: " + args.output)

    finally:
        os.unlink(tmp_path)

    size = os.path.getsize(args.output)
    print("File size: " + str(size) + " bytes")

    print("")
    print("Verify the challenge:")
    print("  file " + args.output)
    print("    -> should report PE32+ executable for MS Windows")
    print("  strings " + args.output + " | grep CTF")
    print("    -> should find NOTHING (flag is stack-constructed)")
    print("  strings " + args.output + " | grep -i acme")
    print("    -> should still find decoy strings")
    print("  floss " + args.output)
    print("    -> should recover the flag in its 'stack strings' output")


if __name__ == "__main__":
    main()
