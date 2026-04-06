"""Generate minimal tab bar icons as simple colored circle PNGs."""
import struct, zlib, os

def make_png(width, height, color_rgb):
    """Create a simple solid-color PNG."""
    r, g, b = color_rgb

    def chunk(name, data):
        c = struct.pack('>I', len(data)) + name + data
        crc = zlib.crc32(name + data) & 0xffffffff
        return c + struct.pack('>I', crc)

    signature = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))

    raw = b''
    for y in range(height):
        row = b'\x00'  # filter type None
        for x in range(width):
            # Draw circle
            cx, cy = width / 2, height / 2
            radius = min(width, height) / 2 - 1
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if dist <= radius:
                row += bytes([r, g, b])
            else:
                row += bytes([0, 0, 0])  # transparent-ish (black bg)
        raw += row

    compressed = zlib.compress(raw)
    idat = chunk(b'IDAT', compressed)
    iend = chunk(b'IEND', b'')
    return signature + ihdr + idat + iend

out = "D:/求职全过程/MindBase/frontend/src/static"
os.makedirs(out, exist_ok=True)

icons = {
    "tab-home":    (0x99, 0x99, 0x99),
    "tab-home-active":    (0x63, 0x66, 0xf1),
    "tab-chat":    (0x99, 0x99, 0x99),
    "tab-chat-active":    (0x63, 0x66, 0xf1),
    "tab-search":  (0x99, 0x99, 0x99),
    "tab-search-active":  (0x63, 0x66, 0xf1),
    "tab-profile": (0x99, 0x99, 0x99),
    "tab-profile-active": (0x63, 0x66, 0xf1),
}

for name, color in icons.items():
    path = f"{out}/{name}.png"
    with open(path, "wb") as f:
        f.write(make_png(24, 24, color))
    print(f"Created {name}.png")

print("Done!")
