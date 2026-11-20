#!/usr/bin/env python3
"""RETIRED v1 composer, kept for reference only. The graded entry is
now main.py, which draws the v2 front page itself (broader, and with
the two Thursday stories below removed to a date-check strip).

Compose entry.png: one image summing up the world news of
Friday 20 November 2026, drawn as a clean newspaper front page.

Stories (all reported on 20 Nov 2026, cross-checked across the day's
news digests):
  * Shenzhen: Trump, Xi and Putin hold their first three-way summit and
    sign a four-point peace declaration (CGTN/PRNewswire, Open Chronicle).
  * The Hague: the ICJ rules Myanmar committed genocide against the
    Rohingya, the court's first such finding against a state (One Turn,
    Kompas, BBC Indonesia).
  * Kyiv: a major Russian missile attack hits three bridges; Austrian
    and Dutch embassies damaged; metro stations used as shelters (BBC).
  * Markets: AI doubts sink global stocks; S&P 500 -2% (fifth straight
    loss), Nikkei -4.8%; Anthropic closes +17% in its Nasdaq debut.
  * Riyadh: Houthi missiles damage the Public Investment Fund tower.
  * Antalya: COP31 draft deal drops the call to phase out fossil fuels.
  * Kenya: last Ebola patient discharged, 37 days after the first case.
  * Also: EU-UK summit seals the Brexit reset deal in Brussels;
    Ukraine strikes the Crimea Bridge a third time; youth protests over
    living costs in 25+ countries.

Run: python3 compose_image.py  ->  writes entry.png (1024x1024).
"""

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 243, 234)
INK = (26, 26, 26)
NAVY = (18, 38, 74)
RED = (178, 34, 44)
GOLD = (198, 148, 32)
GREEN = (28, 124, 68)
GREY = (96, 96, 96)
CARD = (255, 255, 255)
LINE = (210, 202, 186)

FB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


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


def text_block(draw, xy, text, fnt, fill, width, leading=1.12, max_lines=None):
    x, y = xy
    lines = wrap(draw, text, fnt, width)
    if max_lines:
        lines = lines[:max_lines]
    asc, desc = fnt.getmetrics()
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += int((asc + desc) * leading)
    return y


def spaced(draw, xy, text, fnt, fill, tracking=6):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def star(draw, cx, cy, r, fill):
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=fill)


# ------------------------------------------------------------------ icons
def flag_usa(d, x, y, w, h):
    for i in range(7):
        d.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7],
                    fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
    d.rectangle([x, y, x + w * 0.45, y + h * 4 / 7], fill=(30, 40, 110))
    for r in range(4):
        for c in range(5):
            star(d, x + w * (0.09 + 0.09 * c) * 1.0 + 2, y + h * (0.08 + 0.13 * r),
                 3.2, (255, 255, 255))


def flag_china(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    star(d, x + w * 0.18, y + h * 0.28, h * 0.16, (255, 222, 0))
    for dx, dy in ((0.34, 0.10), (0.38, 0.24), (0.38, 0.38), (0.34, 0.52)):
        star(d, x + w * dx, y + h * dy, h * 0.055, (255, 222, 0))


def flag_russia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(245, 245, 245))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 43, 30))


def icon_scales(d, x, y, s, color):
    cx = x + s / 2
    d.line([cx, y + 4, cx, y + s - 8], fill=color, width=5)
    d.line([x + 4, y + 10, x + s - 4, y + 10], fill=color, width=5)
    d.ellipse([cx - 6, y - 4, cx + 6, y + 8], fill=color)
    for px in (x + 10, x + s - 10):
        d.line([px, y + 10, px - 10, y + s * 0.55], fill=color, width=3)
        d.line([px, y + 10, px + 10, y + s * 0.55], fill=color, width=3)
        d.arc([px - 14, y + s * 0.38, px + 14, y + s * 0.72], 0, 180,
              fill=color, width=4)
    d.line([x + s * 0.3, y + s - 6, x + s * 0.7, y + s - 6], fill=color, width=5)


def icon_bridge(d, x, y, s, color):
    deck = y + s * 0.72
    d.line([x, deck, x + s, deck], fill=color, width=6)
    for tx in (x + s * 0.22, x + s * 0.78):
        d.line([tx, y + s * 0.2, tx, deck], fill=color, width=5)
    d.arc([x + s * 0.22, y + s * 0.28, x + s * 0.78, deck + s * 0.3],
          180, 360, fill=color, width=3)
    d.line([x, y + s * 0.92, x + s, y + s * 0.92], fill=color, width=3)
    star(d, x + s * 0.62, y + s * 0.3, s * 0.16, RED)


def icon_chart(d, x, y, s, color):
    d.line([x + 4, y + 4, x + 4, y + s - 6], fill=INK, width=4)
    d.line([x + 4, y + s - 6, x + s - 2, y + s - 6], fill=INK, width=4)
    pts = [(x + s * 0.12, y + s * 0.25), (x + s * 0.38, y + s * 0.42),
           (x + s * 0.55, y + s * 0.34), (x + s * 0.88, y + s * 0.78)]
    d.line(pts, fill=RED, width=6)
    hx, hy = pts[-1]
    d.polygon([(hx, hy), (hx - 16, hy - 2), (hx - 4, hy - 14)], fill=RED)


def icon_tower(d, x, y, s, color):
    bx, bw = x + s * 0.34, s * 0.34
    d.rectangle([bx, y + s * 0.08, bx + bw, y + s * 0.95], outline=color, width=5)
    for r in range(5):
        for c in range(2):
            d.rectangle([bx + 8 + c * (bw - 16) / 2 + c * 2,
                         y + s * (0.16 + 0.15 * r),
                         bx + 8 + (c + 1) * (bw - 16) / 2,
                         y + s * (0.24 + 0.15 * r)], fill=GOLD)
    d.line([x + 2, y + s * 0.1, bx + bw * 0.4, y + s * 0.42], fill=RED, width=5)
    star(d, bx + bw * 0.45, y + s * 0.45, s * 0.13, RED)


def icon_thermo(d, x, y, s, color):
    cx = x + s * 0.62
    d.rounded_rectangle([cx - 9, y + 2, cx + 9, y + s * 0.72], 9,
                        outline=color, width=5)
    d.ellipse([cx - 17, y + s * 0.62, cx + 17, y + s * 0.96], outline=color,
              width=5)
    d.rectangle([cx - 4, y + s * 0.4, cx + 4, y + s * 0.8], fill=RED)
    d.ellipse([cx - 10, y + s * 0.68, cx + 10, y + s * 0.9], fill=RED)
    sx, sy = x + s * 0.2, y + s * 0.2
    d.ellipse([sx - 11, sy - 11, sx + 11, sy + 11], fill=GOLD)
    import math
    for a in range(0, 360, 45):
        dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
        d.line([sx + dx * 15, sy + dy * 15, sx + dx * 22, sy + dy * 22],
               fill=GOLD, width=4)


def icon_health(d, x, y, s, color):
    cx, cy, r = x + s / 2, y + s / 2, s * 0.44
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN)
    wbar = s * 0.13
    d.rectangle([cx - wbar / 2, cy - r * 0.55, cx + wbar / 2, cy + r * 0.55],
                fill=(255, 255, 255))
    d.rectangle([cx - r * 0.55, cy - wbar / 2, cx + r * 0.55, cy + wbar / 2],
                fill=(255, 255, 255))


ICONS = {
    "justice": icon_scales,
    "bridge": icon_bridge,
    "chart": icon_chart,
    "tower": icon_tower,
    "climate": icon_thermo,
    "health": icon_health,
}

# ------------------------------------------------------------------- page
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

M = 36  # page margin

# Header
d.rectangle([0, 0, W, 10], fill=INK)
spaced(d, (M, 26), "THE WORLD IN ONE DAY", font(FB, 25), RED, 8)
d.text((W - M, 26), "GLOBAL NEWS BRIEF", font=font(FB, 25), fill=GREY,
       anchor="ra")
date_text = "FRIDAY 20 NOVEMBER 2026"
date_size = 84
while d.textlength(date_text, font=font(FB, date_size)) > W - 2 * M:
    date_size -= 2
d.text((M, 58), date_text, font=font(FB, date_size), fill=INK)
d.line([M, 158, W - M, 158], fill=INK, width=5)
d.line([M, 166, W - M, 166], fill=INK, width=2)
d.text((M, 176), "The day's biggest stories, at a glance — diplomacy, "
                 "justice, war, markets, climate and health.",
       font=font(FR, 23), fill=GREY)

# Hero: Shenzhen summit
hy, hh = 216, 218
d.rounded_rectangle([M, hy, W - M, hy + hh], 14, fill=NAVY)
d.text((M + 28, hy + 20), "SHENZHEN  ·  DIPLOMACY", font=font(FB, 22),
       fill=(150, 180, 230))
flags = [(flag_usa, "USA"), (flag_china, "CHINA"), (flag_russia, "RUSSIA")]
fw, fh, gap = 128, 84, 26
fx = M + 28
for fn, name in flags:
    fn(d, fx, hy + 56, fw, fh)
    d.rectangle([fx, hy + 56, fx + fw, hy + 56 + fh], outline=(255, 255, 255),
                width=2)
    d.text((fx + fw / 2, hy + 56 + fh + 8), name, font=font(FB, 19),
           fill=(255, 255, 255), anchor="ma")
    fx += fw + gap
hx = M + 28 + 3 * fw + 2 * gap + 26
text_block(d, (hx, hy + 52),
           "TRUMP · XI · PUTIN", font(FB, 44), (255, 255, 255), W - hx - M - 10)
text_block(d, (hx, hy + 108),
           "First-ever three-way summit signs a four-point peace "
           "declaration", font(FR, 26), (214, 226, 245), W - hx - M - 10)

# Story cards, 2 x 3
stories = [
    ("justice", "JUSTICE · THE HAGUE", RED,
     "World Court: Myanmar committed genocide against the Rohingya",
     "First genocide verdict on a state."),
    ("bridge", "WAR IN EUROPE · KYIV", RED,
     "Russia's mass missile strike hits Kyiv",
     "Three bridges hit; residents shelter in metro stations."),
    ("chart", "MARKETS · GLOBAL", NAVY,
     "AI doubts sink world stocks",
     "S&P 500 −2%, Nikkei −4.8% — yet Anthropic jumps 17% on its "
     "Nasdaq debut."),
    ("tower", "MIDDLE EAST · RIYADH", NAVY,
     "Houthi missile damages Riyadh tower",
     "The strike hits the PIF skyscraper in the financial district."),
    ("climate", "CLIMATE · COP31, ANTALYA", GREEN,
     "COP31 draft drops fossil-fuel phase-out",
     "Negotiators cut the pledge as the climate talks falter."),
    ("health", "HEALTH · KENYA", GREEN,
     "Kenya's last Ebola patient goes home",
     "Discharged 37 days after the outbreak's first case."),
]
gy = hy + hh + 18
cw = (W - 2 * M - 16) // 2
chh = 152
for i, (icon, tag, tagc, head, sub) in enumerate(stories):
    cx = M + (i % 2) * (cw + 16)
    cy = gy + (i // 2) * (chh + 12)
    d.rounded_rectangle([cx, cy, cx + cw, cy + chh], 12, fill=CARD,
                        outline=LINE, width=2)
    d.rectangle([cx, cy, cx + cw, cy + 7], fill=tagc)
    ICONS[icon](d, cx + 18, cy + 40, 92, INK)
    tx = cx + 126
    d.text((tx, cy + 15), tag, font=font(FB, 16), fill=tagc)
    y_end = text_block(d, (tx, cy + 36), head, font(FB, 23), INK,
                       cw - 126 - 14, leading=1.08, max_lines=3)
    text_block(d, (tx, y_end + 3), sub, font(FR, 18), GREY, cw - 126 - 14,
               leading=1.1, max_lines=2)

# Footer
fy = gy + 3 * chh + 2 * 12 + 14
d.line([M, fy, W - M, fy], fill=INK, width=3)
d.text((M, fy + 12), "ALSO TODAY", font=font(FB, 20), fill=RED)
text_block(d, (M + 168, fy + 12),
           "EU & UK seal Brexit reset deal in Brussels  ·  Ukraine strikes "
           "Crimea Bridge a third time  ·  Youth protests over living costs "
           "in 25+ countries", font(FR, 20), INK, W - M - 168 - M)

img.save("/home/hatch/workspace/makefun/bots/news-image/entry.png",
         optimize=True)
print("saved entry.png")
