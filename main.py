#!/usr/bin/env python3
"""news-image-20261121 — one image summing up the world news of
Saturday 21 November 2026.

Pure Python 3 standard library only. No network, no files read at run
time: every pixel is drawn in code, deterministically, so two runs
write byte-identical PNGs.

Layout (1024 x 1024, newspaper front page — new direction per AT,
21 Nov 2026, adapted from the news.make.fun 19 Nov front page, NOT a
pixel copy: one big HERO story on top, then a numbered grid of story
cards, each with a region tag and a source line; the dark visual
identity of the 20 Nov entry is kept — cream paper outside, dark navy
hero panel, each story with its own accent colour):
  masthead  : THE WORLD IN ONE DAY / SATURDAY 21 NOVEMBER 2026
  hero      : Kyiv/Poland — Russia's biggest strike, missiles land
              in Poland (dark navy panel, illustrated night sky)
  grid 2x3  : New York markets rout | Brussels UK-EU reset |
              Antalya COP31 overtime | Riyadh missile defence |
              Gen Z protests in 25 countries | GTA VI $3.79bn launch
  footer    : verification line

Each card's top band is a small hand-drawn illustration in the
story's colours (chart, EU stars, sun over waves, defence dome,
crowd, neon skyline) — a colour-block panel, not a photo.

All seven stories were verified against Reuters / AP / BBC / CNN /
WSJ and others on 21 November 2026 (see NEWS.md in this repository).
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (17, 17, 17)
NAVY = (20, 38, 74)
NAVY_D = (12, 24, 48)
RED = (176, 42, 30)
GOLD = (201, 162, 39)
SKY = (58, 110, 165)
SKY_L = (147, 190, 224)
SEA = (28, 68, 110)
SEA_D = (16, 44, 76)
SAND = (214, 196, 150)
GREY = (90, 90, 88)
WHITE = (255, 255, 255)
GREEN = (38, 110, 66)
TEAL = (18, 96, 96)
SPACE = (8, 10, 26)
CREAM2 = (232, 224, 200)
DUSK = (250, 226, 190)
BOARD = (16, 28, 20)

# ---------------------------------------------------------------- 5x7 font
# 7 rows of 5 pixels each; "#" = on. Copy is rendered in capitals only.
FONT = {
    "A": (" .###. ", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
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
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".....", "..#..", ".#..."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ":": (".....", "..#..", ".....", ".....", ".....", "..#..", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "=": (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "$": ("..#..", ".####", "#.#.#", ".#.#.", "..##.", ".#.#.", "####."),
}
FONT = {k: tuple(r.strip()[:5].ljust(5, ".") for r in v)
        for k, v in FONT.items()}


def _chunk(ctype, data):
    out = struct.pack(">I", len(data)) + ctype + data
    return out + struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)


def write_png(path, rgb, w, h):
    """Deterministic PNG: filter-0 rows, zlib level 9, fixed chunk order."""
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += rgb[y * w * 3:(y + 1) * w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for _ in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def hline(self, x, y, w, c, t=1):
        for k in range(t):
            self.rect(x, y + k, w, 1, c)

    def vline(self, x, y, h, c, t=1):
        for k in range(t):
            self.rect(x + k, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx + dy, x0, y0
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x + a, y + b, c)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, t=2):
        for k in range(t):
            rr = r - k
            for yy in range(cy - rr, cy + rr + 1):
                for xx in range(cx - rr, cx + rr + 1):
                    d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                    if rr * rr - 2 * rr <= d2 <= rr * rr:
                        self.set(xx, yy, c)

    def tri(self, pts, c):
        (x0, y0), (x1, y1), (x2, y2) = pts
        for yy in range(min(y0, y1, y2), max(y0, y1, y2) + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy <= max(ay, by):
                    xs.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                self.rect(xa, yy, xb - xa + 1, 1, c)

    def starburst(self, cx, cy, r0, r1, n, c):
        pts = []
        for k in range(2 * n):
            r = r1 if k % 2 == 0 else r0
            a = math.pi * k / n - math.pi / 2
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        for k in range(len(pts)):
            self.tri((pts[k], pts[(k + 1) % len(pts)], (cx, cy)), c)

    # ------------------------------------------------------------ text
    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def draw_text(self, x, y, s, scale, c):
        cx = x
        for ch in s.upper():
            g = FONT.get(ch, FONT[" "])
            for ry in range(7):
                row = g[ry]
                for rx in range(5):
                    if row[rx] == "#":
                        self.rect(cx + rx * scale, y + ry * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, scale, c):
        return self.draw_text(cx - self.text_w(s, scale) // 2, y, s, scale, c)

    def wrap(self, s, scale, maxw):
        lines, cur = [], ""
        for wd in s.upper().split():
            trial = (cur + " " + wd).strip()
            if self.text_w(trial, scale) <= maxw:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

# ---------------------------------------------------------------- palette
# (base palette PAPER/INK/NAVY/NAVY_D/RED/GOLD/SKY/SKY_L/SEA/SEA_D/SAND/
#  GREY/WHITE/GREEN/TEAL/SPACE/CREAM2/DUSK/BOARD comes from the head)
BG = (238, 230, 210)     # page background, classic pale cream (~5%)
CARD = (250, 245, 232)    # story card + header background, lighter cream
INK = (16, 24, 40)        # headline / title ink on cream
FACT_D = (70, 72, 84)     # fact text on cream
CARD_LINE = (160, 150, 125)  # warm grey card borders
DATE_RED = (168, 44, 32)  # masthead date, classic newspaper red
OCEAN = (16, 42, 76)
LAND = (94, 138, 122)     # muted sage-teal continents
GRAT = (38, 74, 112)      # graticule lines
EQUATOR = (70, 110, 150)
OCEAN_LABEL = (110, 140, 175)
MUTED = (150, 168, 192)   # secondary text on dark (map area only)
FACT_C = (214, 222, 232)  # fact text on dark (unused on cream cards)
LAND_EDGE = (150, 190, 172)  # coastline stroke
HALO = (150, 120, 30)     # marker halo

# Each story carries its own accent colour: the number badge, the
# illustration band, the place kicker, the stat line and the card's
# top rule all use the same colour, so a reader can match a card to
# its story at a glance.
ACCENT = {
    1: (201, 162, 39),   # gold     - Kyiv/Poland (hero)
    2: (224, 82, 66),    # red      - New York (markets rout)
    3: (90, 165, 225),   # sky blue - Brussels (UK-EU reset)
    4: (232, 142, 44),   # orange   - Antalya (COP31)
    5: (64, 178, 168),   # teal     - Riyadh (missile defence)
    6: (168, 130, 220),  # violet   - Europe (Gen Z protests)
    7: (232, 64, 160),   # magenta  - Los Angeles (GTA VI)
}

# Darker versions of the accents, for text and rules on cream: the
# bright accents are too light to read on a pale background.
ACCENT_DARK = {
    1: (150, 115, 20),   # dark gold
    2: (175, 45, 35),    # brick red
    3: (35, 105, 165),   # deep blue
    4: (185, 105, 15),   # dark amber
    5: (20, 110, 100),   # deep teal
    6: (115, 80, 175),   # deep violet
    7: (180, 40, 120),   # deep magenta
}

# Dark tinted backgrounds for the illustration band on top of each
# card (and the hero panel): the accent colour pulled down to navy.
BAND = {
    1: (12, 24, 48),     # hero panel: deep navy
    2: (74, 18, 14),     # dark red
    3: (16, 44, 74),     # dark blue
    4: (74, 40, 12),     # dark amber
    5: (10, 44, 44),     # dark teal
    6: (44, 28, 74),     # dark violet
    7: (74, 16, 52),     # dark magenta
}


def halo_of(color):
    return tuple(v * 11 // 20 for v in color)


def newsprint(c, x, y, w, h, line_c):
    """Ghosted newspaper background: column dividers + rows of short
    horizontal 'text' lines, drawn in a colour only just above the
    background (the 80-90% blur: barely visible, never fights the real
    copy drawn on top of it). Fully deterministic."""
    cols = 4 if w > 500 else 2
    for k in range(1, cols):
        c.vline(x + k * w // cols, y + 6, h - 12, line_c, 1)
    row = 0
    yy = y + 8
    while yy + 2 <= y + h - 6:
        for k in range(cols):
            cx0 = x + k * w // cols + 6
            cx1 = x + (k + 1) * w // cols - 6
            frac = 0.55 + 0.4 * ((row * 7 + k * 13) % 10) / 10.0
            lw = int((cx1 - cx0) * frac)
            if row == 0:
                c.hline(cx0, yy, int((cx1 - cx0) * 0.7), line_c, 4)
            elif lw > 8:
                c.hline(cx0, yy, lw, line_c, 2)
        yy += 6
        row += 1

# ------------------------------------------------------------ type tools
# The base 5x7 bitmap font only ships one weight and no tracking, so the
# display treatments below are built on top of it: bold = a second pass
# offset by 1px (thickens strokes at scale >= 2), tracking = extra px
# between glyphs. Type scale: 5 masthead date, 3 masthead title, 2 bold
# headlines/kickers/stats, 2 facts, 1 tracked labels.


def tw(s, scale, tracking=0):
    return len(s) * 6 * scale - scale + max(0, len(s) - 1) * tracking


def draw_text2(c, x, y, s, scale, color, tracking=0, bold=False):
    cx = x
    for ch in s.upper():
        g = FONT.get(ch, FONT[" "])
        for ry in range(7):
            row = g[ry]
            for rx in range(5):
                if row[rx] == "#":
                    c.rect(cx + rx * scale, y + ry * scale, scale, scale,
                           color)
                    if bold:
                        c.rect(cx + rx * scale + 1, y + ry * scale,
                               scale, scale, color)
        cx += 6 * scale + tracking
    return cx


def text_center2(c, cx, y, s, scale, color, tracking=0, bold=False):
    return draw_text2(c, cx - tw(s, scale, tracking) // 2, y, s, scale,
                      color, tracking, bold)


def wrap2(s, scale, maxw, tracking=0):
    lines, cur = [], ""
    for wd in s.upper().split():
        trial = (cur + " " + wd).strip()
        if tw(trial, scale, tracking) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------ illustrations
# Small hand-drawn scenes for the hero panel and the card bands.
# Each takes the canvas, a bounding box (x, y, w, h) and the story's
# accent colour, and draws only with the primitives above.


def _arc(c, x0, y0, x1, y1, lift, color, t=2):
    """A curved trail from (x0, y0) to (x1, y1), arched upward by lift."""
    steps = 24
    px, py = x0, y0
    for k in range(1, steps + 1):
        f = k / steps
        x = int(x0 + (x1 - x0) * f)
        y = int(y0 + (y1 - y0) * f - 4 * lift * f * (1 - f))
        c.line(px, py, x, y, color, t)
        px, py = x, y


def illu_hero(c, x, y, w, h):
    """Night sky over Kyiv: three missile trails arc down, a city
    silhouette with lit windows stands below."""
    c.rect(x, y, w, h, (24, 48, 88))
    for sx, sy in ((12, 14), (40, 40), (70, 10), (104, 34), (140, 16),
                   (170, 44), (200, 12), (228, 38), (30, 80), (120, 66),
                   (190, 74), (90, 96), (160, 100), (220, 88)):
        c.set(x + sx, y + sy, (200, 210, 230))
    _arc(c, x + 16, y + 8, x + 150, y + 150, 26, GOLD, 2)
    _arc(c, x + 90, y + 4, x + 210, y + 140, 30, WHITE, 2)
    _arc(c, x + 170, y + 10, x + 120, y + 158, 22, (224, 82, 66), 2)
    c.starburst(x + 150, y + 150, 6, 14, 8, GOLD)
    c.starburst(x + 210, y + 140, 5, 12, 8, WHITE)
    c.starburst(x + 120, y + 158, 5, 12, 8, (224, 82, 66))
    c.disc(x + 150, y + 150, 3, WHITE)
    c.disc(x + 210, y + 140, 3, WHITE)
    c.disc(x + 120, y + 158, 3, WHITE)
    base = y + h
    for bx, bw, bh in ((0, 34, 52), (38, 26, 78), (68, 30, 60),
                       (102, 24, 88), (130, 36, 56), (170, 28, 80),
                       (202, 30, 64), (236, 20, 46)):
        c.rect(x + bx, base - bh, bw, bh, (8, 10, 26))
        for wy in range(base - bh + 8, base - 6, 12):
            for wx in range(x + bx + 6, x + bx + bw - 4, 10):
                if (wx * 7 + wy * 13) % 3 == 0:
                    c.rect(wx, wy, 3, 4, GOLD)


def illu_chart(c, x, y, w, h, ac):
    """Falling market: a steep red zigzag line over faint bars."""
    for bx in range(0, w, 26):
        bh = 20 + ((bx * 37) % 30)
        c.rect(x + bx + 6, y + h - 8 - bh, 14, bh, (120, 40, 32))
    pts = [(x + 10, y + 12), (x + 60, y + 22), (x + 110, y + 18),
           (x + 160, y + 36), (x + 210, y + 30), (x + 260, y + 52),
           (x + 300, y + 46)]
    for i in range(len(pts) - 1):
        c.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], ac, 3)
    c.disc(pts[-1][0], pts[-1][1], 5, WHITE)


def illu_stars(c, x, y, w, h, ac):
    """EU circle of twelve gold stars + three deal papers."""
    cx, cy, r = x + 52, y + 36, 24
    for k in range(12):
        a = math.pi * 2 * k / 12 - math.pi / 2
        sx = int(cx + r * math.cos(a))
        sy = int(cy + r * math.sin(a))
        c.starburst(sx, sy, 2, 5, 5, GOLD)
    for k in range(3):
        px = x + 120 + k * 58
        c.rect(px, y + 12, 48, 48, (250, 245, 232))
        c.hline(px + 6, y + 22, 36, (35, 105, 165), 2)
        c.hline(px + 6, y + 32, 36, (35, 105, 165), 2)
        c.hline(px + 6, y + 42, 24, (35, 105, 165), 2)


def illu_sun(c, x, y, w, h, ac):
    """Hot sun over waves, with a thermometer: COP31 in Antalya."""
    cx, cy = x + 56, y + 32
    c.disc(cx, cy, 17, ac)
    for k in range(8):
        a = math.pi * k / 4
        x0 = int(cx + 23 * math.cos(a))
        y0 = int(cy + 23 * math.sin(a))
        x1 = int(cx + 32 * math.cos(a))
        y1 = int(cy + 32 * math.sin(a))
        c.line(x0, y0, x1, y1, ac, 2)
    for wy in (y + 56, y + 64):
        for wx in range(x + 110, x + w - 8, 18):
            c.line(wx, wy, wx + 10, wy, (147, 190, 224), 2)
    tx = x + w - 44
    c.rect(tx, y + 10, 10, 40, WHITE)
    c.disc(tx + 5, y + 54, 9, (224, 82, 66))
    c.rect(tx + 3, y + 16, 4, 36, (224, 82, 66))


def illu_shield(c, x, y, w, h, ac):
    """Defence dome: an arc shield with three intercept bursts."""
    cx, cy = x + w // 2, y + h - 4
    _arc(c, cx - 78, cy, cx + 78, cy, 54, ac, 3)
    _arc(c, cx - 56, cy, cx + 56, cy, 38, WHITE, 2)
    for bx, by in ((cx - 52, y + 14), (cx + 8, y + 8), (cx + 58, y + 18)):
        c.starburst(bx, by, 4, 10, 8, GOLD)
        c.disc(bx, by, 2, WHITE)
    c.hline(x + 20, cy, w - 40, ac, 2)


def illu_crowd(c, x, y, w, h, ac):
    """A crowd with placards: Gen Z on the streets."""
    for k in range(7):
        px = x + 18 + k * 42
        c.vline(px + 8, y + 8, 20, WHITE, 2)
        c.rect(px, y + 4, 18, 12, ac if k % 2 else WHITE)
        c.disc(px + 9, y + 40, 7, (250, 226, 190))
        c.rect(px + 1, y + 48, 16, h - 48,
               (230, 230, 230) if k % 2 else ac)


def illu_neon(c, x, y, w, h, ac):
    """Vice City at dusk: neon skyline under a pink sun."""
    c.disc(x + 250, y + 26, 14, ac)
    c.hline(x, y + 44, w, (64, 224, 208), 2)
    for bx, bw, bh, col in ((0, 40, 26, (232, 64, 160)),
                            (44, 30, 40, (64, 224, 208)),
                            (78, 36, 22, (232, 64, 160)),
                            (118, 28, 44, (250, 200, 60)),
                            (150, 34, 30, (64, 224, 208)),
                            (188, 30, 40, (232, 64, 160)),
                            (222, 36, 26, (250, 200, 60)),
                            (262, 32, 34, (64, 224, 208))):
        c.rect(x + bx, y + h - bh, bw, bh, col)
        for wy in range(y + h - bh + 6, y + h - 4, 10):
            for wx in range(x + bx + 5, x + bx + bw - 3, 9):
                if (wx + wy) % 4 == 0:
                    c.rect(wx, wy, 2, 3, WHITE)


ILLU = {2: illu_chart, 3: illu_stars, 4: illu_sun, 5: illu_shield,
        6: illu_crowd, 7: illu_neon}


# ------------------------------------------------------------ stories
# Seven stories, each verified against at least two independent
# sources (see NEWS.md). Story 1 is the hero; stories 2-7 are the
# grid cards. Fields: place, region tag, headline, fact, stat, source.
STORIES = [
    {"n": 1, "place": "KYIV - POLAND", "region": "EUROPE",
     "headline": "RUSSIA'S BIGGEST STRIKE HITS UKRAINE, LANDS IN POLAND",
     "fact": "404 DRONES AND 111 MISSILES OVERNIGHT. 8 KILLED IN KYIV, "
             "BRIDGES HIT. TUSK: INTENTIONAL PROVOCATION. NATO: GRAVE "
             "VIOLATION.",
     "stat": "404 DRONES - 111 MISSILES - 8 DEAD",
     "source": "AP - ISW - CBS"},
    {"n": 2, "place": "NEW YORK, USA", "region": "NORTH AMERICA",
     "headline": "AI SELL-OFF: S&P AND DOW IN CORRECTION",
     "fact": "DOW -950, S&P -3.7%, NASDAQ -5.3%. WORST WEEK SINCE 2020.",
     "stat": "DOW -1.9% - S&P -3.7%",
     "source": "WSJ - MARKETWATCH - INVESTOPEDIA"},
    {"n": 3, "place": "BRUSSELS, BELGIUM", "region": "EUROPE",
     "headline": "UK AND EU SIGN BIGGEST POST-BREXIT RESET",
     "fact": "FOOD, CARBON AND YOUTH DEALS. 100,000 VISAS A YEAR.",
     "stat": "100,000 VISAS A YEAR",
     "source": "REUTERS - THE TIMES - PA"},
    {"n": 4, "place": "ANTALYA, TURKIYE", "region": "CLIMATE",
     "headline": "COP31 IN OVERTIME AS FOSSIL FUELS VANISH",
     "fact": "DRAFT DEAL DROPS ALL FOSSIL FUEL WORDS. 'WORST COP EVER' "
             "FEARS.",
     "stat": "NO FOSSIL FUELS IN DRAFT",
     "source": "AP - REUTERS - LE MONDE"},
    {"n": 5, "place": "RIYADH, SAUDI ARABIA", "region": "MIDDLE EAST",
     "headline": "SAUDI DEFENCES DOWN THREE HOUTHI MISSILES",
     "fact": "THIRD NIGHT OF ALERTS IN RIYADH. NO DAMAGE. PIF TOWER HIT "
             "THURSDAY.",
     "stat": "3 MISSILES DOWNED",
     "source": "REUTERS - AL JAZEERA"},
    {"n": 6, "place": "EUROPE-WIDE", "region": "EUROPE",
     "headline": "GEN Z TAKES TO THE STREETS IN 25 COUNTRIES",
     "fact": "YOUTH STRIKE OVER COSTS, CUTS, ARMS AND CLIMATE.",
     "stat": "25 COUNTRIES",
     "source": "CNN - REUTERS - AL JAZEERA"},
    {"n": 7, "place": "LOS ANGELES, USA", "region": "CULTURE",
     "headline": "GTA VI MAKES $3.79BN IN A DAY",
     "fact": "BIGGEST ENTERTAINMENT LAUNCH EVER. 32.5M COPIES PRE-SOLD.",
     "stat": "$3.79BN IN 24 HOURS",
     "source": "REUTERS - BARRONS - CNN"},
]


def draw_marker(c, cx, cy, n, color=GOLD):
    c.disc(cx, cy, 16, halo_of(color))
    c.disc(cx, cy, 12, color)
    c.ring(cx, cy, 14, WHITE, 2)
    s = str(n)
    draw_text2(c, cx - tw(s, 2) // 2, cy - 7, s, 2, NAVY_D, bold=True)


def story_card(c, x, y, w, h, st):
    c.rect(x, y, w, h, CARD)
    ac = ACCENT[st["n"]]
    acd = ACCENT_DARK[st["n"]]
    c.hline(x, y, w, acd, 3)
    c.hline(x, y + h - 1, w, CARD_LINE, 1)
    c.vline(x, y, h, CARD_LINE, 1)
    c.vline(x + w - 1, y, h, CARD_LINE, 1)
    # illustration band on top (72px): a small hand-drawn scene in the
    # story's colours, not a photo
    c.rect(x + 1, y + 1, w - 2, 72, BAND[st["n"]])
    ILLU[st["n"]](c, x + 1, y + 1, w - 2, 72, ac)
    # ghosted newspaper background behind the copy
    newsprint(c, x + 6, y + 78, w - 12, h - 84, (215, 205, 180))
    # number badge + place kicker (bold, in the story's colour) + region
    draw_marker(c, x + 24, y + 96, st["n"], ac)
    draw_text2(c, x + 44, y + 88, st["place"], 2, acd, bold=True)
    draw_text2(c, x + 44, y + 106, st["region"], 1, (110, 105, 90),
               tracking=2)
    # headline, bold, up to 2 lines
    lines = wrap2(st["headline"], 2, w - 28)[:2]
    hy = y + 124
    for ln in lines:
        draw_text2(c, x + 14, hy, ln, 2, INK, bold=True)
        hy += 18
    # fact, up to 3 lines
    flines = wrap2(st["fact"], 2, w - 28)[:3]
    fy = y + 166
    for ln in flines:
        draw_text2(c, x + 14, fy, ln, 2, FACT_D)
        fy += 18
    # stat highlight + source line at the foot of the card
    c.hline(x + 14, y + 224, w - 28, CARD_LINE, 1)
    draw_text2(c, x + 14, y + 232, st["stat"], 2, acd, bold=True)
    draw_text2(c, x + 14, y + 248, "SOURCE: " + st["source"], 1,
               (110, 105, 90), tracking=1)


# ------------------------------------------------------------- layout
def build():
    c = Canvas(W, H, BG)

    # ---- masthead: cream paper, ghosted newspaper, ink title, red date
    c.rect(24, 24, 976, 104, CARD)
    c.hline(24, 24, 976, INK, 3)
    c.hline(24, 125, 976, INK, 3)
    newsprint(c, 24, 24, 976, 104, (210, 198, 170))
    text_center2(c, 512, 38, "THE WORLD IN ONE DAY", 3, INK, tracking=3)
    text_center2(c, 512, 72, "SATURDAY 21 NOVEMBER 2026", 5, DATE_RED,
                 bold=True)

    # ---- hero: story 1 on a dark navy panel, illustrated night sky right
    st = STORIES[0]
    hx, hy, hw, hh = 24, 140, 976, 280
    c.rect(hx, hy, hw, hh, BAND[1])
    c.hline(hx, hy, hw, GOLD, 3)
    c.hline(hx, hy + hh - 3, hw, GOLD, 3)
    c.vline(hx, hy, hh, GOLD, 3)
    c.vline(hx + hw - 3, hy, hh, GOLD, 3)
    illu_hero(c, hx + 700, hy + 20, 256, 240)
    draw_marker(c, hx + 30, hy + 38, 1, GOLD)
    draw_text2(c, hx + 56, hy + 30, st["place"], 2, GOLD, bold=True)
    draw_text2(c, hx + 56 + tw(st["place"], 2) + 16, hy + 32,
               st["region"], 1, (200, 210, 230), tracking=2)
    hlines = wrap2(st["headline"], 3, 620)[:2]
    hyy = hy + 70
    for ln in hlines:
        draw_text2(c, hx + 24, hyy, ln, 3, WHITE, bold=True)
        hyy += 28
    flines = wrap2(st["fact"], 2, 620)[:3]
    fy = hy + 140
    for ln in flines:
        draw_text2(c, hx + 24, fy, ln, 2, (214, 222, 232))
        fy += 18
    c.hline(hx + 24, hy + 208, 620, (110, 140, 175), 1)
    draw_text2(c, hx + 24, hy + 218, st["stat"], 2, GOLD, bold=True)
    draw_text2(c, hx + 24, hy + 244, "SOURCE: " + st["source"], 1,
               (200, 210, 230), tracking=1)

    # ---- story cards: 2 rows x 3 columns (stories 2-7)
    cw, ch, gap = 317, 258, 12
    for i, st in enumerate(STORIES[1:]):
        col, row = i % 3, i // 3
        x = 24 + col * (cw + gap)
        y = 432 + row * (ch + gap)
        story_card(c, x, y, cw, ch, st)

    # ---- footer
    text_center2(c, 512, 978,
                 "7 STORIES - VERIFIED AGAINST REUTERS, AP, BBC, CNN, WSJ AND OTHERS - 21 NOVEMBER 2026",
                 1, (110, 105, 90), tracking=1)
    return c


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    c = build()
    path = os.path.join(outdir, "entry.png")
    write_png(path, c.px, W, H)
    print("WROTE", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
