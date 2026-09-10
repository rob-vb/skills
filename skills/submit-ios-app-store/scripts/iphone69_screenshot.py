#!/usr/bin/env python3
"""Exit 0 if the image is an accepted 6.9-inch App Store screenshot with no alpha."""
import struct
import sys

IPHONE_6_9_PORTRAIT = {(1320, 2868), (1290, 2796), (1260, 2736)}
JPEG_SOF = (0xC0, 0xC1, 0xC2)
PNG_SIG = b"\x89PNG\r\n\x1a\n"
PNG_COLOR_TYPE_GREYSCALE_ALPHA = 4
PNG_COLOR_TYPE_TRUECOLOR_ALPHA = 6
PNG_ALPHA_COLOR_TYPES = (PNG_COLOR_TYPE_GREYSCALE_ALPHA, PNG_COLOR_TYPE_TRUECOLOR_ALPHA)


def jpeg_size(data: bytes) -> tuple[int, int] | None:
    i = 0
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in JPEG_SOF:
            height = struct.unpack(">H", data[i + 5 : i + 7])[0]
            width = struct.unpack(">H", data[i + 7 : i + 9])[0]
            return width, height
        if marker == 0xD8 or marker == 0x01 or (0xD0 <= marker <= 0xD9):
            i += 2
            continue
        seglen = struct.unpack(">H", data[i + 2 : i + 4])[0]
        i += 2 + seglen
    return None


def png_size_and_alpha(data: bytes) -> tuple[tuple[int, int] | None, bool]:
    if data[:8] != PNG_SIG:
        return None, True
    width, height = struct.unpack(">II", data[16:24])
    color_type = data[25]
    return (width, height), color_type in PNG_ALPHA_COLOR_TYPES


def main() -> int:
    path = sys.argv[1]
    data = open(path, "rb").read()
    lower = path.lower()
    if lower.endswith((".jpg", ".jpeg")):
        size = jpeg_size(data)
        return 0 if size in IPHONE_6_9_PORTRAIT else 1
    size, has_alpha = png_size_and_alpha(data)
    if has_alpha or size not in IPHONE_6_9_PORTRAIT:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
