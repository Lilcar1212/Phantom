"""Modular wall / front / foundation kit (machiya & town buildings).

Module space (Blender): wall runs along X (length L = 4/8/12/16), thickness 1 stud centred on y = 0
(y = +0.5 is the OUTSIDE face = asset front = Roblox -Z), floor height H = 9 studs, z = 0 at the floor.
Every wall module's bbox is exactly L x 1 x H, so modules snap end-to-end on the 4-stud grid; a corner
post (HO_Wall_CornerPost) covers each building corner. Posts sit on the 4-stud grid lines (half posts at
module ends, which pair up with the neighbouring module).
"""
import math, random
from mathutils import Vector
from geo import Builder

MATS = ['Plaster_White', 'Timber_Dark', 'Timber_Light', 'Shoji_Paper', 'Stone_Granite', 'Wood_Planks', 'Iron_Wrought']
H = 9.0
POST = 0.8
SILL = (0.0, 0.5)
HEAD = (H - 0.7, H)
BAND = (7.0, 7.45)          # nageshi / door-head band (door openings are 7 studs tall incl. sill)
PL = 0.38                   # plaster half-thickness (recessed 0.12 from the timber faces)
PV = 1.0 / H                # plaster texture V spans one 9-stud floor


class WallBuilder:
    def __init__(self, L, mats=MATS):
        self.L = L
        self.b = Builder(mats)
        self.doors = []                       # separate builders for openable panels

    # --------------------------------------------------------------------------------- helpers
    def plaster(self, x0, x1, z0, z1, y0=-PL, y1=PL):
        if x1 - x0 < 1e-3 or z1 - z0 < 1e-3: return
        self.b.box((x0, y0, z0), (x1, y1, z1), 'Plaster_White', uvv=PV)

    def timber(self, lo, hi, along, mat='Timber_Dark', b=None):
        (b or self.b).beam_box(lo, hi, mat, along=along, uv_seed=random.random())

    def frame(self, bays, band=True):
        """Posts on grid lines, sill, head beam and (optional) door-head band. Returns bay x-ranges (clear)."""
        L = self.L
        n = int(round(L / 4))
        xs = [-L / 2 + 4 * i for i in range(n + 1)]
        for i, x in enumerate(xs):
            x0 = x if i == 0 else x - POST / 2
            x1 = x if i == n else x + POST / 2
            if i == 0: x1 = x + POST / 2
            if i == n: x0 = x - POST / 2
            self.timber((x0, -0.5, SILL[1]), (x1, 0.5, HEAD[0]), 'z')
        self.timber((-L / 2, -0.5, SILL[0]), (L / 2, 0.5, SILL[1]), 'x')
        self.timber((-L / 2, -0.5, HEAD[0]), (L / 2, 0.5, HEAD[1]), 'x')
        clear = [(xs[i] + POST / 2, xs[i + 1] - POST / 2) for i in range(n)]
        if band:
            for (a, c) in clear:
                self.timber((a, -0.47, BAND[0]), (c, 0.47, BAND[1]), 'x')
        return clear

    def upper_plaster(self, a, c):
        self.plaster(a, c, BAND[1], HEAD[0])

    def shoji(self, x0, x1, z0, z1, y=0.0, b=None, cols=None, rows=None, frame_w=0.14, depth=0.14):
        """Shoji panel: paper sheet with kumiko lattice bars through it and a frame."""
        b = b or self.b
        b.box((x0, y - 0.03, z0), (x1, y + 0.03, z1), 'Shoji_Paper')
        fw, d = frame_w, depth / 2
        for lo, hi, al in (((x0, y - d, z0), (x1, y + d, z0 + fw), 'x'), ((x0, y - d, z1 - fw), (x1, y + d, z1), 'x'),
                           ((x0, y - d, z0), (x0 + fw, y + d, z1), 'z'), ((x1 - fw, y - d, z0), (x1, y + d, z1), 'z')):
            b.beam_box(lo, hi, 'Timber_Light', along=al, uv_seed=random.random())
        cols = cols or max(1, int(round((x1 - x0) / 0.7)) - 1)
        rows = rows or max(1, int(round((z1 - z0) / 0.9)) - 1)
        kb, kd = 0.05, depth / 2 - 0.02
        for i in range(1, cols + 1):
            x = x0 + (x1 - x0) * i / (cols + 1)
            b.beam_box((x - kb, y - kd, z0 + fw), (x + kb, y + kd, z1 - fw), 'Timber_Light', along='z')
        for j in range(1, rows + 1):
            z = z0 + (z1 - z0) * j / (rows + 1)
            b.beam_box((x0 + fw, y - kd, z - kb), (x1 - fw, y + kd, z + kb), 'Timber_Light', along='x')

    def koshi(self, x0, x1, z0, z1, y0=0.12, y1=0.46, bar=0.2, gap=0.26, rails=True, b=None, mat='Timber_Dark'):
        """Vertical-bar lattice (koshi) between x0..x1, z0..z1, bars depth y0..y1."""
        b = b or self.b
        w = x1 - x0
        n = max(2, int(round((w + gap) / (bar + gap))))
        step = (w - bar) / (n - 1)
        for i in range(n):
            x = x0 + i * step
            b.beam_box((x, y0, z0), (x + bar, y1, z1), mat, along='z', uv_seed=random.random())
        if rails:
            for zc in (z0 + 0.1, (z0 + z1) / 2, z1 - 0.1):
                b.beam_box((x0, y0 - 0.06, zc - 0.1), (x1, y0, zc + 0.1), mat, along='x')

    # --------------------------------------------------------------------------------- bay fillers
    def bay_plaster(self, a, c):
        self.plaster(a, c, SILL[1], BAND[0]); self.upper_plaster(a, c)

    def bay_window(self, a, c, lattice=False):
        w0, w1 = 3.0, 6.2
        m = 0.5
        self.upper_plaster(a, c)
        self.plaster(a, c, SILL[1], w0)
        self.plaster(a, c, w1, BAND[0])
        self.plaster(a, a + m, w0, w1); self.plaster(c - m, c, w0, w1)
        xa, xc = a + m, c - m
        # window frame (flush with the timber faces)
        for lo, hi, al in (((xa - 0.12, -0.5, w0 - 0.18), (xc + 0.12, 0.5, w0), 'x'),
                           ((xa - 0.12, -0.5, w1), (xc + 0.12, 0.5, w1 + 0.18), 'x'),
                           ((xa - 0.12, -0.5, w0), (xa, 0.5, w1), 'z'), ((xc, -0.5, w0), (xc + 0.12, 0.5, w1), 'z')):
            self.timber(lo, hi, al)
        mid = (xa + xc) / 2
        self.shoji(xa, mid + 0.04, w0, w1, y=-0.18)
        self.shoji(mid - 0.04, xc, w0, w1, y=-0.34)
        if lattice:
            self.koshi(xa, xc, w0, w1, y0=0.16, y1=0.44, bar=0.16, gap=0.2, rails=False)
            self.timber((xa, 0.1, (w0 + w1) / 2 - 0.08), (xc, 0.44, (w0 + w1) / 2 + 0.08), 'x')

    def bay_mushiko(self, a, c):
        w0, w1 = 2.2, 5.6
        self.upper_plaster(a, c)
        self.plaster(a, c, SILL[1], w0)
        self.plaster(a, c, w1, BAND[0])
        self.plaster(a, a + 0.35, w0, w1); self.plaster(c - 0.35, c, w0, w1)
        xa, xc = a + 0.35, c - 0.35
        # plastered slats (thick, rounded-looking bars), shoji behind
        n = max(3, int(round((xc - xa) / 0.62)))
        step = (xc - xa) / n
        for i in range(n):
            x = xa + i * step + step * 0.22
            self.b.box((x, -0.1, w0), (x + step * 0.56, 0.42, w1), 'Plaster_White', uvv=PV)
        self.b.box((xa, -0.34, w0), (xc, -0.1, w0 + 0.01), 'Plaster_White', uvv=PV)
        self.shoji(xa, xc, w0, w1, y=-0.3, cols=2, rows=2)

    def bay_koshi(self, a, c):
        self.koshi(a, c, SILL[1], BAND[0])
        self.shoji(a, c, SILL[1], BAND[0], y=-0.18, cols=3, rows=5)
        self.upper_plaster(a, c)

    def bay_koshi_door(self, a, c, name='Door'):
        """Sliding lattice entrance door as a separate (openable) mesh."""
        self.upper_plaster(a, c)
        d = Builder(MATS)
        x0, x1 = a, c
        z0, z1 = SILL[1], BAND[0]
        for lo, hi, al in (((x0, 0.0, z0), (x1, 0.3, z0 + 0.25), 'x'), ((x0, 0.0, z1 - 0.2), (x1, 0.3, z1), 'x'),
                           ((x0, 0.0, z0), (x0 + 0.2, 0.3, z1), 'z'), ((x1 - 0.2, 0.0, z0), (x1, 0.3, z1), 'z')):
            d.beam_box(lo, hi, 'Timber_Dark', along=al)
        self.koshi(x0 + 0.2, x1 - 0.2, z0 + 0.25, z1 - 0.2, y0=0.1, y1=0.3, bar=0.14, gap=0.18, rails=False, b=d)
        self.shoji(x0 + 0.2, x1 - 0.2, z0 + 0.25, z1 - 0.2, y=0.03, b=d, cols=2, rows=4, depth=0.1)
        # door track (threshold) in the sill is part of the wall
        self.doors.append((name, d))

    def bay_open(self, a, c):
        self.upper_plaster(a, c)

    def bay_shoji_doors(self, a, c, prefix='Door'):
        """Two sliding shoji panels per bay (each a separate mesh), offset tracks."""
        self.upper_plaster(a, c)
        mid = (a + c) / 2
        for k, (x0, x1, y) in enumerate(((a, mid + 0.05, 0.1), (mid - 0.05, c, -0.1))):
            d = Builder(MATS)
            self.shoji(x0, x1, SILL[1], BAND[0], y=y, b=d, cols=2, rows=5, frame_w=0.16, depth=0.16)
            self.doors.append((f'{prefix}{len(self.doors) + 1}', d))


# ------------------------------------------------------------------------------------------ modules
def wall(L, bay_types, band=True):
    w = WallBuilder(L)
    clear = w.frame(bay_types, band=band)
    for (a, c), t in zip(clear, bay_types):
        {'plaster': w.bay_plaster, 'window': w.bay_window, 'lattice': lambda a, c: w.bay_window(a, c, True),
         'mushiko': w.bay_mushiko, 'koshi': w.bay_koshi, 'door': w.bay_koshi_door, 'open': w.bay_open,
         'shoji': w.bay_shoji_doors}[t](a, c)
    return w


def open_shop(L):
    """Open shop front: posts + head, open bays with a raised wooden counter/display platform inside."""
    w = wall(L, ['open'] * int(L / 4))
    b = w.b
    # counter/platform (mise-no-ma edge) set just inside, full length between end posts
    b.beam_box((-L / 2 + 0.4, -0.5, 0.5), (L / 2 - 0.4, 0.3, 2.6), 'Timber_Light', along='x')
    b.beam_box((-L / 2 + 0.4, -0.5, 2.6), (L / 2 - 0.4, 0.42, 2.85), 'Timber_Dark', along='x')
    # shutters-storage lintel box above the opening (hides the band)
    for x in [-L / 2 + 4 * i for i in range(1, int(L / 4))]:
        b.beam_box((x - 0.12, 0.3, 0.5), (x + 0.12, 0.42, 2.6), 'Timber_Dark', along='z')
    return w


def corner_post(h=H, s=1.3):
    b = Builder(MATS)
    b.beam_box((-s / 2, -s / 2, 0), (s / 2, s / 2, h), 'Timber_Dark', along='z')
    b.beam_box((-s / 2 - 0.05, -s / 2 - 0.05, 0), (s / 2 + 0.05, s / 2 + 0.05, 0.5), 'Timber_Dark', along='x')
    b.beam_box((-s / 2 - 0.05, -s / 2 - 0.05, h - 0.7), (s / 2 + 0.05, s / 2 + 0.05, h), 'Timber_Dark', along='x')
    return b


def plinth(L, depth=1.6, h=1.0, seed=1, corner=False):
    """Stone foundation: fitted granite blocks (real chamfered geometry) on a solid core."""
    random.seed(seed)
    b = Builder(MATS)
    d2 = depth / 2
    b.box((-L / 2 + 0.06, -d2 + 0.08, 0), (L / 2 - 0.06, d2 - 0.08, h - 0.02), 'Stone_Granite')
    ch = 0.09
    def stone(x0, x1, y0, y1, z0, z1):
        prof = [(y0 + ch, z0), (y1 - ch, z0), (y1, z0 + ch), (y1, z1 - ch), (y1 - ch, z1), (y0 + ch, z1), (y0, z1 - ch),
                (y0, z0 + ch)]
        # sweep along X: profile given as (across=y, up=z) -> sweep uses side = d x up; d = +x -> side = -y
        prof = [(-yy, zz) for yy, zz in prof]
        b.sweep([Vector((x0, 0, 0)), Vector((x1, 0, 0))], prof, 'Stone_Granite', uv_off=(random.random(), random.random()))
    if corner:
        stone(-L / 2, L / 2, -d2, d2, 0, h)
        return b
    # two courses: tall face stones on the outside (+Y) and inside (-Y)
    for (y0, y1) in ((d2 - 0.45, d2), (-d2, -d2 + 0.45)):
        x = -L / 2
        while x < L / 2 - 1e-3:
            wdt = min(L / 2 - x, random.choice([0.9, 1.1, 1.3, 1.5, 1.7]))
            if L / 2 - (x + wdt) < 0.6: wdt = L / 2 - x
            stone(x + (0.02 if x > -L / 2 + 1e-6 else 0.0), x + wdt - (0.02 if x + wdt < L / 2 - 1e-6 else 0.0),
                  y0, y1, 0.0, h + random.uniform(-0.04, 0.0))
            x += wdt
    # cap stones on top between
    x = -L / 2
    while x < L / 2 - 1e-3:
        wdt = min(L / 2 - x, random.choice([1.2, 1.6, 2.0]))
        if L / 2 - (x + wdt) < 0.8: wdt = L / 2 - x
        stone(x + 0.03, x + wdt - 0.03, -d2 + 0.43, d2 - 0.43, h - 0.25, h)
        x += wdt
    return b


def balcony(L, proj=2.5):
    """2nd-floor balcony: plank deck, railing with balusters, knee-brace brackets. Back (-Y) mounts on the
    wall face; deck top is 1.6 studs above the pivot (bottom of the brackets)."""
    b = Builder(MATS)
    zd = 1.6
    b.box((-L / 2, 0, zd - 0.3), (L / 2, proj, zd), 'Wood_Planks')
    b.beam_box((-L / 2, proj - 0.3, zd - 0.55), (L / 2, proj, zd - 0.3), 'Timber_Dark', along='x')       # edge beam
    b.beam_box((-L / 2, 0, zd - 0.55), (L / 2, 0.3, zd - 0.3), 'Timber_Dark', along='x')                   # ledger
    n = int(round(L / 4))
    for i in range(n + 1):
        x = -L / 2 + 0.2 + (L - 0.4) * i / n
        b.beam_box((x - 0.2, 0.3, zd - 0.55), (x + 0.2, proj, zd - 0.3), 'Timber_Dark', along='y')         # joists
        # knee brace: from wall down to joist end
        p0 = Vector((x, 0.15, 0.0)); p1 = Vector((x, proj - 0.4, zd - 0.55))
        b.beam(p0, p1, 0.3, 0.3, 'Timber_Dark', up=Vector((1, 0, 0)))
        b.beam_box((x - 0.2, 0.0, 0.0), (x + 0.2, 0.3, 0.6), 'Timber_Dark', along='z')                     # brace foot
        # railing posts
        b.beam_box((x - 0.14, proj - 0.3, zd), (x + 0.14, proj - 0.02, zd + 3.0), 'Timber_Dark', along='z')
    b.beam_box((-L / 2, proj - 0.34, zd + 2.8), (L / 2, proj + 0.02, zd + 3.05), 'Timber_Dark', along='x')  # top rail
    b.beam_box((-L / 2, proj - 0.28, zd + 0.2), (L / 2, proj - 0.04, zd + 0.4), 'Timber_Dark', along='x')    # bottom rail
    nb = int(L / 0.45)
    for i in range(nb):
        x = -L / 2 + 0.2 + (L - 0.4) * (i + 0.5) / nb
        b.beam_box((x - 0.05, proj - 0.22, zd + 0.4), (x + 0.05, proj - 0.1, zd + 2.8), 'Timber_Light', along='z')
    return b


def noren(W, drop=3.2, strips=None, mat='Cloth_Navy'):
    """Shop curtain: rod + cloth split into strips, gentle folds. Pivot bottom-centre; rod top = bbox top."""
    mats = ['Timber_Dark', mat]
    b = Builder(mats)
    strips = strips or (3 if W <= 4 else 5)
    top = drop + 0.35
    b.cylinder((-W / 2 - 0.25, 0, top - 0.12), (W / 2 + 0.25, 0, top - 0.12), 0.12, 8, 'Timber_Dark')
    gap = 0.08
    sw = (W - gap * (strips - 1)) / strips
    head = 0.7
    th = 0.05
    for s in range(strips):
        x0 = -W / 2 + s * (sw + gap)
        x1 = x0 + sw
        nu, nv = 6, 5
        def P(u, v, side):
            x = x0 + (x1 - x0) * u
            z = top - 0.24 - drop * v
            y = 0.1 * math.sin((x / W) * math.pi * 3 + s) * v + side * th / 2
            return Vector((x, y, z))
        for side in (1, -1):
            vs = [[b.bm.verts.new(P(i / nu, j / nv, side)) for i in range(nu + 1)] for j in range(nv + 1)]
            for j in range(nv):
                for i in range(nu):
                    q = [vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]]
                    uv = [((x0 + (x1 - x0) * ii / nu) * 0.25 + 0.5, (1 - jj / nv) * drop * 0.25)
                          for ii, jj in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))]
                    b.face(q, mat, uv, out=Vector((0, side, 0)), smooth=True)
            if side == 1: front = vs
            else: back = vs
        # close edges
        for j in range(nv):
            for col, o in ((0, -1), (nu, 1)):
                b.face([front[j][col], front[j + 1][col], back[j + 1][col], back[j][col]], mat, [(0, 0)] * 4,
                       out=Vector((o, 0, 0)))
        for i in range(nu):
            b.face([front[nv][i], front[nv][i + 1], back[nv][i + 1], back[nv][i]], mat, [(0, 0)] * 4,
                   out=Vector((0, 0, -1)))
            b.face([front[0][i], front[0][i + 1], back[0][i + 1], back[0][i]], mat, [(0, 0)] * 4,
                   out=Vector((0, 0, 1)))
    # header band joining the strips (sewn sleeve around the rod)
    b.box((-W / 2, -0.06, top - 0.24 - head * 0.4), (W / 2, 0.06, top - 0.02), mat)
    return b
