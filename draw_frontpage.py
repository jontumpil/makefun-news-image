#!/usr/bin/env python3
"""news-image-20261120 entry: draw the day's front page to /output.

main.py IS the drawing program: it composes a newspaper front page
summing up the world news of Friday 20 November 2026 and writes it to
/output/entry.png. Pure Python + PIL, no network, fully deterministic
(no timestamps, no randomness): two runs give byte-identical output.

Page contents (33 stories, all Friday 20 Nov 2026, sources named):
  * a six-number stats strip,
  * 3 drawn hero stories (Kyiv strikes, Cyclone Akvan, AI sell-off),
  * 10 numbered story cards (UK-EU reset deal, COP31, Poland missile,
    Iraq, Italy strike, Japan inflation, Korea, Kenya oil, Bukele,
    Phillips 118),
  * a "where it happened" region line,
  * 20 one-line "also on Friday" stories in two columns,
  * a red DATE CHECK strip naming two big stories deliberately left
    out because they happened on Thursday 19 November (the Shenzhen
    three-leader declaration and the World Court's Rohingya ruling).
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 30                      # page margin
CW = W - 2 * M              # content width = 964

PAPER = (247, 243, 234)
INK = (26, 26, 26)
NAVY = (18, 38, 74)
TEAL = (14, 58, 70)
DARK = (22, 22, 32)
RED = (178, 34, 44)
GOLD = (216, 164, 60)
GREY = (96, 96, 96)
CARD = (255, 255, 255)
LINE = (210, 202, 186)
BAND = (238, 231, 216)
TINT = (253, 241, 238)
LIGHT = (219, 228, 244)

SB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SI = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"
FB = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, xy, text, fnt, fill, width, leading=1.12,
               max_lines=None):
    x, y = xy
    lines = wrap(draw, text, fnt, width)
    if max_lines:
        lines = lines[:max_lines]
    asc, desc = fnt.getmetrics()
    step = int((asc + desc) * leading)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += step
    return y


def spaced(draw, xy, text, fnt, fill, tracking=5):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def star(draw, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def _bezier(p0, p1, p2, n=20):
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        pts.append((mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0],
                    mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]))
    return pts


def chip(draw, cx, cy, num, fill=RED):
    r = 15
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    draw.text((cx, cy - 1), str(num), font=font(SB, 17),
              fill=(255, 255, 255), anchor="mm")


# ------------------------------------------------------------- scenes
def scene_kyiv(d, x, y, w, h):
    col = (170, 200, 235)
    deck = y + h - 10
    # dark water under the bridge
    d.rectangle([x, deck + 4, x + w, y + h], fill=(43, 78, 128))
    for i, wfx in enumerate((0.16, 0.46, 0.78)):
        wy = deck + 6 + (i % 2) * 2
        d.line([x + w * wfx, wy, x + w * wfx + 16, wy],
               fill=(110, 160, 215), width=2)
    # two pylons
    for fxp in (0.34, 0.66):
        px = x + w * fxp
        d.rectangle([px - 3, y + 9, px + 3, deck], fill=col)
    # main suspension cable sagging between the pylon tops
    cable = [(x + w * fx, deck + dy) for fx, dy in
             ((0.02, -13), (0.18, -27), (0.34, -37), (0.50, -25),
              (0.66, -37), (0.82, -27), (0.98, -13))]
    d.line(cable, fill=col, width=2)
    for hx_, hy_ in (cable[1], cable[3], cable[5]):
        d.line([hx_, hy_, hx_, deck], fill=col, width=1)
    # deck
    d.line([x + 4, deck, x + w - 4, deck], fill=col, width=5)
    # three missiles on smooth arcs, starburst where each lands
    shots = (((0.99, 0.02), (0.82, 0.30), (0.60, 0.78)),
             ((0.88, 0.00), (0.90, 0.42), (0.79, 0.80)),
             ((0.36, 0.00), (0.30, 0.34), (0.22, 0.72)))
    for p0, p1, p2 in shots:
        pts = _bezier((x + w * p0[0], y + h * p0[1]),
                      (x + w * p1[0], y + h * p1[1]),
                      (x + w * p2[0], y + h * p2[1]))
        d.line(pts, fill=(240, 120, 60), width=2)
        ex, ey = pts[-1]
        star(d, ex, ey, 8, GOLD)
        star(d, ex, ey, 4, RED)


def scene_akvan(d, x, y, w, h):
    cx, cy = x + w * 0.70, y + h * 0.52
    col = (170, 220, 225)
    for r in (25, 18, 11):
        d.arc([cx - r, cy - r * 0.72, cx + r, cy + r * 0.72],
              300, 210, fill=col, width=3)
        d.arc([cx - r, cy - r * 0.72, cx + r, cy + r * 0.72],
              120, 30, fill=col, width=3)
    d.ellipse([cx - 4, cy - 3, cx + 4, cy + 3], fill=col)
    for i in range(9):
        rx = x + 14 + i * (w * 0.42) / 8
        d.line([rx, y + 5, rx - 7, y + 19], fill=col, width=2)
    base = y + h - 7
    d.line([x + 8, base, x + w * 0.52, base], fill=col, width=3)
    bx, by = x + w * 0.15, base
    top = (bx + 15, by - 37)
    d.line(_bezier((bx, by), (bx + 3, by - 20), top, n=12), fill=col,
           width=4)
    for dx, dy in ((-36, -13), (-24, -21), (-9, -25), (7, -25),
                   (22, -20), (35, -11)):
        mid = (top[0] + dx * 0.55, top[1] + dy - 5)
        end = (top[0] + dx, top[1] + dy + 9)
        d.line(_bezier(top, mid, end, n=10), fill=col, width=3)
    d.ellipse([top[0] - 3, top[1] - 1, top[0] + 2, top[1] + 4],
              fill=col)
    d.ellipse([top[0] + 1, top[1] + 1, top[0] + 6, top[1] + 6],
              fill=col)
    for i in range(4):
        wx = x + w * (0.58 + 0.10 * i)
        d.arc([wx, base - 7, wx + 22, base + 5], 180, 360, fill=col,
              width=2)


def scene_selloff(d, x, y, w, h):
    grid = (74, 74, 96)
    for i in range(1, 4):
        gy = y + i * h / 4
        d.line([x + 8, gy, x + w - 8, gy], fill=grid, width=1)
    pts = [(x + w * 0.06, y + h * 0.20), (x + w * 0.22, y + h * 0.32),
           (x + w * 0.36, y + h * 0.26), (x + w * 0.48, y + h * 0.48),
           (x + w * 0.58, y + h * 0.60)]
    d.line(pts, fill=RED, width=5)
    hx, hy = pts[-1]
    d.polygon([(hx + 13, hy + 7), (hx - 2, hy + 5), (hx + 3, hy - 8)],
              fill=RED)
    d.text((x + w - 10, y + h * 0.10), "TAIEX", font=font(SB, 16),
           fill=(200, 200, 214), anchor="ra")
    d.text((x + w - 10, y + h * 0.34), "−6.2%", font=font(SB, 32),
           fill=(240, 90, 90), anchor="ra")


# --------------------------------------------------------- card icons
# Each icon draws in a 42x44 box at (x, y): flat shapes, 2-3 colours,
# no text. Same visual language as the hero scenes.
BLUE = (43, 92, 168)
GREEN = (110, 150, 75)
DGREEN = (84, 120, 56)
STEEL = (105, 105, 115)
SKY = (168, 208, 224)


def icon_flags(d, x, y):
    # EU flag (right, lower)
    d.rectangle([x + 21, y + 14, x + 41, y + 38], fill=BLUE,
                outline=INK, width=1)
    for i in range(6):
        a = math.radians(i * 60 - 90)
        sx, sy = x + 31 + 6 * math.cos(a), y + 26 + 6 * math.sin(a)
        d.ellipse([sx - 1.6, sy - 1.6, sx + 1.6, sy + 1.6], fill=GOLD)
    # Union Jack (left, upper): diagonals, then white and red crosses
    d.rectangle([x, y + 6, x + 20, y + 30], fill=NAVY, outline=INK,
                width=1)
    d.line([x + 1, y + 7, x + 19, y + 29], fill=(255, 255, 255),
           width=2)
    d.line([x + 19, y + 7, x + 1, y + 29], fill=(255, 255, 255),
           width=2)
    d.rectangle([x + 7, y + 6, x + 13, y + 30], fill=(255, 255, 255))
    d.rectangle([x, y + 15, x + 20, y + 21], fill=(255, 255, 255))
    d.rectangle([x + 9, y + 6, x + 11, y + 30], fill=RED)
    d.rectangle([x, y + 17, x + 20, y + 19], fill=RED)


def icon_cop(d, x, y):
    cx, cy = x + 16, y + 20
    d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=SKY,
              outline=TEAL, width=2)
    d.ellipse([cx - 5, cy - 13, cx + 5, cy + 13], outline=TEAL, width=1)
    d.line([cx - 13, cy, cx + 13, cy], fill=TEAL, width=1)
    # clock overlapping the globe's lower right
    kx, ky = x + 32, y + 33
    d.ellipse([kx - 8, ky - 8, kx + 8, ky + 8], fill=(255, 255, 255),
              outline=RED, width=2)
    d.line([kx, ky, kx, ky - 5], fill=INK, width=2)
    d.line([kx, ky, kx + 4, ky + 3], fill=INK, width=2)


def icon_missile(d, x, y):
    d.rectangle([x + 1, y + 31, x + 41, y + 41], fill=GREEN)
    d.line([x + 1, y + 31, x + 41, y + 31], fill=INK, width=1)
    d.line([x + 6, y + 36, x + 14, y + 36], fill=DGREEN, width=2)
    d.line([x + 24, y + 38, x + 34, y + 38], fill=DGREEN, width=2)
    d.polygon([(x + 4, y + 6), (x + 8, y + 15), (x + 12, y + 9)],
              fill=GOLD)
    d.polygon([(x + 8, y + 15), (x + 25, y + 26), (x + 29, y + 20),
               (x + 12, y + 9)], fill=STEEL, outline=INK)
    d.polygon([(x + 25, y + 26), (x + 33, y + 27), (x + 29, y + 20)],
              fill=RED)
    d.polygon([(x + 8, y + 15), (x + 5, y + 20), (x + 13, y + 18)],
              fill=STEEL)
    d.polygon([(x + 12, y + 9), (x + 17, y + 5), (x + 18, y + 12)],
              fill=STEEL)


def icon_tank(d, x, y):
    d.rounded_rectangle([x + 3, y + 30, x + 39, y + 39], 4, fill=INK)
    for i in range(4):
        wx = x + 9 + i * 8
        d.ellipse([wx - 2.6, y + 32, wx + 2.6, y + 37.2],
                  fill=(170, 170, 170))
    d.polygon([(x + 6, y + 30), (x + 10, y + 24), (x + 33, y + 24),
               (x + 37, y + 30)], fill=NAVY)
    d.rectangle([x + 15, y + 17, x + 27, y + 24], fill=NAVY)
    d.rectangle([x + 19, y + 14, x + 24, y + 17], fill=NAVY)
    d.line([x + 27, y + 19, x + 41, y + 16], fill=NAVY, width=3)


def icon_strike(d, x, y):
    for rx, ry, rw, rh, oc in ((2, 8, 12, 11, INK), (15, 4, 13, 12, RED),
                               (29, 8, 12, 11, INK)):
        d.rectangle([x + rx, y + ry, x + rx + rw, y + ry + rh],
                    fill=(255, 255, 255), outline=oc, width=2)
        sx = x + rx + rw // 2
        d.line([sx, y + ry + rh, sx, y + 30], fill=INK, width=2)
    for i, hx_ in enumerate((5, 13, 21, 29, 37)):
        d.ellipse([x + hx_ - 3.2, y + 31.8, x + hx_ + 3.2, y + 38.2],
                  fill=RED if i == 2 else INK)


def icon_bars(d, x, y):
    d.line([x + 3, y + 38, x + 40, y + 38], fill=INK, width=2)
    for bx, bh, col in ((6, 11, NAVY), (17, 19, NAVY), (28, 28, RED)):
        d.rectangle([x + bx, y + 38 - bh, x + bx + 8, y + 38], fill=col)
    d.line([x + 4, y + 22, x + 33, y + 6], fill=GOLD, width=3)
    d.polygon([(x + 33, y + 6), (x + 25, y + 5), (x + 34, y + 14)],
              fill=GOLD)


def icon_gavel(d, x, y):
    cx, cy = x + 15, y + 13
    dx, dy = 0.866, -0.5          # head axis
    px, py = 0.5, 0.866           # head perpendicular
    hl, hh2 = 9.5, 3.6
    corners = [(cx + dx * hl + px * hh2, cy + dy * hl + py * hh2),
               (cx + dx * hl - px * hh2, cy + dy * hl - py * hh2),
               (cx - dx * hl - px * hh2, cy - dy * hl - py * hh2),
               (cx - dx * hl + px * hh2, cy - dy * hl + py * hh2)]
    d.polygon(corners, fill=NAVY)
    for s in (7, -7):
        d.line([(cx + dx * s + px * hh2, cy + dy * s + py * hh2),
                (cx + dx * s - px * hh2, cy + dy * s - py * hh2)],
               fill=GOLD, width=2)
    d.line([x + 17, y + 16, x + 28, y + 30], fill=GOLD, width=4)
    d.rounded_rectangle([x + 23, y + 34, x + 41, y + 40], 2, fill=INK)


def icon_pumpjack(d, x, y):
    d.line([x + 2, y + 39, x + 41, y + 39], fill=INK, width=2)
    d.line([x + 9, y + 39, x + 17, y + 15], fill=NAVY, width=3)
    d.line([x + 25, y + 39, x + 17, y + 15], fill=NAVY, width=3)
    d.line([x + 12, y + 28, x + 22, y + 28], fill=NAVY, width=2)
    d.line([x + 5, y + 13, x + 38, y + 19], fill=INK, width=4)
    d.polygon([(x + 36, y + 17), (x + 41, y + 19), (x + 39, y + 26),
               (x + 35, y + 22)], fill=INK)
    d.line([x + 38, y + 26, x + 38, y + 39], fill=INK, width=2)
    d.rectangle([x + 2, y + 15, x + 8, y + 21], fill=NAVY)
    d.ellipse([x + 14, y + 12, x + 20, y + 18], fill=GOLD)


def icon_ballot(d, x, y):
    d.rectangle([x + 14, y + 5, x + 28, y + 23], fill=(255, 255, 255),
                outline=INK, width=2)
    d.line([x + 17, y + 14, x + 20, y + 17], fill=RED, width=2)
    d.line([x + 20, y + 17, x + 25, y + 9], fill=RED, width=2)
    d.rectangle([x + 7, y + 24, x + 35, y + 41], fill=NAVY)
    d.rectangle([x + 13, y + 23, x + 29, y + 25], fill=INK)


def icon_cricket(d, x, y):
    d.line([x + 9, y + 5, x + 15, y + 15], fill=INK, width=3)
    d.polygon([(x + 13, y + 13), (x + 21, y + 11), (x + 26, y + 27),
               (x + 18, y + 30)], fill=GOLD, outline=INK)
    d.ellipse([x + 29, y + 26, x + 39, y + 36], fill=RED)
    d.arc([x + 31, y + 26, x + 37, y + 36], 90, 270,
          fill=(255, 255, 255), width=1)


ICONS = {4: icon_flags, 5: icon_cop, 6: icon_missile, 7: icon_tank,
         8: icon_strike, 9: icon_bars, 10: icon_gavel,
         11: icon_pumpjack, 12: icon_ballot, 13: icon_cricket}


# --------------------------------------------------------------- data
STATS = [
    ("3", "Dnipro bridges hit in Kyiv"),
    ("47,000+", "people moved in Odisha before Akvan"),
    ("−6.2%", "Taiwan's Taiex, Friday's close"),
    ("£5.1bn", "UK estimate of the EU food deal"),
    ("90 km/h", "Akvan's gusts at landfall"),
    ("100,000", "youth visas a year in the UK–EU deal"),
]

HEROES = [
    (1, "KYIV · WAR IN EUROPE", scene_kyiv, NAVY,
     "Russian missiles hit three Kyiv bridges",
     "Some 110 missiles and 400 drones in an overnight barrage; at "
     "least 9 killed across Ukraine; power and water cut in the "
     "capital. (Kyiv Independent, BBC)"),
    (2, "ODISHA · CYCLONE AKVAN", scene_akvan, TEAL,
     "Cyclone Akvan comes ashore in Odisha",
     "Crossed the coast near Gopalpur about 8 am. Odisha had moved "
     "over 47,000 people to safety; no deaths reported. (IMD, BBC)"),
    (3, "ASIA · MARKETS", scene_selloff, DARK,
     "AI sell-off sinks Asia's stock markets",
     "Taipei −6.2% (worst week since 1991), Seoul −5.2%, Tokyo "
     "−5.1%, Hong Kong −1.9%; SoftBank fell 14% in a day. "
     "(Al Jazeera, Anadolu)"),
]

CARDS = [
    (4, "UK–EU “reset” deal sealed a decade after Brexit",
     "Food trade, youth mobility and linked carbon markets; fee "
     "talks go on. (Al Jazeera)"),
    (5, "COP31 reaches its last day with no deal",
     "In Antalya, Türkiye, the draft text leaves out fossil fuels; "
     "talks may run past the deadline. (UN News)"),
    (6, "Russian cruise missile lands in Poland",
     "A Kh-101 fell in a field near Lublin; two airports paused. "
     "Tusk calls it a provocation. (Reuters)"),
    (7, "Iraq: army enters a militia stronghold",
     "Troops deploy to Jurf al-Sakhar; Kataib Hezbollah given a "
     "deadline to quit. (Reuters)"),
    (8, "General strike over Italy's budget",
     "CGIL union calls out workers and students; about 100 rallies "
     "planned. (Reuters)"),
    (9, "Japan's inflation picks up to 2.3%",
     "October consumer prices; a December rate rise in view. "
     "(Official data, Reuters)"),
    (10, "Korea's ruling party to impeach top judge",
     "Follows an overturned conviction; separately 111 students "
     "caught cheating in the Suneung exam. (Korea Herald)"),
    (11, "Kenya starts drilling its first oil well",
     "In Turkana; first crude is due on 1 December. (allAfrica)"),
    (12, "Bukele files to run for a third term",
     "El Salvador; the vote is on 28 February 2027. (AP)"),
    (13, "Phillips hits 118 against India",
     "Wellington cricket; hundreds v India in all three formats. "
     "(ICC)"),
]

ALSO = [
    ("Lviv", "a strike on a railway station kills two", "BBC"),
    ("Moscow", "Russia decrees Estonia's border closure", "Reuters"),
    ("Berlin", "school pupils strike against military service",
     "Al Jazeera"),
    ("Beijing", "China holds its loan rates for an 18th month",
     "Xinhua"),
    ("Seoul", "Kospi index ends the week 7.9% lower", "Anadolu"),
    ("Ganjam", "209 mm of rain falls as Akvan crosses", "PTI"),
    ("Lebanon", "Israeli air strikes hit the south and the east",
     "Anadolu"),
    ("Yemen", "gunfire on a cargo ship off the coast", "UKMTO"),
    ("Abuja", "court bars new evidence against Tinubu", "Channels TV"),
    ("Kampala", "police told to enforce Ebola ban on rallies",
     "allAfrica"),
    ("Malawi", "fuel crisis brings night-long petrol queues",
     "Al Jazeera"),
    ("Africa", "AfDB says 22 countries are in debt distress",
     "allAfrica"),
    ("Las Vegas", "Russell fastest in wet Grand Prix practice",
     "Autosport"),
    ("New York", "Nasdaq futures fall 1.6% before the bell",
     "24/7 Wall St"),
    ("Washington", "Democrats query a law firm's free work",
     "Reuters"),
    ("Wellington", "Nicholls makes 175 in a stand of 216", "ICC"),
    ("Sydney", "Australian shares fall 1% in the sell-off", "Reuters"),
    ("Antalya", "Panama asks COP31 to cap world oil output",
     "Anadolu"),
    ("Antalya", "EU official calls the climate draft unacceptable",
     "RTÉ"),
    ("Turin", "ATP backs a plan to lift player pay past $350m",
     "Anadolu"),
]

DATE_CHECK = ("Left out as Thursday 19 November news: the three-leader "
              "declaration in Shenzhen and the World Court's Rohingya "
              "genocide ruling — both happened on Thursday, so they "
              "are not on this Friday page.")

FOOTER = ("Every story here happened, or was first reported, on Friday "
          "20 November 2026. Sources named beside each story · "
          "original drawings.")


# ---------------------------------------------------------------- page
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead
    d.rectangle([0, 0, W, 8], fill=INK)
    spaced(d, (M, 16), "THE WORLD IN ONE DAY", font(SB, 21), RED, 5)
    d.text((W - M, 16), "GLOBAL NEWS BRIEF", font=font(SB, 20),
           fill=GREY, anchor="ra")
    date_text = "FRIDAY 20 NOVEMBER 2026"
    size = 64
    while d.textlength(date_text, font=font(FB, size)) > CW:
        size -= 2
    d.text((W / 2, 42), date_text, font=font(FB, size), fill=INK,
           anchor="ma")
    y = 42 + size + 10
    d.line([M, y, W - M, y], fill=INK, width=5)
    d.line([M, y + 7, W - M, y + 7], fill=INK, width=2)
    y += 15

    # Stats strip
    sh = 58
    d.rectangle([M, y, W - M, y + sh], fill=NAVY)
    cell = CW / 6
    lab_f = font(SR, 11)
    for i, (num, label) in enumerate(STATS):
        cx = M + i * cell
        if i:
            d.line([cx, y + 8, cx, y + sh - 8], fill=(70, 96, 140),
                   width=1)
        d.text((cx + cell / 2, y + 5), num, font=font(SB, 23),
               fill=GOLD, anchor="ma")
        ly = y + 33
        for ln in wrap(d, label, lab_f, cell - 12)[:2]:
            d.text((cx + cell / 2, ly), ln, font=lab_f,
                   fill=(225, 232, 245), anchor="ma")
            ly += 12
    y += sh + 7

    # Heroes
    hh = 212
    hw = (CW - 22) // 3
    for i, (num, kicker, scene, bg, head, body) in enumerate(HEROES):
        hx = M + i * (hw + 11)
        d.rounded_rectangle([hx, y, hx + hw, y + hh], 10, fill=bg)
        scene(d, hx + 10, y + 8, hw - 20, 56)
        chip(d, hx + 24, y + 24, num)
        d.text((hx + 16, y + 70), kicker, font=font(SB, 13),
               fill=(160, 190, 235))
        y_end = text_block(d, (hx + 16, y + 88), head, font(FB, 19),
                           (255, 255, 255), hw - 32, leading=1.05,
                           max_lines=2)
        text_block(d, (hx + 16, y_end + 3), body, font(SR, 13),
                   LIGHT, hw - 32, leading=1.1, max_lines=4)
    y += hh + 7

    # Numbered cards, 2 x 5
    chh, cgap = 56, 5
    cw2 = (CW - cgap) // 2
    for i, (num, head, body) in enumerate(CARDS):
        cx = M + (i % 2) * (cw2 + cgap)
        cy = y + (i // 2) * (chh + cgap)
        d.rounded_rectangle([cx, cy, cx + cw2, cy + chh], 8, fill=CARD,
                            outline=LINE, width=2)
        chip(d, cx + 26, cy + chh // 2, num, fill=NAVY)
        icon = ICONS.get(num)
        if icon:
            icon(d, cx + 48, cy + 6)
        tx = cx + 96
        tw = cw2 - 96 - 12
        y_end = text_block(d, (tx, cy + 6), head, font(SB, 15), INK,
                           tw, leading=1.05, max_lines=1)
        text_block(d, (tx, y_end + 2), body, font(SR, 12), GREY, tw,
                   leading=1.08, max_lines=2)
    y += 5 * chh + 4 * cgap + 7

    # Region strip
    rh = 36
    d.rectangle([M, y, W - M, y + rh], fill=BAND)
    d.text((M + 14, y + rh / 2), "WHERE IT HAPPENED", font=font(SB, 14),
           fill=RED, anchor="lm")
    d.text((M + 218, y + rh / 2),
           "Europe 8  ·  Asia 10  ·  Middle East 3  ·  Africa 5  ·  "
           "Americas 4  ·  Oceania 3",
           font=font(SR, 15), fill=INK, anchor="lm")
    d.text((W - M - 14, y + rh / 2), "33 stories in all",
           font=font(SB, 14), fill=NAVY, anchor="rm")
    y += rh + 7

    # Also on Friday: two columns of one-liners
    d.text((M, y), "ALSO ON FRIDAY", font=font(SB, 16), fill=RED)
    d.line([M + 168, y + 10, W - M, y + 10], fill=LINE, width=2)
    y += 23
    colw = (CW - 28) // 2
    fb13, fr13 = font(SB, 13), font(SR, 13)
    for j, (city, text, src) in enumerate(ALSO):
        ax = M + (j // 10) * (colw + 28)
        ay = y + (j % 10) * 15
        d.text((ax, ay), city, font=fb13, fill=INK)
        x2 = ax + d.textlength(city, font=fb13)
        rest = " — " + text + " "
        d.text((x2, ay), rest, font=fr13, fill=INK)
        x3 = x2 + d.textlength(rest, font=fr13)
        d.text((x3, ay), "(" + src + ")", font=fr13, fill=GREY)
    y += 10 * 15 + 5

    # Date check strip
    bh = 54
    d.rounded_rectangle([M, y, W - M, y + bh], 8, fill=TINT,
                        outline=RED, width=3)
    d.text((M + 14, y + 9), "DATE CHECK", font=font(SB, 13), fill=RED)
    text_block(d, (M + 118, y + 9), DATE_CHECK, font(SR, 13), INK,
               CW - 118 - 14, leading=1.12, max_lines=3)
    y += bh + 7

    # Footer
    d.line([M, y, W - M, y], fill=INK, width=2)
    d.text((W / 2, y + 6), FOOTER, font=font(SI, 12), fill=GREY,
           anchor="ma")
    return img


def main():
    out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "entry.png")
    img = build()
    img.save(out, optimize=True)
    size = os.path.getsize(out)
    with open(out, "rb") as f:
        magic = f.read(8)
    if magic[:4] != b"\x89PNG" and magic[:2] != b"\xff\xd8":
        raise SystemExit("output is not a PNG or JPEG")
    print(f"wrote {out} ({size} bytes)")


if __name__ == "__main__":
    main()
