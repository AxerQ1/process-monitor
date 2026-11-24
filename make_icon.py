import struct
import zlib

def make_ico(path, size=32):
    # Windows blue + white "PM" style simple icon
    bg = (0, 120, 215, 255)      # #0078d4
    fg = (255, 255, 255, 255)    # white

    pixels = []
    for y in range(size):
        for x in range(size):
            # Simple design: blue bg, white rounded rect border, white dot center
            if x < 4 or x >= size - 4 or y < 4 or y >= size - 4:
                pixels.append(fg)
            elif abs(x - size // 2) < 2 and abs(y - size // 2) < 2:
                pixels.append(fg)
            else:
                pixels.append(bg)

    # BMP header (BITMAPINFOHEADER, top-down = negative height)
    width = size
    height = -size
    row_size = ((width * 32 + 31) // 32) * 4
    image_size = row_size * size

    bmp_header = struct.pack("<IiiHHIIIIII",
        40,           # biSize
        width,        # biWidth
        height,       # biHeight (negative = top-down)
        1,            # biPlanes
        32,           # biBitCount
        0,            # biCompression (BI_RGB)
        image_size,   # biSizeImage
        0,            # biXPelsPerMeter
        0,            # biYPelsPerMeter
        0,            # biClrUsed
        0)            # biClrImportant

    # Pixel data (BGRA, padded to row_size)
    pixel_data = b""
    for y in range(size):
        row = b""
        for x in range(size):
            r, g, b, a = pixels[y * size + x]
            row += struct.pack("BBBB", b, g, r, a)
        padding = row_size - len(row)
        pixel_data += row + b"\x00" * padding

    # AND mask (all opaque = 0)
    and_mask = b"\x00" * ((width + 7) // 8 * size)

    # XOR mask = pixel data (BMP)
    xor_mask = bmp_header + pixel_data

    # ICO directory entry (16 bytes)
    entry = struct.pack("<BBBBHHII",
        size,       # bWidth (0 = 256)
        size,       # bHeight (0 = 256)
        0,          # bColorCount
        0,          # bReserved
        1,          # wColorPlanes
        32,         # wBitCount
        len(xor_mask) + len(and_mask),  # dwBytesInRes
        6 + 16      # dwImageOffset (after header + 1 entry)
    )

    # ICO header (6 bytes)
    ico_header = struct.pack("<HHH", 0, 1, 1)  # reserved, type=1, count=1

    with open(path, "wb") as f:
        f.write(ico_header)
        f.write(entry)
        f.write(and_mask)
        f.write(xor_mask)

make_ico("icon.ico")
print("icon.ico created")
