#!/usr/bin/env python3
"""news-image-20261121: draw one 1024x1024 newspaper front page summing up
Saturday 21 November 2026's world news, and write it to /output/entry.png.

Pure Python 3 standard library only: no network, no third-party packages.
The PNG is encoded by hand (zlib + struct) and all text is drawn with an
embedded 5x7 bitmap font, so the program is fully deterministic: two runs
produce byte-identical output.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 229)
INK = (24, 24, 26)
NAVY = (22, 35, 63)
NAVY_LT = (38, 58, 96)
RED = (178, 34, 34)
RED_LT = (214, 90, 70)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)
GREY = (120, 118, 110)
SKY = (16, 28, 54)
SKY2 = (30, 52, 92)
ORANGE = (240, 140, 40)
YELLOW = (250, 200, 60)
GREEN = (46, 125, 70)
GREEN_LT = (120, 180, 110)
BLUE = (40, 90, 160)
TEAL = (30, 130, 130)
BROWN = (120, 84, 50)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 strings of 5 chars, '#' = pixel on.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    'a': (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    'g': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
    'j': (".....", "...#.", ".....", "..##.", "...#.", "...#.", "...#.", ".##.."),
    'k': ("#....", "#....", "#.#..", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "#...#", "#...#", "####.", "#....", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", "#...#", ".####", "....#", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#...#", ".###."),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".....", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".....", ".##..", "..#.."),
    ':': (".....", ".##..", ".....", ".....", ".##..", ".....", "....."),
    ';': (".....", ".##..", ".....", ".....", ".##..", ".##..", "..#.."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "...#.", "..#..", ".#...", "#...."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.#.#", "#..##"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '$': ("..#..", ".####", "#.#.#", ".###.", "...#.", "####.", "..#.."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '[': (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    ']': (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    '<': ("....#", "...#.", "..#..", ".#...", "..#..", "...#.", "....#"),
    '>': ("#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."),
    '~': (".....", ".....", ".##.#", "#.##.", ".....", ".....", "....."),
}
# 'g','j','p','q','y' have descenders: store 9-row glyphs, render rows 0..8.
DESCENDERS = set('gjpqy')


def glyph_rows(ch):
    g = FONT.get(ch)
    if g is None:
        g = FONT['?']
    return g


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def border(self, x, y, w, h, c, t=1):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            for a in range(-(t // 2), t // 2 + 1):
                for b in range(-(t // 2), t // 2 + 1):
                    self.set(x + a, y + b, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d <= r * r:
                        self.set(xx, yy, c)
                else:
                    if abs(d - r * r) <= r:
                        self.set(xx, yy, c)

    def poly(self, pts, c):
        # scanline fill of a simple polygon
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                    self.set(x, y, c)

    def burst(self, cx, cy, r, c):
        # starburst: 12 spikes
        for k in range(12):
            import math
            a = math.pi * k / 6
            x1 = cx + int(r * 0.35 * math.cos(a))
            y1 = cy + int(r * 0.35 * math.sin(a))
            x2 = cx + int(r * math.cos(a))
            y2 = cy + int(r * math.sin(a))
            self.line(x1, y1, x2, y2, c, 3)
        self.circle(cx, cy, max(2, r // 3), c)

    # ------------------------------------------------------------- text
    def text(self, x, y, s, scale, c, align='l'):
        rows_cache = [glyph_rows(ch) for ch in s]
        widths = []
        for g in rows_cache:
            widths.append(6)  # 5 px + 1 spacing
        total = sum(widths) * scale - scale
        if align == 'c':
            x -= total // 2
        elif align == 'r':
            x -= total
        cx = x
        for g in rows_cache:
            nrows = len(g)
            for r in range(nrows):
                for col in range(5):
                    if g[r][col] == '#':
                        self.rect(cx + col * scale, y + r * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return total

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def wrap(self, s, max_w, scale):
        words = s.split(' ')
        lines, cur = [], ''
        for w_ in words:
            trial = (cur + ' ' + w_).strip()
            if self.text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w_
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, max_w, scale, c, leading=None):
        if leading is None:
            leading = 9 * scale
        for ln in self.wrap(s, max_w, scale):
            self.text(x, y, ln, scale, c)
            y += leading
        return y


def chunk(typ, data):
    out = struct.pack('>I', len(data)) + typ + data
    out += struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff)
    return out


def write_png(cv, path):
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 9)
    with open(path, 'wb') as f:
        f.write(sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat)
                + chunk(b'IEND', b''))

# ------------------------------------------------------------- illustrations
def draw_lead_scene(cv, x, y, w, h):
    """Night sky over a simplified map: missile trails and explosions."""
    # sky bands
    for i in range(h):
        t = i / max(1, h - 1)
        c = tuple(int(SKY[k] + (SKY2[k] - SKY[k]) * t) for k in range(3))
        cv.rect(x, y + i, w, 1, c)
    # stars
    stars = [(18, 22), (70, 60), (130, 18), (205, 48), (260, 26), (330, 70),
             (400, 20), (470, 55), (520, 30), (95, 95), (300, 100), (430, 110),
             (160, 130), (360, 140), (500, 90)]
    for sx, sy in stars:
        cv.set(x + sx, y + sy, WHITE)
        cv.set(x + sx + 1, y + sy, WHITE)
    # ground silhouette
    cv.poly([(x, y + h), (x, y + h - 70), (x + 120, y + h - 95),
             (x + 260, y + h - 60), (x + 400, y + h - 88), (x + w, y + h - 55),
             (x + w, y + h)], (18, 22, 20))
    # simplified country outlines (Poland left, Ukraine right) as land
    cv.poly([(x + 60, y + h - 60), (x + 150, y + h - 150), (x + 250, y + h - 140),
             (x + 300, y + h - 70), (x + 200, y + h - 40)], (52, 74, 110))
    cv.poly([(x + 310, y + h - 75), (x + 380, y + h - 160), (x + 500, y + h - 150),
             (x + 545, y + h - 60), (x + 420, y + h - 35)], (64, 88, 124))
    cv.text(x + 105, y + h - 105, "POLAND", 2, GOLD)
    cv.text(x + 385, y + h - 105, "UKRAINE", 2, GOLD)
    # missile trails (dashed arcs)
    for (x0, y0, x1, y1) in [(70, 60, 300, 210), (480, 40, 330, 200),
                             (250, 30, 420, 190)]:
        steps = 24
        for i in range(steps):
            if i % 2:
                continue
            t = i / steps
            px = int(x + x0 + (x1 - x0) * t)
            py = int(y + y0 + (y1 - y0) * t - 60 * t * (1 - t) * 4)
            cv.circle(px, py, 2, WHITE)
    # explosions
    cv.burst(x + 300, y + 185, 26, ORANGE)
    cv.burst(x + 300, y + 185, 15, YELLOW)
    cv.burst(x + 425, y + 172, 20, ORANGE)
    cv.burst(x + 425, y + 172, 12, YELLOW)
    cv.burst(x + 150, y + 198, 16, ORANGE)
    cv.text(x + 14, y + 12, "KYIV UNDER FIRE", 2, WHITE)
    cv.text(x + 14, y + 34, "MISSILES ALSO LAND IN POLAND", 2, (255, 220, 160))


def draw_chart(cv, x, y, w, h):
    """Falling market chart."""
    cv.rect(x, y, w, h, WHITE)
    cv.border(x, y, w, h, INK, 2)
    # grid
    for gy in range(y + 20, y + h - 10, 22):
        cv.line(x + 8, gy, x + w - 8, gy, (225, 225, 220), 1)
    pts = [(x + 12, y + 18), (x + 40, y + 24), (x + 68, y + 22),
           (x + 95, y + 40), (x + 122, y + 38), (x + 150, y + 58),
           (x + 178, y + 56), (x + 205, y + 74)]
    for i in range(len(pts) - 1):
        cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED, 4)
    for px, py in pts:
        cv.circle(px, py, 4, RED)
    cv.text(x + 12, y + h - 40, "S&P 500 -3.7%", 2, RED)
    cv.text(x + 12, y + h - 20, "NASDAQ -5.3%", 2, RED)


def draw_scales(cv, x, y, w, h):
    """Scales of justice."""
    cv.rect(x, y, w, h, (232, 226, 205))
    cv.border(x, y, w, h, INK, 2)
    cx, cy = x + w // 2, y + 18
    cv.rect(cx - 3, cy, 6, h - 40, GOLD)
    cv.line(cx - 62, cy + 12, cx + 62, cy + 12, GOLD, 4)
    cv.circle(cx, cy + 6, 7, GOLD)
    for sgn in (-1, 1):
        px = cx + sgn * 62
        cv.line(px, cy + 12, px - 22, cy + 48, GOLD, 2)
        cv.line(px, cy + 12, px + 22, cy + 48, GOLD, 2)
        cv.poly([(px - 24, cy + 48), (px + 24, cy + 48), (px, cy + 66)], GOLD)
    cv.rect(cx - 34, y + h - 22, 68, 8, GOLD)


def draw_summit(cv, x, y, w, h):
    """Three flags over a table."""
    cv.rect(x, y, w, h, (222, 232, 240))
    cv.border(x, y, w, h, INK, 2)
    flags = [((200, 40, 60), "USA"), ((190, 30, 30), "CHN"),
             ((40, 80, 160), "RUS")]
    fx = x + 30
    for (col, _lbl) in flags:
        cv.line(fx + 6, y + 14, fx + 6, y + 62, INK, 2)
        cv.rect(fx + 8, y + 14, 46, 26, col)
        cv.rect(fx + 8, y + 14, 46, 9, WHITE)
        fx += 78
    cv.rect(x + 18, y + h - 34, w - 36, 10, BROWN)
    cv.rect(x + 28, y + h - 24, 8, 24, BROWN)
    cv.rect(x + w - 36, y + h - 24, 8, 24, BROWN)


def draw_quake(cv, x, y, w, h):
    """Cracked ground and seismograph line."""
    cv.rect(x, y, w, h, (238, 228, 205))
    cv.border(x, y, w, h, INK, 2)
    # seismograph
    pts = []
    import math
    for i in range(0, w - 20, 6):
        yy = y + 26 + int(11 * math.sin(i / 9.0) * (1 if i < 90 else 1.5))
        pts.append((x + 10 + i, yy))
    for i in range(len(pts) - 1):
        cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED, 3)
    # cracked ground
    gy = y + h - 36
    cv.rect(x, gy, w, 46, (150, 120, 80))
    crack = [(x + 30, gy), (x + 60, gy + 14), (x + 45, gy + 24),
             (x + 80, gy + 30), (x + 70, gy + 36)]
    for i in range(len(crack) - 1):
        cv.line(crack[i][0], crack[i][1], crack[i + 1][0], crack[i + 1][1],
                INK, 3)
    crack2 = [(x + w - 40, gy), (x + w - 70, gy + 16), (x + w - 55, gy + 28),
              (x + w - 85, gy + 36)]
    for i in range(len(crack2) - 1):
        cv.line(crack2[i][0], crack2[i][1], crack2[i + 1][0], crack2[i + 1][1],
                INK, 3)
    cv.rect(x + 8, gy + 10, 104, 20, (96, 74, 48))
    cv.text(x + 12, gy + 14, "MAG 6.8", 2, WHITE)


def draw_climate(cv, x, y, w, h):
    """Globe with sun over Antalya."""
    cv.rect(x, y, w, h, (214, 232, 226))
    cv.border(x, y, w, h, INK, 2)
    cx, cy = x + w // 2 - 12, y + h // 2 + 6
    sx, sy = x + w - 32, y + 18
    cv.circle(sx, sy, 9, YELLOW)
    for k in range(8):
        import math
        a = math.pi * k / 4
        cv.line(sx + int(13 * math.cos(a)), sy + int(13 * math.sin(a)),
                sx + int(19 * math.cos(a)), sy + int(19 * math.sin(a)),
                YELLOW, 2)
    cv.circle(cx, cy, 34, BLUE)
    cv.poly([(cx - 24, cy - 6), (cx - 4, cy - 18), (cx + 10, cy - 4),
             (cx - 2, cy + 6), (cx - 20, cy + 12)], GREEN)
    cv.poly([(cx + 6, cy + 12), (cx + 24, cy + 8), (cx + 27, cy + 22),
             (cx + 11, cy + 27)], GREEN_LT)
    cv.poly([(cx - 27, cy - 24), (cx - 10, cy - 30), (cx - 2, cy - 20),
             (cx - 16, cy - 14)], GREEN_LT)


# ------------------------------------------------------------------- page
def build():
    cv = Canvas(W, H, PAPER)
    cv.border(8, 8, W - 16, H - 16, INK, 3)

    # ---- masthead
    cv.rect(24, 24, W - 48, 118, NAVY)
    cv.text(W // 2, 40, "THE WORLD TODAY", 7, WHITE, align='c')
    cv.rect(24, 108, W - 48, 4, GOLD)
    cv.text(W // 2, 122, "SATURDAY, 21 NOVEMBER 2026", 3, RED_LT, align='c')
    cv.text(W // 2, 152, "One day in world news  -  six stories from around the globe",
            2, INK, align='c')
    cv.line(24, 176, W - 24, 176, INK, 2)

    # ---- lead story: Russia / Poland
    ly = 192
    cv.text(24, ly, "WAR IN EUROPE", 2, RED)
    cv.text(24, ly + 22, "RUSSIAN MISSILES", 4, INK)
    cv.text(24, ly + 58, "LAND IN POLAND", 4, INK)
    cv.text(24, ly + 94, "Biggest air attack of the year on Ukraine", 2, INK)
    draw_lead_scene(cv, 24, ly + 124, 560, 236)
    tx = 608
    cv.text(tx, ly, "KYIV HIT BY 400+", 3, INK)
    cv.text(tx, ly + 32, "DRONES AND 110", 3, INK)
    cv.text(tx, ly + 64, "MISSILES", 3, INK)
    body = ("Russia fired more than 400 drones and 110 missiles at Ukraine "
            "overnight. At least eight people were killed in Kyiv. Two "
            "Russian missiles and a suspected drone came down in Poland. "
            "Prime Minister Donald Tusk called it a deliberate provocation, "
            "and NATO jets scrambled.")
    cv.para(tx, ly + 108, body, 392, 2, INK, leading=20)
    cv.line(24, 576, W - 24, 576, INK, 2)

    # ---- row 2: markets + ICJ
    ry = 592
    cw = (W - 48 - 24) // 2  # 476
    # markets card
    cv.text(24, ry, "MARKETS TUMBLE", 3, INK)
    draw_chart(cv, 24, ry + 34, 220, 120)
    mx = 24 + 220 + 16
    cv.para(mx, ry + 36,
            "US stocks fell sharply in an AI sell-off. The S&P 500 fell "
            "3.7% into correction. Nvidia dropped 13.8%.", 236, 2, INK,
            leading=18)
    cv.line(W // 2, ry, W // 2, ry + 158, GREY, 1)
    # ICJ card
    ix = W // 2 + 12
    cv.text(ix, ry, "GENOCIDE RULING", 3, INK)
    draw_scales(cv, ix, ry + 34, 220, 120)
    jx = ix + 220 + 16
    cv.para(jx, ry + 36,
            "The UN's top court ruled Myanmar committed genocide against "
            "the Rohingya in 2017, the first ruling of its kind.", 236, 2,
            INK, leading=18)
    cv.line(24, 772, W - 24, 772, INK, 2)

    # ---- row 3: summit / quake / climate
    ty = 786
    tw = (W - 48 - 2 * 20) // 3  # 304
    cards = [
        ("SHENZHEN SUMMIT", draw_summit,
         "Trump, Xi and Putin met in Shenzhen. Trump called the Ukraine "
         "talks very good."),
        ("QUAKE HITS PERU", draw_quake,
         "A magnitude 6.8 earthquake struck Junin in central Peru. Tremors "
         "were felt in Lima, 320 km away."),
        ("COP31 STALLS", draw_climate,
         "Climate talks in Antalya missed their deadline. The draft dropped "
         "any mention of fossil fuels."),
    ]
    for i, (title, draw, txt) in enumerate(cards):
        cx = 24 + i * (tw + 20)
        cv.text(cx, ty, title, 3, INK)
        draw(cv, cx, ty + 30, tw, 84)
        cv.para(cx, ty + 122, txt, tw, 2, INK, leading=17)

    # ---- footer
    cv.line(24, 984, W - 24, 984, INK, 2)
    cv.text(W // 2, 990, "Reported Saturday 21 November 2026  -  Sources: BBC, Reuters, "
            "AP, FT, The Guardian, Al Jazeera", 1, GREY, align='c')
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.environ.get(
        "OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    write_png(cv, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
