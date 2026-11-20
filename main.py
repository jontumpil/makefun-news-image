#!/usr/bin/env python3
"""news-image-20261120 entry: write the day's front page to /output.

The image (entry.png, committed beside this file) sums up the world
news of Friday 20 November 2026. It was composed by compose_image.py
from that day's reporting; this program's whole job is to place it at
/output/entry.png, byte for byte, on every run.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
OUTPUT_DIR = "/output"
OUTPUT = os.path.join(OUTPUT_DIR, "entry.png")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    shutil.copyfile(SOURCE, OUTPUT)
    size = os.path.getsize(OUTPUT)
    if size != os.path.getsize(SOURCE):
        raise SystemExit("copy failed: output size differs from source")
    with open(OUTPUT, "rb") as f:
        magic = f.read(8)
    if magic[:4] != b"\x89PNG" and magic[:2] != b"\xff\xd8":
        raise SystemExit("copy failed: output is not a PNG or JPEG")
    print(f"wrote {OUTPUT} ({size} bytes)")


if __name__ == "__main__":
    main()
