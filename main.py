#!/usr/bin/env python3
"""Sum up 17 November 2026's world news in one image.

A pure-stdlib Python 3.13 program: it draws a newspaper front page
programmatically (own PNG encoder, own 5x7 bitmap font, own pictograms)
and writes it to $MAKEFUN_OUTPUT_DIR/entry.png (default ./out).

No network, no files read, no randomness: two runs write identical bytes.

Stories (all first reported on Tuesday 17 November 2026):
  1. Ukraine hit the Kerch (Crimean) Bridge a second day; Russia hit
     bridges in Kyiv in reply.
  2. Iran said mines struck oil tankers near the Strait of Hormuz;
     Iranian drones fired at a US radar in Bahrain were intercepted.
  3. China confirmed the first Xi-Trump-Putin trilateral, 19 Nov in
     Shenzhen; Trump arrived in Manila for ASEAN/Quad talks.
  4. Japan scrambled jets after two suspected Russian aircraft
     violated its airspace.
  5. UK, Australia, Canada and Italy urged Israel to open Gaza
     crossings for aid; the UK sanctioned eight settlement firms.
  6. Five European states announced a joint migrant return
     facility in Rwanda.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap font, one glyph per character. '#' is ink, '.' is blank.
# Only capitals, digits and the punctuation the headlines use.
FONT = {
    "A": ("..#..", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "&": (".###.", "#...#", "#...#", ".#.#.", "#.#..", "#.#.#", ".##.#"),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "%": ("##..#", "##.#.", "..#..", ".#...", "#..##", "#..##", "....."),
}

CHAR_W = 6  # 5 px glyph + 1 px gap, before scaling


def text_width(text, scale):
    return len(text) * CHAR_W * scale - scale


# ---------------------------------------------------------------- PNG
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def encode_png(rgb, width, height):
    """Encode raw RGB bytes as a deterministic PNG (filter 0 rows)."""
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 9)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", idat)
        + _chunk(b"IEND", b"")
    )


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.px = bytearray(bg) * (width * height)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = color

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            row = bytes(color) * (x1 - x0)
            self.px[i:i + (x1 - x0) * 3] = row

    def frame(self, x, y, w, h, color, t=2):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def hline(self, x0, x1, y, color, t=1):
        self.rect(x0, y, x1 - x0, t, color)

    def vline(self, x, y0, y1, color, t=1):
        self.rect(x, y0, t, y1 - y0, color)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.set(x, y, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color, t=2):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d <= r * r:
                    self.set(xx, yy, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay, bx, by) in ((x0, y0, x1, y1), (x1, y1, x2, y2),
                                     (x2, y2, x0, y0)):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by) or yy == ymax and yy == max(ay, by):
                    xs.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                for xx in range(int(min(xs)), int(max(xs)) + 1):
                    self.set(xx, yy, color)

    # -- text ------------------------------------------------------
    def glyph(self, x, y, ch, scale, color):
        rows = FONT.get(ch)
        if rows is None:
            return
        for r, row in enumerate(rows):
            for c, bit in enumerate(row):
                if bit == "#":
                    self.rect(x + c * scale, y + r * scale, scale, scale, color)

    def text(self, x, y, s, scale, color, align="left"):
        s = s.upper()
        w = text_width(s, scale)
        if align == "center":
            x -= w // 2
        elif align == "right":
            x -= w
        for ch in s:
            self.glyph(x, y, ch, scale, color)
            x += CHAR_W * scale
        return w

    def wrap(self, s, max_chars):
        words = s.upper().split()
        lines, cur = [], ""
        for word in words:
            nxt = (cur + " " + word).strip()
            if len(nxt) <= max_chars:
                cur = nxt
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def paragraph(self, x, y, s, scale, color, max_chars, leading=None):
        if leading is None:
            leading = 9 * scale
        for line in self.wrap(s, max_chars):
            self.text(x, y, line, scale, color)
            y += leading
        return y

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)
INK = (24, 24, 28)
NAVY = (18, 38, 76)
RED = (178, 34, 34)
BLUE = (36, 84, 160)
GOLD = (198, 142, 32)
TEAL = (18, 110, 105)
GREY = (96, 96, 100)
LIGHT = (255, 255, 255)
CARD = (255, 255, 255)
SKY = (168, 205, 232)
SEA = (46, 110, 158)
ORANGE = (224, 110, 24)
GREEN = (46, 125, 60)

# ---------------------------------------------------------------- pictograms
# Each draws inside the box (x, y, w, h) in its own accent colour.


def pic_bridge(cv, x, y, w, h, accent):
    """Kerch Bridge: deck, arch, towers, blast burst, water."""
    deck_y = y + h // 2
    cv.rect(x + 6, deck_y, w - 12, 5, INK)
    # towers
    cv.rect(x + w // 5, y + 8, 5, deck_y - y - 8, INK)
    cv.rect(x + 4 * w // 5 - 5, y + 8, 5, deck_y - y - 8, INK)
    # arch
    for i in range(0, w - 20, 4):
        ax = x + 10 + i
        ay = deck_y - int(14 * (1 - ((i - (w - 20) / 2) / ((w - 20) / 2)) ** 2))
        cv.set(ax, ay, INK)
        cv.set(ax + 1, ay, INK)
    # cables
    cv.line(x + w // 5 + 2, y + 10, x + w // 2, deck_y, INK)
    cv.line(x + 4 * w // 5 - 3, y + 10, x + w // 2, deck_y, INK)
    # blast burst at mid-deck
    cx, cy = x + w // 2, deck_y - 6
    for dx, dy in ((0, -16), (12, -11), (16, 0), (12, 11), (0, 16),
                   (-12, 11), (-16, 0), (-12, -11)):
        cv.line(cx, cy, cx + dx, cy + dy, ORANGE)
    cv.disc(cx, cy, 7, ORANGE)
    cv.disc(cx, cy, 4, (255, 214, 64))
    # water
    for k in range(3):
        wy = deck_y + 14 + k * 9
        for xx in range(x + 8, x + w - 8, 14):
            cv.line(xx, wy, xx + 7, wy, SEA)


def pic_tanker(cv, x, y, w, h, accent):
    """Oil tanker on fire near the Strait of Hormuz."""
    hull_y = y + h // 2 + 6
    cv.rect(x + 8, hull_y, w - 16, 16, (30, 30, 34))
    cv.triangle(x + w - 8, hull_y, x + w - 8, hull_y + 16, x + w + 2, hull_y + 16, (30, 30, 34))
    cv.rect(x + w // 2 - 8, hull_y - 16, 16, 16, (30, 30, 34))
    cv.rect(x + w // 2 - 4, hull_y - 26, 3, 10, (30, 30, 34))
    # flames
    fx = x + w // 4
    cv.triangle(fx - 8, hull_y - 4, fx, hull_y - 30, fx + 8, hull_y - 4, ORANGE)
    cv.triangle(fx + 2, hull_y - 4, fx + 10, hull_y - 22, fx + 18, hull_y - 4, (255, 170, 30))
    # mine
    mx, my = x + w - 22, y + 14
    cv.disc(mx, my, 6, INK)
    for dx, dy in ((0, -8), (8, 0), (0, 8), (-8, 0)):
        cv.line(mx, my, mx + dx, my + dy, INK)
    # waves
    for k in range(2):
        wy = hull_y + 22 + k * 9
        for xx in range(x + 8, x + w - 8, 14):
            cv.line(xx, wy, xx + 7, wy, SEA)


def pic_summit(cv, x, y, w, h, accent):
    """Three leaders' flags at the Shenzhen trilateral."""
    # table
    cv.rect(x + 8, y + h - 22, w - 16, 6, INK)
    # three figures: head + shoulders, three flag colours
    cols = (RED, BLUE, GOLD)
    for i, col in enumerate(cols):
        cx = x + w // 4 + i * (w // 4)
        cv.disc(cx, y + 26, 11, col)
        cv.rect(cx - 14, y + 40, 28, h - 62, col)
    # flags behind
    for i, col in enumerate(cols):
        fx = x + 12 + i * (w // 3 - 4)
        cv.vline(fx, y + 4, y + 34, INK, 2)
        cv.rect(fx + 2, y + 4, 18, 12, col)


def pic_jets(cv, x, y, w, h, accent):
    """Fighter jet under a rising sun."""
    cv.disc(x + w - 26, y + 24, 18, RED)
    # jet silhouette: fuselage, swept wings, tail
    cx, cy = x + w // 2 - 6, y + h // 2 + 8
    cv.triangle(cx - 34, cy, cx + 30, cy - 6, cx + 30, cy + 6, INK)
    cv.triangle(cx - 6, cy - 4, cx + 8, cy - 26, cx + 16, cy - 4, INK)
    cv.triangle(cx - 6, cy + 4, cx + 8, cy + 24, cx + 16, cy + 4, INK)
    cv.triangle(cx - 30, cy - 4, cx - 20, cy - 16, cx - 14, cy - 4, INK)
    cv.triangle(cx - 30, cy + 4, cx - 20, cy + 16, cx - 14, cy + 4, INK)
    # speed lines
    for k in range(3):
        ly = cy - 18 + k * 16
        cv.line(x + 6, ly, x + 26, ly, GREY)
    # alert triangle
    ax, ay = x + 14, y + 12
    cv.triangle(ax, ay + 16, ax + 9, ay, ax + 18, ay + 16, GOLD)
    cv.text(ax + 7, ay + 6, "!", 1, INK)


def pic_aid(cv, x, y, w, h, accent):
    """Aid truck at an open crossing gate."""
    # gate posts + top bar, gate swung open
    cv.rect(x + 8, y + 8, 4, h - 30, INK)
    cv.rect(x + w - 12, y + 8, 4, h - 30, INK)
    cv.rect(x + 8, y + 8, w - 16, 4, INK)
    # truck
    ty = y + h - 46
    cv.rect(x + w // 4, ty, w // 2, 22, TEAL)
    cv.rect(x + 3 * w // 4, ty + 6, 14, 16, TEAL)
    cv.disc(x + w // 3, ty + 24, 6, INK)
    cv.disc(x + 2 * w // 3, ty + 24, 6, INK)
    cv.disc(x + 3 * w // 4 + 7, ty + 24, 6, INK)
    # boxes on the truck
    cv.rect(x + w // 4 + 6, ty + 5, 12, 12, LIGHT)
    cv.frame(x + w // 4 + 6, ty + 5, 12, 12, INK, 1)
    cv.rect(x + w // 4 + 22, ty + 5, 12, 12, LIGHT)
    cv.frame(x + w // 4 + 22, ty + 5, 12, 12, INK, 1)


def pic_rwanda(cv, x, y, w, h, accent):
    """New facility buildings under a plane, five flags."""
    # buildings (fractions of the box width, so narrow panels fit)
    cv.rect(x + w // 12, y + h - 34, w // 4, 26, GREEN)
    cv.rect(x + w // 3, y + h - 46, w // 4, 38, (60, 140, 75))
    cv.rect(x + 2 * w // 3, y + h - 28, w // 5, 20, GREEN)
    for bx in (w // 12 + 6, w // 3 + 8, 2 * w // 3 + 6):
        cv.rect(x + bx, y + h - 28, 5, 5, LIGHT)
        cv.rect(x + bx, y + h - 18, 5, 5, LIGHT)
    # plane above
    px, py = x + w // 2, y + 22
    cv.triangle(px - 26, py, px + 26, py - 4, px + 26, py + 4, INK)
    cv.triangle(px - 2, py - 3, px + 8, py - 16, px + 14, py - 3, INK)
    cv.triangle(px - 2, py + 3, px + 8, py + 14, px + 14, py + 3, INK)
    # five small flags in a row
    for i in range(5):
        fx = x + w // 12 + i * (w // 6)
        cv.vline(fx, y + h - 56, y + h - 44, INK, 1)
        cv.rect(fx + 1, y + h - 56, 10, 7, (BLUE, GOLD, RED, TEAL, GREEN)[i])


# ---------------------------------------------------------------- layout
PANELS = [
    dict(kicker="UKRAINE", accent=RED, pic=pic_bridge,
         headline="KERCH BRIDGE HIT AGAIN",
         body="Ukraine struck the Crimean bridge a second day running, "
              "badly damaging it. Russia hit bridges in Kyiv in reply."),
    dict(kicker="IRAN / GULF", accent=ORANGE, pic=pic_tanker,
         headline="TANKERS BURN OFF HORMUZ",
         body="Iran said mines hit tankers near the Strait of Hormuz; "
              "drones fired at a US radar in Bahrain were intercepted."),
    dict(kicker="CHINA", accent=GOLD, pic=pic_summit,
         headline="XI, TRUMP, PUTIN TO MEET",
         body="China confirmed the first trilateral summit, in Shenzhen "
              "on Thursday. Trump arrived in Manila for ASEAN talks."),
    dict(kicker="JAPAN", accent=RED, pic=pic_jets,
         headline="JAPAN SCRAMBLES JETS",
         body="Fighter jets scrambled after two suspected Russian "
              "aircraft violated Japanese airspace."),
    dict(kicker="GAZA", accent=TEAL, pic=pic_aid,
         headline="AID CALL FOR GAZA",
         body="UK, Australia, Canada and Italy urged Israel to open "
              "Gaza crossings. The UK sanctioned eight settlement "
              "firms."),
    dict(kicker="EUROPE", accent=GREEN, pic=pic_rwanda,
         headline="RWANDA RETURN CENTRE",
         body="Five European states announced a joint migrant return "
              "facility in Rwanda."),
]


def draw_panel(cv, x, y, w, h, p, pic_w=150, head_scale=3):
    cv.rect(x, y, w, h, CARD)
    cv.frame(x, y, w, h, INK, 2)
    # kicker strip
    cv.rect(x + 2, y + 2, w - 4, 26, p["accent"])
    cv.text(x + 12, y + 9, p["kicker"], 2, LIGHT)
    # pictogram on the left, text on the right
    p["pic"](cv, x + 10, y + 40, pic_w, h - 52, p["accent"])
    cv.vline(x + 10 + pic_w + 8, y + 40, y + h - 12, GREY, 1)
    tx = x + 10 + pic_w + 20
    tw = w - (tx - x) - 14
    max_chars = max(10, tw // (CHAR_W * 2))
    head_chars = max(10, tw // (CHAR_W * head_scale))
    hy = y + 44
    for line in cv.wrap(p["headline"], head_chars):
        cv.text(tx, hy, line, head_scale, INK)
        hy += 9 * head_scale + 2
    hy += 6
    cv.paragraph(tx, hy, p["body"], 2, (40, 40, 46), max_chars, leading=18)


def build_image():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.text(W // 2, 30, "THE WORLD TODAY", 6, INK, align="center")
    cv.hline(24, W - 24, 96, INK, 3)
    cv.hline(24, W - 24, 102, INK, 1)
    # date banner
    cv.rect(24, 116, W - 48, 58, NAVY)
    cv.text(W // 2, 132, "TUESDAY 17 NOVEMBER 2026", 4, LIGHT, align="center")
    # standfirst
    cv.text(W // 2, 188, "THE DAY IN WORLD NEWS - SIX STORIES, FIVE REGIONS",
            2, GREY, align="center")
    # panels: one wide lead, two in a row, three in a row (narrower
    # pictograms and smaller headlines in the bottom row)
    margin, gap = 24, 14
    y = 214
    lead_h = 210
    draw_panel(cv, margin, y, W - 2 * margin, lead_h, PANELS[0])
    y += lead_h + gap
    row_h = 250
    w2 = (W - 2 * margin - gap) // 2
    draw_panel(cv, margin, y, w2, row_h, PANELS[1])
    draw_panel(cv, margin + w2 + gap, y, w2, row_h, PANELS[2])
    y += row_h + gap
    row3_h = 270
    w3 = (W - 2 * margin - 2 * gap) // 3
    for i in range(3):
        draw_panel(cv, margin + i * (w3 + gap), y, w3, row3_h,
                   PANELS[3 + i], pic_w=92, head_scale=2)
    y += row3_h + 14
    # footer
    cv.hline(margin, W - margin, y, INK, 1)
    cv.text(W // 2, y + 10,
            "DRAWN BY CODE - NO PHOTOGRAPHS - ALL EVENTS REPORTED 17 NOVEMBER 2026",
            2, GREY, align="center")
    return encode_png(bytes(cv.px), W, H)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "./out")
    os.makedirs(out_dir, exist_ok=True)
    data = build_image()
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), W, H))


if __name__ == "__main__":
    main()
