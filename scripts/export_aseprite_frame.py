#!/usr/bin/env python3
import argparse
import struct
import zlib
from pathlib import Path

from PIL import Image


ASEPRITE_FILE_MAGIC = 0xA5E0
ASEPRITE_FRAME_MAGIC = 0xF1FA
LAYER_CHUNK = 0x2004
CEL_CHUNK = 0x2005
COMPRESSED_IMAGE_CEL = 2


def read_chunks(data):
    file_magic = struct.unpack_from("<H", data, 4)[0]
    if file_magic != ASEPRITE_FILE_MAGIC:
        raise ValueError("Not an Aseprite file")

    frames = struct.unpack_from("<H", data, 6)[0]
    width = struct.unpack_from("<H", data, 8)[0]
    height = struct.unpack_from("<H", data, 10)[0]
    depth = struct.unpack_from("<H", data, 12)[0]
    if frames != 1:
        raise ValueError("Only single-frame assets are supported")
    if depth != 32:
        raise ValueError("Only RGBA Aseprite assets are supported")

    offset = 128
    frame_bytes, frame_magic, old_chunk_count = struct.unpack_from("<IHH", data, offset)
    if frame_magic != ASEPRITE_FRAME_MAGIC:
        raise ValueError("Invalid frame header")
    new_chunk_count = struct.unpack_from("<I", data, offset + 12)[0]
    chunk_count = new_chunk_count or old_chunk_count
    chunk_offset = offset + 16
    chunks = []
    for _ in range(chunk_count):
        chunk_size, chunk_type = struct.unpack_from("<IH", data, chunk_offset)
        payload = data[chunk_offset + 6 : chunk_offset + chunk_size]
        chunks.append((chunk_type, payload))
        chunk_offset += chunk_size

    if chunk_offset != offset + frame_bytes:
        raise ValueError("Unexpected frame size while parsing chunks")

    return width, height, chunks


def export_first_frame(source_path, target_path):
    width, height, chunks = read_chunks(Path(source_path).read_bytes())
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    visible_layers = set()
    layer_index = 0
    for chunk_type, payload in chunks:
        if chunk_type != LAYER_CHUNK:
            continue
        flags = struct.unpack_from("<H", payload, 0)[0]
        layer_type = struct.unpack_from("<H", payload, 2)[0]
        if layer_type == 0 and flags & 0x1:
            visible_layers.add(layer_index)
        layer_index += 1

    for chunk_type, payload in chunks:
        if chunk_type != CEL_CHUNK:
            continue

        layer_index = struct.unpack_from("<H", payload, 0)[0]
        if visible_layers and layer_index not in visible_layers:
            continue

        x = struct.unpack_from("<h", payload, 2)[0]
        y = struct.unpack_from("<h", payload, 4)[0]
        cel_type = struct.unpack_from("<H", payload, 7)[0]
        if cel_type != COMPRESSED_IMAGE_CEL:
            raise ValueError("Only compressed image cel chunks are supported")

        cel_width = struct.unpack_from("<H", payload, 16)[0]
        cel_height = struct.unpack_from("<H", payload, 18)[0]
        raw_pixels = zlib.decompress(payload[20:])
        cel_image = Image.frombytes("RGBA", (cel_width, cel_height), raw_pixels)
        canvas.alpha_composite(cel_image, dest=(x, y))

    target = Path(target_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target)


def main():
    parser = argparse.ArgumentParser(description="Export a single-frame RGBA Aseprite file to PNG.")
    parser.add_argument("source")
    parser.add_argument("target")
    args = parser.parse_args()
    export_first_frame(args.source, args.target)


if __name__ == "__main__":
    main()
