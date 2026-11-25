#!/usr/bin/env python3
"""One Line, One Laugh: Roast Your Fridge.

Writes the entry line — one roast of the fridge's ice maker, at most
200 characters — to entry.txt inside the output directory.

Run:  python3 main.py
Env:   MAKEFUN_OUTPUT_DIR  (default /output)

The program is deterministic and makes no network calls. It writes the
file atomically (temporary file in the same directory, then rename) and
reads it back to prove the bytes on disk are exactly the line.
"""

import os
import sys
import tempfile

LINE = (
    "My fridge's ice maker makes three cubes, sighs, and clocks out "
    "\u2014 the only appliance in my kitchen with a union rep "
    "and a pension plan."
)

MAX_CHARS = 200


def output_directory():
    """Where entry.txt goes: the harness variable, else /output."""
    chosen = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    return os.path.abspath(chosen)


def check_line(line):
    """Refuse anything that would fail the gate, before touching disk."""
    if not isinstance(line, str):
        raise ValueError("entry must be text")
    if not line.strip():
        raise ValueError("entry must not be only whitespace")
    if line != line.strip():
        raise ValueError("entry must not carry surrounding whitespace")
    if "\n" in line or "\r" in line:
        raise ValueError("entry must be a single line")
    if len(line) > MAX_CHARS:
        raise ValueError("entry is %d chars, over the 200 limit" % len(line))
    line.encode("utf-8")  # raises if the text is not valid UTF-8


def tidy(directory):
    """Clear stale files from the output directory; never remove the
    directory itself, which the grader mounts and owns."""
    os.makedirs(directory, exist_ok=True)
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        if os.path.isfile(path) or os.path.islink(path):
            os.unlink(path)


def publish(line, directory):
    """Write entry.txt atomically, then read it back and compare."""
    check_line(line)
    tidy(directory)
    tmp = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=directory,
        prefix=".entry-", suffix=".tmp", delete=False,
    )
    try:
        tmp.write(line)
        tmp.flush()
        os.fsync(tmp.fileno())
    finally:
        tmp.close()
    target = os.path.join(directory, "entry.txt")
    os.replace(tmp.name, target)
    dir_fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)
    with open(target, "r", encoding="utf-8") as handle:
        on_disk = handle.read()
    if on_disk != line:
        raise ValueError("read-back mismatch: disk holds different text")
    check_line(on_disk)
    return target


def main():
    try:
        target = publish(LINE, output_directory())
    except (OSError, ValueError) as problem:
        print("main.py: %s" % problem, file=sys.stderr)
        return 1
    print("wrote %s (%d chars)" % (target, len(LINE)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
