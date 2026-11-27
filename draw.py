#!/usr/bin/env python3
"""The World in One Day -- Thursday 26 November 2026.

A one-page newspaper front page drawn from scratch with Pillow.
Every story on the page happened, or was first reported, on
Thursday 26 November 2026 (any time zone). Stories that belong to
another day are kept out of the news columns and named only in the
DATE CHECK box, so the reader can see where the day ends.

Layout, top to bottom: masthead, THE DAY IN UTC timeline, numbers
strip, three hero panels, ten secondary cards, dotted world map with
region counts, a numbered list of the remaining stories, the DATE
CHECK box, and a sources footer.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = 1024
MARGIN = 14
GUT = 8
CONTENT = PAGE - 2 * MARGIN  # 996

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)
INK = (20, 20, 20)
SOFT = (84, 84, 78)
FAINT = (150, 146, 136)
CARD = (255, 255, 255)
HAIR = (206, 200, 186)
RED = (178, 34, 24)
BLUE = (31, 58, 95)
TEAL = (14, 107, 107)
GOLD = (176, 124, 12)
SKY = (38, 52, 84)
SAND = (227, 201, 143)
DUSK = (232, 146, 84)

# ---------------------------------------------------------------- fonts
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def load(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


class Type:
    """The typefaces used across the page, loaded once."""

    def __init__(self):
        self.mast = load(SERIF_B, 40)
        self.date = load(SANS, 14)
        self.counts = load(SANS_B, 13)
        self.fields = load(SANS, 10)
        self.sect = load(SANS_B, 12)
        self.time = load(SANS_B, 14)
        self.tline = load(SANS, 11)
        self.bignum = load(SANS_B, 27)
        self.numlab = load(SANS, 10)
        self.hero_head = load(SANS_B, 16)
        self.hero_deck = load(SANS, 12)
        self.banner = load(SANS_B, 13)
        self.tag = load(SANS_B, 9)
        self.src = load(SANS, 10)
        self.sec_head = load(SANS_B, 13)
        self.map_title = load(SANS_B, 12)
        self.region = load(SANS, 12)
        self.region_b = load(SANS_B, 12)
        self.list_no = load(SANS_B, 12)
        self.list_tx = load(SANS, 12)
        self.dc_title = load(SANS_B, 11)
        self.dc_body = load(SANS, 10)
        self.foot = load(SANS, 10)
        self.foot_b = load(SANS_B, 10)
        self.pin = load(SANS_B, 11)


F = Type()

# ---------------------------------------------------------------- data
FIELDS = [
    "CONFLICT", "HEALTH", "SECURITY", "POLITICS", "ECONOMY", "TRADE",
    "DISASTER", "MARKETS", "SPORT", "CULTURE", "MEDIA", "WEATHER",
    "JUSTICE", "SCIENCE", "MIGRATION",
]

TIMELINE = [
    ("00:58", "Bank of Korea lifts its rate"),
    ("07:45", "Bangkok refinery blast"),
    ("11:00", "Kuwait drones kill 2 Italians"),
    ("13:47", "Ebola cases pass 12,000"),
    ("14:00", "Chess game 3 begins"),
    ("16:03", "Zelenskyy warns of grid attack"),
    ("21:20", "Trump calls GDP figures fake"),
]

NUMBERS = [
    ("9", "killed in Gaza strikes"),
    ("12,021", "Ebola cases worldwide"),
    ("2", "Italians killed in Kuwait"),
    ("3.25%", "Bank of Korea rate"),
    ("57,499", "Nikkei close"),
    ("€45bn", "EU loan for Ukraine"),
]

REGIONS = [
    ("EUROPE", 9), ("AMERICAS", 8), ("ASIA", 6), ("MIDDLE EAST", 5),
    ("AFRICA", 3), ("OCEANIA", 2), ("GLOBAL", 2),
]

HEROES = [
    {
        "num": "1",
        "art": "gaza",
        "headline": "Strikes kill 9 in Gaza as ceasefire frays",
        "deck": "Abu Nada, a Hamas deputy minister, and his wife die "
                "at dawn in Deir al-Balah — a third straight night "
                "of raids.",
        "banner": "9 KILLED IN GAZA",
        "tag": "CONFIRMED",
        "src": "Reuters · AP",
    },
    {
        "num": "2",
        "art": "kuwait",
        "headline": "Drones kill 2 Italians in Kuwait",
        "deck": "Iranian drones hit an air-defence site at about "
                "14:00 local. Rome and Kuwait City blame Tehran; "
                "Iran denies it.",
        "banner": "2 ITALIANS KILLED",
        "tag": "CONFIRMED",
        "src": "Reuters · BBC",
    },
    {
        "num": "3",
        "art": "ebola",
        "headline": "Ebola cases pass 12,000",
        "deck": "12,021 cases, 5,904 dead — the fastest-growing "
                "outbreak on record. Bundibugyo strain, now in "
                "8 of 26 provinces.",
        "banner": "12,021 CASES · 5,904 DEAD",
        "tag": "CONFIRMED",
        "src": "AP · Reuters",
    },
]

SECONDARY = [
    ("Houthis hit Jazan port; 1 killed at refinery", "OFFICIAL"),
    ("Zelenskyy warns of imminent grid attack", "OFFICIAL"),
    ("Kim orders wider tactical nuclear deployment", "REPORTED"),
    ("EU split over €45bn Ukraine loan", "REPORTED"),
    ("Hernández de Cos picked as next ECB chief", "REPORTED"),
    ("China, Brazil push back on US tariffs", "REPORTED"),
    ("Bangkok refinery blast injures 9", "CONFIRMED"),
    ("Bank of Korea lifts rate to 3.25%", "CONFIRMED"),
    ("Trump calls GDP figures “fake”", "REPORTED"),
    ("Stocks rebound; Nikkei tops 57,499", "CONFIRMED"),
]

LISTED = [
    "Serbia vote 27 Dec",
    "Chess game 3, 60-move draw, 1.5–1.5",
    "Depardieu trial",
    "UK writes to 100,000 reserve veterans",
    "Judge blocks FCC review of ABC",
    "Mexico president blasts DEA",
    "Trump to visit TSMC Arizona",
    "Nor’easter floods US East",
    "Gausman to Tigers $25m",
    "Bears’ Loveland hurt",
    "Egypt detains Cairo tanker driver",
    "Kenya court rules Ebola centre unlawful",
    "Irbil protests",
    "Iran arrests activist Mahmoudian",
    "Bangladesh arrests two police officers",
    "Pakistan hails Shenzhou flight",
    "UK net migration falls",
    "Spain’s far right eyes power",
    "Alpine Fault mapped in fine detail",
    "Audit slams Australia sanctions office",
    "AP Gaza team wins Rory Peck prize",
    "Macy’s parade acts in limbo",
]

EXCLUDED = (
    "Cairo fire, 31 dead · Iran tankers hit mines · US tariffs on 14 partners · "
    "Shenzhou-24 launch · FCC approves 1m SpaceX satellites · Iowa blast · "
    "Australia tech bill · Solomons pact · Sudan strikes, 19 dead · Nigeria, "
    "30 killed · Abuelouf killed · Ras Tanura claim · Macy’s parade postponed · "
    "1Password breach · FedEx Miami overrun · Kyiv missiles, 2 dead · Canary "
    "record arrivals, 1,990 (24 Nov) · Chess game 2 · GDP 4.3% · Netanyahu "
    "bribery plea · Eni/Repsol $2bn Venezuela pledge · Sydney runway scare, "
    "QF426 (25 Nov morning) — all 25 November unless noted."
)

NOT_YET = (
    "Not yet: Macy’s parade (Sat 28 Nov) · Chess game 4 (Sat) · Taiwan vote "
    "+ nuclear poll (Sat) · NZ election result (Fri 27 Nov) · EU summit ends "
    "(Fri) · Serbia vote 27 Dec · Tariff hearing 25 Jan 2027."
)

# A rough dotted world, 64 columns by 22 rows, drawn from memory.
# '#' marks land. Columns run west to east, rows north to south.
WORLD = [
    "........#####..........................##########..............",
    "...############......................##################......",
    "..###############........######......#####################....",
    "..###############.......#######......####################....",
    "...##############.......######.......###################......",
    "....############.........####.........###############.........",
    ".....##########.........#######........############...........",
    "......########..........########.......##########............",
    "......######...####.....#########........######...............",
    ".............######.....########.............................",
    ".............######.....#######..............................",
    ".............#####......#######..............................",
    ".............####.......######.........####...................",
    ".............###.........####.........######..................",
    ".............###......................######.................",
    ".............##........................#####..................",
    ".............##..............................................",
    "............................................................",
    "............................................................",
    "............................................................",
]

PINS = [
    # (grid col, grid row, number) -- Gaza, Kuwait, DR Congo
    (38, 7, "1"),
    (41, 6, "2"),
    (36, 11, "3"),
]

# ---------------------------------------------------------------- helpers
def text_w(s, font):
    return font.getlength(s)


def wrap(s, font, width):
    """Split s into lines that fit width pixels, word by word."""
    words = s.split()
    if not words:
        return [""]
    lines = []
    cur = words[0]
    for w in words[1:]:
        trial = cur + " " + w
        if text_w(trial, font) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def fit_lines(s, font, width, max_lines):
    """Wrap s, shrinking the font one step at a time if it runs long."""
    lines = wrap(s, font, width)
    while len(lines) > max_lines and font.size > 8:
        font = load(SANS_B if font is F.sec_head or font is F.hero_head
                    else SANS, font.size - 1)
        lines = wrap(s, font, width)
    return lines, font


def block_h(lines, font, leading=1.25):
    return int(len(lines) * font.size * leading)


def paint_wrapped(d, x, y, s, font, fill, width, leading=1.25):
    lines = wrap(s, font, width)
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += int(font.size * leading)
    return y


def tag_chip(d, x, y, label, fg, bg):
    """A small filled tag; returns its width."""
    pad_x, pad_y = 5, 2
    w = int(text_w(label, F.tag)) + 2 * pad_x
    h = F.tag.size + 2 * pad_y
    d.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=bg)
    d.text((x + pad_x, y + pad_y), label, font=F.tag, fill=fg)
    return w


def hairline(d, x0, x1, y, fill=HAIR):
    d.line([(x0, y), (x1, y)], fill=fill, width=1)


def section_head(d, x, y, title, width):
    d.text((x, y), title, font=F.sect, fill=INK)
    hairline(d, x, x + width, y + F.sect.size + 4)
    return y + F.sect.size + 9


# ---------------------------------------------------------------- masthead
def paint_masthead(d, x, y, w):
    title = "THE WORLD IN ONE DAY"
    tw = text_w(title, F.mast)
    d.text((x + (w - tw) / 2, y), title, font=F.mast, fill=INK)
    y += F.mast.size + 4
    d.text((x, y), "Thursday, 26 November 2026", font=F.date, fill=SOFT)
    right = "35 STORIES · 7 REGIONS · 15 FIELDS"
    d.text((x + w - text_w(right, F.counts), y), right,
           font=F.counts, fill=RED)
    y += F.date.size + 4
    fields = " · ".join(FIELDS)
    d.text((x, y), fields, font=F.fields, fill=FAINT)
    y += F.fields.size + 4
    d.rectangle([x, y, x + w, y + 3], fill=INK)
    y += 3 + GUT
    return y


# ---------------------------------------------------------------- timeline
def paint_timeline(d, x, y, w):
    y = section_head(d, x, y, "THE DAY IN UTC", w)
    cell = (w - 6 * GUT) // 7
    top = y
    for i, (t, evt) in enumerate(TIMELINE):
        cx = x + i * (cell + GUT)
        d.text((cx, top), t, font=F.time, fill=RED)
        lines = wrap(evt, F.tline, cell)
        ly = top + F.time.size + 3
        for ln in lines[:3]:
            d.text((cx, ly), ln, font=F.tline, fill=INK)
            ly += int(F.tline.size * 1.2)
        if i < 6:
            d.line([(cx + cell + GUT // 2, top),
                    (cx + cell + GUT // 2, top + 44)], fill=HAIR, width=1)
    return top + 48


# ---------------------------------------------------------------- numbers
def paint_numbers(d, x, y, w):
    cell = (w - 5 * GUT) // 6
    for i, (val, lab) in enumerate(NUMBERS):
        cx = x + i * (cell + GUT)
        d.rectangle([cx, y, cx + cell, y + 46], outline=HAIR, width=1)
        vw = text_w(val, F.bignum)
        d.text((cx + (cell - vw) / 2, y + 4), val, font=F.bignum, fill=BLUE)
        lw = text_w(lab, F.numlab)
        d.text((cx + (cell - lw) / 2, y + 30), lab, font=F.numlab, fill=SOFT)
    return y + 46 + GUT

# ---------------------------------------------------------------- hero art
def art_gaza(d, x, y, w, h):
    """Dusk sky, rooftops, smoke rising, a pale moon."""
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + h * 2 // 3, x + w, y + h], fill=DUSK)
    d.ellipse([x + w - 52, y + 10, x + w - 22, y + 40], fill=(238, 232, 214))
    base = y + h
    for bx, bw, bh in [(0, 52, 34), (58, 40, 52), (104, 62, 30),
                       (172, 44, 46), (222, 56, 36), (284, 42, 28)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(24, 24, 30))
        for wy in range(base - bh + 6, base - 6, 12):
            d.rectangle([x + bx + 8, wy, x + bx + 13, wy + 5],
                        fill=(240, 200, 90))
    for cx, cy, r in [(96, y + 26, 12), (108, y + 12, 16), (122, y + 4, 11)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 118, 112))


def art_kuwait(d, x, y, w, h):
    """Desert, sun, radar mast, two drones, a blast starburst."""
    d.rectangle([x, y, x + w, y + h], fill=SAND)
    d.ellipse([x + 18, y + 12, x + 52, y + 46], fill=(242, 214, 130))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(198, 164, 102))
    mx, my = x + w // 2, y + h - 26
    d.line([(mx, my), (mx, my - 46)], fill=INK, width=3)
    d.arc([mx - 30, my - 62, mx + 30, my - 34], 180, 360, fill=INK, width=3)
    d.line([(mx - 30, my - 48), (mx + 30, my - 48)], fill=INK, width=3)
    for dx, dy in [(x + 52, y + 30), (x + w - 78, y + 22)]:
        d.ellipse([dx, dy, dx + 26, dy + 9], fill=(40, 40, 40))
        d.line([(dx - 6, dy - 3), (dx + 32, dy - 3)], fill=(40, 40, 40),
               width=2)
        d.line([(dx + 11, dy + 9), (dx + 15, dy + 16)], fill=(40, 40, 40),
               width=2)
    bx, by = x + w - 44, y + h - 44
    for ang in range(0, 360, 30):
        import math
        r = math.radians(ang)
        d.line([(bx, by),
                (bx + int(16 * math.cos(r)), by + int(16 * math.sin(r)))],
               fill=RED, width=2)
    d.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=RED)


def art_ebola(d, x, y, w, h):
    """Dark data board: big case count, province squares, virus marks."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 54, 58))
    big = load(SANS_B, 34)
    num = "12,021"
    d.text((x + 12, y + 8), num, font=big, fill=(255, 255, 255))
    d.text((x + 12, y + 46), "CASES CONFIRMED", font=F.tag,
           fill=(150, 210, 205))
    d.text((x + w - 92, y + 14), "5,904 DEAD", font=F.banner, fill=DUSK)
    import math
    for cx, cy, r in [(x + w - 42, y + 50, 10), (x + w - 112, y + 54, 7)]:
        for k in range(10):
            a = math.radians(k * 36)
            d.line([(cx + int(r * math.cos(a)), cy + int(r * math.sin(a))),
                    (cx + int((r + 6) * math.cos(a)),
                     cy + int((r + 6) * math.sin(a)))],
                   fill=(220, 90, 70), width=2)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(200, 60, 45))
    # 26 province squares, 8 filled: the outbreak's spread.
    d.text((x + 12, y + 60), "8 OF 26 PROVINCES", font=F.tag,
           fill=(200, 200, 190))
    sq, gap = 9, 4
    start_x = x + 12
    start_y = y + h - 22
    for i in range(26):
        sx = start_x + i * (sq + gap)
        if sx + sq > x + w - 12:
            break
        fill = RED if i < 8 else (58, 96, 100)
        d.rectangle([sx, start_y, sx + sq, start_y + sq], fill=fill)


ART = {"gaza": art_gaza, "kuwait": art_kuwait, "ebola": art_ebola}

TAG_BG = {"CONFIRMED": TEAL, "OFFICIAL": BLUE, "REPORTED": GOLD,
          "FORECAST": (110, 110, 110)}


def paint_hero(d, x, y, w, h, hero):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=HAIR, width=1)
    art_h = 96
    ART[hero["art"]](d, x + 1, y + 1, w - 2, art_h)
    # Key-number banner laid over the foot of the picture.
    bw = int(text_w(hero["banner"], F.banner)) + 16
    bx = x + (w - bw) // 2
    by = y + art_h - 12
    d.rectangle([bx, by, bx + bw, by + 22], fill=RED)
    d.text((bx + 8, by + 4), hero["banner"], font=F.banner, fill=CARD)
    ty = y + art_h + 10
    tx = x + 10
    tw = w - 20
    lines, fnt = fit_lines(hero["headline"], F.hero_head, tw, 2)
    for ln in lines:
        d.text((tx, ty), ln, font=fnt, fill=INK)
        ty += int(fnt.size * 1.25)
    ty += 2
    deck_lines, dfont = fit_lines(hero["deck"], F.hero_deck, tw, 2)
    for ln in deck_lines:
        d.text((tx, ty), ln, font=dfont, fill=SOFT)
        ty += int(dfont.size * 1.25)
    # Tag chip bottom-left, source bottom-right.
    by2 = y + h - 18
    tag_chip(d, tx, by2, hero["tag"], CARD, TAG_BG[hero["tag"]])
    sw = text_w(hero["src"], F.src)
    d.text((x + w - 10 - sw, by2 + 1), hero["src"], font=F.src, fill=FAINT)
    return y + h


def paint_heroes(d, x, y, w):
    cell = (w - 2 * GUT) // 3
    h = 200
    for i, hero in enumerate(HEROES):
        paint_hero(d, x + i * (cell + GUT), y, cell, h, hero)
    return y + h + GUT


# ---------------------------------------------------------------- secondary
def paint_secondary(d, x, y, w):
    cell = (w - 4 * GUT) // 5
    h = 74
    for row in range(2):
        for col in range(5):
            idx = row * 5 + col
            head, tag = SECONDARY[idx]
            cx = x + col * (cell + GUT)
            cy = y + row * (h + GUT)
            d.rectangle([cx, cy, cx + cell, cy + h], fill=CARD,
                        outline=HAIR, width=1)
            d.rectangle([cx, cy, cx + cell, cy + 3], fill=TAG_BG[tag])
            tag_chip(d, cx + 8, cy + 9, tag, CARD, TAG_BG[tag])
            lines, fnt = fit_lines(head, F.sec_head, cell - 16, 3)
            ly = cy + 26
            for ln in lines:
                d.text((cx + 8, ly), ln, font=fnt, fill=INK)
                ly += int(fnt.size * 1.25)
    return y + 2 * h + GUT + GUT

# ---------------------------------------------------------------- map row
def paint_map_row(d, x, y, w):
    map_w = 620
    side_w = w - map_w - GUT
    h = 128
    d.rectangle([x, y, x + map_w, y + h], fill=CARD, outline=HAIR, width=1)
    d.text((x + 10, y + 7), "WHERE THE DAY HAPPENED", font=F.map_title,
           fill=INK)
    cols = 64
    rows = len(WORLD)
    dot_dx = (map_w - 20) / cols
    dot_dy = (h - 32) / rows
    ox, oy = x + 10, y + 26
    for r, line in enumerate(WORLD):
        for c, ch in enumerate(line[:cols]):
            if ch == "#":
                cx = ox + c * dot_dx + dot_dx / 2
                cy = oy + r * dot_dy + dot_dy / 2
                d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=BLUE)
    for (c, r, num) in PINS:
        cx = ox + c * dot_dx + dot_dx / 2
        cy = oy + r * dot_dy + dot_dy / 2
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=RED,
                  outline=CARD, width=2)
        nw = text_w(num, F.pin)
        d.text((cx - nw / 2, cy - F.pin.size // 2 - 1), num, font=F.pin,
               fill=CARD)
    # Right-hand panel: region counts.
    sx = x + map_w + GUT
    d.rectangle([sx, y, sx + side_w, y + h], fill=CARD, outline=HAIR,
                width=1)
    d.text((sx + 10, y + 7), "REGIONS — 35 STORIES", font=F.map_title,
           fill=INK)
    ry = y + 28
    for name, count in REGIONS:
        d.text((sx + 10, ry), name, font=F.region, fill=INK)
        cw = text_w(str(count), F.region_b)
        d.text((sx + side_w - 10 - cw, ry), str(count), font=F.region_b,
               fill=RED)
        ry += 14
    return y + h + GUT


# ---------------------------------------------------------------- list
def paint_list(d, x, y, w):
    y = section_head(d, x, y, "THE REST OF THE DAY — 22 MORE STORIES", w)
    cols = 3
    per_col = (len(LISTED) + cols - 1) // cols
    col_w = (w - (cols - 1) * 20) // cols
    row_h = 15
    top = y
    for i, item in enumerate(LISTED):
        col = i // per_col
        row = i % per_col
        ix = x + col * (col_w + 20)
        iy = top + row * row_h
        no = "%d." % (14 + i)
        d.text((ix, iy), no, font=F.list_no, fill=RED)
        nw = text_w(no + " ", F.list_no)
        d.text((ix + nw, iy), item, font=F.list_tx, fill=INK)
    return top + per_col * row_h + 2


# ---------------------------------------------------------------- date check
def paint_datecheck(d, x, y, w):
    lines = wrap(EXCLUDED, F.dc_body, w - 20)
    notyet = wrap(NOT_YET, F.dc_body, w - 20)
    h = 6 + F.dc_title.size + 3 + len(lines) * 12 + 2 + len(notyet) * 12 + 6
    d.rectangle([x, y, x + w, y + h], outline=RED, width=1)
    d.text((x + 10, y + 6), "DATE CHECK — NONE OF THIS IS 26 NOVEMBER",
           font=F.dc_title, fill=RED)
    ly = y + 6 + F.dc_title.size + 3
    for ln in lines:
        d.text((x + 10, ly), ln, font=F.dc_body, fill=SOFT)
        ly += 12
    ly += 2
    for ln in notyet:
        d.text((x + 10, ly), ln, font=F.dc_body, fill=INK)
        ly += 12
    return y + h + GUT


# ---------------------------------------------------------------- footer
def paint_footer(d, x, y, w):
    d.text((x, y), "Sources: Reuters · AP · BBC · Al Jazeera · PTI · AAP",
           font=F.foot_b, fill=INK)
    legend = ("CONFIRMED — seen by reporters · OFFICIAL — stated by "
              "authorities · REPORTED — one or more outlets · FORECAST — "
              "what is expected")
    d.text((x, y + 13), legend, font=F.foot, fill=SOFT)
    claim = "Original drawings. Claims are attributed, not stated as fact."
    d.text((x + w - text_w(claim, F.foot), y + 13), claim, font=F.foot,
           fill=SOFT)
    return y + 26


# ---------------------------------------------------------------- assembly
def build():
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    d = ImageDraw.Draw(img)
    y = MARGIN
    y = paint_masthead(d, MARGIN, y, CONTENT)
    y = paint_timeline(d, MARGIN, y, CONTENT)
    y = paint_numbers(d, MARGIN, y, CONTENT)
    y = paint_heroes(d, MARGIN, y, CONTENT)
    y = paint_secondary(d, MARGIN, y, CONTENT)
    y = paint_map_row(d, MARGIN, y, CONTENT)
    y = paint_list(d, MARGIN, y, CONTENT)
    y = paint_datecheck(d, MARGIN, y, CONTENT)
    y = paint_footer(d, MARGIN, y, CONTENT)
    return img, y


def main():
    img, end_y = build()
    if end_y + MARGIN > PAGE:
        print("OVERFLOW: content ends at y=%d (page %d)" % (end_y, PAGE),
              file=sys.stderr)
        sys.exit(1)
    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    size = os.path.getsize(out)
    print("wrote %s %dx%d %d bytes (content ends y=%d)"
          % (out, PAGE, PAGE, size, end_y))
    if size >= 1048576:
        print("TOO BIG: entry.png exceeds 1 MiB", file=sys.stderr)
        sys.exit(1)
    # Count reconciliation, printed for the record.
    total = len(HEROES) + len(SECONDARY) + len(LISTED)
    regions = sum(c for _, c in REGIONS)
    print("stories: %d heroes + %d secondary + %d listed = %d; "
          "regions sum %d; fields %d; timeline %d; numbers %d"
          % (len(HEROES), len(SECONDARY), len(LISTED), total,
             regions, len(FIELDS), len(TIMELINE), len(NUMBERS)))
    assert total == 35 and regions == 35 and len(FIELDS) == 15


if __name__ == "__main__":
    main()
