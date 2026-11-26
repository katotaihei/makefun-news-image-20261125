#!/usr/bin/env python3
"""Draw the front page of THE WORLD TODAY for Wednesday 25 November 2026.

Everything here is written from scratch in this file: a 5x7 bitmap font
designed glyph by glyph, a small raster canvas, and a hand-rolled PNG
encoder (struct + zlib only).  No network, no clock, no randomness, so
running the program twice produces byte-identical output.

Layout (1024 x 1024, newspaper front page):
  masthead, lead story on the Strait of Hormuz with an oil-price chart,
  then Ras Tanura, the Macy's parade, Shenzhou-24, the Cairo fuel fire,
  an ALSO TODAY ticker strip and a sources footer.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

PAPER = (246, 241, 230)
INK = (20, 33, 61)
RED = (178, 34, 24)
BLUE = (29, 78, 216)
PURPLE = (96, 44, 160)
ORANGE = (192, 88, 8)
GOLD = (214, 178, 58)
GREY = (96, 94, 88)
LIGHT = (246, 241, 230)
FLAME_YELLOW = (240, 196, 60)
FLAME_ORANGE = (232, 116, 28)


# ---------------------------------------------------------------------------
# 5x7 bitmap font.  Each glyph is seven rows of five cells; '#' is ink.
# Designed here: straight stems, open counters, and a slightly narrow
# look so headlines stay compact at large scales.
# ---------------------------------------------------------------------------
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
    ".": (".....", ".....", ".....", ".....", ".....", ".....", "..#.."),
    ",": (".....", ".....", ".....", ".....", ".....", "..#..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ":": (".....", "..#..", ".....", ".....", ".....", "..#..", "....."),
    ";": (".....", "..#..", ".....", ".....", "..#..", "..#..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "....#", "...#.", "...#.", "..#..", ".#...", "#...."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "&": (".###.", "#...#", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    ">": ("#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."),
}


# ---------------------------------------------------------------------------
# Raster canvas: a plain RGB bytearray with pixel, rectangle, line,
# circle, ellipse and triangle helpers, plus text drawn from FONT.
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, width, height, colour):
        self.w = width
        self.h = height
        self.px = bytearray(width * height * 3)
        self.fill(colour)

    def fill(self, colour):
        r, g, b = colour
        self.px[:] = bytes((r, g, b)) * (self.w * self.h)

    def set_pixel(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = colour[0]
            self.px[i + 1] = colour[1]
            self.px[i + 2] = colour[2]

    def fill_rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def rect(self, x, y, w, h, colour, thick=1):
        self.fill_rect(x, y, w, thick, colour)
        self.fill_rect(x, y + h - thick, w, thick, colour)
        self.fill_rect(x, y, thick, h, colour)
        self.fill_rect(x + w - thick, y, thick, h, colour)

    def hline(self, x, y, w, colour, thick=1):
        self.fill_rect(x, y, w, thick, colour)

    def vline(self, x, y, h, colour, thick=1):
        self.fill_rect(x, y, thick, h, colour)

    def line(self, x0, y0, x1, y1, colour):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.set_pixel(x, y, colour)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, colour):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, colour)

    def ellipse(self, cx, cy, rx, ry, colour):
        for dy in range(-ry, ry + 1):
            span = int(rx * (1.0 - (dy * dy) / float(ry * ry)) ** 0.5)
            self.fill_rect(cx - span, cy + dy, 2 * span + 1, 1, colour)

    def triangle(self, ax, ay, bx, by, cx, cy, colour):
        # Scanline fill: walk the edges and fill between them per row.
        ys = sorted(((ax, ay), (bx, by), (cx, cy)), key=lambda p: p[1])
        (x0, y0), (x1, y1), (x2, y2) = ys
        for y in range(y0, y2 + 1):
            xs = []
            for (px, py), (qx, qy) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x0, y0), (x2, y2))):
                if py == qy:
                    continue
                if min(py, qy) <= y <= max(py, qy):
                    t = (y - py) / (qy - py)
                    xs.append(px + t * (qx - px))
            if len(xs) >= 2:
                lo, hi = int(min(xs)), int(max(xs))
                self.fill_rect(lo, y, hi - lo + 1, 1, colour)

    # -- text ---------------------------------------------------------------
    def text_width(self, text, scale):
        return len(text) * 6 * scale - scale

    def draw_text(self, x, y, text, scale, colour):
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "#":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, colour)
            cx += 6 * scale
        return cx

    def draw_text_centered(self, cx, y, text, scale, colour):
        x = cx - self.text_width(text, scale) // 2
        return self.draw_text(x, y, text, scale, colour)

    def wrap(self, text, scale, max_width):
        """Greedy word wrap; returns a list of lines that fit max_width."""
        lines = []
        current = ""
        for word in text.split(" "):
            trial = word if not current else current + " " + word
            if self.text_width(trial, scale) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines


# ---------------------------------------------------------------------------
# PNG encoder: 8-bit RGB, no filtering, one zlib stream.  Deterministic by
# construction -- no ancillary chunks, no timestamps.
# ---------------------------------------------------------------------------
def _chunk(kind, payload):
    out = struct.pack(">I", len(payload))
    out += kind
    out += payload
    out += struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    return out


def encode_png(canvas):
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter type: none
        raw += canvas.px[y * stride:(y + 1) * stride]
    data = b"\x89PNG\r\n\x1a\n"
    data += _chunk(b"IHDR", ihdr)
    data += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += _chunk(b"IEND", b"")
    return data


# ---------------------------------------------------------------------------
# Small spot illustrations, all drawn from rectangles, discs and triangles.
# ---------------------------------------------------------------------------
def draw_flame(c, cx, base_y, size, outline=INK):
    """A three-layer flame inside a thin box, centred on cx."""
    half = size // 2
    c.rect(cx - half - 6, base_y - size - 14, size + 12, size + 20, outline, 2)
    c.triangle(cx - half, base_y, cx, base_y - size, cx + half, base_y, RED)
    c.triangle(cx - half + 6, base_y, cx, base_y - size + 12,
               cx + half - 6, base_y, FLAME_ORANGE)
    c.triangle(cx - half + 11, base_y, cx, base_y - size + 22,
               cx + half - 11, base_y, FLAME_YELLOW)


def draw_balloon(c, cx, top_y, outline=INK):
    """A parade balloon: round envelope, basket, strings, in a thin box."""
    c.rect(cx - 34, top_y - 6, 68, 92, outline, 2)
    c.ellipse(cx, top_y + 22, 24, 24, BLUE)
    c.disc(cx - 8, top_y + 16, 4, LIGHT)
    c.line(cx - 14, top_y + 42, cx - 8, top_y + 66, outline)
    c.line(cx + 14, top_y + 42, cx + 8, top_y + 66, outline)
    c.fill_rect(cx - 10, top_y + 66, 20, 12, ORANGE)
    c.rect(cx - 10, top_y + 66, 20, 12, outline, 1)


def draw_station(c, cx, mid_y, outline=INK):
    """A space station: hub, two solar panels and a dish, in a thin box."""
    c.rect(cx - 40, mid_y - 34, 80, 68, outline, 2)
    c.fill_rect(cx - 38, mid_y - 6, 26, 12, BLUE)
    c.fill_rect(cx + 12, mid_y - 6, 26, 12, BLUE)
    c.fill_rect(cx - 7, mid_y - 12, 14, 24, LIGHT)
    c.rect(cx - 7, mid_y - 12, 14, 24, outline, 1)
    c.disc(cx, mid_y, 4, RED)
    c.line(cx, mid_y - 12, cx + 12, mid_y - 26, outline)
    c.disc(cx + 14, mid_y - 28, 4, GOLD)


def draw_oil_chart(c, x, y, w, h):
    """Two bars: Brent +2.4% and WTI +1.8% on Wednesday."""
    c.draw_text(x, y, "OIL JUMPS ON WEDNESDAY", 2, GREY)
    base = y + h - 26
    c.hline(x, base, w, INK, 2)
    bw = 62
    brent_h = 148
    wti_h = 108
    bx = x + 34
    wx = x + w - 34 - bw
    c.fill_rect(bx, base - brent_h, bw, brent_h, RED)
    c.fill_rect(wx, base - wti_h, bw, wti_h, RED)
    c.draw_text_centered(bx + bw // 2, base - brent_h - 20, "+2.4%", 2, RED)
    c.draw_text_centered(wx + bw // 2, base - wti_h - 20, "+1.8%", 2, RED)
    c.draw_text_centered(bx + bw // 2, base + 8, "BRENT", 2, INK)
    c.draw_text_centered(wx + bw // 2, base + 8, "WTI", 2, INK)


def draw_story(c, y, top_rule, kicker, kicker_colour, headline, deck,
               icon=None, icon_x=None, text_x=44, text_w=840):
    """One stacked story: coloured rule, kicker, headline, deck lines."""
    c.hline(32, y, 960, top_rule, 3)
    c.draw_text(text_x, y + 12, kicker, 2, kicker_colour)
    head_lines = c.wrap(headline, 3, text_w)
    hy = y + 34
    for line in head_lines:
        c.draw_text(text_x, hy, line, 3, INK)
        hy += 30
    dy = hy + 6
    for line in c.wrap(deck, 2, text_w):
        c.draw_text(text_x, dy, line, 2, INK)
        dy += 18
    if icon == "flame":
        draw_flame(c, icon_x, y + 96, 44)
    elif icon == "balloon":
        draw_balloon(c, icon_x, y + 26)
    elif icon == "station":
        draw_station(c, icon_x, y + 62)
    return dy


# ---------------------------------------------------------------------------
# Front page layout.
# ---------------------------------------------------------------------------
def build_page():
    c = Canvas(WIDTH, HEIGHT, PAPER)
    # Double outer frame.
    c.rect(14, 14, WIDTH - 28, HEIGHT - 28, INK, 2)
    c.rect(20, 20, WIDTH - 40, HEIGHT - 40, INK, 1)

    # Masthead.
    c.draw_text_centered(WIDTH // 2, 34, "THE WORLD TODAY", 7, INK)
    c.draw_text_centered(WIDTH // 2, 96, "WEDNESDAY 25 NOVEMBER 2026",
                          2, RED)
    c.hline(32, 120, 960, INK, 3)
    c.hline(32, 127, 960, INK, 1)

    # Lead story: two tankers hit mines in the Strait of Hormuz.
    lead_y = 140
    c.hline(32, lead_y, 960, RED, 3)
    c.draw_text(44, lead_y + 12, "MIDDLE EAST - LEAD STORY", 2, RED)
    head = ["TWO TANKERS HIT MINES IN", "THE STRAIT OF HORMUZ"]
    hy = lead_y + 36
    for line in head:
        c.draw_text(44, hy, line, 4, INK)
        hy += 40
    deck = ("IRGC SAYS THE TANKERS SAILED AN UNAUTHORISED ROUTE AND "
            "HIT MINES AT DAWN. BRENT CRUDE TOPS $93 AS GULF "
            "SHIPPING FEARS GROW.")
    dy = hy + 8
    for line in c.wrap(deck, 2, 620):
        c.draw_text(44, dy, line, 2, INK)
        dy += 18
    # Vertical divider and the oil chart on the right.
    c.vline(688, lead_y + 12, 236, GREY, 1)
    draw_oil_chart(c, 712, lead_y + 12, 268, 236)

    # Story 2: Houthis claim a strike on Ras Tanura.
    draw_story(
        c, 412, RED, "MIDDLE EAST", RED,
        "HOUTHIS CLAIM STRIKE ON RAS TANURA REFINERY",
        "SAUDI ARABIA SAYS IT SHOT DOWN FOUR DRONES OVER THE SITE; "
        "SMOKE SEEN OVER THE REFINERY.",
        icon="flame", icon_x=936, text_w=840)

    # Story 3: the 100th Macy's parade is postponed by a storm.
    draw_story(
        c, 528, BLUE, "NEW YORK", BLUE,
        "100TH MACY'S PARADE DELAYED BY STORM",
        "THE THANKSGIVING MARCH MOVES TO SATURDAY, NOV 28, AS GUSTS "
        "REACH 60 MPH. A FIRST IN 100 YEARS.",
        icon="balloon", icon_x=936, text_w=840)

    # Story 4: Shenzhou-24 docks with Pakistan's first astronaut aboard.
    draw_story(
        c, 644, PURPLE, "SPACE", PURPLE,
        "PAKISTAN'S FIRST ASTRONAUT REACHES ORBIT",
        "SHENZHOU-24 DOCKS AT TIANGONG; MUHAMMAD ZEESHAN ALI IS THE "
        "FIRST FOREIGNER ABOARD THE STATION.",
        icon="station", icon_x=936, text_w=840)

    # Story 5: fuel truck fire in Cairo.
    draw_story(
        c, 760, ORANGE, "EGYPT", ORANGE,
        "FUEL TRUCK FIRE KILLS AT LEAST 30 IN CAIRO",
        "A VEHICLE CARRYING PETROLEUM PRODUCTS OVERTURNS ON CAIRO'S "
        "RING ROAD; 15 INJURED, THE HEALTH MINISTRY SAYS.",
        icon="flame", icon_x=936, text_w=840)

    # ALSO TODAY ticker strip.
    c.fill_rect(32, 876, 960, 92, INK)
    c.draw_text(48, 888, "ALSO TODAY", 2, GOLD)
    c.draw_text(48, 914,
                ">> SOLOMON ISLANDS SIGNS PACT WITH AUSTRALIA, "
                "BARS FOREIGN BASES", 2, LIGHT)
    c.draw_text(48, 938,
                ">> POPE LEO XIV LAMENTS FAILURE OF COP31 "
                "CLIMATE TALKS", 2, LIGHT)

    # Footer: sources.
    c.draw_text_centered(
        WIDTH // 2, 980,
        "SOURCES: REUTERS, AP, CNN, XINHUA, AL JAZEERA, STRAITS TIMES, "
        "NIKKEI ASIA, OILPRICE", 1, GREY)
    c.draw_text_centered(
        WIDTH // 2, 994, "FIGURES AS REPORTED ON 25 NOVEMBER 2026.",
        1, GREY)
    return c


def main():
    page = build_page()
    data = encode_png(page)
    here = os.path.dirname(os.path.abspath(__file__))
    targets = []
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        targets.append(os.path.join(out_dir, "entry.png"))
    targets.append(os.path.join(here, "entry.png"))
    if os.path.isdir("/output"):
        targets.append("/output/entry.png")
    wrote = []
    for path in targets:
        try:
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(path, "wb") as f:
                f.write(data)
            wrote.append(path)
        except OSError as exc:
            print("note: could not write", path, ":", exc)
    if not wrote:
        raise SystemExit("could not write entry.png anywhere")
    print("wrote", ", ".join(wrote), len(data), "bytes")


if __name__ == "__main__":
    main()
