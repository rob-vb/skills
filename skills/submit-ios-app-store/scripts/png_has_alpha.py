#!/usr/bin/env python3
"""Exit 0 if the PNG has no alpha. Exit 1 otherwise or if the file is not a PNG."""
import struct
import sys

PNG_SIG = b"\x89PNG\r\n\x1a\n"
PNG_COLOR_TYPE_GREYSCALE_ALPHA = 4
PNG_COLOR_TYPE_TRUECOLOR_ALPHA = 6
PNG_ALPHA_COLOR_TYPES = (PNG_COLOR_TYPE_GREYSCALE_ALPHA, PNG_COLOR_TYPE_TRUECOLOR_ALPHA)


def png_has_alpha(data: bytes) -> bool:
    if data[:8] != PNG_SIG:
        return True
    pos = 8
    while pos + 12 <= len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        chunk_type = data[pos + 4 : pos + 8]
        chunk = data[pos + 8 : pos + 8 + length]
        if chunk_type == b"IHDR" and chunk[9] in PNG_ALPHA_COLOR_TYPES:
            return True
        if chunk_type == b"tRNS":
            return True
        pos += 12 + length
        if chunk_type == b"IEND":
            break
    return False


def main() -> int:
    data = open(sys.argv[1], "rb").read()
    return 1 if png_has_alpha(data) else 0


if __name__ == "__main__":
    raise SystemExit(main())
