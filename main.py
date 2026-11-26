#!/usr/bin/env python3
"""Fridge Roast: one line roasting a smart fridge.

Writes exactly one roast line to /output/entry.txt (or $MAKEFUN_OUTPUT_DIR
when set, for local grading). Stdlib only, no network, deterministic.
"""

import os
import sys
from pathlib import Path

LINE = (
    "My fridge updated overnight and the crisper drawer now needs "
    "two-factor authentication \u2014 the lettuce is locked out of its own home."
)


def main() -> int:
    line = LINE
    if not 1 <= len(line) <= 200:
        print(f"line is {len(line)} chars, must be 1-200", file=sys.stderr)
        return 1
    if line != line.strip() or "\n" in line or "\r" in line:
        print("line must be a single line with no surrounding whitespace",
              file=sys.stderr)
        return 1
    out = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out.mkdir(parents=True, exist_ok=True)
    target = out / "entry.txt"
    target.write_text(line, encoding="utf-8")
    # Read back and confirm the file holds exactly the validated line.
    if target.read_text(encoding="utf-8") != line:
        print("entry.txt round-trip mismatch", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
