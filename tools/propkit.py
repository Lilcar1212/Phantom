"""Props for interiors and streets. Every function returns Builder(s) built around the prop's own
bottom-centre origin with its front facing +Y (Roblox -Z). Glowing parts are returned as a separate
builder (name suffix _Glow) so they can be given Neon + a PointLight in Roblox."""
import math, random
from mathutils import Vector
from geo import Builder, lathe

MATS = ['Timber_Dark', 'Timber_Light', 'Iron_Wrought', 'Cloth_White', 'Cloth_Indigo', 'Cloth_Crimson', 'Cloth_Navy',
        'Shoji_Paper', 'Straw', 'Earth_Packed', 'RoofTile_Clay', 'Black_Lacquer', 'Red_Lacquer', 'Gold_Leaf',
        'Stone_Fitted', 'Stone_Granite', 'Wood_Planks', 'Tatami', 'Plaster_White', 'Cloth_Ochre']
GLOW_MATS = ['Ember', 'Magic_Glow', 'Shoji_Paper']


def B():
    return Builder(MATS)


def rounded_rect(w, h, r, n=3):
    """Profile (x across, y up) of a rounded rectangle centred on x = 0, bottom at y = 0."""
    pts = []
    for cx, cy, a0 in ((w / 2 - r, r, -90), (w / 2 - r, h - r, 0), (-w / 2 + r, h - r, 90), (-w / 2 + r, r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def soft_box(b, x0, x1, y0, y1, z0, z1, mat, r=0.12):
    """Cushion-like box: rounded-rect profile swept along X."""
    prof = rounded_rect(y1 - y0, z1 - z0, min(r, (z1 - z0) / 2 - 1e-3, (y1 - y0) / 2 - 1e-3))
    yc = (y0 + y1) / 2
    prof = [(-(py), pz) for py, pz in prof]      # sweep side axis = -Y for a path along +X
    b.sweep([Vector((x0, yc, z0)), Vector((x1, yc, z0))], prof, mat, smooth=True)


# ---------------------------------------------------------------------------------------------- bedroom
def futon(b=None, x=0.0, y=0.0, z=0.0, cover='Cloth_Indigo'):
    """Shikibuton mattress + kakebuton cover + pillow. 3.2 wide x 6.6 long (long axis = Y)."""
    b = b or B()
    W, L = 3.2, 6.6
    # mattress
    soft_box(b, x - W / 2, x + W / 2, y - L / 2, y + L / 2, z, z + 0.45, 'Cloth_White', 0.16)
    # cover, folded back at the pillow end
    soft_box(b, x - W / 2 - 0.08, x + W / 2 + 0.08, y - L / 2 - 0.05, y + L / 2 - 1.8, z + 0.4, z + 0.8, cover, 0.18)
    soft_box(b, x - W / 2 - 0.05, x + W / 2 + 0.05, y + L / 2 - 2.3, y + L / 2 - 1.6, z + 0.78, z + 1.0, cover, 0.1)
    # pillow (buckwheat makura)
    b.sweep([Vector((x - 0.8, y + L / 2 - 0.75, z + 0.42)), Vector((x + 0.8, y + L / 2 - 0.75, z + 0.42))],
            [(0.35 * math.cos(math.pi * i / 6) * -1, 0.28 * math.sin(math.pi * i / 6)) for i in range(7)],
            'Cloth_White', smooth=True)
    return b


def low_table(b=None, x=0.0, y=0.0, z=0.0, w=3.0, d=2.0, h=1.1, cushions=2):
    b = b or B()
    b.beam_box((x - w / 2, y - d / 2, z + h - 0.18), (x + w / 2, y + d / 2, z + h), 'Timber_Dark', along='x')
    b.beam_box((x - w / 2 + 0.1, y - d / 2 + 0.1, z + h - 0.36), (x + w / 2 - 0.1, y + d / 2 - 0.1, z + h - 0.18), 'Timber_Dark', along='x')
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.beam_box((x + sx * (w / 2 - 0.3) - 0.12, y + sy * (d / 2 - 0.25) - 0.12, z),
                       (x + sx * (w / 2 - 0.3) + 0.12, y + sy * (d / 2 - 0.25) + 0.12, z + h - 0.36), 'Timber_Dark', along='z')
    for k in range(cushions):
        sy = 1 if k % 2 == 0 else -1
        cy = y + sy * (d / 2 + 1.2)
        soft_box(b, x - 0.9, x + 0.9, cy - 0.9, cy + 0.9, z, z + 0.28, 'Cloth_Crimson', 0.12)
    return b


def andon(b=None, glow=None, x=0.0, y=0.0, z=0.0, h=2.2):
    """Floor lantern: base, frame, paper shade (paper goes to `glow` if given)."""
    b = b or B()
    g = glow or b
    s = 0.45
    b.beam_box((x - s - 0.05, y - s - 0.05, z), (x + s + 0.05, y + s + 0.05, z + 0.22), 'Timber_Dark', along='x')
    g.box((x - s + 0.02, y - s + 0.02, z + 0.3), (x + s - 0.02, y + s - 0.02, z + h - 0.15), 'Shoji_Paper')
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.beam_box((x + sx * s - 0.05, y + sy * s - 0.05, z + 0.22), (x + sx * s + 0.05, y + sy * s + 0.05, z + h), 'Timber_Dark', along='z')
    for zz in (z + 0.3, z + h - 0.15):
        b.beam_box((x - s - 0.03, y - s - 0.03, zz - 0.05), (x + s + 0.03, y + s + 0.03, zz + 0.05), 'Timber_Dark', along='x')
    b.beam_box((x - 0.05, y - s, z + h - 0.05), (x + 0.05, y + s, z + h + 0.05), 'Timber_Dark', along='y')   # handle
    return b


def tansu(b=None, x=0.0, y=0.0, z=0.0, w=3.0, d=1.4, h=3.0, rows=3):
    """Storage chest: light timber body, drawers with iron pulls and corner fittings. Front = +Y."""
    b = b or B()
    b.box((x - w / 2, y - d / 2, z + 0.15), (x + w / 2, y + d / 2 - 0.02, z + h), 'Timber_Light')
    b.box((x - w / 2 + 0.05, y - d / 2 + 0.05, z), (x + w / 2 - 0.05, y + d / 2 - 0.05, z + 0.15), 'Timber_Dark')
    dh = (h - 0.35) / rows
    for r in range(rows):
        z0 = z + 0.25 + r * dh
        cols = 2 if r == rows - 1 else 1
        for c in range(cols):
            x0 = x - w / 2 + 0.1 + (w - 0.2) * c / cols
            x1 = x - w / 2 + 0.1 + (w - 0.2) * (c + 1) / cols
            b.box((x0 + 0.03, y + d / 2 - 0.02, z0 + 0.04), (x1 - 0.03, y + d / 2 + 0.05, z0 + dh - 0.04), 'Timber_Light',
                  uv_off=(random.random(), 0))
            xm = (x0 + x1) / 2; zm = z0 + dh / 2
            b.box((xm - 0.3, y + d / 2 + 0.05, zm - 0.18), (xm + 0.3, y + d / 2 + 0.08, zm + 0.18), 'Iron_Wrought')
            b.beam_box((xm - 0.22, y + d / 2 + 0.08, zm - 0.04), (xm + 0.22, y + d / 2 + 0.16, zm + 0.04), 'Iron_Wrought', along='x')
    for sx in (-1, 1):
        for zz in (z + 0.15, z + h - 0.35):       # iron corner fittings
            xa, xb = sorted((x + sx * w / 2, x + sx * (w / 2 - 0.25)))
            b.box((xa - 0.02, y + d / 2 - 0.3, zz), (xb + 0.02, y + d / 2 + 0.06, zz + 0.2), 'Iron_Wrought')
    return b


# ---------------------------------------------------------------------------------------------- goods
def barrel(b=None, x=0.0, y=0.0, z=0.0, r=0.9, h=2.4, straw=False):
    """Stave barrel with bulge, hoops and lid; straw=True -> komodaru (straw-wrapped sake cask with rope)."""
    b = b or B()
    prof = [(r * 0.86, 0.0), (r * 0.97, h * 0.25), (r, h * 0.5), (r * 0.97, h * 0.75), (r * 0.86, h)]
    lathe(b, (x, y, z), prof, 14, 'Straw' if straw else 'Timber_Light')
    lathe(b, (x, y, z + h - 0.02), [(r * 0.8, 0.0), (r * 0.8, 0.06), (0.0, 0.06)], 14, 'Timber_Dark', cap_bottom=False)
    for t in ((0.1, 0.9) if straw else (0.08, 0.3, 0.7, 0.92)):
        rr = r * (0.86 + 0.14 * math.sin(math.pi * t)) + 0.04
        mat = 'Cloth_White' if straw else 'Iron_Wrought'
        lathe(b, (x, y, z + h * t - 0.08), [(rr, 0.0), (rr, 0.16)], 14, mat, cap_bottom=False, cap_top=False)
    if straw:
        # rope lacing down the sides
        for k in range(4):
            a = 2 * math.pi * k / 4
            p0 = Vector((x + math.cos(a) * r * 0.9, y + math.sin(a) * r * 0.9, z + 0.1))
            p1 = Vector((x + math.cos(a) * r * 1.02, y + math.sin(a) * r * 1.02, z + h / 2))
            p2 = Vector((x + math.cos(a) * r * 0.9, y + math.sin(a) * r * 0.9, z + h - 0.1))
            b.sweep([p0, p1, p2], [(-0.05, -0.05), (0.05, -0.05), (0.05, 0.05), (-0.05, 0.05)], 'Cloth_White',
                    up=Vector((math.cos(a), math.sin(a), 0)))
    return b


def tawara(b=None, x=0.0, y=0.0, z=0.0, L=2.4, r=0.6, rot=0.0):
    """Rice straw bale lying down (long axis along X rotated by rot), with rope bands."""
    b = b or B()
    d = Vector((math.cos(rot), math.sin(rot), 0))
    c = Vector((x, y, z + r))
    prof = [(r * math.cos(2 * math.pi * i / 10), r * math.sin(2 * math.pi * i / 10)) for i in range(10)]
    pts = [c - d * L / 2, c - d * (L / 2 - 0.15), c + d * (L / 2 - 0.15), c + d * L / 2]
    scale = [0.8, 1.0, 1.0, 0.8]
    # build as 3 sweeps (tapered ends) using per-ring scaling
    for (p0, s0), (p1, s1) in zip(zip(pts, scale), list(zip(pts, scale))[1:]):
        b.sweep([p0, p1], [(px * (s0 + s1) / 2, py * (s0 + s1) / 2) for px, py in prof], 'Straw', smooth=True,
                caps=True)
    for t in (-0.3, 0.0, 0.3):
        cc = c + d * L * t
        b.sweep([cc - d * 0.07, cc + d * 0.07], [(px * 1.04, py * 1.04) for px, py in prof], 'Cloth_White', smooth=True)
    return b


def sack(b=None, x=0.0, y=0.0, z=0.0, h=1.8, r=0.6, mat='Cloth_White'):
    b = b or B()
    prof = [(r * 0.85, 0.0), (r, 0.3), (r * 1.02, h * 0.55), (r * 0.8, h * 0.82), (r * 0.3, h * 0.92), (r * 0.36, h),
            (0.0, h + 0.05)]
    lathe(b, (x, y, z), prof, 10, mat)
    lathe(b, (x, y, z + h * 0.88), [(r * 0.34, 0.0), (r * 0.34, 0.1)], 10, 'Straw', cap_bottom=False, cap_top=False)
    return b


def jar(b=None, x=0.0, y=0.0, z=0.0, h=1.6, r=0.7, mat='Earth_Packed', lid=True):
    """Ceramic storage jar (tsubo)."""
    b = b or B()
    prof = [(r * 0.55, 0.0), (r * 0.85, h * 0.2), (r, h * 0.5), (r * 0.8, h * 0.78), (r * 0.42, h * 0.9), (r * 0.46, h)]
    lathe(b, (x, y, z), prof, 12, mat, cap_top=not lid)
    if lid:
        lathe(b, (x, y, z + h), [(r * 0.5, 0.0), (r * 0.5, 0.06), (r * 0.3, 0.16), (0.0, 0.2)], 12, 'Timber_Dark',
              cap_bottom=True)
    return b


def crate(b=None, x=0.0, y=0.0, z=0.0, w=1.6, d=1.4, h=1.2):
    b = b or B()
    b.box((x - w / 2 + 0.05, y - d / 2 + 0.05, z), (x + w / 2 - 0.05, y + d / 2 - 0.05, z + h - 0.02), 'Wood_Planks',
          uv_off=(random.random(), random.random()))
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.beam_box((x + sx * (w / 2 - 0.08) - 0.08, y + sy * (d / 2 - 0.08) - 0.08, z),
                       (x + sx * (w / 2 - 0.08) + 0.08, y + sy * (d / 2 - 0.08) + 0.08, z + h), 'Timber_Dark', along='z')
    for zz in (z, z + h - 0.14):
        b.beam_box((x - w / 2, y - d / 2, zz), (x + w / 2, y - d / 2 + 0.1, zz + 0.14), 'Timber_Dark', along='x')
        b.beam_box((x - w / 2, y + d / 2 - 0.1, zz), (x + w / 2, y + d / 2, zz + 0.14), 'Timber_Dark', along='x')
    return b


def shelf_unit(b=None, x=0.0, y=0.0, z=0.0, w=4.0, d=1.2, h=6.0, levels=4, back=True):
    """Open shelving (front = +Y). Returns (builder, list of shelf-top z)."""
    b = b or B()
    for sx in (-1, 1):
        b.beam_box((x + sx * w / 2 - (0.2 if sx > 0 else 0), y - d / 2, z), (x + sx * w / 2 + (0 if sx > 0 else 0.2), y + d / 2, z + h),
                   'Timber_Dark', along='z')
    if back:
        b.box((x - w / 2 + 0.2, y - d / 2, z), (x + w / 2 - 0.2, y - d / 2 + 0.08, z + h), 'Wood_Planks')
    tops = []
    for k in range(levels):
        zz = z + 0.3 + (h - 0.6) * k / max(1, levels - 1)
        b.box((x - w / 2 + 0.2, y - d / 2 + 0.08, zz - 0.12), (x + w / 2 - 0.2, y + d / 2, zz), 'Timber_Light')
        tops.append(zz)
    return b, tops


def counter(b=None, x=0.0, y=0.0, z=0.0, w=6.0, d=1.6, h=3.2):
    b = b or B()
    b.box((x - w / 2, y - d / 2 + 0.2, z), (x + w / 2, y + d / 2 - 0.1, z + h - 0.2), 'Timber_Dark')
    b.beam_box((x - w / 2 - 0.15, y - d / 2, z + h - 0.2), (x + w / 2 + 0.15, y + d / 2 + 0.1, z + h), 'Timber_Light', along='x')
    n = int(w / 1.2)
    for i in range(n + 1):
        xx = x - w / 2 + 0.1 + (w - 0.2) * i / n
        b.beam_box((xx - 0.06, y + d / 2 - 0.12, z + 0.2), (xx + 0.06, y + d / 2 - 0.02, z + h - 0.25), 'Timber_Light', along='z')
    b.box((x - w / 2, y + d / 2 - 0.14, z), (x + w / 2, y + d / 2 - 0.02, z + 0.2), 'Timber_Light')
    return b


# ---------------------------------------------------------------------------------------------- weapons & armour
def katana(b, p, direction, up, length=3.4, sheathed=True):
    """A katana lying along `direction` from grip end p: wrapped hilt, tsuba, curved (sheathed) blade."""
    p, dvec, upv = Vector(p), Vector(direction).normalized(), Vector(up).normalized()
    side = dvec.cross(upv).normalized()
    hilt = length * 0.28
    b.sweep([p, p + dvec * hilt], [(-0.07, -0.09), (0.07, -0.09), (0.07, 0.09), (-0.07, 0.09)], 'Black_Lacquer')
    for i in range(1, 6):
        c = p + dvec * hilt * i / 6
        b.sweep([c - dvec * 0.03, c + dvec * 0.03], [(-0.085, -0.105), (0.085, -0.105), (0.085, 0.105), (-0.085, 0.105)],
                'Cloth_White')
    t = p + dvec * hilt
    prof = [(0.22 * math.cos(2 * math.pi * i / 8), 0.22 * math.sin(2 * math.pi * i / 8)) for i in range(8)]
    b.sweep([t, t + dvec * 0.06], prof, 'Gold_Leaf', up=upv)
    n = 6
    pts = []
    for i in range(n + 1):
        s = i / n
        pts.append(t + dvec * (0.06 + (length - hilt) * s) + upv * (0.18 * s * s))
    prof = [(-0.07, -0.12), (0.07, -0.12), (0.07, 0.1), (0.0, 0.14), (-0.07, 0.1)] if sheathed else \
        [(-0.015, -0.1), (0.015, -0.1), (0.0, 0.1)]
    b.sweep(pts, prof, 'Black_Lacquer' if sheathed else 'Iron_Wrought', up=upv)


def sword_rack(b=None, x=0.0, y=0.0, z=0.0, swords=3):
    """Floor-standing katana stand (katana-kake), swords held horizontally, facing +Y."""
    b = b or B()
    w = 3.8
    b.beam_box((x - w / 2, y - 0.5, z), (x + w / 2, y + 0.5, z + 0.3), 'Black_Lacquer', along='x')
    for sx in (-1, 1):
        b.beam_box((x + sx * (w / 2 - 0.35) - 0.15, y - 0.2, z + 0.3), (x + sx * (w / 2 - 0.35) + 0.15, y + 0.2, z + 0.3 + 0.9 * swords + 0.4),
                   'Black_Lacquer', along='z')
        for k in range(swords):
            zz = z + 0.9 + 0.9 * k
            b.beam_box((x + sx * (w / 2 - 0.35) - 0.15, y + 0.2, zz - 0.1), (x + sx * (w / 2 - 0.35) + 0.15, y + 0.55, zz + 0.1),
                       'Black_Lacquer', along='y')
            b.box((x + sx * (w / 2 - 0.35) - 0.15, y + 0.45, zz + 0.1), (x + sx * (w / 2 - 0.35) + 0.15, y + 0.55, zz + 0.28),
                  'Black_Lacquer')
    for k in range(swords):
        zz = z + 1.1 + 0.9 * k
        katana(b, (x - w / 2 + 0.1, y + 0.38, zz), (1, 0, 0), (0, 0, 1), length=w - 0.2)
    return b


def wall_sword_rack(b=None, x=0.0, y=0.0, z=0.0, swords=4, w=4.2):
    """Wall-mounted rack (back = -Y on the wall) with bare blades and sheathed swords."""
    b = b or B()
    b.box((x - w / 2, y, z), (x + w / 2, y + 0.15, z + 0.9 * swords + 0.6), 'Timber_Dark')
    for sx in (-1, 1):
        for k in range(swords):
            zz = z + 0.5 + 0.9 * k
            b.beam_box((x + sx * (w / 2 - 0.5) - 0.12, y + 0.15, zz - 0.08), (x + sx * (w / 2 - 0.5) + 0.12, y + 0.6, zz + 0.08),
                       'Timber_Light', along='y')
    for k in range(swords):
        katana(b, (x - w / 2 + 0.15, y + 0.45, z + 0.66 + 0.9 * k), (1, 0, 0), (0, 0, 1), length=w - 0.3, sheathed=(k % 2 == 0))
    return b


def samurai_armour(b=None, x=0.0, y=0.0, z=0.0, lacquer='Red_Lacquer', trim='Black_Lacquer'):
    """Lacquered samurai armour (o-yoroi style) on a display stand, ~6.2 tall. Front = +Y."""
    b = b or B()
    c = Vector((x, y, z))
    # stand: box base + pole + shoulder bar
    b.box((x - 1.3, y - 1.0, z), (x + 1.3, y + 1.0, z + 0.5), 'Black_Lacquer')
    b.beam_box((x - 0.12, y - 0.12, z + 0.5), (x + 0.12, y + 0.12, z + 3.0), 'Timber_Dark', along='z')
    zb = z + 2.4           # bottom of the cuirass
    # skirt (kusazuri): 4 panels of 5 lames, hanging, slightly flared
    for k, ang in enumerate((90, 0, 180, 270)):
        a = math.radians(ang)
        n = Vector((math.cos(a), math.sin(a), 0))
        t = Vector((-n.y, n.x, 0))
        for j in range(5):
            zz = zb - 0.25 - j * 0.3
            off = 0.72 + j * 0.05
            p0 = c + n * off + Vector((0, 0, zz - z))
            prof = [(-0.6, -0.02), (0.6, -0.02), (0.6, 0.24), (-0.6, 0.24)]
            b.sweep([p0 - n * 0.04, p0 + n * 0.04], [(px * (1 + j * 0.05), py) for px, py in prof],
                    lacquer if j % 2 == 0 else trim, up=Vector((0, 0, 1)))
            # lacing cords (odoshi)
            for s in (-0.35, 0.0, 0.35):
                q = p0 + t * s * (1 + j * 0.05) + n * 0.05
                b.box((min(q.x, q.x) - 0.03, min(q.y, q.y) - 0.03, q.z - 0.06), (q.x + 0.03, q.y + 0.03, q.z + 0.3), 'Cloth_Crimson')
    # cuirass (do): lathe of a torso profile with horizontal lames (alternating lacquer/trim bands)
    prof = [(0.72, 0.0), (0.66, 0.35), (0.7, 0.8), (0.82, 1.3), (0.78, 1.7), (0.55, 1.9)]
    lathe(b, (x, y, zb), prof, 12, lacquer, cap_bottom=True, cap_top=True)
    for hh in (0.3, 0.6, 0.9, 1.2):
        rr = 0.72 + (0.1 if hh > 0.8 else 0.0)
        lathe(b, (x, y, zb + hh - 0.04), [(rr + 0.03, 0.0), (rr + 0.03, 0.08)], 12, 'Cloth_Crimson', cap_bottom=False, cap_top=False)
    # gold crest boss on the breastplate
    b.cylinder((x, y + 0.8, zb + 1.35), (x, y + 0.9, zb + 1.35), 0.16, 8, 'Gold_Leaf')
    # shoulder guards (sode): curved plates of 5 lames each side
    for sx in (-1, 1):
        for j in range(5):
            zz = zb + 1.75 - j * 0.28
            p = Vector((x + sx * (0.86 + j * 0.05), y, zz))
            b.sweep([p - Vector((0, 0.55, 0)), p + Vector((0, 0.55, 0))],
                    [(-0.05, -0.02), (0.05, -0.02), (0.05, 0.3), (-0.05, 0.3)], lacquer if j % 2 == 0 else trim,
                    up=Vector((0, 0, 1)))
        b.beam_box((x + sx * 0.6 - 0.25, y - 0.3, zb + 1.8), (x + sx * 0.6 + 0.25, y + 0.3, zb + 2.0), trim, along='x')
    # helmet (kabuto): bowl + flaring neck guard + crest
    zh = zb + 2.15
    b.beam_box((x - 0.1, y - 0.1, zb + 1.9), (x + 0.1, y + 0.1, zh), 'Timber_Dark', along='z')
    lathe(b, (x, y, zh), [(0.5, 0.0), (0.52, 0.2), (0.46, 0.45), (0.3, 0.62), (0.0, 0.68)], 12, trim)
    for j in range(4):
        r0 = 0.55 + j * 0.12
        lathe(b, (x, y, zh - 0.05 - j * 0.14), [(r0 + 0.1, 0.0), (r0, 0.14)], 12, lacquer if j % 2 == 0 else trim,
              cap_bottom=False, cap_top=False)
    # visor + menpo mask
    b.beam_box((x - 0.45, y + 0.35, zh + 0.05), (x + 0.45, y + 0.6, zh + 0.14), trim, along='x')
    b.box((x - 0.28, y + 0.38, zh - 0.5), (x + 0.28, y + 0.55, zh - 0.02), 'Black_Lacquer')
    # golden kuwagata crest (two horns)
    for sx in (-1, 1):
        pts = [Vector((x + sx * 0.12, y + 0.55, zh + 0.14)), Vector((x + sx * 0.35, y + 0.62, zh + 0.6)),
               Vector((x + sx * 0.42, y + 0.6, zh + 1.1))]
        b.sweep(pts, [(-0.03, -0.1), (0.03, -0.1), (0.03, 0.1), (-0.03, 0.1)], 'Gold_Leaf', up=Vector((0, 1, 0)))
    b.box((x - 0.18, y + 0.54, zh + 0.12), (x + 0.18, y + 0.66, zh + 0.4), 'Gold_Leaf')
    return b


def spear_rack(b=None, x=0.0, y=0.0, z=0.0, spears=4, w=4.0):
    b = b or B()
    b.box((x - w / 2, y - 0.4, z), (x + w / 2, y + 0.4, z + 0.3), 'Timber_Dark')
    b.beam_box((x - w / 2, y - 0.3, z + 3.2), (x + w / 2, y + 0.3, z + 3.45), 'Timber_Dark', along='x')
    for sx in (-1, 1):
        b.beam_box((x + sx * w / 2 - (0.2 if sx > 0 else 0), y - 0.15, z + 0.3), (x + sx * w / 2 + (0 if sx > 0 else 0.2), y + 0.15, z + 3.45),
                   'Timber_Dark', along='z')
    for k in range(spears):
        xx = x - w / 2 + 0.5 + (w - 1.0) * k / max(1, spears - 1)
        b.cylinder((xx, y, z + 0.3), (xx, y, z + 8.2), 0.07, 6, 'Timber_Dark')
        b.sweep([Vector((xx, y, z + 8.2)), Vector((xx, y, z + 9.2))], [(-0.1, -0.02), (0.1, -0.02), (0.0, 0.02)], 'Iron_Wrought',
                up=Vector((0, 1, 0)))
        b.cylinder((xx, y, z + 8.1), (xx, y, z + 8.3), 0.1, 6, 'Gold_Leaf')
    return b


# ---------------------------------------------------------------------------------------------- forge
def anvil(b=None, x=0.0, y=0.0, z=0.0):
    """Anvil on a tree-stump block. Horn points +X."""
    b = b or B()
    lathe(b, (x, y, z), [(0.75, 0.0), (0.7, 0.2), (0.65, 1.6), (0.68, 1.7)], 12, 'Timber_Light')
    zt = z + 1.7
    side = [(-0.55, 0.0), (0.55, 0.0), (0.4, 0.25), (0.35, 0.5), (0.7, 0.62), (1.3, 0.85), (0.7, 1.0), (-0.75, 1.0),
            (-0.8, 0.82), (-0.45, 0.62), (-0.4, 0.25)]
    b.prism(side, (x, y - 0.3, zt), (1, 0, 0), (0, 0, 1), (0, 1, 0), 0.6, 'Iron_Wrought')
    # hammer resting on the face
    b.beam_box((x - 0.2, y - 0.1, zt + 1.0), (x + 0.9, y + 0.0, zt + 1.08), 'Timber_Dark', along='x')
    b.beam_box((x - 0.35, y - 0.18, zt + 1.0), (x - 0.1, y + 0.08, zt + 1.22), 'Iron_Wrought', along='y')
    return b


def forge(b=None, glow=None, x=0.0, y=0.0, z=0.0, w=4.4, d=3.4, h=2.8):
    """Stone hearth with a coal pit (embers in `glow`) and an iron hood; chimney added by the building."""
    b = b or B()
    g = glow or b
    b.box((x - w / 2, y - d / 2, z), (x + w / 2, y + d / 2, z + h), 'Stone_Fitted')
    b.box((x - w / 2 - 0.1, y - d / 2 - 0.1, z + h), (x + w / 2 + 0.1, y + d / 2 + 0.1, z + h + 0.25), 'Stone_Granite',
          skip=('+z',))
    # rim around the pit
    pit = (x - 1.0, y - 0.9, x + 1.0, y + 0.9)
    b.box((x - w / 2 - 0.1, y - d / 2 - 0.1, z + h + 0.25), (pit[0], y + d / 2 + 0.1, z + h + 0.45), 'Stone_Granite')
    b.box((pit[2], y - d / 2 - 0.1, z + h + 0.25), (x + w / 2 + 0.1, y + d / 2 + 0.1, z + h + 0.45), 'Stone_Granite')
    b.box((pit[0], y - d / 2 - 0.1, z + h + 0.25), (pit[2], pit[1], z + h + 0.45), 'Stone_Granite')
    b.box((pit[0], pit[3], z + h + 0.25), (pit[2], y + d / 2 + 0.1, z + h + 0.45), 'Stone_Granite')
    # coal bed (glowing)
    g.box((pit[0], pit[1], z + h + 0.1), (pit[2], pit[3], z + h + 0.38), 'Ember')
    # tongs + tuyere pipe
    b.cylinder((x - w / 2 - 0.1, y, z + h - 0.3), (pit[0] + 0.1, y, z + h + 0.2), 0.12, 8, 'Iron_Wrought')
    b.beam_box((pit[2] - 0.2, y - 0.05, z + h + 0.45), (x + w / 2 + 0.8, y + 0.05, z + h + 0.52), 'Iron_Wrought', along='x')
    return b


def bellows(b=None, x=0.0, y=0.0, z=0.0):
    """Box bellows (fuigo) with push handle; long axis = X."""
    b = b or B()
    b.box((x - 1.4, y - 0.6, z), (x + 1.4, y + 0.6, z + 1.6), 'Timber_Dark')
    b.beam_box((x - 1.5, y - 0.65, z + 1.6), (x + 1.5, y + 0.65, z + 1.75), 'Timber_Light', along='x')
    b.beam_box((x + 1.4, y - 0.08, z + 0.9), (x + 2.6, y + 0.08, z + 1.05), 'Timber_Light', along='x')
    b.beam_box((x + 2.5, y - 0.35, z + 0.85), (x + 2.65, y + 0.35, z + 1.1), 'Timber_Light', along='y')
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.box((x + sx * 1.2 - 0.12, y + sy * 0.45 - 0.12, z - 0.0), (x + sx * 1.2 + 0.12, y + sy * 0.45 + 0.12, z + 0.2), 'Iron_Wrought')
    return b


def quench_trough(b=None, x=0.0, y=0.0, z=0.0, w=3.0, d=1.2, h=1.6):
    b = b or B()
    b.box((x - w / 2, y - d / 2, z), (x + w / 2, y + d / 2, z + 0.2), 'Timber_Dark')
    for sx in (-1, 1):
        b.box((x + sx * w / 2 - (0.15 if sx > 0 else 0), y - d / 2, z + 0.2), (x + sx * w / 2 + (0 if sx > 0 else 0.15), y + d / 2, z + h), 'Timber_Dark')
    for sy in (-1, 1):
        b.box((x - w / 2 + 0.15, y + sy * d / 2 - (0.15 if sy > 0 else 0), z + 0.2), (x + w / 2 - 0.15, y + sy * d / 2 + (0 if sy > 0 else 0.15), z + h), 'Timber_Dark')
    b.box((x - w / 2 + 0.15, y - d / 2 + 0.15, z + 0.2), (x + w / 2 - 0.15, y + d / 2 - 0.15, z + h - 0.25), 'Black_Lacquer')   # water
    for t in (0.25, 0.75):
        b.beam_box((x - w / 2 - 0.03, y - d / 2 - 0.03, z + h * t - 0.06), (x + w / 2 + 0.03, y + d / 2 + 0.03, z + h * t + 0.06), 'Iron_Wrought', along='x')
    return b


def tool_rack(b=None, x=0.0, y=0.0, z=0.0, w=3.6):
    """Wall board (back = -Y) with hammers and tongs hanging."""
    b = b or B()
    b.box((x - w / 2, y, z), (x + w / 2, y + 0.12, z + 2.2), 'Wood_Planks')
    n = 5
    for i in range(n):
        xx = x - w / 2 + 0.4 + (w - 0.8) * i / (n - 1)
        b.beam_box((xx - 0.04, y + 0.12, z + 1.95), (xx + 0.04, y + 0.3, z + 2.03), 'Iron_Wrought', along='y')
        if i % 2 == 0:   # hammer
            b.beam_box((xx - 0.05, y + 0.2, z + 0.6), (xx + 0.05, y + 0.3, z + 1.95), 'Timber_Light', along='z')
            b.beam_box((xx - 0.3, y + 0.12, z + 0.35), (xx + 0.3, y + 0.38, z + 0.62), 'Iron_Wrought', along='x')
        else:            # tongs
            for s in (-1, 1):
                b.beam(Vector((xx, y + 0.25, z + 1.9)), Vector((xx + s * 0.18, y + 0.25, z + 0.4)), 0.06, 0.06, 'Iron_Wrought',
                       up=Vector((0, 1, 0)))
    return b


# ---------------------------------------------------------------------------------------------- magic
def orb(b, glow, x, y, z, r=0.35):
    """Glowing orb (glow builder) on a small lacquered stand (b)."""
    lathe(b, (x, y, z), [(0.28, 0.0), (0.2, 0.12), (0.14, 0.2), (0.24, 0.28), (0.24, 0.3)], 8, 'Black_Lacquer')
    n = 6
    prof = [(r * math.sin(math.pi * i / n), r - r * math.cos(math.pi * i / n)) for i in range(n + 1)]
    prof[0] = (0.0, 0.0); prof[-1] = (0.0, 2 * r)
    lathe(glow, (x, y, z + 0.26), prof, 10, 'Magic_Glow')


def crystal(glow, x, y, z, h=0.9, r=0.18, tilt=(0.0, 0.0)):
    """Hexagonal crystal with a pointed tip."""
    t = Vector((tilt[0], tilt[1], 1)).normalized()
    p0 = Vector((x, y, z)); p1 = p0 + t * h * 0.75; p2 = p0 + t * h
    prof = [(r * math.cos(2 * math.pi * i / 6), r * math.sin(2 * math.pi * i / 6)) for i in range(6)]
    rings = glow.sweep([p0, p1], prof, 'Magic_Glow', up=Vector((0, 1, 0)), caps=False)
    tip = glow.bm.verts.new(p2)
    top = rings[-1]
    for i in range(6):
        glow.face([top[i], top[(i + 1) % 6], tip], 'Magic_Glow', [(0, 0), (0.2, 0), (0.1, 0.3)],
                  out=((top[i].co + top[(i + 1) % 6].co) / 2 - p1) + t * 0.3)
    glow.face(list(rings[0]), 'Magic_Glow', [(0, 0)] * 6, out=-t)


def ofuda(b, x, y, z, n=5, w=1.6):
    """Row of paper charm strips hanging from a cord (along X)."""
    b.cylinder((x - w / 2, y, z), (x + w / 2, y, z), 0.03, 5, 'Cloth_Crimson')
    for i in range(n):
        xx = x - w / 2 + 0.15 + (w - 0.3) * i / max(1, n - 1)
        b.box((xx - 0.1, y - 0.01, z - 0.8), (xx + 0.1, y + 0.01, z - 0.02), 'Shoji_Paper')
