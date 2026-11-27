#!/usr/bin/env python3
"""Draw entry.png: a one-page newspaper front page summing up 26 Nov 2026.

Thursday 26 November 2026. 35 stories across 7 regions (EUROPE 9,
AMERICAS 8, ASIA 6, MIDDLE EAST 5, AFRICA 3, OCEANIA 2, GLOBAL 2),
3 hero + 10 secondary original flat illustrations, a THE DAY IN UTC
timeline strip, a numbers strip of six separate cells where every
number tells a complete mini-story, verification tags on every
illustrated story, a pinned dotted world map whose legend carries the
region counts, a 22-story numbered list, a DATE CHECK box with dated
exclusions plus a "Not yet" tail, and a sources footer. Counts
reconcile: 3 + 10 + 22 = 35; region counts sum to 35; 15 fields.

Every story was verified as having happened, or first been reported,
on Thursday 26 November 2026, from Reuters, AP, BBC, Al Jazeera,
PTI and AAP. Disputed figures are shown as claims, never as fact.
Near-misses are named in the DATE CHECK box, not shown as news.
Drawn with Pillow only; no photos, no copied art. Layout follows the
winning newspaper pattern (date header, timeline, region strip,
numbers strip, 3 heroes, map, numbered list, date check); all
content, headlines and drawings are original to this day.
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os

W = H = 1024
PAPER = (248, 245, 238)
INK = (20, 20, 20)
MUTED = (90, 86, 78)
RED = (166, 27, 27)
NAVY = (18, 34, 64)
RULE = (180, 174, 162)
CARD = (255, 255, 255)
MAPDOT = (158, 168, 180)
GREEN = (46, 134, 74)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(d, text, fnt, width):
    """Greedy word wrap; returns list of lines that fit width."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if d.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def put_text(d, xy, text, fnt, width, fill, leading=2, limit=None):
    """Draw wrapped text; returns y after last line. Warns on overflow."""
    x, y = xy
    lines = wrap_text(d, text, fnt, width)
    if limit is not None and len(lines) > limit:
        print(f"OVERFLOW: {text[:48]!r} -> {len(lines)} lines (max {limit})")
        lines = lines[:limit]
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + leading
    return y


# ---------- small flat-drawing primitives ----------
def sky(d, box, top, mid, bot):
    x0, y0, x1, y1 = box
    for i, c in enumerate((top, mid, bot)):
        d.rectangle([x0, y0 + (y1 - y0) * i // 3,
                     x1, y0 + (y1 - y0) * (i + 1) // 3], fill=c)


def disc(d, cx, cy, r, color):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def puff(d, x, y, s, color):
    d.ellipse([x, y, x + s, y + s * 0.55], fill=color)
    d.ellipse([x + s * 0.5, y - s * 0.25, x + s * 1.5, y + s * 0.4], fill=color)
    d.ellipse([x + s, y, x + s * 2, y + s * 0.55], fill=color)


def spark(d, cx, cy, r, color):
    d.polygon([(cx, cy - r), (cx + r * 0.28, cy - r * 0.28), (cx + r, cy),
               (cx + r * 0.28, cy + r * 0.28), (cx, cy + r),
               (cx - r * 0.28, cy + r * 0.28), (cx - r, cy),
               (cx - r * 0.28, cy - r * 0.28)], fill=color)


def fire(d, x, y, s):
    """Flame with base at (x, y), height s."""
    d.polygon([(x - s * 0.4, y), (x, y - s), (x + s * 0.4, y)], fill=(255, 140, 40))
    d.polygon([(x - s * 0.2, y), (x, y - s * 0.55), (x + s * 0.2, y)],
              fill=(255, 220, 120))


def figure(d, x, y, s, skin=(232, 190, 160), shirt=(30, 90, 160)):
    """Small standing person: head, torso, legs."""
    d.ellipse([x - s * 0.28, y, x + s * 0.28, y + s * 0.55], fill=skin)
    d.rectangle([x - s * 0.3, y + s * 0.55, x + s * 0.3, y + s * 1.15], fill=shirt)
    d.rectangle([x - s * 0.22, y + s * 1.15, x - s * 0.02, y + s * 1.7],
                fill=(30, 30, 34))
    d.rectangle([x + s * 0.02, y + s * 1.15, x + s * 0.22, y + s * 1.7],
                fill=(30, 30, 34))


def banner(d, box, text):
    """Red key-number banner across the bottom of a hero picture."""
    x0, y0, x1, y1 = box
    d.rectangle([x0, y1 - 18, x1, y1], fill=RED)
    f = F(SANS_B, 13)
    d.text((x0 + (x1 - x0 - d.textlength(text, font=f)) / 2, y1 - 16),
           text, font=f, fill=(255, 255, 255))


# ---------- hero pictures (310 x 124) ----------
def pic_gaza(d, box):
    """Hero 1: Deir al-Balah at dawn — a four-storey apartment block
    with a dark hole and flame where the strike hit, a smoke plume, a
    helicopter silhouette, and a stretcher team below."""
    x0, y0, x1, y1 = box
    sky(d, box, (238, 196, 158), (228, 180, 142), (214, 162, 126))
    disc(d, x0 + 24, y0 + 12, 9, (255, 214, 90))
    # a small pale cloud drifting at the top right
    puff(d, x0 + 236, y0 + 10, 14, (226, 214, 196))
    # apartment block
    fx, fy = x0 + 60, y1 - 78
    d.rectangle([fx, fy, fx + 150, y1 - 18], fill=(176, 158, 128))
    d.rectangle([fx, fy - 6, fx + 150, fy], fill=(146, 128, 100))
    for row in range(3):
        for wx in range(fx + 9, fx + 141, 20):
            d.rectangle([wx, fy + 8 + row * 20, wx + 10, fy + 17 + row * 20],
                        fill=(255, 214, 90))
    # dark hole and flame on the second floor
    d.rectangle([fx + 58, fy + 24, fx + 92, fy + 42], fill=(0, 0, 0))
    fire(d, fx + 75, fy + 26, 20)
    puff(d, fx + 40, y0 + 4, 20, (110, 110, 116))
    puff(d, fx + 96, y0 + 14, 16, (130, 130, 134))
    spark(d, fx + 75, fy + 8, 8, (255, 140, 40))
    # a lower block and a tent row at the left
    d.rectangle([x0 + 8, y1 - 46, x0 + 48, y1 - 18], fill=(150, 130, 104))
    for tx in (x0 + 220, x0 + 248, x0 + 276):
        d.polygon([(tx, y1 - 34), (tx + 12, y1 - 46), (tx + 24, y1 - 34)],
                  fill=(240, 240, 238))
        d.rectangle([tx, y1 - 34, tx + 24, y1 - 18], fill=(220, 216, 206))
    # stretcher team at the foot of the block
    figure(d, x0 + 92, y1 - 58, 13, shirt=(220, 180, 60))
    figure(d, x0 + 118, y1 - 58, 13, shirt=(60, 140, 90))
    d.rectangle([x0 + 100, y1 - 40, x0 + 118, y1 - 36], fill=(200, 200, 196))
    d.rectangle([x0, y1 - 18, x1, y1], fill=(110, 94, 74))
    banner(d, box, "9 KILLED IN GAZA")


def pic_kuwait(d, box):
    """Hero 2: the Kuwait air-defence station — radar dishes and a
    mast under a pale desert sky, three drone silhouettes above, an
    interception burst, and a blast at the station building."""
    x0, y0, x1, y1 = box
    sky(d, box, (226, 208, 176), (216, 196, 162), (204, 182, 146))
    disc(d, x0 + 22, y0 + 10, 8, (255, 214, 90))
    # three drones in the sky
    for dx, dy in [(x0 + 130, y0 + 14), (x0 + 180, y0 + 26), (x0 + 232, y0 + 10)]:
        d.ellipse([dx - 10, dy - 3, dx + 10, dy + 3], fill=(50, 50, 54))
        d.polygon([(dx - 4, dy), (dx + 2, dy - 7), (dx + 6, dy)], fill=(50, 50, 54))
        d.polygon([(dx - 4, dy), (dx + 2, dy + 7), (dx + 6, dy)], fill=(50, 50, 54))
    # interception burst between the drones and the station
    spark(d, x0 + 206, y0 + 44, 10, (255, 220, 120))
    spark(d, x0 + 206, y0 + 44, 5, (255, 140, 40))
    # station building with radar dishes
    sx, sy = x0 + 30, y1 - 58
    d.rectangle([sx, sy, sx + 150, y1 - 18], fill=(150, 142, 122))
    d.rectangle([sx, sy - 6, sx + 150, sy], fill=(120, 112, 94))
    for wx in range(sx + 10, sx + 140, 24):
        d.rectangle([wx, sy + 10, wx + 12, sy + 20], fill=(180, 220, 240))
    # radar dish on a mast
    mx, my = sx + 34, sy - 6
    d.line([mx, my, mx, my - 26], fill=(90, 90, 94), width=3)
    d.pieslice([mx - 16, my - 40, mx + 16, my - 12], start=180, end=360,
               fill=(200, 200, 204))
    # second dish, larger, at the right end of the roof
    mx2 = sx + 122
    d.line([mx2, sy - 6, mx2, sy - 20], fill=(90, 90, 94), width=3)
    d.pieslice([mx2 - 12, sy - 32, mx2 + 12, sy - 10], start=180, end=360,
               fill=(200, 200, 204))
    # blast at the station wall
    fire(d, sx + 84, sy + 30, 18)
    puff(d, sx + 60, sy - 2, 14, (110, 110, 116))
    # a sand-coloured watchtower at the right
    tx = x0 + 210
    d.rectangle([tx, y1 - 66, tx + 34, y1 - 18], fill=(168, 150, 118))
    d.rectangle([tx - 4, y1 - 74, tx + 38, y1 - 66], fill=(140, 124, 96))
    d.rectangle([tx + 8, y1 - 70, tx + 16, y1 - 66], fill=(60, 60, 64))
    d.rectangle([tx + 18, y1 - 70, tx + 26, y1 - 66], fill=(60, 60, 64))
    d.rectangle([x0, y1 - 18, x1, y1], fill=(120, 104, 80))
    banner(d, box, "2 ITALIANS KILLED")


def pic_ebola(d, box):
    """Hero 3: the outbreak by the numbers — a data board: cases,
    deaths, provinces hit, and the record it sets. A small red virus
    motif sits in the corner."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(244, 240, 228))
    d.rectangle([x0, y1 - 18, x1, y1], fill=(232, 224, 204))
    rows = [("CASES", "12,021", "confirmed", RED),
            ("DEAD", "5,904", "nearly half", RED),
            ("PROVINCES", "8 of 26", "hit so far", INK),
            ("RECORD", "FASTEST", "outbreak ever", INK)]
    for i, (name, lvl, note, col) in enumerate(rows):
        ry = y0 + 8 + i * 24
        d.text((x0 + 14, ry), name, font=F(SANS_B, 13), fill=INK)
        d.text((x0 + 118, ry - 1), lvl, font=F(SERIF_B, 16), fill=col)
        d.text((x0 + 228, ry + 2), note, font=F(SANS, 11), fill=MUTED)
        if i < 3:
            d.line([x0 + 12, ry + 20, x1 - 12, ry + 20], fill=(210, 204, 190),
                   width=1)
    banner(d, box, "12,021 CASES · 5,904 DEAD")

# ---------- secondary pictures (185 x 58) ----------
def pic_houthi(d, box):
    """4: Jazan on the Red Sea — a refinery tower with a flame, a
    ship at the quay, missile trails arcing in and an interception
    burst overhead."""
    x0, y0, x1, y1 = box
    sky(d, box, (150, 196, 220), (178, 212, 232), (206, 226, 240))
    disc(d, x0 + 16, y0 + 8, 7, (255, 214, 90))
    d.rectangle([x0, y1 - 16, x1, y1], fill=(36, 76, 118))
    for wx in range(x0 + 8, x1 - 8, 26):
        d.line([wx, y1 - 10, wx + 12, y1 - 10], fill=(90, 140, 180), width=1)
    # refinery tower with a flame, left
    tx, ty = x0 + 14, y1 - 40
    d.rectangle([tx, ty, tx + 18, y1 - 16], fill=(150, 150, 154))
    d.rectangle([tx + 4, ty - 6, tx + 14, ty], fill=(120, 120, 124))
    fire(d, tx + 9, ty - 6, 12)
    puff(d, tx + 2, ty - 12, 10, (110, 110, 116))
    # ship at the quay, centre
    hx, hy = x0 + 48, y1 - 28
    d.polygon([(hx, hy + 12), (hx + 66, hy + 12), (hx + 72, hy + 2),
               (hx, hy + 2)], fill=(24, 24, 28))
    d.rectangle([hx + 8, hy - 8, hx + 24, hy + 2], fill=(200, 60, 50))
    d.rectangle([hx + 28, hy - 8, hx + 46, hy + 2], fill=(220, 160, 40))
    # missile trails arcing in from the right, and a burst
    d.arc([x0 + 118, y0 - 6, x0 + 182, y0 + 40], start=200, end=340,
          fill=(255, 140, 40), width=2)
    spark(d, x0 + 152, y0 + 22, 7, (255, 220, 120))
    spark(d, x0 + 152, y0 + 22, 3, (255, 140, 40))
    d.rectangle([x0, y1 - 8, x1, y1], fill=(24, 56, 92))


def pic_grid(d, box):
    """5: the power grid under threat — pylons marching across a
    darkening sky, a substation, and a red warning triangle."""
    x0, y0, x1, y1 = box
    sky(d, box, (30, 44, 78), (48, 64, 104), (70, 88, 128))
    spark(d, x0 + 22, y0 + 10, 3, (255, 255, 255))
    spark(d, x0 + 160, y0 + 8, 3, (255, 255, 255))
    # pylons
    for px, ph in [(x0 + 30, 30), (x0 + 78, 38), (x0 + 126, 30)]:
        d.line([px, y1 - 8, px, y1 - 8 - ph], fill=(20, 20, 24), width=3)
        d.line([px - 12, y1 - 8 - ph + 8, px + 12, y1 - 8 - ph + 8],
               fill=(20, 20, 24), width=2)
        d.line([px - 8, y1 - 8 - ph + 16, px + 8, y1 - 8 - ph + 16],
               fill=(20, 20, 24), width=2)
    d.line([x0 + 30, y1 - 40, x0 + 78, y1 - 48], fill=(20, 20, 24), width=1)
    d.line([x0 + 78, y1 - 48, x0 + 126, y1 - 40], fill=(20, 20, 24), width=1)
    # substation box with lit windows
    d.rectangle([x0 + 142, y1 - 26, x0 + 178, y1 - 8], fill=(60, 60, 66))
    d.rectangle([x0 + 148, y1 - 22, x0 + 156, y1 - 16], fill=(255, 214, 90))
    d.rectangle([x0 + 162, y1 - 22, x0 + 170, y1 - 16], fill=(255, 214, 90))
    # red warning triangle
    d.polygon([(x0 + 62, y0 + 8), (x0 + 76, y0 + 30), (x0 + 48, y0 + 30)],
              fill=(255, 214, 90))
    d.text((x0 + 60, y0 + 14), "!", font=F(SANS_B, 12), fill=RED)
    d.rectangle([x0, y1 - 8, x1, y1], fill=(16, 24, 44))


def pic_kim(d, box):
    """6: the nuclear hall — rows of centrifuge cylinders under a
    green-tinged roof, and a warhead cone on a stand."""
    x0, y0, x1, y1 = box
    sky(d, box, (90, 110, 96), (110, 130, 116), (130, 148, 132))
    d.rectangle([x0, y1 - 14, x1, y1], fill=(60, 70, 64))
    # centrifuge rows: two rows of silver cylinders
    for row, ry in enumerate((y0 + 14, y0 + 30)):
        for cx in range(x0 + 12, x0 + 118, 16):
            d.rectangle([cx, ry, cx + 9, ry + 12], fill=(200, 200, 204))
            d.rectangle([cx, ry, cx + 9, ry + 3], fill=(150, 150, 154))
    # warhead cone on a stand, right
    wx, wy = x0 + 140, y1 - 34
    d.polygon([(wx, wy - 14), (wx + 9, wy), (wx + 18, wy - 14)],
              fill=(178, 44, 44))
    d.rectangle([wx, wy, wx + 18, wy + 12], fill=(90, 90, 94))
    d.rectangle([wx - 4, wy + 12, wx + 22, wy + 16], fill=(60, 60, 64))
    d.line([wx + 9, wy + 16, wx + 9, y1 - 14], fill=(60, 60, 64), width=2)
    spark(d, wx + 9, wy - 20, 4, (255, 220, 120))
    # red star on the wall
    spark(d, x0 + 168, y0 + 12, 6, (178, 44, 44))
    d.rectangle([x0, y1 - 8, x1, y1], fill=(40, 48, 44))


def pic_eu(d, box):
    """7: Brussels — the EU flag, a ring of gold stars on blue, and a
    table with a €45bn loan board."""
    x0, y0, x1, y1 = box
    sky(d, box, (36, 84, 160), (48, 100, 178), (64, 118, 196))
    # EU flag, left: blue field, ring of stars
    fx, fy = x0 + 12, y0 + 6
    d.rectangle([fx, fy, fx + 64, fy + 34], fill=(20, 50, 120))
    for k in range(12):
        ang = math.radians(k * 30 - 90)
        sx = fx + 32 + int(12 * math.cos(ang))
        sy = fy + 17 + int(10 * math.sin(ang))
        spark(d, sx, sy, 2, (255, 214, 0))
    # table with the loan board
    d.rectangle([x0 + 88, y1 - 30, x0 + 178, y1 - 8], fill=(120, 96, 66))
    d.rectangle([x0 + 96, y0 + 10, x0 + 170, y0 + 34], fill=(255, 255, 255),
                outline=NAVY, width=2)
    d.text((x0 + 102, y0 + 14), "€45bn", font=F(SANS_B, 15), fill=NAVY)
    d.text((x0 + 102, y0 + 26), "UKRAINE LOAN", font=F(SANS, 7), fill=MUTED)
    # two figures at the table
    figure(d, x0 + 100, y1 - 44, 11, shirt=(30, 90, 160))
    figure(d, x0 + 156, y1 - 44, 11, shirt=(178, 44, 44))
    d.rectangle([x0, y1 - 8, x1, y1], fill=(20, 40, 80))


def pic_ecb(d, box):
    """8: Frankfurt — the ECB tower, a big euro sign, and a small
    Spanish flag for the incoming chief."""
    x0, y0, x1, y1 = box
    sky(d, box, (150, 196, 220), (178, 212, 232), (206, 226, 240))
    disc(d, x0 + 16, y0 + 8, 7, (255, 214, 90))
    # ECB tower: two slabs with lit windows
    tx, ty = x0 + 96, y1 - 44
    d.rectangle([tx, ty, tx + 40, y1 - 8], fill=(90, 110, 130))
    d.rectangle([tx + 44, ty + 8, tx + 76, y1 - 8], fill=(70, 90, 110))
    for row in range(3):
        for wx in range(tx + 5, tx + 71, 12):
            d.rectangle([wx, ty + 5 + row * 11, wx + 6, ty + 11 + row * 11],
                        fill=(255, 214, 90))
    # big euro sign
    d.text((x0 + 14, y0 + 6), "€", font=F(SANS_B, 34), fill=NAVY)
    # small Spanish flag on a pole
    px, py = x0 + 62, y0 + 12
    d.line([px, py, px, py + 26], fill=(60, 60, 60), width=2)
    d.rectangle([px + 1, py, px + 21, py + 5], fill=(178, 44, 44))
    d.rectangle([px + 1, py + 5, px + 21, py + 10], fill=(255, 214, 0))
    d.rectangle([px + 1, py + 10, px + 21, py + 15], fill=(178, 44, 44))
    d.rectangle([x0, y1 - 8, x1, y1], fill=(90, 110, 130))


def pic_tariffs(d, box):
    """9: the tariff pushback — port cranes over stacked containers,
    a red percent board, and two small flags: China and Brazil."""
    x0, y0, x1, y1 = box
    sky(d, box, (150, 196, 220), (178, 212, 232), (206, 226, 240))
    disc(d, x0 + 16, y0 + 8, 7, (255, 214, 90))
    d.rectangle([x0, y1 - 16, x1, y1], fill=(36, 76, 118))
    # stacked containers
    for i, c in enumerate([(200, 60, 50), (40, 120, 90), (220, 160, 40)]):
        d.rectangle([x0 + 12 + i * 26, y1 - 34, x0 + 34 + i * 26, y1 - 22],
                    fill=c)
    d.rectangle([x0 + 24, y1 - 46, x0 + 46, y1 - 34], fill=(36, 84, 160))
    # crane
    d.line([x0 + 108, y0 + 6, x0 + 108, y1 - 16], fill=(60, 60, 64), width=3)
    d.line([x0 + 108, y0 + 6, x0 + 150, y0 + 6], fill=(60, 60, 64), width=3)
    d.line([x0 + 150, y0 + 6, x0 + 150, y0 + 20], fill=(60, 60, 64), width=2)
    d.rectangle([x0 + 144, y0 + 20, x0 + 156, y0 + 30], fill=(220, 160, 40))
    # percent board
    bx, by = x0 + 122, y0 + 28
    d.rectangle([bx, by, bx + 52, by + 20], fill=(255, 255, 255),
                outline=RED, width=2)
    d.text((bx + 5, by + 2), "+20%", font=F(SANS_B, 13), fill=RED)
    # China and Brazil flags
    for i, cols in enumerate([[(178, 44, 44)], [(40, 120, 90), (255, 214, 0)]]):
        fx = x0 + 126 + i * 26
        d.line([fx, by - 12, fx, by - 2], fill=(60, 60, 60), width=1)
        for j, col in enumerate(cols):
            d.rectangle([fx + 1 + j * 10, by - 12, fx + 11 + j * 10, by - 2],
                        fill=col)
    d.rectangle([x0, y1 - 8, x1, y1], fill=(24, 56, 92))


def pic_bangkok(d, box):
    """10: the Bangchak refinery — distillation towers, a flame and
    smoke at the hydrocracking unit, and a red fire truck."""
    x0, y0, x1, y1 = box
    sky(d, box, (232, 196, 150), (224, 182, 138), (212, 166, 124))
    disc(d, x0 + 16, y0 + 8, 7, (255, 214, 90))
    # distillation towers
    for tx, th in [(x0 + 24, 30), (x0 + 52, 38), (x0 + 80, 26)]:
        d.rectangle([tx, y1 - 14 - th, tx + 16, y1 - 14], fill=(150, 150, 154))
        d.rectangle([tx + 3, y1 - 14 - th - 5, tx + 13, y1 - 14 - th],
                    fill=(120, 120, 124))
    # flame and smoke at the middle tower
    fire(d, x0 + 60, y1 - 50, 16)
    puff(d, x0 + 44, y0 + 4, 16, (110, 110, 116))
    puff(d, x0 + 70, y0 + 12, 12, (130, 130, 134))
    # fire truck at the right
    fx, fy = x0 + 118, y1 - 30
    d.rectangle([fx, fy, fx + 58, fy + 14], fill=(178, 34, 34))
    d.rectangle([fx + 42, fy - 9, fx + 58, fy], fill=(178, 34, 34))
    d.rectangle([fx + 45, fy - 7, fx + 55, fy - 2], fill=(180, 220, 240))
    disc(d, fx + 12, fy + 14, 5, (20, 20, 20))
    disc(d, fx + 46, fy + 14, 5, (20, 20, 20))
    d.rectangle([fx + 6, fy + 3, fx + 36, fy + 7], fill=(240, 240, 238))
    d.rectangle([x0, y1 - 8, x1, y1], fill=(120, 104, 84))


def pic_bok(d, box):
    """11: Seoul — a central bank building, a green up arrow, and a
    board reading 3.25%."""
    x0, y0, x1, y1 = box
    sky(d, box, (150, 196, 220), (178, 212, 232), (206, 226, 240))
    disc(d, x0 + 16, y0 + 8, 7, (255, 214, 90))
    # bank building with columns
    bx, by = x0 + 18, y1 - 40
    d.rectangle([bx, by, bx + 84, y1 - 8], fill=(200, 196, 188))
    d.polygon([(bx - 4, by), (bx + 42, by - 12), (bx + 88, by)],
              fill=(160, 156, 148))
    for cx in range(bx + 8, bx + 78, 16):
        d.rectangle([cx, by + 6, cx + 6, y1 - 12], fill=(150, 146, 138))
    # up arrow
    ax, ay = x0 + 118, y0 + 34
    d.line([ax, ay + 12, ax, ay - 14], fill=GREEN, width=4)
    d.polygon([(ax - 7, ay - 8), (ax, ay - 18), (ax + 7, ay - 8)], fill=GREEN)
    # rate board
    d.rectangle([x0 + 132, y0 + 8, x0 + 178, y0 + 32], fill=(255, 255, 255),
                outline=GREEN, width=2)
    d.text((x0 + 136, y0 + 11), "3.25%", font=F(SANS_B, 12), fill=GREEN)
    d.rectangle([x0, y1 - 8, x1, y1], fill=(90, 110, 130))


def pic_gdp(d, box):
    """12: the GDP row — two bars, 3.4% then 4.3%, a magnifier over
    the revision, and a podium with a microphone."""
    x0, y0, x1, y1 = box
    sky(d, box, (220, 232, 238), (206, 224, 232), (190, 212, 224))
    # bar chart: 3.4% (grey) and 4.3% (green), axis at the bottom
    d.line([x0 + 12, y1 - 16, x0 + 110, y1 - 16], fill=INK, width=1)
    d.rectangle([x0 + 22, y1 - 34, x0 + 48, y1 - 16], fill=(150, 150, 154))
    d.rectangle([x0 + 58, y1 - 42, x0 + 84, y1 - 16], fill=GREEN)
    d.text((x0 + 24, y1 - 46), "3.4%", font=F(SANS_B, 10), fill=MUTED)
    d.text((x0 + 60, y1 - 54), "4.3%", font=F(SANS_B, 10), fill=GREEN)
    # magnifier over the taller bar
    disc(d, x0 + 96, y0 + 16, 9, (255, 255, 255))
    d.ellipse([x0 + 87, y0 + 7, x0 + 105, y0 + 25], outline=INK, width=2)
    d.line([x0 + 102, y0 + 22, x0 + 112, y0 + 32], fill=INK, width=2)
    # podium with a microphone, right
    px, py = x0 + 128, y1 - 34
    d.polygon([(px, py), (px + 44, py), (px + 38, y1 - 8), (px + 6, y1 - 8)],
              fill=(90, 84, 74))
    d.line([px + 22, py, px + 22, py - 14], fill=(40, 40, 44), width=2)
    disc(d, px + 22, py - 16, 4, (40, 40, 44))
    d.rectangle([x0, y1 - 8, x1, y1], fill=(90, 84, 74))


def pic_markets(d, box):
    """13: the rebound board — three ticker rows, all green: Nikkei,
    Kospi and DAX, each with an up triangle."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(244, 240, 228))
    rows = [("NIKKEI", "57,499", "+0.86%"),
            ("KOSPI", "4,711", "+0.29%"),
            ("DAX", "25,180", "+1.9%")]
    for i, (name, lvl, chg) in enumerate(rows):
        ry = y0 + 4 + i * 18
        d.text((x0 + 8, ry), name, font=F(SANS_B, 10), fill=INK)
        d.text((x0 + 66, ry - 1), lvl, font=F(SERIF_B, 12), fill=INK)
        tx, ty = x0 + 126, ry + 7
        d.polygon([(tx, ty + 4), (tx + 4, ty - 3), (tx + 8, ty + 4)],
                  fill=GREEN)
        d.text((x0 + 138, ry), chg, font=F(SANS_B, 10), fill=GREEN)
        if i < 2:
            d.line([x0 + 6, ry + 15, x1 - 6, ry + 15], fill=(210, 204, 190),
                   width=1)
    d.rectangle([x0, y1 - 8, x1, y1], fill=(232, 224, 204))


PICS = {1: pic_gaza, 2: pic_kuwait, 3: pic_ebola, 4: pic_houthi,
        5: pic_grid, 6: pic_kim, 7: pic_eu, 8: pic_ecb, 9: pic_tariffs,
        10: pic_bangkok, 11: pic_bok, 12: pic_gdp, 13: pic_markets}

# ---------- story data ----------
# (num, region, topic, source, tag, headline, summary)
HEROES = [
    (1, "MIDDLE EAST", "GAZA", "REUTERS", "CONFIRMED",
     "Gaza strikes kill 9",
     "Abu Nada and wife die at dawn; 3rd night of raids despite ceasefire."),
    (2, "MIDDLE EAST", "KUWAIT", "REUTERS", "CONFIRMED",
     "Kuwait drones kill 2 Italians",
     "Italy and Kuwait blame Iran; Tehran denies it. Rheinmetall technicians."),
    (3, "AFRICA", "HEALTH", "AP", "CONFIRMED",
     "Ebola passes 12,000 cases",
     "Fastest-growing outbreak on record; fighting stalls responders."),
]
SECONDARY = [
    (4, "MIDDLE EAST", "SAUDI", "AP", "OFFICIAL",
     "Houthis hit Jazan port",
     "Riyadh missiles intercepted; 1 worker killed at Jazan refinery."),
    (5, "EUROPE", "UKRAINE", "AP", "OFFICIAL",
     "Zelenskyy warns of grid attack",
     "Trump tells Putin to pull back; Kushner cites nuclear pledge."),
    (6, "ASIA", "N. KOREA", "REUTERS", "REPORTED",
     "Kim widens nuclear push",
     "Tactical nukes for 'multiple domains'; arsenal 'irreversible'."),
    (7, "EUROPE", "EU", "AP", "CONFIRMED",
     "EU split over €45bn loan",
     "Ukraine loan and €2tn budget divide leaders in Brussels."),
    (8, "EUROPE", "ECB", "AP", "OFFICIAL",
     "Hernández de Cos to lead ECB",
     "Spain's ex-central bank chief succeeds Lagarde in February."),
    (9, "ASIA", "TRADE", "AL JAZEERA", "CONFIRMED",
     "China, Brazil hit back at tariffs",
     "Beijing calls overcapacity claim 'false'; Brasília vows reply."),
    (10, "ASIA", "THAILAND", "AP", "CONFIRMED",
     "Bangkok refinery blast hurts 9",
     "Fire at Bangchak plant; all units shut, 3 critical."),
    (11, "ASIA", "S. KOREA", "REUTERS", "OFFICIAL",
     "Bank of Korea lifts rate to 3.25%",
     "Two-year high; third hike of 2026 on chip boom."),
    (12, "AMERICAS", "USA", "AP", "OFFICIAL",
     "Trump calls GDP figures 'fake'",
     "Demands probe of Commerce Dept; revision 3.4% to 4.3%."),
    (13, "GLOBAL", "MARKETS", "AP", "OFFICIAL",
     "World stocks rebound",
     "Nikkei +0.86% to 57,499; DAX +1.9%; US shut for Thanksgiving."),
]
LISTED = [
    "Serbia sets presidential vote for 27 Dec",
    "Chess game 3: 60-move draw, 1.5–1.5",
    "Depardieu to stand trial on rape charge",
    "UK writes to 100,000 reserve veterans",
    "Judge blocks FCC early review of ABC",
    "Mexico president blasts DEA tip lines",
    "Trump to visit TSMC Arizona expansion",
    "Nor'easter floods US East on Thanksgiving",
    "Gausman joins Tigers on $25m deal",
    "Bears' Loveland hurt in Lions game",
    "Egypt detains driver in tanker crash",
    "Kenya court: Ebola centre unlawful",
    "Irbil protests over Kurdish oil seizure",
    "Iran arrests activist Mahmoudian",
    "Bangladesh arrests two police officers",
    "Pakistan hails Shenzhou astronaut flight",
    "UK net migration falls; Indians top exits",
    "Spain's far right eyes power",
    "Alpine Fault mapped in fine detail",
    "Audit slams Australia sanctions office",
    "AP Gaza team wins Rory Peck prize",
    "Macy's parade acts in limbo",
]
REGIONS = [("EUROPE", 9, (36, 84, 160)), ("AMERICAS", 8, (14, 128, 128)),
           ("ASIA", 6, (122, 62, 158)), ("AFRICA", 3, (46, 134, 74)),
           ("MIDDLE EAST", 5, (178, 44, 44)), ("OCEANIA", 2, (214, 122, 26)),
           ("GLOBAL", 2, (96, 96, 100))]
FIELDS = ["CONFLICT", "HEALTH", "SECURITY", "POLITICS", "ECONOMY",
          "TRADE", "DISASTER", "MARKETS", "SPORT", "CULTURE", "MEDIA",
          "WEATHER", "JUSTICE", "SCIENCE", "MIGRATION"]
# numbers strip: six cells, two rows of three; each a complete mini-story
NUMBERS = [("9", "killed in Gaza strikes overnight"),
           ("12,021", "Ebola cases in DR Congo"),
           ("2", "Italians killed in Kuwait drone attack"),
           ("3.25%", "Bank of Korea base rate, a 2-year high"),
           ("57,499", "Nikkei close after the AI rebound"),
           ("€45bn", "EU loan for Ukraine debated in Brussels")]
# timeline strip: seven timed events across the day (UTC)
TIMELINE = [("00:58", "Bank of Korea lifts rate"),
            ("07:45", "Bangkok refinery blast"),
            ("11:00", "Kuwait drones kill 2"),
            ("13:47", "Ebola tops 12,000 cases"),
            ("14:00", "Chess game 3 begins"),
            ("16:03", "Zelenskyy warns of attack"),
            ("21:20", "Trump calls GDP 'fake'")]
# map pins: (num, x, y); red for 1-3, navy for 4-13
PINS = [(1, 228, 864), (2, 244, 856), (3, 210, 892), (4, 240, 876),
        (5, 214, 842), (6, 297, 862), (7, 194, 840), (8, 203, 850),
        (9, 278, 866), (10, 268, 884), (11, 286, 849), (12, 96, 848),
        (13, 306, 846)]
LAND = [  # ellipses (x0, y0, x1, y1) forming a coarse dotted world map
    (45, 826, 170, 880), (175, 824, 200, 837), (130, 883, 185, 940),
    (185, 837, 235, 862), (190, 865, 250, 929), (235, 830, 310, 880),
    (255, 880, 285, 897), (265, 912, 305, 935), (180, 840, 192, 851),
    (300, 844, 312, 862), (235, 862, 265, 894), (190, 855, 230, 869),
    (165, 840, 195, 858), (205, 865, 235, 887), (185, 826, 205, 844),
    (308, 928, 318, 940),
]


def kicker(d, x, y, num, region, topic, src, tag, width, size=10):
    """Left: 'N · REGION · TOPIC'; right: 'SOURCE · TAG'. Drops topic if tight."""
    f, sf = F(SANS_B, size), F(SANS, size - 1)
    right = f"{src} · {tag}"
    full = f"{num} · {region} · {topic}"
    if d.textlength(full, font=f) + d.textlength(right, font=sf) + 12 > width:
        full = f"{num} · {region}"
    d.text((x, y), full, font=f, fill=RED)
    d.text((x + width - d.textlength(right, font=sf), y), right, font=sf,
           fill=MUTED)


def kicker2(d, x, y, num, region, topic, src, tag, width):
    """Two-line kicker for the narrow secondary cards: line 1 is the
    number/region/topic, line 2 is the source and verification tag."""
    d.text((x, y), f"{num} · {region} · {topic}", font=F(SANS_B, 9), fill=RED)
    d.text((x, y + 11), f"{src} · {tag}", font=F(SANS, 8), fill=MUTED)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 24
    X1 = W - M

    # ---- header ----
    d.rectangle([M, 14, 116, 136], fill=RED)
    d.text((30, 20), "NOV", font=F(SANS_B, 22), fill=(255, 255, 255))
    d.text((30, 44), "26", font=F(SERIF_B, 52), fill=(255, 255, 255))
    d.text((30, 104), "THU 2026", font=F(SANS_B, 13), fill=(255, 255, 255))
    d.text((132, 18), "THE DAY IN WORLD NEWS", font=F(SANS_B, 15), fill=RED)
    d.text((132, 38), "Thursday 26 November 2026", font=F(SERIF_B, 44), fill=INK)
    d.text((132, 98),
           "Everything on this page happened, or was first reported, on Thursday 26 November 2026.",
           font=F(SANS, 15), fill=MUTED)
    for i, line in enumerate(["35 STORIES", "7 REGIONS", "15 FIELDS"]):
        f = F(SANS_B, 19)
        d.text((X1 - d.textlength(line, font=f), 24 + i * 26), line, font=f, fill=INK)
    d.line([M, 142, X1, 142], fill=INK, width=2)

    # ---- timeline strip: seven timed events across the day ----
    ty = 147
    d.text((M, ty), "THE DAY IN UTC", font=F(SANS_B, 11), fill=RED)
    tw = (X1 - M) / 7
    for i, (t, lab) in enumerate(TIMELINE):
        cx = M + i * tw
        d.text((cx, ty + 13), t, font=F(SANS_B, 12), fill=RED)
        put_text(d, (cx, ty + 26), lab, F(SANS, 9), tw - 8, INK, leading=1,
                 limit=1)
    d.line([M, 182, X1, 182], fill=RULE, width=1)

    # ---- region strip ----
    y0, y1 = 186, 210
    total_w = X1 - M
    widths = [max(64, int(total_w * n / 35)) for _, n, _ in REGIONS]
    scale = total_w / sum(widths)
    widths = [int(w * scale) for w in widths]
    widths[-1] += total_w - sum(widths)
    x = M
    for (name, n, col), w in zip(REGIONS, widths):
        d.rectangle([x, y0, x + w - 1, y1], fill=col)
        label = f"{name} {n}"
        f = F(SANS_B, 13)
        if d.textlength(label, font=f) <= w - 8:
            d.text((x + (w - d.textlength(label, font=f)) / 2, y0 + 6),
                   label, font=f, fill=(255, 255, 255))
        else:
            f2 = F(SANS_B, 10)
            d.text((x + (w - d.textlength(name, font=f2)) / 2, y0 + 2),
                   name, font=f2, fill=(255, 255, 255))
            d.text((x + (w - d.textlength(str(n), font=f2)) / 2, y0 + 13),
                   str(n), font=f2, fill=(255, 255, 255))
        x += w

    # ---- numbers strip: six cells, two rows of three ----
    ny = 216
    for row in range(2):
        for col in range(3):
            num, lab = NUMBERS[row * 3 + col]
            cx = M + col * 325
            cy = ny + row * 23
            f1, f2 = F(SANS_B, 16), F(SANS, 11)
            d.text((cx, cy), num, font=f1, fill=RED)
            lx = cx + d.textlength(num + " ", font=f1)
            d.text((lx, cy + 3), lab, font=f2, fill=INK)
            end = lx + d.textlength(lab, font=f2)
            if end > X1:
                print(f"OVERFLOW: numbers cell {num!r} ends at {end}, edge {X1}")
    d.line([M, 266, X1, 266], fill=RULE, width=1)

    # ---- hero stories ----
    hy, hh = 272, 228
    hw, gap = 312, 20
    for i, (num, region, topic, src, tag, head, summ) in enumerate(HEROES):
        x = M + i * (hw + gap)
        d.rectangle([x, hy, x + hw, hy + hh], fill=CARD, outline=RULE, width=1)
        PICS[num](d, (x + 1, hy + 1, x + hw - 1, hy + 125))
        ky = hy + 132
        kicker(d, x + 10, ky, num, region, topic, src, tag, hw - 20, size=11)
        y2 = put_text(d, (x + 10, ky + 17), head, F(SERIF_B, 21),
                      hw - 20, INK, leading=1, limit=2)
        put_text(d, (x + 10, y2 + 3), summ, F(SANS, 12),
                 hw - 20, MUTED, leading=1, limit=2)

    # ---- secondary stories: 5 columns x 2 rows ----
    sy = 508
    cw, cgap = 187, 10
    ch = 140
    for i, (num, region, topic, src, tag, head, summ) in enumerate(SECONDARY):
        col, row = i % 5, i // 5
        x = M + col * (cw + cgap)
        yy = sy + row * (ch + 8)
        d.rectangle([x, yy, x + cw, yy + ch], fill=CARD, outline=RULE, width=1)
        PICS[num](d, (x + 1, yy + 1, x + cw - 1, yy + 57))
        kicker2(d, x + 8, yy + 61, num, region, topic, src, tag, cw - 16)
        y2 = put_text(d, (x + 8, yy + 86), head, F(SERIF_B, 14),
                      cw - 16, INK, leading=1, limit=2)
        put_text(d, (x + 8, y2 + 2), summ, F(SANS, 10),
                 cw - 16, MUTED, leading=1, limit=2)

    # ---- map + list ----
    my = 804
    d.line([M, my - 4, X1, my - 4], fill=INK, width=2)
    d.text((M, my), "WHERE IT HAPPENED", font=F(SANS_B, 14), fill=INK)
    d.text((330, my), "ALSO ON THURSDAY 26 NOVEMBER — 22 MORE STORIES",
           font=F(SANS_B, 14), fill=INK)
    # dotted map
    mx0, my0, mx1, my1 = M, my + 20, 318, 940
    for gx in range(mx0, mx1, 6):
        for gy in range(my0, my1, 6):
            cx, cy = gx + 3, gy + 3
            if any((cx - (a + c) / 2) ** 2 / (((c - a) / 2) ** 2) +
                   (cy - (b + e) / 2) ** 2 / (((e - b) / 2) ** 2) <= 1
                   for a, b, c, e in LAND):
                d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=MAPDOT)
    for num, px, py in PINS:
        col = RED if num <= 3 else NAVY
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=col,
                  outline=(255, 255, 255), width=1)
        f = F(SANS_B, 9 if num < 10 else 8)
        t = str(num)
        d.text((px - d.textlength(t, font=f) / 2, py - 5), t, font=f,
               fill=(255, 255, 255))
    d.text((M, 944),
           "Europe 9 · Americas 8 · Asia 6 · Middle East 5 · Africa 3 · Oceania 2 · Global 2",
           font=F(SANS, 9), fill=MUTED)
    # numbered list, two columns of 11
    lf = F(SANS, 11)
    for i, item in enumerate(LISTED):
        col = i // 11
        row = i % 11
        lx = 330 + col * 336
        ly = my + 22 + row * 10.5
        num = 14 + i
        d.text((lx, ly), f"{num}", font=F(SANS_B, 11), fill=RED)
        d.text((lx + 22, ly), item, font=lf, fill=INK)

    # ---- date check box ----
    by0 = 954
    d.rectangle([M, by0, X1, by0 + 48], outline=RED, width=2)
    d.text((M + 10, by0 + 3), "DATE CHECK", font=F(SANS_B, 12), fill=RED)
    d.text((M + 108, by0 + 3),
           "Left out on purpose — each was first reported before Thursday:",
           font=F(SANS, 12), fill=INK)
    dc = F(SANS, 9)
    d.text((M + 10, by0 + 16),
           "Cairo fire 31 · Iran tankers hit mines · US tariffs on 14 · Shenzhou 24 launches · FCC 1m SpaceX sats · Iowa blast · Australia tech bill · Solomons pact (all 25 Nov)",
           font=dc, fill=MUTED)
    d.text((M + 10, by0 + 26),
           "Sudan strikes 19 · Nigeria 30 killed · Abuelouf killed · Ras Tanura claim · Macy's parade postponed · 1Password breach · FedEx Miami overrun · Kyiv missiles 2 (25 Nov) · Canary record (24 Nov)",
           font=dc, fill=MUTED)
    d.text((M + 10, by0 + 36),
           "Not yet: Macy's parade (Sat 28 Nov) · Chess game 4 (Sat) · Taiwan vote + nuclear poll (Sat) · NZ election result (Fri) · EU summit ends (Fri) · Serbia vote 27 Dec · Tariff hearing 25 Jan",
           font=dc, fill=RED)
    # ---- footer ----
    d.text((M, 1006),
           "Tags: CONFIRMED — two or more outlets · OFFICIAL — on the record · REPORTED — one outlet",
           font=F(SANS, 8), fill=MUTED)
    d.text((M, 1015),
           "Sources: Reuters · AP · BBC · Al Jazeera · PTI · AAP",
           font=F(SANS, 8), fill=MUTED)
    attr = "Original drawings. Claims are attributed, not stated as fact."
    d.text((X1 - d.textlength(attr, font=F(SANS, 8)), 1015), attr,
           font=F(SANS, 8), fill=MUTED)

    total = len(HEROES) + len(SECONDARY) + len(LISTED)
    rsum = sum(n for _, n, _ in REGIONS)
    print(f"counts: heroes {len(HEROES)} + secondary {len(SECONDARY)} + listed {len(LISTED)} = {total}; regions sum {rsum}; fields {len(FIELDS)}")
    assert total == 35 and rsum == 35, "counts do not reconcile to 35"
    assert len(FIELDS) == 15, "field count wrong"

    img.save("entry.png", optimize=True)
    print("saved entry.png", img.size, "bytes:", os.path.getsize("entry.png"))


if __name__ == "__main__":
    main()
