#!/usr/bin/env python3
"""Pack PNG favicons into a minimal multi-size .ico (PNG-compressed images)."""
from __future__ import annotations

import struct
import sys
from pathlib import Path


def png_to_ico(png_paths: list[Path], out_path: Path) -> None:
    chunks: list[bytes] = []
    for p in png_paths:
        data = p.read_bytes()
        if not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError(f"Not a PNG: {p}")
        w, h = struct.unpack(">II", data[16:24])
        # ICO stores combined height for PNG (height field is 2x for BMP; for PNG use actual)
        # For PNG-in-ICO, width/height bytes: 0 means 256; else 1-255
        wb = 0 if w >= 256 else w
        hb = 0 if h >= 256 else h
        chunks.append((wb, hb, data))

    # ICONDIR + ICONDIRENTRY per image
    num = len(chunks)
    header = struct.pack("<HHH", 0, 1, num)
    offset = 6 + num * 16
    entries = bytearray()
    image_blob = bytearray()
    for wb, hb, data in chunks:
        size = len(data)
        entries.extend(
            struct.pack(
                "<BBBBHHII",
                wb,
                hb,
                0,
                0,
                1,
                32,
                size,
                offset + len(image_blob),
            )
        )
        image_blob.extend(data)

    out_path.write_bytes(header + bytes(entries) + bytes(image_blob))


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    fav = root / "src" / "images" / "favicon"
    pngs = [fav / "favicon-16x16.png", fav / "favicon-32x32.png"]
    for p in pngs:
        if not p.exists():
            print(f"Missing {p}", file=sys.stderr)
            sys.exit(1)
    out = fav / "favicon.ico"
    png_to_ico(pngs, out)
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
