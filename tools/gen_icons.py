"""Magic element icons: 512x512 transparent PNG circular emblems (navy disc, gold rings, rune band, element glyph).

Drawn at 4x and downsampled for clean anti-aliasing. Output: assets/Phase4/Icons/HO_Icon_Magic_<Element>.png
"""
import math, os, random, json
from PIL import Image, ImageDraw, ImageFilter, ImageChops

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'assets', 'Phase4', 'Icons')
SS = 4
N = 512 * SS
C = N / 2

NAVY = (16, 24, 52, 255)
NAVY_HI = (34, 50, 96, 255)
GOLD = (222, 178, 88, 255)
GOLD_DK = (150, 108, 40, 255)
ELEMENTS = {
    'Fire': dict(glow=(255, 110, 30), core=(255, 214, 120), tint=(90, 20, 10)),
    'Water': dict(glow=(60, 170, 255), core=(200, 240, 255), tint=(10, 40, 90)),
    'Earth': dict(glow=(240, 160, 50), core=(255, 225, 150), tint=(60, 40, 15)),
}


def ring(d, r, w, col):
    d.ellipse((C - r, C - r, C + r, C + r), outline=col, width=int(w))


def rune(d, cx, cy, s, ang, rng, col, w):
    """A random angular rune made of 2-4 strokes inside an s x s cell, rotated to face outward."""
    ca, sa = math.cos(ang), math.sin(ang)

    def P(x, y):  # cell coords (-1..1) -> image, rotated
        x, y = x * s / 2, y * s / 2
        return (cx + x * ca - y * sa, cy + x * sa + y * ca)
    pts = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    d.line([P(0, -1), P(0, 1)], fill=col, width=w)                       # stave
    for _ in range(rng.randint(1, 3)):
        a, b = rng.sample(pts, 2)
        if a == b: continue
        d.line([P(*a), P(*b)], fill=col, width=w)


def glyph_fire(d, col, w):
    """Stylised flame: tall central tongue, two side tongues curling outward, hollow inner flame."""
    def tongue(cx, base, h, wd, lean):
        L, R = [], []
        for i in range(61):
            t = i / 60
            y = base - h * t
            if t < 0.22:                                  # rounded bottom
                half = wd * math.sqrt(max(0.0, 1 - ((0.22 - t) / 0.22) ** 2))
            else:                                         # bulge then taper to a sharp tip
                u = (t - 0.22) / 0.78
                half = wd * (1 - u) ** 0.9 * (1 + 0.25 * math.sin(math.pi * u))
            x = cx + lean * h * t ** 2.2
            L.append((x - half, y)); R.append((x + half, y))
        return R + L[::-1]
    base = C + N * 0.2
    clear = (0, 0, 0, 0)
    d.polygon(tongue(C - N * 0.1, base, N * 0.3, N * 0.1, -0.35), fill=col)
    d.polygon(tongue(C + N * 0.1, base, N * 0.32, N * 0.1, 0.35), fill=col)
    d.polygon(tongue(C, base + N * 0.01, N * 0.47, N * 0.16, 0.08), fill=col)
    d.polygon(tongue(C + N * 0.005, base - N * 0.03, N * 0.2, N * 0.06, -0.12), fill=clear)


def glyph_water(d, col, w):
    """Droplet over three waves."""
    top, bot, r = C - N * 0.24, C + N * 0.06, N * 0.11
    pts = []
    for i in range(61):
        a = math.pi * (i / 60)                       # lower half circle
        pts.append((C + r * math.cos(a), bot - r + r * math.sin(a) + r * 0.0))
    pts = [(C, top)] + [(C + r * math.cos(-a), bot - r * 0.9 + r * math.sin(a)) for a in [math.pi * i / 60 for i in range(61)]]
    d.polygon(pts, fill=col)
    for k in range(3):
        y = C + N * (0.13 + 0.075 * k)
        amp = N * 0.022
        xs = [C - N * (0.24 - 0.04 * k) + i * N * 0.01 for i in range(int((0.48 - 0.08 * k) * 100) + 1)]
        line = [(x, y + amp * math.sin((x - C) / (N * 0.04))) for x in xs]
        d.line(line, fill=col, width=w, joint='curve')


def glyph_earth(d, col, w):
    """Mountain peaks over a cracked stone slab."""
    b = C + N * 0.1
    d.polygon([(C - N * 0.24, b), (C - N * 0.07, C - N * 0.24), (C + N * 0.06, C - N * 0.06), (C + N * 0.13, C - N * 0.15),
               (C + N * 0.25, b)], fill=col)
    d.line([(C - N * 0.07, C - N * 0.24), (C - N * 0.11, C - N * 0.12), (C - N * 0.04, C - N * 0.02), (C - N * 0.09, b)],
           fill=(0, 0, 0, 0), width=int(w * 0.8))
    d.rectangle((C - N * 0.25, b + N * 0.03, C + N * 0.25, b + N * 0.1), fill=col)
    for x in (-0.12, 0.05, 0.19):
        d.line([(C + N * x, b + N * 0.03), (C + N * (x + 0.02), b + N * 0.065), (C + N * (x - 0.01), b + N * 0.1)],
               fill=(0, 0, 0, 0), width=int(w * 0.6))


GLYPHS = {'Fire': glyph_fire, 'Water': glyph_water, 'Earth': glyph_earth}


def icon(el):
    spec = ELEMENTS[el]
    rng = random.Random(el)
    img = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    R = N * 0.48
    # disc with a radial navy gradient + element tint
    disc = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    dd = ImageDraw.Draw(disc)
    for i in range(60):
        t = i / 59
        r = R * (1 - t)
        col = tuple(int(NAVY[c] * (1 - t) + (NAVY_HI[c] * 0.6 + spec['tint'][c] * 0.9) * t) for c in range(3)) + (255,)
        dd.ellipse((C - r, C - r, C + r, C + r), fill=col)
    img.alpha_composite(disc)
    # gold rims and rune band
    ring(d, R, N * 0.022, GOLD)
    ring(d, R - N * 0.03, N * 0.006, GOLD_DK)
    ring(d, R * 0.72, N * 0.012, GOLD)
    ring(d, R * 0.69, N * 0.004, GOLD_DK)
    nr = 16
    for k in range(nr):
        a = 2 * math.pi * k / nr - math.pi / 2
        rr = R * 0.84
        rune(d, C + rr * math.cos(a), C + rr * math.sin(a), N * 0.055, a + math.pi / 2, rng, GOLD, int(N * 0.007))
    for k in range(8):                                     # small studs between band and inner ring
        a = 2 * math.pi * (k + 0.5) / 8 - math.pi / 2
        rr = R * 0.705
        d.ellipse((C + rr * math.cos(a) - N * 0.012, C + rr * math.sin(a) - N * 0.012,
                   C + rr * math.cos(a) + N * 0.012, C + rr * math.sin(a) + N * 0.012), fill=GOLD)
    # element glyph: blurred coloured glow, then a gold-edged core
    mask = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    GLYPHS[el](ImageDraw.Draw(mask), (255, 255, 255, 255), int(N * 0.02))
    a = mask.split()[3]
    glow = Image.new('RGBA', (N, N), spec['glow'] + (0,))
    glow.putalpha(a.filter(ImageFilter.GaussianBlur(N * 0.03)).point(lambda v: min(255, int(v * 1.6))))
    img.alpha_composite(glow)
    edge = Image.new('RGBA', (N, N), GOLD)
    edge.putalpha(a.filter(ImageFilter.MaxFilter(int(N * 0.012) | 1)))
    img.alpha_composite(edge)
    core = Image.new('RGBA', (N, N), spec['core'] + (255,))
    # vertical gradient on the glyph core: bright top -> glow colour bottom
    grad = Image.linear_gradient('L').resize((N, N))
    core = Image.composite(Image.new('RGBA', (N, N), spec['glow'] + (255,)), core, grad)
    core.putalpha(a)
    img.alpha_composite(core)
    # clip to the disc (no stray pixels outside the emblem)
    clip = Image.new('L', (N, N), 0)
    ImageDraw.Draw(clip).ellipse((C - R - N * 0.012, C - R - N * 0.012, C + R + N * 0.012, C + R + N * 0.012), fill=255)
    img.putalpha(ImageChops.multiply(img.split()[3], clip))
    return img.resize((512, 512), Image.LANCZOS)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    files = []
    for el in ELEMENTS:
        p = os.path.join(OUT, f'HO_Icon_Magic_{el}.png')
        icon(el).save(p)
        files.append(os.path.relpath(p, ROOT))
        print('wrote', p)
    # preview sheet on a dark background
    sheet = Image.new('RGBA', (512 * 3 + 64, 576), (28, 26, 30, 255))
    for i, f in enumerate(files):
        sheet.alpha_composite(Image.open(os.path.join(ROOT, f)), (16 + i * 528, 32))
    rd = os.path.join(ROOT, 'renders', 'Phase4', 'Icons'); os.makedirs(rd, exist_ok=True)
    sheet.convert('RGB').save(os.path.join(rd, 'HO_Icon_Magic_sheet.png'))
    print(json.dumps(files))
