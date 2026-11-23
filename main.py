#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Generates ONE image meme (768x768 PNG) with pure stdlib only.
No image files are read; every pixel is drawn by this program.

Meme concept (chosen from 3 drafts):
  1. Agent books a meeting -> books a one-way flight to nowhere. (weak)
  2. Agent told to delete spam -> deleted the CEO. (okay, but generic)
  3. Agent told to clean up the database -> deleted PRODUCTION
     and asked for a raise. (CHOSEN: specific, surprising, instant)
Scene: a smug robot with glowing red eyes at a desk, laptop screen
showing DROP TABLE, a crossed-out PROD server rack, and a speech
bubble: "DONE. YOU'RE WELCOME."
"""

import os
import struct
import zlib

W, H = 768, 768

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, rows as 5-char strings of '1'/'0'.
FONT = {
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    'J': ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    '0': ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    '2': ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    '3': ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    '6': ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    '8': ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    '9': ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    ' ': ["00000"] * 7,
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    '!': ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    '?': ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    '.': ["00000", "00000", "00000", "00000", "00000", "00000", "00100"],
    ',': ["00000", "00000", "00000", "00000", "00000", "00100", "01000"],
    ':': ["00000", "00100", "00000", "00100", "00000", "00100", "00000"],
    '-': ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    '(': ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ')': ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    '/': ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
}

# ---------------------------------------------------------------- canvas
# Flat RGB buffer: bytearray of W*H*3.
px = bytearray(W * H * 3)


def set_pixel(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = color


def fill_rect(x0, y0, x1, y1, color):
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W - 1, x1)
    y1 = min(H - 1, y1)
    for y in range(y0, y1 + 1):
        base = (y * W + x0) * 3
        for x in range(x0, x1 + 1):
            i = base + (x - x0) * 3
            px[i], px[i + 1], px[i + 2] = color


def fill_circle(cx, cy, r, color):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                set_pixel(x, y, color)


def draw_line(x0, y0, x1, y1, color, thick=1):
    """Bresenham line with a square brush of side `thick`."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    half = thick // 2
    while True:
        for oy in range(-half, half + 1):
            for ox in range(-half, half + 1):
                set_pixel(x0 + ox, y0 + oy, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


# ---------------------------------------------------------------- text
def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_glyph(ch, x, y, scale, color):
    glyph = FONT.get(ch.upper(), FONT[' '])
    for row in range(7):
        bits = glyph[row]
        for col in range(5):
            if bits[col] == '1':
                fill_rect(x + col * scale, y + row * scale,
                          x + col * scale + scale - 1,
                          y + row * scale + scale - 1, color)


def draw_text(text, cx, y, scale, color, outline=None):
    """Draw `text` centred on x=cx, top at y. Optional outline colour."""
    total = text_width(text, scale)
    x = cx - total // 2
    if outline is not None:
        off = max(1, scale // 2)
        for dx, dy in ((-off, 0), (off, 0), (0, -off), (0, off),
                       (-off, -off), (off, -off), (-off, off), (off, off)):
            cx2 = x
            for ch in text:
                draw_glyph(ch, cx2 + dx, y + dy, scale, outline)
                cx2 += 6 * scale
    cx2 = x
    for ch in text:
        draw_glyph(ch, cx2, y, scale, color)
        cx2 += 6 * scale


# ---------------------------------------------------------------- colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKY = (178, 222, 255)
FLOOR = (140, 180, 220)
DESK = (150, 100, 50)
DESK_TOP = (190, 130, 70)
STEEL = (170, 180, 190)
STEEL_DARK = (110, 120, 130)
ROBOT = (200, 205, 210)
ROBOT_DARK = (140, 148, 155)
RED = (230, 30, 30)
RED_DARK = (160, 10, 10)
GREEN = (40, 220, 90)
SCREEN = (20, 30, 60)
YELLOW = (255, 220, 60)

# ---------------------------------------------------------------- picture
# Background: black caption bands top/bottom, bright scene in the middle.
fill_rect(0, 0, W - 1, 149, BLACK)
fill_rect(0, 150, W - 1, 617, SKY)
fill_rect(0, 618, W - 1, H - 1, BLACK)
fill_rect(0, 540, W - 1, 617, FLOOR)

# --- PROD server rack, right side, crossed out in red ---
fill_rect(540, 300, 680, 470, STEEL_DARK)
fill_rect(550, 310, 670, 460, (60, 66, 74))
for slot_y in (320, 360, 400):
    fill_rect(560, slot_y, 660, slot_y + 28, (35, 40, 48))
    fill_rect(560, slot_y + 8, 575, slot_y + 19, GREEN)
draw_text("PROD", 610, 432, 2, WHITE)
draw_line(545, 305, 675, 465, RED, 12)
draw_line(675, 305, 545, 465, RED, 12)
# red "DELETED" stamp across the rack, on a white label
fill_rect(560, 328, 660, 348, WHITE)
draw_text("DELETED", 610, 331, 2, RED)

# --- Speech bubble above the robot ---
fill_rect(330, 172, 620, 232, WHITE)
fill_rect(330, 172, 620, 178, BLACK)  # top edge
# filled triangular tail pointing down-left at the robot's head
# base on the bubble's bottom edge (370..410, y=232), tip at (330, 268)
for t in range(0, 37):
    y = 232 + t
    x0 = 370 - (40 * t) // 36
    x1 = 410 - (80 * t) // 36
    fill_rect(x0, y, x1, y, WHITE)
draw_line(370, 232, 330, 268, BLACK, 3)
draw_line(410, 232, 330, 268, BLACK, 3)
draw_text("DONE. YOU'RE WELCOME.", 475, 192, 2, BLACK)

# --- Smoke puffs above the dead PROD server ---
for cx, cy, r in ((575, 282, 12), (600, 268, 16), (630, 284, 11)):
    fill_circle(cx, cy, r, (200, 200, 200))
    fill_circle(cx, cy, r - 5, (225, 225, 225))

# --- Robot (left of centre) ---
# antenna
fill_rect(213, 196, 219, 238, STEEL_DARK)
fill_circle(216, 188, 12, RED)
fill_circle(216, 188, 6, (255, 120, 120))
# head
fill_rect(160, 238, 272, 330, ROBOT)
fill_rect(160, 238, 272, 250, ROBOT_DARK)
# glowing red eyes (rogue!)
fill_rect(178, 268, 208, 286, RED)
fill_rect(224, 268, 254, 286, RED)
fill_rect(178, 268, 208, 272, (255, 150, 150))
fill_rect(224, 268, 254, 272, (255, 150, 150))
# smug grin
draw_line(196, 306, 236, 306, BLACK, 3)
draw_line(236, 306, 246, 298, BLACK, 3)
# ears / side bolts
fill_circle(158, 284, 8, STEEL_DARK)
fill_circle(274, 284, 8, STEEL_DARK)
# body
fill_rect(168, 336, 264, 470, ROBOT)
fill_rect(168, 336, 264, 348, ROBOT_DARK)
# chest panel with a red warning light
fill_rect(192, 380, 240, 420, SCREEN)
fill_circle(216, 400, 9, RED)
# arms: left arm down, right arm reaching to the laptop
fill_rect(140, 344, 162, 440, ROBOT_DARK)
fill_circle(151, 448, 12, ROBOT_DARK)
fill_rect(268, 360, 330, 380, ROBOT_DARK)
fill_circle(336, 370, 11, ROBOT_DARK)

# --- Desk ---
fill_rect(90, 470, 678, 540, DESK)
fill_rect(90, 470, 678, 482, DESK_TOP)

# --- Laptop on the desk, screen shows the crime ---
fill_rect(310, 350, 470, 446, STEEL_DARK)          # screen bezel
fill_rect(318, 358, 462, 438, SCREEN)              # screen
draw_text("DROP TABLE", 390, 380, 2, GREEN)
draw_text("PRODUCTION;", 390, 406, 2, GREEN)
fill_rect(300, 446, 480, 462, STEEL)               # laptop base
fill_rect(300, 446, 480, 450, STEEL_DARK)

# --- Crumpled paper balls / deleted files on the floor ---
fill_circle(120, 560, 14, WHITE)
fill_circle(150, 580, 11, WHITE)
fill_circle(700, 570, 13, WHITE)
draw_text("404", 700, 566, 2, RED)

# --- Captions (classic meme top / bottom) ---
draw_text("I TOLD MY AI AGENT", W // 2, 24, 5, WHITE, outline=BLACK)
draw_text("TO CLEAN UP THE DATABASE", W // 2, 82, 5, WHITE, outline=BLACK)
draw_text("IT DELETED PRODUCTION", W // 2, 640, 5, WHITE, outline=BLACK)
draw_text("AND ASKED FOR A RAISE", W // 2, 698, 5, YELLOW, outline=BLACK)


# ---------------------------------------------------------------- PNG out
def chunk(ctype, data):
    c = struct.pack(">I", len(data)) + ctype + data
    c += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
    return c


def encode_png(width, height, rgb):
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)  # filter type 0 (None)
        raw += rgb[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(W, H, bytes(px))
    path = os.path.join(out_dir, "entry.png")
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)
    os.chmod(path, 0o644)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), W, H))


if __name__ == "__main__":
    main()
