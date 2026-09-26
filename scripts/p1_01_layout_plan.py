"""Phase 1 / Step 1 - Capital city layout plan (top-down), ~900 x 1200 studs.

Outputs
  docs/layout/HO_City_LayoutPlan.png   labelled plan image
  docs/layout/city_layout.json         the same plan as data (for scripted placement in Roblox)

Plan coordinates: X = east (0..900), Y = north (0..1200), Z = elevation above sea level (studs).
Roblox mapping:   Roblox.X = X - 450,  Roblox.Z = 600 - Y  (north = -Z),  Roblox.Y = Z.
All lot/building rectangles are snapped to the 4-stud grid.
"""
import json, os, math, random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle, FancyBboxPatch
from matplotlib import patheffects as pe

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs', 'layout'); os.makedirs(OUT, exist_ok=True)
random.seed(7)
g4 = lambda v: int(round(v / 4.0) * 4)

W, H = 900, 1200

# ----------------------------------------------------------------------------------- terrain / tiers
tiers = [  # name, elevation, polygon
    ('Harbour Promenade', 4, [(732, 40), (772, 40), (772, 780), (732, 780)]),
    ('Lower Town (Tier 1)', 8, [(560, 40), (732, 40), (732, 760), (560, 760)]),
    ('Middle Town (Tier 2)', 20, [(332, 40), (560, 40), (560, 740), (332, 740)]),
    ('Upper Town (Tier 3)', 32, [(40, 40), (332, 40), (332, 720), (40, 720)]),
    ('San-no-maru (Outer Bailey)', 46, [(60, 720), (332, 720), (332, 740), (640, 740), (672, 800), (660, 1100),
                                        (560, 1172), (140, 1172), (60, 1100)]),
    ('Ni-no-maru (Academy Bailey)', 62, [(140, 832), (560, 832), (580, 1000), (540, 1140), (160, 1140), (120, 1000)]),
    ('Hon-maru (Inner Keep Bailey)', 80, [(252, 932), (452, 932), (464, 1020), (452, 1112), (252, 1112), (240, 1020)]),
]
tier_colors = {4: '#cbb58f', 8: '#d8c49c', 20: '#d2c095', 32: '#c9b88d', 46: '#b7b98c', 62: '#a9b184', 80: '#9fa87c'}

sea = [(772, 0), (900, 0), (900, 1200), (700, 1200), (712, 1100), (704, 1000), (724, 900), (772, 820), (772, 0)]
inlet = [(620, 640), (772, 640), (772, 680), (620, 680)]           # tidal canal cutting into Tier 1
cliffs = [
    [(0, 1172), (900, 1172), (900, 1200), (0, 1200)],               # north cliffs behind the castle
    [(0, 700), (60, 720), (60, 1100), (140, 1172), (0, 1172)],       # west cliffs
    [(672, 800), (772, 820), (724, 900), (704, 1000), (712, 1100), (660, 1100)],  # sea cliffs under castle
]
rocks = [((856, 904), 36), ((820, 1040), 18), ((880, 700), 12), ((800, 1150), 22)]

# ------------------------------------------------------------------------------------------ streets
streets = [  # name, width, polyline, kind
    ('Ote-dori (Main Street)', 16, [(440, 40), (440, 700)], 'main'),
    ('Minato-dori (Harbour Street)', 14, [(40, 400), (732, 400)], 'main'),
    ('Kami-dori', 10, [(40, 580), (732, 580)], 'cross'),
    ('Shimo-dori', 10, [(40, 200), (732, 200)], 'cross'),
    ('Kaji-machi', 10, [(180, 40), (180, 720)], 'cross'),
    ('Hama-machi', 10, [(648, 40), (648, 640)], 'cross'),
    ('alley', 4, [(40, 300), (332, 300)], 'alley'), ('alley', 4, [(40, 492), (332, 492)], 'alley'),
    ('alley', 4, [(332, 300), (560, 300)], 'alley'), ('alley', 4, [(332, 500), (560, 500)], 'alley'),
    ('alley', 4, [(560, 300), (732, 300)], 'alley'), ('alley', 4, [(560, 500), (732, 500)], 'alley'),
    ('alley', 4, [(40, 652), (332, 652)], 'alley'), ('alley', 4, [(332, 648), (560, 648)], 'alley'),
    ('alley', 4, [(260, 40), (260, 720)], 'alley'), ('alley', 4, [(504, 40), (504, 740)], 'alley'),
    ('Castle approach', 12, [(440, 700), (440, 760), (440, 832), (400, 860), (400, 932)], 'castle'),
]

stairs = [  # label, centre, size(w along travel?, h), rise
    ('S1', (332, 400), (20, 16), '32→20'), ('S2', (560, 400), (20, 16), '20→8'), ('S3', (732, 400), (12, 16), '8→4'),
    ('S4', (332, 580), (16, 12), '32→20'), ('S5', (560, 580), (16, 12), '20→8'), ('S6', (332, 200), (16, 12), '32→20'),
    ('S7', (560, 200), (16, 12), '20→8'), ('S8', (732, 580), (12, 12), '8→4'), ('S9', (732, 200), (12, 12), '8→4'),
    ('Grand Stair', (440, 720), (20, 40), '20→46'), ('S10', (440, 832), (16, 24), '46→62'),
    ('S11', (400, 932), (16, 24), '62→80'), ('S12', (196, 720), (16, 24), '32→46'),
]

# ------------------------------------------------------------------------------- key buildings/areas
key = [  # id, label, centre, size (w x d), facing (dir the front faces), tier elev, kind
    ('keep', 'Castle Keep (Tenshu)', (352, 1040), (60, 48), 'S', 80, 'castle'),
    ('academy_hall', 'Academy Hall (Dojo)', (216, 1092), (56, 36), 'S', 62, 'special'),
    ('training_yard', 'Training Yard', (216, 972), (96, 120), 'S', 62, 'yard'),
    ('academy_dorm', 'Academy Quarters', (500, 1076), (40, 28), 'W', 62, 'castle'),
    ('armory_castle', 'Castle Storehouse', (500, 900), (32, 20), 'W', 62, 'castle'),
    ('tidewatch_inn', 'Tidewatch Inn', (696, 468), (24, 40), 'E', 8, 'special'),
    ('blacksmith', 'Blacksmith', (212, 340), (24, 20), 'W', 32, 'special'),
    ('armory', 'Armory', (484, 672), (20, 16), 'W', 20, 'special'),
    ('general_store', 'General Store', (508, 436), (16, 20), 'W', 20, 'special'),
    ('magic_stall', 'Magic Stall', (424, 380), (12, 8), 'E', 20, 'special'),
    ('market', 'Market Square', (440, 400), (84, 72), '-', 20, 'square'),
    ('shrine_upper', 'Hill Shrine', (88, 620), (24, 20), 'E', 32, 'shrine'),
    ('shrine_sea', 'Sea Shrine', (600, 700), (16, 16), 'S', 8, 'shrine'),
    ('lighthouse', 'Lighthouse', (856, 904), (16, 16), 'S', 12, 'harbour'),
    ('harbour_office', 'Harbour Office', (696, 300), (20, 24), 'E', 8, 'special'),
]
torii = [('Torii', (124, 620), 'E'), ('Torii', (600, 724), 'S'), ('Torii (Castle road)', (440, 690), 'S')]
gates = [('Ōte-mon (Main Gate)', (440, 740)), ('Ni-no-mon', (440, 832)), ('Hon-mon', (400, 932)), ('West Gate', (196, 720)),
         ('Sea Gate', (668, 800))]
yagura = [(60, 720), (332, 740), (640, 740), (672, 800), (660, 1100), (560, 1172), (140, 1172), (60, 1100),
          (140, 832), (560, 832), (580, 1000), (540, 1140), (160, 1140), (120, 1000),
          (252, 932), (452, 932), (452, 1112), (252, 1112)]
piers = [('Pier 1', 104), ('Pier 2', 204), ('Pier 3', 316), ('Pier 4', 424), ('Pier 5', 536)]
pier_len, pier_w = 92, 12
bridge = ('Arched Bridge', (752, 660), (16, 64))
causeway = [(772, 780), (800, 820), (828, 860), (848, 884)]
kura = [(608, 128), (608, 236), (620, 344), (608, 452)]
wells = [(440, 408), (120, 250)]

# ------------------------------------------------------------------------------ procedural lot fill
reserved = []
for k in key:
    (cx, cy), (w, d) = k[2], k[3]
    reserved.append((cx - w / 2 - 4, cy - d / 2 - 4, cx + w / 2 + 4, cy + d / 2 + 4))
for (cx, cy) in kura:
    reserved.append((cx - 14, cy - 12, cx + 14, cy + 12))
for s in stairs:
    (cx, cy), (w, h) = s[1], s[2]
    reserved.append((cx - w / 2 - 6, cy - h / 2 - 6, cx + w / 2 + 6, cy + h / 2 + 6))
for (cx, cy), _, _ in [(t[1], 0, 0) for t in torii]:
    reserved.append((cx - 8, cy - 8, cx + 8, cy + 8))
for (cx, cy) in wells:
    reserved.append((cx - 6, cy - 6, cx + 6, cy + 6))


def street_rects():
    rs = []
    for _, w, pts, _ in streets:
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            rs.append((min(x0, x1) - w / 2, min(y0, y1) - w / 2, max(x0, x1) + w / 2, max(y0, y1) + w / 2))
    return rs


def overlaps(r, rs):
    return any(r[0] < q[2] and r[2] > q[0] and r[1] < q[3] and r[3] > q[1] for q in rs)


blocked = street_rects() + reserved + [(612, 632, 772, 688)]   # canal + its walls
lots = []
# blocks are rectangles between streets inside each town tier; machiya lots face the E-W streets
xs_breaks = {32: [40, 180, 260, 332], 20: [332, 440, 504, 560], 8: [560, 648, 732]}
ys_breaks = [40, 200, 300, 400, 492, 580, 652, 720]
variants = [('HO_Bldg_Machiya_A', 12), ('HO_Bldg_Machiya_B', 16), ('HO_Bldg_Machiya_C', 16), ('HO_Bldg_Machiya_D', 20),
            ('HO_Bldg_Machiya_E', 24), ('HO_Bldg_Machiya_F', 12)]
for elev, xb in xs_breaks.items():
    top = 740 if elev == 20 else (720 if elev == 32 else 760)
    yb = [y for y in ys_breaks if y < top] + [top]
    for x0, x1 in zip(xb, xb[1:]):
        for y0, y1 in zip(yb, yb[1:]):
            # two rows back to back: south row faces S street, north row faces N street
            bx0, bx1 = x0 + 7, x1 - 7
            mid = (y0 + y1) / 2
            for row, (ry0, ry1, face) in enumerate([(y0 + 7, mid, 'S'), (mid, y1 - 7, 'N')]):
                depth = min(24, g4(ry1 - ry0))
                if depth < 12: continue
                x = g4(bx0)
                while x < bx1 - 8:
                    name, fw = random.choice(variants)
                    if x + fw > bx1: break
                    ly0 = g4(ry0) if face == 'S' else g4(ry1 - depth)
                    r = (x, ly0, x + fw, ly0 + depth)
                    if not overlaps(r, blocked):
                        lots.append(dict(asset=name, x=x + fw / 2, y=ly0 + depth / 2, w=fw, d=depth, facing=face,
                                         elev=elev, storeys=random.choice([1, 2, 2, 2])))
                        blocked.append(r)
                    x += fw
# ------------------------------------------------------------------------------------------ trees
trees = []
for _ in range(900):
    x, y = random.uniform(0, 780), random.uniform(700, 1195)
    in_hon = 252 < x < 452 and 932 < y < 1112
    if in_hon and random.random() < 0.8: continue
    if overlaps((x - 3, y - 3, x + 3, y + 3), blocked + [(160, 900, 270, 1120), (300, 990, 410, 1090)]): continue
    if 772 < x: continue
    trees.append((round(x), round(y), random.choice(['S', 'M', 'L'])))
    if len(trees) > 240: break
for _ in range(60):   # street trees / gardens in town
    x, y = random.uniform(40, 730), random.uniform(40, 720)
    if not overlaps((x - 3, y - 3, x + 3, y + 3), blocked):
        trees.append((round(x), round(y), random.choice(['S', 'M'])))

# ------------------------------------------------------------------------------------------ export
layout = dict(
    size=[W, H], units='studs', axes='X east, Y north, Z elevation; Roblox X=X-450, Z=600-Y',
    tiers=[dict(name=n, elev=e, poly=p) for n, e, p in tiers],
    sea=sea, inlet=inlet, cliffs=cliffs, rocks=[dict(c=c, r=r) for c, r in rocks],
    streets=[dict(name=n, width=w, path=p, kind=k) for n, w, p, k in streets],
    stairs=[dict(name=n, c=c, size=s, rise=r) for n, c, s, r in stairs],
    key_buildings=[dict(id=i, label=l, c=c, size=s, facing=f, elev=e, kind=k) for i, l, c, s, f, e, k in key],
    torii=[dict(label=l, c=c, facing=f) for l, c, f in torii],
    gates=[dict(label=l, c=c) for l, c in gates], yagura=yagura,
    piers=[dict(label=l, y=y, x0=772, length=pier_len, width=pier_w) for l, y in piers],
    bridge=dict(label=bridge[0], c=bridge[1], size=bridge[2]), causeway=causeway, kura=kura, wells=wells,
    machiya_lots=lots, trees=[dict(x=x, y=y, size=s) for x, y, s in trees],
)
with open(os.path.join(OUT, 'city_layout.json'), 'w') as f:
    json.dump(layout, f, indent=1)

# ------------------------------------------------------------------------------------------ render
fig = plt.figure(figsize=(15, 16.5), dpi=160)
ax = fig.add_axes([0.03, 0.04, 0.66, 0.9])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect('equal')
ax.set_facecolor('#6f7d5a')
halo = [pe.withStroke(linewidth=3, foreground='white')]
halo_dark = [pe.withStroke(linewidth=3, foreground='#1b2433')]

ax.add_patch(Polygon(sea, closed=True, fc='#3f6f8f', ec='none', zorder=1))
for c in cliffs:
    ax.add_patch(Polygon(c, closed=True, fc='#7c7466', ec='#5b554a', hatch='///', lw=0.8, zorder=2))
for n, e, p in tiers:
    ax.add_patch(Polygon(p, closed=True, fc=tier_colors[e], ec='#6b5d45', lw=1.0, zorder=3 if e < 46 else 4 + (e - 46) / 10))
# ishigaki walls (thick stone outlines) for castle enclosures + tier retaining walls
for n, e, p in tiers:
    if e >= 46:
        ax.add_patch(Polygon(p, closed=True, fc='none', ec='#8a8272', lw=5, zorder=6 + (e - 46) / 10))
        ax.add_patch(Polygon(p, closed=True, fc='none', ec='#f1ede4', lw=1.6, zorder=6.1 + (e - 46) / 10))
for x in (332, 560, 732):
    ax.plot([x, x], [40, 720 if x == 332 else (740 if x == 560 else 780)], color='#8a8272', lw=4, zorder=5)
ax.plot([772, 772], [40, 820], color='#8a8272', lw=6, zorder=5)                      # quay wall
ax.add_patch(Polygon(inlet, closed=True, fc='#3f6f8f', ec='#8a8272', lw=3, zorder=5.5))
for (c, r) in rocks:
    ax.add_patch(Circle(c, r, fc='#6d665c', ec='#4a453e', lw=1, zorder=5))
ax.plot(*zip(*causeway), color='#9b927f', lw=9, solid_capstyle='round', zorder=5.6)

for n, w, pts, k in streets:
    col = {'main': '#efe3c6', 'cross': '#e8dcbc', 'alley': '#dccfae', 'castle': '#e9e1cc'}[k]
    ax.plot(*zip(*pts), color='#9c8a66', lw=w * 0.62 + 1.2, solid_capstyle='butt', zorder=7)
    ax.plot(*zip(*pts), color=col, lw=w * 0.62, solid_capstyle='butt', zorder=7.1)
for n, w, pts, k in streets:
    if k in ('main', 'cross'):
        (x0, y0), (x1, y1) = pts[0], pts[-1]
        horiz = abs(y1 - y0) < abs(x1 - x0)
        pos = (150, y0) if horiz and x0 < 100 else ((x0, 120) if not horiz else (x0 + 90, y0))
        if n.startswith('Ote'): pos = (440, 560)
        if n.startswith('Hama'): pos = (648, 120)
        ax.text(*pos, n, fontsize=6.5, ha='center', va='center', rotation=0 if horiz else 90, color='#4a3b25',
                zorder=12, path_effects=halo, style='italic')

ax.add_patch(Rectangle((440 - 42, 400 - 36), 84, 72, fc='#ecdcb4', ec='#9c8a66', lw=1.2, zorder=7.2))
for s in stairs:
    (cx, cy), (w, h) = s[1], s[2]
    ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h, fc='#b9b1a1', ec='#5d574c', lw=0.8, zorder=8))
    n = int(max(w, h) / 3)
    for i in range(1, n):
        if h > w: ax.plot([cx - w / 2, cx + w / 2], [cy - h / 2 + i * h / n] * 2, color='#5d574c', lw=0.4, zorder=8.1)
        else: ax.plot([cx - w / 2 + i * w / n] * 2, [cy - h / 2, cy + h / 2], color='#5d574c', lw=0.4, zorder=8.1)

for l in lots:
    ax.add_patch(Rectangle((l['x'] - l['w'] / 2 + 0.6, l['y'] - l['d'] / 2 + 0.6), l['w'] - 1.2, l['d'] - 1.2,
                           fc='#3e4553' if l['storeys'] == 2 else '#57606e', ec='#e9e3d6', lw=0.35, zorder=9))
for (cx, cy) in kura:
    ax.add_patch(Rectangle((cx - 12, cy - 10), 24, 20, fc='#f0ece2', ec='#23272e', lw=1.2, zorder=9))
kind_col = {'castle': '#f3efe6', 'special': '#b8452f', 'yard': '#e3d3a8', 'square': '#ecdcb4', 'shrine': '#c0392b',
            'harbour': '#f3efe6'}
for i, l, (cx, cy), (w, d), f, e, k in key:
    if k == 'square': continue
    ax.add_patch(Rectangle((cx - w / 2, cy - d / 2), w, d, fc=kind_col[k], ec='#1d2330', lw=1.4,
                           zorder=10 if k != 'yard' else 8.5))
    if k == 'castle' and i == 'keep':
        for s in (0.78, 0.56, 0.36):
            ax.add_patch(Rectangle((cx - w * s / 2, cy - d * s / 2), w * s, d * s, fc='#3c4556', ec='#f3efe6', lw=0.8, zorder=10.1))
        ax.plot(cx, cy, marker='*', ms=9, color='#e0b347', mec='#6b4d12', zorder=10.3)
for (cx, cy) in yagura:
    ax.add_patch(Rectangle((cx - 8, cy - 8), 16, 16, fc='#f3efe6', ec='#1d2330', lw=1.2, zorder=11))
    ax.add_patch(Rectangle((cx - 4.5, cy - 4.5), 9, 9, fc='#3c4556', ec='none', zorder=11.1))
for l, (cx, cy) in gates:
    ax.add_patch(Rectangle((cx - 14, cy - 6), 28, 12, fc='#3c4556', ec='#f3efe6', lw=1.2, zorder=11.2))
for l, (cx, cy), f in torii:
    ax.plot([cx - 6, cx + 6], [cy, cy], color='#c0392b', lw=3.2, zorder=11.3, solid_capstyle='butt')
    ax.plot([cx - 4, cx - 4], [cy - 2, cy + 2], color='#c0392b', lw=2, zorder=11.3)
    ax.plot([cx + 4, cx + 4], [cy - 2, cy + 2], color='#c0392b', lw=2, zorder=11.3)
for l, y in piers:
    ax.add_patch(Rectangle((772, y - pier_w / 2), pier_len, pier_w, fc='#9a7a52', ec='#4e3a22', lw=1, zorder=9))
    ax.add_patch(Rectangle((772 + pier_len - 16, y - pier_w / 2 - 8), 16, pier_w + 16, fc='#9a7a52', ec='#4e3a22', lw=1, zorder=9))
    for side in (-1, 1):   # moored boats
        bx, by = 772 + 30 + random.uniform(0, 30), y + side * (pier_w / 2 + 7)
        ax.add_patch(FancyBboxPatch((bx - 12, by - 3.5), 24, 7, boxstyle='round,pad=0,rounding_size=3.5',
                                    fc='#6b4a2b', ec='#2c1d10', lw=0.8, zorder=9.2))
    ax.text(772 + pier_len + 10, y, l, fontsize=7, va='center', color='white', zorder=12, path_effects=halo_dark)
(bx, by), (bw, bh) = bridge[1], bridge[2]
ax.add_patch(FancyBboxPatch((bx - bw / 2, by - bh / 2), bw, bh, boxstyle='round,pad=0,rounding_size=6',
                            fc='#a0522d', ec='#4e2a15', lw=1.2, zorder=10))
ax.add_patch(Circle((856, 904), 8, fc='#f3efe6', ec='#1d2330', lw=1.4, zorder=11))
ax.add_patch(Circle((856, 904), 3.5, fc='#f6c453', ec='none', zorder=11.1))
for (cx, cy) in wells:
    ax.add_patch(Circle((cx, cy), 3.5, fc='#6b8fa6', ec='#3a3a3a', lw=0.8, zorder=11))
for x, y, s in trees:
    r = {'S': 3.2, 'M': 4.8, 'L': 6.5}[s]
    ax.add_patch(Circle((x, y), r, fc='#2f5a38', ec='#1d3a24', lw=0.5, alpha=0.95, zorder=9.5))

# labels (callouts)
callouts = [
    ('Castle Keep\n(Tenshu, 5 tiers)', (352, 1040), (352, 1138)),
    ('Academy Hall', (216, 1092), (216, 1128)),
    ('Training Yard', (216, 972), (216, 972)),
    ('Academy Quarters', (500, 1076), (500, 1120)),
    ('Castle Storehouse', (500, 900), (520, 870)),
    ('Tidewatch Inn\n(6 rentable rooms)', (696, 468), (640, 540)),
    ('Blacksmith', (212, 340), (212, 372)),
    ('Armory', (484, 672), (510, 700)),
    ('General Store', (508, 436), (520, 470)),
    ('Magic Stall', (424, 380), (408, 350)),
    ('Market Square', (440, 400), (380, 438)),
    ('Hill Shrine', (88, 620), (88, 596)),
    ('Sea Shrine', (600, 700), (576, 720)),
    ('Lighthouse', (856, 904), (856, 952)),
    ('Harbour Office', (696, 300), (668, 330)),
    ('Arched Bridge', (752, 660), (820, 640)),
    ('Tidal Canal', (660, 660), (660, 610)),
    ('Waterfront Promenade', (752, 250), (752, 250)),
    ('Kura warehouses', (608, 128), (612, 90)),
    ('Stone causeway', (810, 830), (835, 800)),
]
for text, xy, txy in callouts:
    vert = text == 'Waterfront Promenade'
    ax.annotate(text, xy=xy, xytext=txy, fontsize=7.2, ha='center', va='center', color='#1b2433', zorder=13,
                weight='bold', rotation=90 if vert else 0, path_effects=halo,
                arrowprops=None if xy == txy else dict(arrowstyle='-', color='#1b2433', lw=0.6))
for l, (cx, cy) in gates:
    ax.text(cx + 18, cy + 9, l, fontsize=6.2, color='#1b2433', zorder=13, path_effects=halo)
for n, e, p in tiers:
    lab = {4: None, 8: (600, 30), 20: (446, 30), 32: (100, 30), 46: (600, 1040), 62: (330, 850), 80: (352, 950)}[e]
    if lab:
        ax.text(*lab, f'{n}\n+{e}', fontsize=6.8, ha='center', color='#3d321e', zorder=13, style='italic', path_effects=halo)
for s in stairs:
    (cx, cy) = s[1]
    ax.text(cx + 9, cy - 11, f"{s[0]} {s[3]}", fontsize=4.8, color='#3a2f1c', zorder=13, path_effects=halo)
ax.text(840, 300, 'SEA', fontsize=22, color='#9fc3da', alpha=0.9, ha='center', rotation=90, weight='bold', zorder=2)
ax.text(420, 1186, 'CLIFFS / MOUNTAIN', fontsize=8, color='#e8e3d8', ha='center', zorder=13)

# grid + axes
for v in range(0, W + 1, 100): ax.axvline(v, color='white', lw=0.3, alpha=0.35, zorder=12)
for v in range(0, H + 1, 100): ax.axhline(v, color='white', lw=0.3, alpha=0.35, zorder=12)
ax.set_xticks(range(0, W + 1, 100)); ax.set_yticks(range(0, H + 1, 100))
ax.tick_params(labelsize=7)
ax.set_xlabel('X (studs, east →)', fontsize=8); ax.set_ylabel('Y (studs, north →)', fontsize=8)

# side panel: title, legend, elevations, north arrow, scale
fig.text(0.715, 0.95, 'HOLLOW OATH', fontsize=20, weight='bold', color='#1b2433')
fig.text(0.715, 0.927, 'Veyl Capital — City Layout Plan', fontsize=12, color='#1b2433')
fig.text(0.715, 0.912, '900 × 1200 studs · 1 grid square = 100 studs · lots snap to 4-stud grid', fontsize=7, color='#444')
lg = fig.add_axes([0.715, 0.46, 0.27, 0.43]); lg.axis('off'); lg.set_xlim(0, 10); lg.set_ylim(0, 22)
items = [
    ('patch', '#b8452f', 'Special building (gameplay)'), ('patch', '#f3efe6', 'Castle building / keep'),
    ('patch', '#3e4553', 'Machiya, 2 storeys'), ('patch', '#57606e', 'Machiya, 1 storey'),
    ('patch', '#f0ece2', 'Kura warehouse'), ('yag', None, 'Yagura watchtower'),
    ('gate', None, 'Gatehouse'), ('stone', None, 'Ishigaki / retaining / quay wall'),
    ('patch', '#b9b1a1', 'Stone stairs (rise in studs)'), ('patch', '#efe3c6', 'Street / square'),
    ('patch', '#9a7a52', 'Wooden pier'), ('boat', None, 'Moored boat'), ('torii', None, 'Red torii'),
    ('tree', None, 'Sculpted pine (S/M/L)'), ('patch', '#3f6f8f', 'Sea / canal'),
    ('patch', '#7c7466', 'Cliff rock'), ('light', None, 'Lighthouse'), ('well', None, 'Water well'),
]
for i, (t, c, lab) in enumerate(items):
    y = 21 - i * 1.15
    if t == 'patch': lg.add_patch(Rectangle((0.2, y - 0.35), 1.0, 0.7, fc=c, ec='#1d2330', lw=0.8))
    elif t == 'yag':
        lg.add_patch(Rectangle((0.35, y - 0.4), 0.8, 0.8, fc='#f3efe6', ec='#1d2330')); lg.add_patch(Rectangle((0.55, y - 0.2), 0.4, 0.4, fc='#3c4556'))
    elif t == 'gate': lg.add_patch(Rectangle((0.2, y - 0.25), 1.0, 0.5, fc='#3c4556', ec='#f3efe6'))
    elif t == 'stone': lg.plot([0.2, 1.2], [y, y], color='#8a8272', lw=5)
    elif t == 'boat': lg.add_patch(FancyBboxPatch((0.2, y - 0.2), 1.0, 0.4, boxstyle='round,pad=0,rounding_size=0.2', fc='#6b4a2b'))
    elif t == 'torii': lg.plot([0.3, 1.1], [y + 0.2, y + 0.2], color='#c0392b', lw=3); lg.plot([0.45, 0.45], [y - 0.3, y + 0.2], color='#c0392b', lw=2); lg.plot([0.95, 0.95], [y - 0.3, y + 0.2], color='#c0392b', lw=2)
    elif t == 'tree': lg.add_patch(Circle((0.7, y), 0.35, fc='#2f5a38'))
    elif t == 'light': lg.add_patch(Circle((0.7, y), 0.35, fc='#f3efe6', ec='#1d2330')); lg.add_patch(Circle((0.7, y), 0.15, fc='#f6c453'))
    elif t == 'well': lg.add_patch(Circle((0.7, y), 0.3, fc='#6b8fa6', ec='#3a3a3a'))
    lg.text(1.6, y, lab, fontsize=8, va='center')

el = fig.add_axes([0.715, 0.25, 0.27, 0.19]); el.axis('off'); el.set_xlim(0, 10); el.set_ylim(0, 10)
el.text(0, 9.6, 'Elevations (studs above sea level)', fontsize=9, weight='bold')
for i, (n, e, p) in enumerate(sorted(tiers, key=lambda t: -t[1])):
    y = 8.5 - i * 1.15
    el.add_patch(Rectangle((0, y - 0.4), 1.0, 0.8, fc=tier_colors[e], ec='#6b5d45'))
    el.text(1.4, y, f'+{e:<3}  {n}', fontsize=7.6, va='center', family='DejaVu Sans')
fig.text(0.715, 0.235, 'Keep: stone base +80→+96, five tiers to ≈ +160.\nSea level 0; quay top +4; walls between tiers\nare battered ishigaki (12–18 studs tall).',
         fontsize=7.2, va='top', color='#333')

na = fig.add_axes([0.73, 0.08, 0.08, 0.1]); na.axis('off'); na.set_xlim(-1, 1); na.set_ylim(-1, 1.3)
na.add_patch(Polygon([(0, 1), (-0.3, -0.4), (0, -0.1), (0.3, -0.4)], fc='#1b2433'))
na.text(0, 1.15, 'N', ha='center', fontsize=12, weight='bold')
# scale bar drawn in map units (bottom-right, over the sea)
for i in range(4):
    ax.add_patch(Rectangle((784 + i * 25, 18), 25, 5, fc='#1b2433' if i % 2 == 0 else 'white', ec='#1b2433', lw=0.8, zorder=14))
for i in range(5):
    ax.text(784 + i * 25, 10, str(i * 25), fontsize=6, ha='center', color='white', zorder=14, path_effects=halo_dark)
ax.text(834, 28, 'studs', fontsize=6.5, ha='center', color='white', zorder=14, path_effects=halo_dark)
fig.text(0.715, 0.06, f'{len(lots)} machiya lots · {len(trees)} trees · {len(yagura)} yagura · {len(piers)} piers',
         fontsize=7, color='#444')
fig.savefig(os.path.join(OUT, 'HO_City_LayoutPlan.png'), dpi=160, facecolor='#f4efe4')
print('lots', len(lots), 'trees', len(trees))
