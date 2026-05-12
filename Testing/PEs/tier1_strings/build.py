#!/usr/bin/env python3
"""
build.py - Tier 1 PE Challenge Builder

Compiles source.c into a Windows PE executable (LicenseValidator.exe)
with the provided flag baked in as a plain string constant.

The flag is recoverable with `strings <output>.exe | grep CTF` -
this is the beginner tier, intentionally easy.

Usage:
  python3 build.py --flag "CTF{example_flag}"
  python3 build.py --flag "CTF{x}" --output MyValidator.exe
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


def main():
    parser = argparse.ArgumentParser(
        description="Build Tier 1 PE challenge (plain string flag)."
    )
    parser.add_argument("--flag", required=True, help='Flag, e.g. "CTF{example}"')
    parser.add_argument("--output", default="LicenseValidator.exe", help="Output .exe path")
    args = parser.parse_args()

    check_compiler()

    if not os.path.isfile(SOURCE_FILE):
        print("ERROR: " + SOURCE_FILE + " not found in current directory.", file=sys.stderr)
        sys.exit(1)

    # Read source, substitute the flag placeholder
    with open(SOURCE_FILE, "r") as f:
        source = f.read()

    if "{{FLAG}}" not in source:
        print("ERROR: source.c missing {{FLAG}} placeholder.", file=sys.stderr)
        sys.exit(1)

    patched_source = source.replace("{{FLAG}}", args.flag)

    # Write patched source to a temp file, compile, clean up
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
                "-Os",            # optimize for size
                "-s",             # strip symbols
                "-static",        # static link to reduce DLL deps
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

    # Verify the output is a valid PE
    size = os.path.getsize(args.output)
    print("File size: " + str(size) + " bytes")

    print("")
    print("Verify the challenge:")
    print("  file " + args.output)
    print("    -> should report PE32+ executable for MS Windows")
    print("  strings " + args.output + " | grep CTF")
    print("    -> should reveal the flag plainly")
    print("  python3 -c \"import pefile; p=pefile.PE('" + args.output + "'); print(p.dump_info()[:500])\"")
    print("    -> shows PE structure")


if __name__ == "__main__":
    main()
