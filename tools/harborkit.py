"""Harbour, street and nature props: quay walls, piers, boats, lighthouse, arched bridge, stone stairs, torii,
stone lantern, chochin, banner, cart, market stall, benches, well, bamboo fence, sculpted pines, cliff rocks.

Front = +Y (Roblox -Z), up = +Z. Glowing parts are returned in a separate builder (-> '_Glow' mesh).
"""
import math, random
import bmesh
from mathutils import Vector, Matrix, noise
from geo import Builder, lathe, loft, tube
import propkit as pk
from castlekit import ishigaki_straight, mesh_join, banner, remap, CASTLE_MATS
from roofkit import MATS as ROOF_MATS

MATS = sorted(set(CASTLE_MATS + pk.MATS + ['Bamboo', 'Pine_Bark', 'Pine_Needles', 'Rope', 'Sail_Canvas', 'Cloth_Ochre']))
GLOW = ['Shoji_Paper', 'Magic_Glow', 'Ember']


def B():
    return Builder(MATS)


def G():
    return Builder(GLOW)


# ------------------------------------------------------------------------------------------------ helpers
def blob(b, c, radii, mat, subdiv=2, amp=0.25, freq=0.6, seed=0, flat_bottom=None, octaves=3, smooth=True):
    """Noise-displaced icosphere (rocks, foliage pads). radii = (rx, ry, rz)."""
    tmp = bmesh.new()
    bmesh.ops.create_icosphere(tmp, subdivisions=subdiv, radius=1.0)
    off = Vector((seed * 13.7, seed * 7.1, seed * 3.3))
    c = Vector(c)
    vmap = {}
    for v in tmp.verts:
        n = v.co.normalized()
        d = noise.fractal(n * freq * 3 + off, 1.0, 2.0, octaves) * amp
        p = Vector((n.x * radii[0], n.y * radii[1], n.z * radii[2])) * (1.0 + d)
        if flat_bottom is not None and p.z < flat_bottom:
            p.z = flat_bottom + (p.z - flat_bottom) * 0.05
        vmap[v] = b.bm.verts.new(c + p)
    for f in tmp.faces:
        vs = [vmap[v] for v in f.verts]
        uvs = [((v.co.x + v.co.y * 0.5) * 0.25, v.co.z * 0.25) for v in vs]
        b.face(vs, mat, uvs, out=(sum((v.co for v in vs), Vector()) / len(vs)) - c, smooth=smooth)
    tmp.free()


def rope(b, p0, p1, sag=0.4, r=0.06, n=6):
    p0, p1 = Vector(p0), Vector(p1)
    pts = [p0.lerp(p1, i / n) - Vector((0, 0, sag * math.sin(math.pi * i / n))) for i in range(n + 1)]
    tube(b, pts, [r] * len(pts), 5, 'Rope', smooth=True)


def post(b, x, y, z0, z1, r=0.3, mat='Timber_Dark', segs=8):
    b.cylinder((x, y, z0), (x, y, z1), r, segs, mat)


# ================================================================================================ HARBOUR
def quay(L=16.0, steps=False):
    """Quay wall: near-vertical fitted stone (8 tall) + dressed cap stones (top at +8.6).
    Origin = bottom of the wall directly under the top face edge. With steps=True a flight of stone
    steps runs down the face along X (top at x = -L/2, bottom near the water at x = +L/2)."""
    b = ishigaki_straight(L, H=8.0, B=0.8, T=3.0, seed=int(L) + (5 if steps else 0))
    r = random.Random(7)
    x = -L / 2
    while x < L / 2 - 1e-6:
        w = min(L / 2 - x, r.uniform(1.8, 3.0))
        if L / 2 - (x + w) < 1.0: w = L / 2 - x
        b.box((x + 0.03, -2.2, 8.0), (x + w - 0.03, 0.35, 8.6), 'Stone_Fitted', uv_off=(r.random(), r.random()))
        x += w
    if steps:
        n = 10
        for i in range(n):
            zt = 8.6 - (i + 1) * 0.45
            x0 = -L / 2 + 1.0 + i * (L - 2.0) / n
            b.box((x0, 0.2, 0.0), (L / 2 - 0.2, 3.0, zt), 'Stone_Fitted', uv_off=(0.1 * i, 0.3 * i))
        b.box((-L / 2 + 0.6, 2.8, 0.0), (L / 2 - 0.2, 3.3, 1.2), 'Stone_Granite')
    return b


def pier_segment(b, y0, y1, w=12.0, deck=4.0, depth=-8.0, rail=True, posts_at_start=True):
    """Pier deck from y0 to y1 (along +Y), deck top at `deck`, piles down to `depth`."""
    b.box((-w / 2, y0, deck - 0.4), (w / 2, y1, deck), 'Wood_Planks')
    for xs in (-w / 2 + 0.6, 0.0, w / 2 - 0.6):
        b.beam_box((xs - 0.3, y0, deck - 1.1), (xs + 0.3, y1, deck - 0.4), 'Timber_Dark', along='y')
    ys = [y0 + 0.5 + (y1 - y0 - 1.0) * k / max(1, round((y1 - y0) / 8)) for k in range(int(max(1, round((y1 - y0) / 8))) + 1)]
    if not posts_at_start: ys = ys[1:]
    for yy in ys:
        b.beam_box((-w / 2, yy - 0.3, deck - 1.7), (w / 2, yy + 0.3, deck - 1.1), 'Timber_Dark', along='x')
        for xs in (-w / 2 + 0.6, w / 2 - 0.6):
            post(b, xs, yy, depth, deck - 1.1, r=0.45, mat='Timber_Dark')
        post(b, 0.0, yy, depth, deck - 1.1, r=0.4, mat='Timber_Dark')
    if rail:
        for side in (-1, 1):
            xr = side * (w / 2 - 0.3)
            rp = [y0 + 1.0 + (y1 - y0 - 2.0) * k / max(1, int((y1 - y0) / 4)) for k in range(int((y1 - y0) / 4) + 1)]
            for yy in rp:
                post(b, xr, yy, deck, deck + 2.2, r=0.14, mat='Timber_Dark', segs=6)
            for a, c in zip(rp, rp[1:]):
                rope(b, (xr, a, deck + 2.0), (xr, c, deck + 2.0), sag=0.35)


def bollard(b, x, y, z):
    lathe(b, (x, y, z), [(0.35, 0.0), (0.28, 0.6), (0.38, 0.75), (0.3, 0.9), (0.0, 0.95)], 8, 'Timber_Dark')


def pier_full(length=92.0, w=12.0, head=(28.0, 16.0)):
    """Whole pier as placed by the city builder: origin = shore end centre at SEA LEVEL (z = 0), deck at +4,
    extends along +Y (front) for `length`, T-shaped head at the end."""
    b = B()
    pier_segment(b, 0.0, length - head[1], w=w)
    hw, hd = head
    b.box((-hw / 2, length - hd, 3.6), (hw / 2, length, 4.0), 'Wood_Planks')
    for xs in [-hw / 2 + 0.6 + (hw - 1.2) * k / 4 for k in range(5)]:
        b.beam_box((xs - 0.3, length - hd, 2.9), (xs + 0.3, length, 3.6), 'Timber_Dark', along='y')
        for yy in (length - hd + 0.5, length - hd / 2, length - 0.5):
            post(b, xs, yy, -8.0, 2.9, r=0.45)
    for side in (-1, 1):
        for yy in (length - hd + 2.0, length - 2.0):
            bollard(b, side * (hw / 2 - 1.0), yy, 4.0)
        for yy in range(8, int(length - hd), 16):
            bollard(b, side * (w / 2 - 0.8), yy + 2.0, 4.0)
    # rope rail around the head
    for k in range(7):
        xx = -hw / 2 + 0.4 + (hw - 0.8) * k / 6
        post(b, xx, length - 0.4, 4.0, 6.2, r=0.14, segs=6)
        if k: rope(b, (xx - (hw - 0.8) / 6, length - 0.4, 6.0), (xx, length - 0.4, 6.0), sag=0.35)
    # a few barrels, crates and a coil of rope
    pk.barrel(b, -hw / 2 + 2.0, length - 3.0, 4.0); pk.barrel(b, -hw / 2 + 3.9, length - 3.2, 4.0, straw=True)
    pk.crate(b, hw / 2 - 2.5, length - 3.0, 4.0); pk.crate(b, hw / 2 - 2.5, length - 3.0, 5.2, w=1.4, d=1.2, h=1.0)
    lathe(b, (hw / 2 - 5.0, length - 2.5, 4.0), [(0.9, 0.0), (1.0, 0.15), (1.0, 0.45), (0.9, 0.6), (0.5, 0.6), (0.5, 0.0)], 12, 'Rope')
    return b


# ------------------------------------------------------------------------------------------------ boats
def hull(b, L, W, D, sheer_bow=1.6, sheer_stern=1.0, rake=0.25, stations=14, mat='Wood_Planks'):
    """Lofted wooden hull along +Y (bow at +Y), keel at z = 0, deck at z = D (+ sheer at the ends)."""
    secs = []
    for i in range(stations + 1):
        s = i / stations                          # 0 = stern, 1 = bow
        yy = -L / 2 + L * s
        wf = math.sin(math.pi * min(1.0, 0.12 + 0.88 * s)) ** 0.55 if s > 0.5 else (0.55 + 0.45 * math.sin(math.pi * (0.12 + s)) ** 0.6)
        wf = max(0.08, wf if s < 0.97 else 0.08)
        hw = W / 2 * wf
        zt = D + sheer_bow * max(0.0, s - 0.6) ** 2 / 0.16 + sheer_stern * max(0.0, 0.3 - s) ** 2 / 0.09
        zb = 0.0 + rake * 3 * max(0.0, s - 0.75) ** 1.5 / 0.13 + 0.6 * max(0.0, 0.15 - s) / 0.15
        pts = [(-hw, zt), (-hw * 0.97, zb + (zt - zb) * 0.55), (-hw * 0.78, zb + (zt - zb) * 0.12), (-hw * 0.35, zb),
               (hw * 0.35, zb), (hw * 0.78, zb + (zt - zb) * 0.12), (hw * 0.97, zb + (zt - zb) * 0.55), (hw, zt)]
        secs.append([Vector((x, yy, z)) for x, z in pts])
    loft(b, secs, mat)
    return secs


def sail(b, x0, x1, z0, z1, y, billow=0.6, strips=6, mat='Sail_Canvas'):
    """Square sail: double-sided cloth with billow toward +Y, battens/seams across."""
    nu, nv = 8, 6
    def P(u, v, s):
        x = x0 + (x1 - x0) * u; z = z1 - (z1 - z0) * v
        yy = y + billow * math.sin(math.pi * u) * math.sin(math.pi * (0.2 + 0.8 * v)) + s * 0.03
        return Vector((x, yy, z))
    for s in (1, -1):
        vs = [[b.bm.verts.new(P(i / nu, j / nv, s)) for i in range(nu + 1)] for j in range(nv + 1)]
        for j in range(nv):
            for i in range(nu):
                q = [vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]]
                b.face(q, mat, [((x0 + (x1 - x0) * ii / nu) * 0.25, (z1 - (z1 - z0) * jj / nv) * 0.25)
                                for ii, jj in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))], out=Vector((0, s, 0)), smooth=True)
        if s == 1: front = vs
        else: back = vs
    for j in range(nv):
        for col, o in ((0, -1), (nu, 1)):
            b.face([front[j][col], front[j + 1][col], back[j + 1][col], back[j][col]], mat, [(0, 0)] * 4, out=Vector((o, 0, 0)))
    for i in range(nu):
        for row, o in ((0, 1), (nv, -1)):
            b.face([front[row][i], front[row][i + 1], back[row][i + 1], back[row][i]], mat, [(0, 0)] * 4, out=Vector((0, 0, o)))
    # horizontal battens (thin bamboo) across the sail
    for k in range(1, strips):
        v = k / strips
        pts = [P(i / 8, v, 1) + Vector((0, 0.05, 0)) for i in range(9)]
        tube(b, pts, [0.05] * 9, 4, 'Bamboo', smooth=True, caps=True)


def boat_small():
    """Small fishing/sailing boat (~16 long): lofted hull, gunwales, thwarts, mast, yard, square sail, oar."""
    b = B()
    L, W, D = 16.0, 4.4, 1.6
    hull(b, L, W, D, sheer_bow=1.4, sheer_stern=0.7)
    for side in (-1, 1):                                 # gunwale rails
        pts = []
        for i in range(13):
            s = 0.04 + 0.92 * i / 12
            yy = -L / 2 + L * s
            wf = math.sin(math.pi * min(1.0, 0.12 + 0.88 * s)) ** 0.55 if s > 0.5 else (0.55 + 0.45 * math.sin(math.pi * (0.12 + s)) ** 0.6)
            zt = D + 1.4 * max(0.0, s - 0.6) ** 2 / 0.16 + 0.7 * max(0.0, 0.3 - s) ** 2 / 0.09
            pts.append(Vector((side * W / 2 * wf, yy, zt + 0.1)))
        b.sweep(pts, [(-0.12, -0.12), (0.12, -0.12), (0.12, 0.12), (-0.12, 0.12)], 'Timber_Dark')
    for yy in (-3.0, 1.0, 4.0):
        b.beam_box((-W / 2 + 0.3, yy - 0.3, D - 0.15), (W / 2 - 0.3, yy + 0.3, D + 0.05), 'Timber_Light', along='x')
    post(b, 0.0, 1.0, D, D + 11.0, r=0.2, mat='Timber_Light')
    b.beam_box((-3.6, 1.1, D + 10.2), (3.6, 1.4, D + 10.5), 'Bamboo', along='x')
    sail(b, -3.4, 3.4, D + 3.0, D + 10.2, 1.45, billow=0.8)
    for sx in (-1, 1):
        rope(b, (0.0, 1.0, D + 10.8), (sx * W / 2 * 0.9, -2.0, D + 0.2), sag=0.1, r=0.04)
    rope(b, (0.0, 1.0, D + 10.8), (0.0, L / 2 - 1.0, D + 1.3), sag=0.1, r=0.04)
    b.beam(Vector((1.2, -L / 2 + 1.0, D + 0.4)), Vector((2.6, -L / 2 - 2.5, 0.3)), 0.15, 0.15, 'Timber_Light')   # sculling oar
    b.box((2.3, -L / 2 - 2.9, 0.1), (2.9, -L / 2 - 2.0, 0.5), 'Timber_Light')
    return b


def boat_cargo():
    """Cargo ship (benzaisen style, ~36 long): big lofted hull, deck, deck house, tall mast with a large square
    sail of stitched strips, rudder, cargo of bales and casks."""
    b = B()
    L, W, D = 36.0, 9.0, 4.0
    hull(b, L, W, D, sheer_bow=3.5, sheer_stern=2.0, rake=0.4)
    for side in (-1, 1):                               # bulwark rails
        pts = []
        for i in range(17):
            s = 0.05 + 0.9 * i / 16
            yy = -L / 2 + L * s
            wf = math.sin(math.pi * min(1.0, 0.12 + 0.88 * s)) ** 0.55 if s > 0.5 else (0.55 + 0.45 * math.sin(math.pi * (0.12 + s)) ** 0.6)
            zt = D + 3.5 * max(0.0, s - 0.6) ** 2 / 0.16 + 2.0 * max(0.0, 0.3 - s) ** 2 / 0.09
            pts.append(Vector((side * (W / 2 * wf - 0.1), yy, zt + 0.5)))
        b.sweep(pts, [(-0.18, -0.5), (0.18, -0.5), (0.18, 0.2), (-0.18, 0.2)], 'Timber_Dark')
    # deck house at the stern
    b.box((-3.0, -L / 2 + 3.5, D), (3.0, -L / 2 + 9.5, D + 3.2), 'Timber_Light')
    b.sweep([Vector((-3.6, -L / 2 + 6.5, D + 3.2)), Vector((3.6, -L / 2 + 6.5, D + 3.2))], [(-3.6, 0.0), (3.6, 0.0), (0.0, 1.6)], 'RoofTile_Clay')
    for yy in (-L / 2 + 5.0, -L / 2 + 8.0):
        b.box((-3.02, yy - 0.6, D + 1.0), (-2.98, yy + 0.6, D + 2.4), 'Shoji_Paper')
    # mast, yard, big sail
    post(b, 0.0, 1.0, D, D + 30.0, r=0.5, mat='Timber_Light')
    b.beam_box((-9.0, 1.3, D + 28.0), (9.0, 1.9, D + 28.6), 'Timber_Light', along='x')
    sail(b, -8.6, 8.6, D + 7.0, D + 28.0, 2.0, billow=2.0, strips=10)
    for sx in (-1, 1):
        rope(b, (0.0, 1.0, D + 29.5), (sx * W / 2 * 0.95, -6.0, D + 0.6), sag=0.2, r=0.07)
        rope(b, (sx * 8.6, 2.0, D + 7.0), (sx * W / 2 * 0.9, -10.0, D + 0.6), sag=0.5, r=0.06)
    rope(b, (0.0, 1.0, D + 29.5), (0.0, L / 2 - 1.5, D + 3.4), sag=0.3, r=0.07)
    # rudder
    b.box((-0.25, -L / 2 - 1.8, -1.5), (0.25, -L / 2 + 0.6, D + 1.0), 'Timber_Dark')        # rudder (hung on the sternpost)
    b.beam_box((-0.15, -L / 2 - 0.4, D + 2.5), (0.15, -L / 2 + 3.0, D + 2.8), 'Timber_Dark', along='y')
    # cargo
    for i in range(3):
        for j in range(2):
            pk.tawara(b, -2.2 + j * 4.4, 6.0 + i * 1.3, D, L=2.6, r=0.62)
    for i in range(3):
        pk.barrel(b, -2.5 + i * 2.5, 11.5, D, straw=True)
    for i in range(2):
        pk.crate(b, -1.2 + i * 2.4, -4.5, D, w=2.0, d=1.8, h=1.6)
    return b


# ------------------------------------------------------------------------------------------------ lighthouse
def lighthouse():
    """Stone-and-plaster lighthouse (~33 tall): octagonal fitted-stone base, white tower with door and windows,
    red-railed gallery, octagonal lantern room (glowing paper panels), tiled octagonal roof, gold finial."""
    b = B(); g = G()
    lathe(b, (0, 0, 0), [(5.4, 0.0), (5.0, 3.0), (4.4, 10.0), (4.2, 14.0), (4.6, 14.2), (4.6, 14.8)], 8, 'Stone_Fitted')
    lathe(b, (0, 0, 14.8), [(3.8, 0.0), (3.4, 9.0), (3.8, 9.3), (3.8, 9.8)], 8, 'Plaster_White')
    b.box((-0.9, 3.3, 14.8), (0.9, 4.1, 17.6), 'Timber_Dark')                   # door
    for zz in (18.5, 21.5):
        for a in (0.0, 2.1, 4.2):
            x, y = 3.45 * math.sin(a), 3.45 * math.cos(a)
            b.box((x - 0.35, y - 0.35, zz), (x + 0.35, y + 0.35, zz + 1.2), 'Black_Lacquer')
    zg = 24.6
    lathe(b, (0, 0, zg), [(5.0, 0.0), (5.0, 0.4), (0.0, 0.4)], 8, 'Wood_Planks')
    for k in range(16):
        a = 2 * math.pi * k / 16
        x, y = 4.8 * math.cos(a), 4.8 * math.sin(a)
        b.beam_box((x - 0.1, y - 0.1, zg + 0.4), (x + 0.1, y + 0.1, zg + 2.4), 'Red_Lacquer', along='z')
    lathe(b, (0, 0, zg + 2.3), [(4.95, 0.0), (4.95, 0.2), (4.65, 0.2), (4.65, 0.0)], 16, 'Red_Lacquer', cap_bottom=False, cap_top=False)
    zl = zg + 0.4
    for k in range(8):
        a = 2 * math.pi * (k + 0.5) / 8
        x, y = 2.7 * math.cos(a), 2.7 * math.sin(a)
        b.beam_box((x - 0.18, y - 0.18, zl), (x + 0.18, y + 0.18, zl + 4.2), 'Timber_Dark', along='z')
    lathe(g, (0, 0, zl), [(2.55, 0.0), (2.55, 4.2), (0.0, 4.2)], 8, 'Shoji_Paper', cap_bottom=True)
    zr = zl + 4.2
    lathe(b, (0, 0, zr), [(4.4, 0.0), (4.6, 0.25), (3.2, 0.9), (1.6, 2.2), (0.4, 3.4), (0.0, 3.5)], 8, 'RoofTile_Clay')
    lathe(b, (0, 0, zr + 3.4), [(0.35, 0.0), (0.5, 0.4), (0.3, 0.9), (0.45, 1.2), (0.0, 1.8)], 8, 'Gold_Leaf')
    return b, g


# ------------------------------------------------------------------------------------------------ arched bridge
def arch_bridge(L=64.0, W=12.0, rise=6.0):
    """Arched wooden bridge spanning L along Y. Origin = deck ends' level at the centre (z = 0 at both ends);
    piles go down into the water. Vermilion railings with gold gibōshi finials."""
    b = B()
    n = 24
    zc = lambda y: rise * (1 - (2 * y / L) ** 2)
    ys = [-L / 2 + L * i / n for i in range(n + 1)]
    for a, c in zip(ys, ys[1:]):
        za, zb = zc(a), zc(c)
        prof = [(-W / 2, -0.5), (W / 2, -0.5), (W / 2, 0.0), (-W / 2, 0.0)]
        b.sweep([Vector((0, a, za)), Vector((0, c, zb))], prof, 'Wood_Planks', up=Vector((0, 0, 1)), caps=False)
    b.sweep([Vector((0, ys[0], zc(ys[0]))), Vector((0, ys[0] + 0.01, zc(ys[0])))], [(-W / 2, -0.5), (W / 2, -0.5), (W / 2, 0.0), (-W / 2, 0.0)], 'Wood_Planks')
    b.sweep([Vector((0, ys[-1] - 0.01, 0.0)), Vector((0, ys[-1], 0.0))], [(-W / 2, -0.5), (W / 2, -0.5), (W / 2, 0.0), (-W / 2, 0.0)], 'Wood_Planks')
    for side in (-1, 1):                               # arched girders
        pts = [Vector((side * (W / 2 - 0.6), y, zc(y) - 0.5)) for y in ys]
        b.sweep(pts, [(-0.4, -1.4), (0.4, -1.4), (0.4, 0.0), (-0.4, 0.0)], 'Timber_Dark', up=Vector((0, 0, 1)))
    for yy in (-L / 2 + 6, -L / 4, 0.0, L / 4, L / 2 - 6):   # pile bents
        for xs in (-W / 2 + 0.6, 0.0, W / 2 - 0.6):
            post(b, xs, yy, -10.0, zc(yy) - 1.9, r=0.45)
        b.beam_box((-W / 2, yy - 0.35, zc(yy) - 2.5), (W / 2, yy + 0.35, zc(yy) - 1.9), 'Timber_Dark', along='x')
    for side in (-1, 1):                               # railings
        xr = side * (W / 2 - 0.3)
        rp = ys[::2]
        for yy in rp:
            z0 = zc(yy)
            b.beam_box((xr - 0.2, yy - 0.2, z0), (xr + 0.2, yy + 0.2, z0 + 3.0), 'Red_Lacquer', along='z')
            if yy in (rp[0], rp[len(rp) // 2], rp[-1]):
                lathe(b, (xr, yy, z0 + 3.0), [(0.28, 0.0), (0.3, 0.2), (0.4, 0.45), (0.25, 0.8), (0.0, 1.05)], 8, 'Gold_Leaf')
        for h, sz in ((2.8, 0.22), (1.4, 0.14)):
            pts = [Vector((xr, y, zc(y) + h)) for y in ys]
            b.sweep(pts, [(-sz, -sz), (sz, -sz), (sz, sz), (-sz, sz)], 'Red_Lacquer', up=Vector((0, 0, 1)))
    return b


# ------------------------------------------------------------------------------------------------ stairs
def stone_stairs(width=8.0, steps=5, rise=0.8, run=1.2, turning=False):
    """Dressed stone stairs with stone cheek walls. Straight: climbs toward -Y (front/bottom step at +Y).
    Turning: first flight climbs toward -Y to a landing, second flight climbs toward -X."""
    b = B()
    r = random.Random(steps * 7 + int(turning))
    def flight(x0, y0, dirv, sidev, z0, n):
        for i in range(n):
            p = Vector((x0, y0, 0)) + dirv * (run * i)
            q = p + dirv * run
            zt = z0 + rise * (i + 1)
            lo = Vector((min(p.x, q.x, p.x + sidev.x * width, q.x + sidev.x * width), min(p.y, q.y, p.y + sidev.y * width, q.y + sidev.y * width), 0.0))
            hi = Vector((max(p.x, q.x, p.x + sidev.x * width, q.x + sidev.x * width), max(p.y, q.y, p.y + sidev.y * width, q.y + sidev.y * width), zt))
            b.box(lo, hi, 'Stone_Fitted', uv_off=(r.random(), r.random()))
            b.box((lo.x, lo.y, zt - 0.2), (hi.x, hi.y, zt), 'Stone_Granite', uv_off=(r.random(), 0))
        return z0 + rise * n
    if not turning:
        top = flight(-width / 2, steps * run / 2, Vector((0, -1, 0)), Vector((1, 0, 0)), 0.0, steps)
        for sx in (-1, 1):
            outline = [(steps * run / 2, 0.0), (steps * run / 2, 1.0)] + [(steps * run / 2 - run * (i + 1), rise * (i + 1) + 1.0) for i in range(steps)] + [(-steps * run / 2, 0.0)]
            b.prism([(yv, zv) for yv, zv in outline], (sx * (width / 2) + (0 if sx > 0 else -1.0), 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 0), 1.0, 'Stone_Granite')
    else:
        half = steps
        z1 = flight(-width / 2, width + half * run, Vector((0, -1, 0)), Vector((1, 0, 0)), 0.0, half)
        b.box((-width / 2, 0.0, 0.0), (width / 2, width, z1), 'Stone_Fitted')                    # landing
        b.box((-width / 2, 0.0, z1 - 0.2), (width / 2, width, z1), 'Stone_Granite')
        flight(-width / 2, width, Vector((-1, 0, 0)), Vector((0, -1, 0)), z1, half)
        b.box((width / 2, 0.0, 0.0), (width / 2 + 1.0, width + half * run, z1 + 1.0), 'Stone_Granite')
        b.box((-width / 2 - half * run, -1.0, 0.0), (width / 2 + 1.0, 0.0, z1 + rise * half + 1.0), 'Stone_Granite')
    return b


# ================================================================================================ STREET PROPS
def torii(W=12.0, H=13.0):
    """Myōjin torii: vermilion pillars on stone bases with black foot bands, nuki tie-beam, upswept black
    kasagi over a vermilion shimaki, central strut with a blank plaque (face returned separately)."""
    b = B(); face = Builder(['Timber_Light'])
    px = W / 2 - 1.2
    for sx in (-1, 1):
        lathe(b, (sx * px, 0, 0), [(1.1, 0.0), (1.0, 0.5), (0.8, 0.8), (0.0, 0.85)], 10, 'Stone_Granite')
        lathe(b, (sx * px, 0, 0.8), [(0.72, 0.0), (0.72, 1.0), (0.0, 1.0)], 12, 'Black_Lacquer', cap_bottom=False)
        lathe(b, (sx * px, 0, 1.8), [(0.62, 0.0), (0.55, H - 3.4), (0.0, H - 3.4)], 12, 'Red_Lacquer', cap_bottom=False)
    zn = H - 3.6
    b.beam_box((-px - 1.8, -0.35, zn), (px + 1.8, 0.35, zn + 0.7), 'Red_Lacquer', along='x')
    for sx in (-1, 1):
        b.box((sx * px - 0.25 + sx * 0.75, -0.42, zn - 0.1), (sx * px + 0.25 + sx * 0.75, 0.42, zn + 0.8), 'Red_Lacquer')
    zs = H - 1.6
    n = 12
    xs = [-(W / 2 + 1.4) + (W + 2.8) * i / n for i in range(n + 1)]
    up = lambda x: 0.9 * (abs(x) / (W / 2 + 1.4)) ** 3
    b.sweep([Vector((x, 0, zs + up(x) * 0.6)) for x in xs], [(-0.45, -0.35), (0.45, -0.35), (0.45, 0.35), (-0.45, 0.35)], 'Red_Lacquer')
    b.sweep([Vector((x, 0, zs + 0.75 + up(x))) for x in xs], [(-0.6, -0.4), (0.6, -0.4), (0.55, 0.45), (-0.55, 0.45)], 'Black_Lacquer')
    b.beam_box((-0.3, -0.3, zn + 0.7), (0.3, 0.3, zs - 0.35), 'Red_Lacquer', along='z')
    b.box((-0.9, -0.28, zn + 0.9), (0.9, 0.28, zs - 0.45), 'Black_Lacquer')
    for s in (1, -1):
        face.box((-0.7, min(s * 0.28, s * 0.32), zn + 1.05), (0.7, max(s * 0.28, s * 0.32), zs - 0.6), 'Timber_Light', uvd=0.5)
    return b, face


def stone_lantern():
    """Kasuga-style stone lantern (tōrō), ~5.4 tall; the fire-box windows glow (glow builder)."""
    b = B(); g = G()
    lathe(b, (0, 0, 0), [(1.0, 0.0), (1.0, 0.35), (0.7, 0.55), (0.0, 0.55)], 6, 'Stone_Granite')
    lathe(b, (0, 0, 0.55), [(0.32, 0.0), (0.28, 1.8), (0.0, 1.8)], 10, 'Stone_Granite', cap_bottom=False)
    lathe(b, (0, 0, 2.35), [(0.5, 0.0), (0.85, 0.35), (0.85, 0.5), (0.0, 0.5)], 6, 'Stone_Granite')
    lathe(b, (0, 0, 2.85), [(0.62, 0.0), (0.62, 1.1), (0.0, 1.1)], 6, 'Stone_Granite')
    for a in (0.0, math.pi):
        c = Vector((0.63 * math.cos(a + math.pi / 6), 0.63 * math.sin(a + math.pi / 6), 3.15))
        n = Vector((math.cos(a + math.pi / 6), math.sin(a + math.pi / 6), 0))
        t = Vector((-n.y, n.x, 0))
        g.prism([(-0.25, 0.0), (0.25, 0.0), (0.25, 0.55), (-0.25, 0.55)], c - n * 0.02, t, (0, 0, 1), n, 0.03, 'Shoji_Paper')
    lathe(b, (0, 0, 3.95), [(0.9, 0.0), (1.25, 0.12), (1.15, 0.3), (0.5, 0.75), (0.2, 0.85), (0.0, 0.88)], 6, 'Stone_Granite')
    lathe(b, (0, 0, 4.8), [(0.2, 0.0), (0.3, 0.2), (0.2, 0.45), (0.0, 0.6)], 8, 'Stone_Granite')
    return b, g


def chochin_prop(color='Red_Lacquer'):
    """Hanging paper lantern on a small wall bracket (back = -Y on the wall). Glow body in the glow builder."""
    b = B(); g = G()
    b.beam_box((-0.06, -0.1, 3.2), (0.06, 1.4, 3.32), 'Iron_Wrought', along='y')
    b.box((-0.2, -0.1, 2.9), (0.2, 0.0, 3.5), 'Iron_Wrought')
    r, h = 0.6, 1.6
    lathe(g, (0, 1.2, 0.6), [(r * 0.55, 0.0), (r * 0.9, h * 0.15), (r, h * 0.5), (r * 0.9, h * 0.85), (r * 0.55, h)], 12, 'Shoji_Paper')
    lathe(b, (0, 1.2, 0.48), [(r * 0.6, 0.0), (r * 0.6, 0.14)], 12, color)
    lathe(b, (0, 1.2, 0.6 + h - 0.02), [(r * 0.6, 0.0), (r * 0.6, 0.14)], 12, color)
    b.cylinder((0, 1.2, 0.6 + h + 0.12), (0, 1.2, 3.2), 0.03, 4, 'Rope')
    return b, g


def cart(loaded=True):
    """Two-wheeled handcart (daihachiguruma), long axis along Y (handles toward +Y)."""
    b = B()
    R = 1.7
    for sx in (-1, 1):
        x = sx * 1.9
        # rim (iron-shod) as a ring of boxes
        for k in range(16):
            a0, a1 = 2 * math.pi * k / 16, 2 * math.pi * (k + 1) / 16
            p0 = Vector((x, R * math.cos(a0), R + R * math.sin(a0))); p1 = Vector((x, R * math.cos(a1), R + R * math.sin(a1)))
            b.beam(p0, p1, 0.32, 0.22, 'Timber_Dark', up=(p0 + p1) / 2 - Vector((x, 0, R)))
        for k in range(8):
            a = 2 * math.pi * k / 8
            b.beam(Vector((x, 0, R)), Vector((x, R * 0.95 * math.cos(a), R + R * 0.95 * math.sin(a))), 0.14, 0.14, 'Timber_Light',
                   up=Vector((1, 0, 0)))
        b.cylinder((x - 0.3, 0, R), (x + 0.3, 0, R), 0.3, 10, 'Iron_Wrought')
    b.cylinder((-2.0, 0, R), (2.0, 0, R), 0.12, 8, 'Iron_Wrought')
    b.box((-1.6, -3.5, R + 0.2), (1.6, 2.5, R + 0.45), 'Wood_Planks')
    for sx in (-1, 1):
        b.beam_box((sx * 1.5 - 0.15, -3.6, R + 0.0), (sx * 1.5 + 0.15, 6.5, R + 0.25), 'Timber_Light', along='y')
    b.beam_box((-1.5, 6.1, R + 0.0), (1.5, 6.4, R + 0.25), 'Timber_Light', along='x')
    b.beam_box((-0.12, -3.4, 0.0), (0.12, -3.1, R + 0.2), 'Timber_Light', along='z')
    if loaded:
        for i in range(3):
            pk.tawara(b, 0.0, -2.6 + i * 1.35, R + 0.45, L=2.8, r=0.62, rot=0.0)
        pk.sack(b, -0.8, 1.8, R + 0.45, h=1.3, r=0.5); pk.sack(b, 0.7, 1.9, R + 0.45, h=1.2, r=0.45, mat='Cloth_Ochre')
    return b


def market_stall(canopy='Cloth_Crimson', seed=1):
    """Street market stall 8 x 5: posts, counter with baskets of produce, jars, sloped cloth canopy."""
    random.seed(seed)
    b = B()
    W, D = 8.0, 5.0
    for sx in (-1, 1):
        for sy, h in ((1, 6.8), (-1, 7.8)):
            b.beam_box((sx * (W / 2 - 0.2) - 0.18, sy * (D / 2 - 0.2) - 0.18, 0.0), (sx * (W / 2 - 0.2) + 0.18, sy * (D / 2 - 0.2) + 0.18, h), 'Timber_Dark', along='z')
    pk.counter(b, 0.0, D / 2 - 1.0, 0.0, w=W - 0.8, d=1.6, h=3.0)
    b.box((-W / 2 + 0.4, -D / 2 + 0.4, 0.0), (W / 2 - 0.4, -D / 2 + 1.4, 1.8), 'Wood_Planks')
    cl = Builder(MATS)
    for s in (1, -1):
        pts = [Vector((-W / 2 - 0.4, -D / 2 - 0.2, 7.9 + s * 0.03)), Vector((W / 2 + 0.4, -D / 2 - 0.2, 7.9 + s * 0.03)),
               Vector((W / 2 + 0.4, D / 2 + 1.0, 6.4 + s * 0.03)), Vector((-W / 2 - 0.4, D / 2 + 1.0, 6.4 + s * 0.03))]
        vs = [cl.bm.verts.new(p) for p in pts]
        cl.face(vs, canopy, [(0, 0), (2, 0), (2, 1.5), (0, 1.5)], out=Vector((0, 0.3, s)))
    mesh_join(b, cl)
    for i in range(3):                                 # produce baskets
        cx = -2.4 + i * 2.4
        lathe(b, (cx, D / 2 - 1.0, 3.0), [(0.5, 0.0), (0.8, 0.45), (0.85, 0.5), (0.0, 0.5)], 10, 'Straw', cap_top=True)
        for k in range(5):
            a = 2 * math.pi * k / 5
            lathe(b, (cx + 0.4 * math.cos(a), D / 2 - 1.0 + 0.4 * math.sin(a), 3.45),
                  [(0.0, 0.0), (0.22, 0.08), (0.24, 0.2), (0.16, 0.36), (0.0, 0.4)], 6, random.choice(['Cloth_Ochre', 'Red_Lacquer', 'Cloth_White']))
    for i in range(3):
        pk.jar(b, -2.6 + i * 2.6, -D / 2 + 0.9, 1.8, h=1.1, r=0.45, mat=random.choice(['Earth_Packed', 'Black_Lacquer', 'RoofTile_Clay']))
    return b


def bench(tea=False):
    """Bench: plank bench, or tea-house bench with red felt and a big red parasol."""
    b = B()
    b.box((-3.0, -0.9, 1.6), (3.0, 0.9, 1.85), 'Wood_Planks')
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.beam_box((sx * 2.6 - 0.12, sy * 0.65 - 0.12, 0.0), (sx * 2.6 + 0.12, sy * 0.65 + 0.12, 1.6), 'Timber_Dark', along='z')
        b.beam_box((sx * 2.6 - 0.1, -0.7, 0.5), (sx * 2.6 + 0.1, 0.7, 0.65), 'Timber_Dark', along='y')
    if tea:
        b.box((-2.9, -0.95, 1.85), (2.9, 0.95, 1.92), 'Cloth_Crimson')
        b.box((-2.9, 0.92, 1.35), (2.9, 0.97, 1.92), 'Cloth_Crimson')
        post(b, 3.8, -0.6, 0.0, 8.0, r=0.1, mat='Bamboo')
        lathe(b, (3.8, -0.6, 7.2), [(4.2, 0.0), (3.6, 0.45), (2.0, 1.0), (0.3, 1.4), (0.0, 1.45)], 16, 'Cloth_Crimson', cap_bottom=True)
        for k in range(16):
            a = 2 * math.pi * k / 16
            b.beam(Vector((3.8, -0.6, 6.0)), Vector((3.8 + 3.9 * math.cos(a), -0.6 + 3.9 * math.sin(a), 7.25)), 0.05, 0.05, 'Bamboo')
    return b


def well():
    """Village well: stone ring with dark water, wooden A-frame with a small tiled roof, pulley, rope, bucket."""
    b = B()
    lathe(b, (0, 0, 0), [(1.9, 0.0), (1.9, 2.4), (1.5, 2.4), (1.5, 1.4), (0.0, 1.4)], 16, 'Stone_Granite', cap_bottom=False)
    b.cylinder((0, 0, 1.3), (0, 0, 1.45), 1.52, 16, 'Black_Lacquer')        # dark water surface
    for sx in (-1, 1):
        b.beam_box((sx * 2.2 - 0.18, -0.18, 0.0), (sx * 2.2 + 0.18, 0.18, 6.0), 'Timber_Dark', along='z')
    b.beam_box((-2.6, -0.2, 5.6), (2.6, 0.2, 6.0), 'Timber_Dark', along='x')
    b.sweep([Vector((-3.0, 0, 6.0)), Vector((3.0, 0, 6.0))], [(-1.6, 0.0), (1.6, 0.0), (0.0, 1.2)], 'RoofTile_Clay')
    b.cylinder((-0.1, 0, 5.2), (0.1, 0, 5.2), 0.35, 10, 'Timber_Light')
    b.cylinder((0, 0.35, 5.2), (0, 0.35, 3.36), 0.03, 4, 'Rope')
    lathe(b, (0, 0.35, 2.4), [(0.35, 0.0), (0.42, 0.9), (0.0, 0.9)], 10, 'Timber_Light', cap_bottom=True, cap_top=False)
    b.box((-0.4, 0.33, 3.3), (0.4, 0.37, 3.4), 'Iron_Wrought')
    return b


def bamboo_fence(L=8.0, h=4.0):
    """Yotsume-gaki bamboo fence module L long: posts at the ends, 4 horizontal rails, verticals with rope ties."""
    b = B()
    for x in (-L / 2 + 0.2, L / 2 - 0.2):
        post(b, x, 0, 0.0, h + 0.3, r=0.2, mat='Timber_Dark')
    for k in range(4):
        z = 0.6 + (h - 0.8) * k / 3
        b.cylinder((-L / 2 + 0.2, 0.15, z), (L / 2 - 0.2, 0.15, z), 0.09, 6, 'Bamboo')
    n = int(L / 0.9)
    for i in range(n):
        x = -L / 2 + 0.6 + (L - 1.2) * i / (n - 1)
        y = -0.05 if i % 2 else 0.35
        b.cylinder((x, y, 0.0), (x, y, h), 0.08, 6, 'Bamboo')
        for k in range(4):
            z = 0.6 + (h - 0.8) * k / 3
            b.box((x - 0.12, min(y, 0.15) - 0.1, z - 0.08), (x + 0.12, max(y, 0.15) + 0.1, z + 0.08), 'Rope')
    return b


# ================================================================================================ NATURE
def pine(size='M', seed=1):
    """Sculpted Japanese pine (niwaki): leaning twisted trunk, horizontal branches ending in layered cloud pads."""
    r = random.Random(seed * 31 + {'S': 1, 'M': 2, 'L': 3}[size])
    H = {'S': 10.0, 'M': 16.0, 'L': 24.0}[size]
    npads = {'S': 4, 'M': 7, 'L': 10}[size]
    b = B()
    pts = [Vector((0, 0, 0))]
    lean = Vector((r.uniform(-0.25, 0.25), r.uniform(-0.25, 0.25), 1.0)).normalized()
    for i in range(1, 9):
        t = i / 8
        wob = Vector((math.sin(t * 5 + seed) * 0.08, math.cos(t * 4 + seed) * 0.08, 0)) * H * 0.3
        pts.append(lean * H * 0.82 * t + wob * t)
    radii = [H * 0.045 * (1.25 - t) for t in [i / 8 for i in range(9)]]
    radii[0] *= 1.35
    tube(b, pts, radii, 8, 'Pine_Bark', smooth=True)
    pads = []
    for k in range(npads):
        t = 0.35 + 0.6 * k / max(1, npads - 1)
        i = min(7, int(t * 8)); f = t * 8 - i
        base = pts[i].lerp(pts[i + 1], f)
        ang = r.uniform(0, 2 * math.pi) + k * 2.4
        reach = H * (0.34 - 0.18 * t) * r.uniform(0.8, 1.1)
        tip = base + Vector((math.cos(ang) * reach, math.sin(ang) * reach, H * r.uniform(0.02, 0.08)))
        mid = base.lerp(tip, 0.5) + Vector((0, 0, H * 0.03))
        br = H * 0.022 * (1.1 - t)
        tube(b, [base, mid, tip], [br, br * 0.75, br * 0.5], 6, 'Pine_Bark', smooth=True)
        pads.append((tip, H * (0.16 - 0.06 * t)))
    pads.append((pts[-1] + Vector((0, 0, H * 0.04)), H * 0.14))
    for j, (c, rad) in enumerate(pads):
        blob(b, c + Vector((0, 0, rad * 0.15)), (rad * 1.25, rad * 1.1, rad * 0.45), 'Pine_Needles', subdiv=3, amp=0.35,
             freq=0.9, seed=seed * 10 + j)
        blob(b, c + Vector((rad * 0.3, -rad * 0.2, rad * 0.4)), (rad * 0.8, rad * 0.75, rad * 0.35), 'Pine_Needles', subdiv=2,
             amp=0.3, freq=0.9, seed=seed * 10 + j + 50)
    return b


def cliff_rock(size='M', seed=1):
    """Cliff / sea rock: layered noise boulder with a flat base (origin at the base centre)."""
    R = {'S': 3.0, 'M': 7.0, 'L': 14.0}[size]
    sd = {'S': 4, 'M': 4, 'L': 5}[size]
    b = B()
    blob(b, (0, 0, R * 0.55), (R, R * 0.8, R * 0.75), 'Stone_Granite', subdiv=sd, amp=0.35, freq=0.45, seed=seed, flat_bottom=-R * 0.55,
         octaves=4, smooth=False)
    blob(b, (R * 0.45, R * 0.2, R * 0.9), (R * 0.55, R * 0.5, R * 0.5), 'Stone_Granite', subdiv=sd - 1, amp=0.3, freq=0.6, seed=seed + 5,
         flat_bottom=-R * 0.9, smooth=False)
    return b
