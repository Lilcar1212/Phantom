"""Castle kit: ishigaki stone walls, castle walls (dobei), tiered skirt roofs, chidori / karahafu gables,
shachihoko, keep tiers, yagura, gatehouse, Academy Hall.

Conventions as elsewhere: front = +Y (Roblox -Z), up = +Z, 1 unit = 1 stud.
"""
import math, random
from mathutils import Vector, Matrix
import ho
import wallkit as wk
import propkit as pk
import buildkit as bk
from buildkit import Assembly, M, PLINTH, FLOOR, ALL_MATS
from geo import Builder, loft, tube, lathe
from roofkit import Irimoya, MATS as ROOF_MATS
from specialkit import railing

CASTLE_MATS = ALL_MATS + ['Black_Lacquer', 'Stone_Fitted', 'Namako_Wall', 'Red_Lacquer', 'Cloth_Navy', 'Cloth_White']


# ================================================================================================= ISHIGAKI
def batter(z, H, B):
    """Outward offset of the stone face at height z: concave 'fan slope' (steep at the top, flaring at the base)."""
    t = max(0.0, min(1.0, 1.0 - z / H))
    return B * t * t


def courses_for(H, seed, lo=1.0, hi=2.3):
    """Course heights: bigger stones at the bottom."""
    r = random.Random(seed)
    zs = [0.0]
    while zs[-1] < H - 1e-6:
        frac = zs[-1] / H
        h = r.uniform(lo, hi) * (1.15 - 0.3 * frac)
        if H - (zs[-1] + h) < lo * 0.7:
            h = H - zs[-1]
        zs.append(min(H, zs[-1] + h))
    return list(zip(zs, zs[1:]))


def stone(b, x0, x1, z0, z1, H, B, depth=1.5, jitter=0.0, mat='Stone_Granite'):
    """One fitted stone on a +Y facing battered face (face line y = batter(z))."""
    g = 0.035
    x0, x1, z0, z1 = x0 + g, x1 - g, z0 + g, z1 - g
    o0, o1 = batter(z0, H, B) + jitter, batter(z1, H, B) + jitter
    ch = min(0.16, (z1 - z0) * 0.2)
    def sec(x, pull, bulge):
        f0 = o0 - pull + bulge; f1 = o1 - pull + bulge
        zi = pull * 0.7
        return [Vector((x, o0 - depth, z0 + zi)), Vector((x, f0 - ch, z0 + zi)), Vector((x, f0, z0 + ch + zi)),
                Vector((x, f1, z1 - ch - zi)), Vector((x, f1 - ch, z1 - zi)), Vector((x, o1 - depth, z1 - zi))]
    e = min(0.2, (x1 - x0) * 0.15)
    xm = x0 + (x1 - x0) * random.uniform(0.35, 0.65)
    rings = loft(b, [sec(x0, e, 0.0), sec(xm, 0.0, random.uniform(0.05, 0.16)), sec(x1, e, 0.0)], mat)
    # per-stone texture offset so neighbouring stones don't repeat the same grain/colour
    du, dv = random.random(), random.random()
    for ring in rings:
        for v in ring:
            for l in v.link_loops:
                l[b.uv].uv = (l[b.uv].uv[0] + du, l[b.uv].uv[1] + dv)


def stone_face(b, H, B, courses, ext, seed, depth=1.5, wmin=1.1, wmax=3.6):
    """Stones for a +Y face. ext(k, z0, z1) -> (xa, xb) extent of course k."""
    r = random.Random(seed)
    for k, (z0, z1) in enumerate(courses):
        xa, xb = ext(k, z0, z1)
        x = xa
        while x < xb - 1e-6:
            w = r.uniform(wmin, wmax) * (1.1 - 0.25 * z0 / H)
            if xb - (x + w) < wmin * 0.6:
                w = xb - x
            stone(b, x, min(xb, x + w), z0, z1, H, B, depth=depth, jitter=r.uniform(-0.05, 0.05))
            x += w


def core(b, x0, x1, H, B, T, mat='Stone_Granite'):
    """Solid fill behind the stones (prism of the battered profile, set back 0.3)."""
    n = 8
    outline = [(-T, 0.0)] + [(batter(H * i / n, H, B) - 0.35, H * i / n) for i in range(n + 1)] + [(-T, H)]
    b.prism(outline, (x0, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 0), x1 - x0, mat)


def ishigaki_straight(L, H=16.0, B=3.0, T=4.0, seed=1):
    """Straight module: face along X (length L), battered toward +Y. Origin = bottom of the wall directly
    below the TOP edge of the face (so it snaps to a terrace edge); the base flares out to y = +B."""
    b = Builder(CASTLE_MATS)
    cs = courses_for(H, 100 + int(H))            # same courses for every module of this height -> seamless rows
    core(b, -L / 2, L / 2, H, B, T)
    stone_face(b, H, B, cs, lambda k, z0, z1: (-L / 2, L / 2), seed)
    return b


def ishigaki_corner(L=16.0, H=16.0, B=3.0, T=4.0, seed=2, inner=False):
    """Corner module. Outer (convex): platform lies at x<0, y<0; faces +Y (along x in [-L, 0]) and +X
    (along y in [-L, 0]) meet at the corner, long stones interlocking (sangi-zumi).
    Inner (concave): faces +Y (x in [0, L]) and +X (y in [0, L]) meet in the re-entrant corner."""
    b = Builder(CASTLE_MATS)
    D = 1.5
    cs = courses_for(H, 100 + int(H))
    rot = Matrix.Rotation(-math.pi / 2, 4, 'Z')            # local +Y face -> world +X face; local x -> world -y
    fa = Builder(CASTLE_MATS); fb = Builder(CASTLE_MATS)
    if not inner:
        def ext_a(k, z0, z1):
            o = batter((z0 + z1) / 2, H, B)
            return (-L, o if k % 2 == 0 else o - D - 0.05)
        def ext_b(k, z0, z1):              # in local coords of face B: corner end is at local x = 0 side (world y=0)
            o = batter((z0 + z1) / 2, H, B)
            return (-(o if k % 2 == 1 else o - D - 0.05), L)
        core(fa, -L, 0.0, H, B, T); core(fb, T, L, H, B, T)      # cores must not overlap (coplanar tops z-fight)
        stone_face(fa, H, B, cs, ext_a, seed, depth=D)
        stone_face(fb, H, B, cs, ext_b, seed + 7, depth=D)
    else:
        def ext_a(k, z0, z1):
            o = batter((z0 + z1) / 2, H, B)
            return (o, L)
        def ext_b(k, z0, z1):
            o = batter((z0 + z1) / 2, H, B)
            return (-L, -o)
        core(fa, 0.0, L, H, B, T); core(fb, -L, 0.0, H, B, T)
        stone_face(fa, H, B, cs, ext_a, seed, depth=D)
        stone_face(fb, H, B, cs, ext_b, seed + 7, depth=D)
    fb.deform(lambda co: (rot @ co.to_4d()).to_3d())
    for src in (fa, fb):
        mesh_join(b, src)
    return b


def mesh_join(dst, src):
    """Append src builder geometry into dst builder (materials matched by name)."""
    import bmesh
    vmap = {}
    uv_s, uv_d = src.uv, dst.uv
    for v in src.bm.verts:
        vmap[v] = dst.bm.verts.new(v.co)
    for f in src.bm.faces:
        nf = dst.bm.faces.new([vmap[v] for v in f.verts])
        nf.material_index = dst.mats[src.mat_names[f.material_index]]
        nf.smooth = f.smooth
        for l_new, l_old in zip(nf.loops, f.loops):
            l_new[uv_d].uv = l_old[uv_s].uv


def ishigaki_stepped(L=16.0, H=16.0, step=4.0, B=3.0, T=4.0, seed=3):
    """Straight module whose top steps down by `step` at the middle (left half H, right half H - step)."""
    b = Builder(CASTLE_MATS)
    H2 = H - step
    cs1 = courses_for(H, 100 + int(H)); cs2 = courses_for(H2, 100 + int(H2))
    core(b, -L / 2, 0.0, H, B, T); core(b, 0.0, L / 2, H2, B * H2 / H, T)
    stone_face(b, H, B, cs1, lambda k, z0, z1: (-L / 2, 0.0), seed)
    stone_face(b, H2, B * H2 / H, cs2, lambda k, z0, z1: (0.0, L / 2), seed + 3)
    # exposed end of the tall half (faces +X): a few stones on a vertical face
    e = Builder(CASTLE_MATS)
    for z0, z1 in courses_for(step, 7):
        zz0, zz1 = H2 + z0, H2 + z1
        o = batter((zz0 + zz1) / 2, H, B)
        yy = -T
        while yy < o - 0.3:
            w = min(o - yy, random.uniform(1.2, 2.2))
            e.box((0.02, yy + 0.04, zz0 + 0.04), (0.8, yy + w - 0.04, zz1 - 0.04), 'Stone_Granite')   # in front of the core end
            yy += w
    mesh_join(b, e)
    return b


def ishigaki_platform(Wt, Dt, H=16.0, B=3.0, T=5.0, seed=5, cap='Stone_Fitted'):
    """Four battered stone faces around a Wt x Dt top rectangle with interlocking corners + top cap.
    Origin = bottom centre; the top surface (z = H) is exactly Wt x Dt. Returns dict side -> Builder."""
    D = 1.5
    cs = courses_for(H, 200 + int(H))
    sides = {}
    for name, half_len, other_half, rot, off, even_long in (
            ('Front', Wt / 2, Dt / 2, 0.0, (0, Dt / 2), True), ('Back', Wt / 2, Dt / 2, math.pi, (0, -Dt / 2), True),
            ('Right', Dt / 2, Wt / 2, -math.pi / 2, (Wt / 2, 0), False), ('Left', Dt / 2, Wt / 2, math.pi / 2, (-Wt / 2, 0), False)):
        b = Builder(CASTLE_MATS)
        def ext(k, z0, z1, half_len=half_len, even_long=even_long):
            o = batter((z0 + z1) / 2, H, B)
            long_ = (k % 2 == 0) == even_long
            e = (half_len + o) if long_ else (half_len + o - D - 0.05)
            return (-e, e)
        core(b, -half_len, half_len, H, B, min(T, other_half))
        stone_face(b, H, B, cs, ext, seed + len(sides) * 13, depth=D)
        mtx = Matrix.Translation((off[0], off[1], 0)) @ Matrix.Rotation(rot, 4, 'Z')
        b.deform(lambda co, mtx=mtx: (mtx @ co.to_4d()).to_3d())
        sides[name] = b
    c = Builder(CASTLE_MATS)
    c.box((-Wt / 2 + 0.2, -Dt / 2 + 0.2, H - 0.25), (Wt / 2 - 0.2, Dt / 2 - 0.2, H + 0.06), cap, skip=('-z',))   # sits just above the core tops (no coplanar faces)
    if min(Wt, Dt) > 2 * T:        # inner fill between the four cores
        c.box((-Wt / 2 + T - 0.1, -Dt / 2 + T - 0.1, 0.0), (Wt / 2 - T + 0.1, Dt / 2 - T + 0.1, H - 0.35), 'Stone_Granite',
              skip=('+z', '-z'))
    sides['Top'] = c
    return sides


# ================================================================================================= CASTLE WALL (DOBEI)
def coping(b, x0, x1, z, w, rise=0.9, rows_every=1.0):
    """Small tiled gable coping along X centred on y = 0: two tile slopes, cover rows, half-round ridge."""
    hw = w / 2
    for s in (1, -1):
        outline = [(0.0, 0.0), (s * hw, -rise), (s * hw, -rise - 0.3), (0.0, -0.3)]
        b.prism([(u, v) for u, v in outline], (x0, 0, z + rise + 0.3), (0, 1, 0), (0, 0, 1), (1, 0, 0), x1 - x0, 'RoofTile_Clay')
        n = int((x1 - x0) / rows_every)
        for i in range(n):
            xx = x0 + (x1 - x0) * (i + 0.5) / n
            p0 = Vector((xx, 0.0, z + rise + 0.3)); p1 = Vector((xx, s * (hw + 0.05), z + 0.25))
            prof = [(0.13 * math.cos(math.pi * k / 3), 0.13 * math.sin(math.pi * k / 3)) for k in range(4)] + [(-0.13, -0.05), (0.13, -0.05)]
            b.sweep([p0, p1], prof, 'RoofTile_Clay', smooth=True, smooth_sides={0, 1, 2}, up=Vector((0, 0, 1)))
            c = p1 + (p1 - p0).normalized() * 0.02
            b.cylinder(c - (p1 - p0).normalized() * 0.1, c + (p1 - p0).normalized() * 0.06, 0.17, 6, 'RoofTile_Clay')
    prof = [(0.28, -0.2), (0.28, 0.15)] + [(0.24 * math.cos(math.pi * k / 4), 0.15 + 0.24 * math.sin(math.pi * k / 4)) for k in range(1, 4)] + [(-0.28, 0.15), (-0.28, -0.2)]
    b.sweep([Vector((x0 - 0.1, 0, z + rise + 0.3)), Vector((x1 + 0.1, 0, z + rise + 0.3))], prof, 'RoofTile_Clay')


def dobei(L, kind='straight', h=6.0, t=1.6, seed=1):
    """Castle wall: stone footing, white plaster body with square/rectangular loopholes (sama), tiled coping.
    kind: 'straight' | 'end' (capped end at +X) | 'corner' (L-shape: +X leg turns toward -Y)."""
    random.seed(seed)
    b = Builder(CASTLE_MATS)
    fh = 1.4
    def run(x0, x1, rot=0.0, off=(0, 0), end_caps=()):
        rb = Builder(CASTLE_MATS)
        rb.box((x0, -t / 2 - 0.25, 0.0), (x1, t / 2 + 0.25, fh), 'Stone_Fitted')
        # plaster body with loopholes (openings built as panels around holes)
        holes = []
        x = x0 + 1.4
        k = 0
        while x < x1 - 1.4:
            if k % 2 == 0: holes.append((x - 0.35, x + 0.35, fh + 2.2, fh + 2.9))       # square teppo-zama
            else: holes.append((x - 0.18, x + 0.18, fh + 1.7, fh + 3.4))                 # tall ya-zama slit
            x += 2.0; k += 1
        us = sorted({x0, x1} | {q[0] for q in holes} | {q[1] for q in holes})
        zs = sorted({fh, fh + h} | {q[2] for q in holes} | {q[3] for q in holes})
        for ua, ub in zip(us, us[1:]):
            for za, zc in zip(zs, zs[1:]):
                um, zm = (ua + ub) / 2, (za + zc) / 2
                if any(q[0] <= um <= q[1] and q[2] <= zm <= q[3] for q in holes): continue
                rb.box((ua, -t / 2, za), (ub, t / 2, zc), 'Plaster_White', uvv=1 / 9.0)
        for q in holes:                                   # dark timber lining inside each loophole
            rb.box((q[0], -t / 2 + 0.2, q[2] - 0.02), (q[1], t / 2 - 0.2, q[2]), 'Timber_Dark')
        # black base band (koshi-ita) on the outside face
        rb.box((x0, t / 2, fh), (x1, t / 2 + 0.08, fh + 1.2), 'Black_Lacquer')
        coping(rb, x0 - 0.2, x1 + 0.2, fh + h, t + 1.6)
        mtx = Matrix.Translation((off[0], off[1], 0)) @ Matrix.Rotation(rot, 4, 'Z')
        rb.deform(lambda co: (mtx @ co.to_4d()).to_3d())
        mesh_join(b, rb)
    if kind == 'straight':
        run(-L / 2, L / 2)
    elif kind == 'end':
        run(-L / 2, L / 2)
        b.box((L / 2, -t / 2 - 0.35, 0.0), (L / 2 + 0.6, t / 2 + 0.35, fh + h + 0.6), 'Plaster_White', uvv=1 / 9.0)
        b.box((L / 2 - 0.05, -t / 2 - 0.4, fh + h + 0.6), (L / 2 + 0.7, t / 2 + 0.4, fh + h + 1.3), 'RoofTile_Clay')
    else:   # corner: leg A along -X..0 at y=0, leg B from 0 toward -Y at x=0
        run(-L, t / 2)
        run(-L, -t / 2, rot=math.pi / 2, off=(0, 0))
        # corner post cap block
        b.box((-t / 2 - 0.3, -t / 2 - 0.3, 0.0), (t / 2 + 0.3, t / 2 + 0.3, fh + h + 0.3), 'Plaster_White', uvv=1 / 9.0)
    return b


# ================================================================================================= CASTLE ROOFS
def remap(b, mapping):
    """Re-assign materials by name on a builder (e.g. castle eaves: all timber -> white plaster)."""
    for f in b.bm.faces:
        name = b.mat_names[f.material_index]
        if name in mapping:
            f.material_index = b.mats[mapping[name]]


class Skirt(Irimoya):
    """Tiled skirt roof (hip ring) around a keep tier: covers a W x D tier top and rises inward to meet the next
    tier's walls, which stand `inset` studs further in on every side. z = 0 is the lower tier's wall top.
    White-plastered castle eaves (soffit, fascia, frieze)."""

    def __init__(self, W, D, inset=2.0, overhang=2.6, pitch=0.6, **kw):
        super().__init__(W, D, overhang=overhang, gable_overhang=0.0, pitch=pitch, concave=0.3, **kw)
        self.inset = inset
        self.soffit = 'Plaster_White'
        self.t_in = (D / 2 - inset) / self.Ye
        self.ze = 0.0
        self.ze = -0.25 - (self.H(1.0) - self.T)          # eave underside slightly below the lower wall top

    def build(self):
        b = self.b
        Xe, Ye, ti = self.Xe, self.Ye, self.t_in
        for sg in (1, -1):
            m_long = lambda a, t, sg=sg: self.long(a, t, sg)
            m_hip = lambda a, t, sg=sg: self.hip(a, t, sg)
            self.slab(m_long, ti, 1.0, lambda t: (-(Xe - Ye + t * Ye), Xe - Ye + t * Ye), max(6, int(2 * Xe / 1.6)))
            self.slab(m_hip, ti, 1.0, lambda t: (-t * Ye, t * Ye), max(4, int(2 * Ye / 1.6)))
            n = int(Xe / self.tp) + 1
            for i in range(-n, n):
                a = (i + 0.5) * self.tp
                t0 = max(ti + 0.01, (abs(a) - (Xe - Ye)) / Ye + 0.02)
                if t0 < 0.97: self.cover_row(m_long, a, t0, 1.0)
            n = int(Ye / self.tp) + 1
            for i in range(-n, n):
                a = (i + 0.5) * self.tp
                t0 = max(ti + 0.01, abs(a) / Ye + 0.02)
                if t0 < 0.97: self.cover_row(m_hip, a, t0, 1.0)
        rs = 0.8
        for sg in (1, -1):
            for sy in (1, -1):
                path = [Vector((sg * (Xe - Ye + t * Ye), sy * t * Ye, self.H(t) + 0.02)) for t in [ti + (1 - ti) * k / 8 for k in range(9)]]
                path[-1] += (path[-1] - path[-2]).normalized() * 0.3
                self.ridge(path, s=rs)
                self.onigawara(Vector((sg * (Xe + 0.15), sy * (Ye + 0.15), self.H(1.0) + 0.05)), (sg, sy, 0), s=0.5,
                               tilt=math.radians(12))
        # flashing ridge where the skirt meets the upper walls
        zi = self.H(ti) - 0.05
        xi, yi = self.W / 2 - self.inset + 0.25, self.D / 2 - self.inset + 0.25
        for sg in (1, -1):
            self.ridge([Vector((x, sg * yi, zi)) for x in (-xi, 0.0, xi)], s=0.6)
            self.ridge([Vector((sg * xi, y, zi)) for y in (-yi, 0.0, yi)], s=0.6)
        # plaster fascia + frieze on the lower wall line
        zf = self.H(1.0) - self.T
        for sg in (1, -1):
            b.beam(Vector((-Xe, sg * (Ye - 0.2), zf)), Vector((Xe, sg * (Ye - 0.2), zf)), 0.3, 0.3, 'Plaster_White', nseg=14, anchor='top')
            b.beam(Vector((sg * (Xe - 0.2), -Ye, zf)), Vector((sg * (Xe - 0.2), Ye, zf)), 0.3, 0.3, 'Plaster_White', nseg=10, anchor='top')
        zw = self.zu(0.0)
        W2, D2 = self.W / 2, self.D / 2
        for sg in (1, -1):
            b.box((-W2, sg * D2 - (1.0 if sg > 0 else 0), -0.01), (W2, sg * D2 + (0 if sg > 0 else 1.0), zw), 'Plaster_White', uvv=1 / 9)
            b.box((sg * W2 - (1.0 if sg > 0 else 0), -D2 + 1, -0.01), (sg * W2 + (0 if sg > 0 else 1.0), D2 - 1, zw), 'Plaster_White', uvv=1 / 9)
        b.deform(self.lift_fn)
        b.mark_sharp()
        return b


class Patch(Irimoya):
    """Helper roof patch driven by an arbitrary surface mapping (used for chidori and karahafu gables)."""

    def __init__(self, L, fn, course=0.9):
        super().__init__(8, 8, overhang=1.0, lift=0.0, flare=0.0)
        self.L = L
        self.course = course
        self.fn = fn
        self.soffit = 'Plaster_White'

    def long(self, a, t, sign=1):
        return self.fn(a, t)


def chidori(x_c, y_wall, z_eave, w=8.0, depth=4.5, rise=3.6, facing=1):
    """Triangular chidori gable on a skirt: ridge runs outward (+Y*facing) from the upper wall to the front
    gable; eaves at z_eave. Returns a Builder in the same space (add it to the assembly)."""
    parts = []
    for s in (1, -1):
        L = math.hypot(w / 2 + 0.6, rise)
        fn = lambda a, t, s=s: Vector((x_c + s * t * (w / 2 + 0.6), y_wall + facing * a, z_eave + rise * (1 - t) + 0.55))
        p = Patch(L, fn)
        p.slab(fn, 0.0, 1.0, lambda t: (0.0, depth + 0.4), 4)
        n = int((depth + 0.2) / 1.0)
        for i in range(n):
            p.cover_row(fn, (i + 0.6), 0.04, 1.0)
        parts.append(p.b)
    top = Builder(ROOF_MATS)
    rp = Patch(1, lambda a, t: Vector())
    rp.b = top
    rp.ridge([Vector((x_c, y_wall + facing * yy, z_eave + rise + 0.57)) for yy in (0.0, (depth + 0.4) / 2, depth + 0.6)], s=0.75)
    rp.onigawara(Vector((x_c, y_wall + facing * (depth + 0.7), z_eave + rise + 0.4)), (0, facing, 0), s=0.55)
    # gable face (plaster triangle), barge boards (white), gold gegyo
    yf = y_wall + facing * depth
    outline = [(-w / 2, 0.0), (w / 2, 0.0), (0.0, rise)]
    top.prism(outline, Vector((x_c, yf - facing * 0.4, z_eave)), (1, 0, 0), (0, 0, 1), (0, facing, 0), 0.4, 'Plaster_White')
    for s in (1, -1):
        pts = [Vector((x_c + s * (w / 2 + 0.6) * k / 6, yf + facing * 0.25, z_eave + rise * (1 - k / 6) + 0.5)) for k in range(7)]
        top.sweep(pts, [(-0.15, -0.55), (0.15, -0.55), (0.15, 0.05), (-0.15, 0.05)], 'Plaster_White')
    g = [(-0.5, 0.0), (0.5, 0.0), (0.7, -0.4), (0.0, -1.0), (-0.7, -0.4)]
    top.prism(g, Vector((x_c, yf + facing * 0.4, z_eave + rise + 0.1)), (1, 0, 0), (0, 0, 1), (0, facing, 0), 0.14, 'Gold_Leaf')
    for pb in parts:
        remap(pb, {'Timber_Light': 'Plaster_White', 'Timber_Dark': 'Plaster_White'})
    return parts + [top]


def karahafu(x_c, y_wall, z_base, w=10.0, depth=4.0, rise=2.4, facing=1):
    """Curved 'wave' gable (karahafu): barrel-like tiled roof whose front edge arches up in the middle and flicks
    up at the ends; white karahafu board with gold caps; plaster face below."""
    def zc(x):
        u = max(-1.0, min(1.0, (x - x_c) / (w / 2)))
        hump = rise * (1 - u * u) ** 1.3
        flick = 0.5 * max(0.0, abs(u) - 0.82) / 0.18
        return hump + flick
    fn = lambda a, t: Vector((a, y_wall + facing * t * depth, z_base + zc(a) - 0.35 * t))
    p = Patch(depth, fn, course=0.8)
    p.slab(fn, 0.0, 1.0, lambda t: (x_c - w / 2, x_c + w / 2), 16)
    n = int(w / 0.95)
    for i in range(n):
        p.cover_row(fn, x_c - w / 2 + w * (i + 0.5) / n, 0.02, 1.0)
    b = p.b
    remap(b, {'Timber_Light': 'Plaster_White', 'Timber_Dark': 'Plaster_White'})
    top = Builder(ROOF_MATS)
    yf = y_wall + facing * depth
    xs = [x_c - w / 2 + w * k / 20 for k in range(21)]
    pts = [Vector((x, yf + facing * 0.1, z_base + zc(x) - 0.35 - 0.55)) for x in xs]
    top.sweep(pts, [(-0.18, -0.5), (0.18, -0.5), (0.18, 0.1), (-0.18, 0.1)], 'Plaster_White', up=Vector((0, 0, 1)))
    for x in (x_c - w / 2 + 0.3, x_c, x_c + w / 2 - 0.3):
        c = Vector((x, yf + facing * 0.3, z_base + zc(x) - 1.05))
        top.box((x - 0.3, min(c.y, c.y + facing * 0.08), c.z - 0.35), (x + 0.3, max(c.y, c.y + facing * 0.08), c.z + 0.1), 'Gold_Leaf')
    # plaster face under the curve (closes the gable), set back slightly
    top.prism([(-w / 2 + 0.2, -1.8), (w / 2 - 0.2, -1.8)] + [(x - x_c, zc(x) - 0.95) for x in reversed(xs[1:-1])],
              Vector((x_c, yf - facing * 0.3, z_base)), (1, 0, 0), (0, 0, 1), (0, facing, 0), 0.3, 'Plaster_White')
    return [b, top]


def shachihoko(b, x, y, z, facing=1, s=1.0):
    """Gold shachihoko (tiger-headed carp): head down on the ridge facing inward (-X*facing), body arching up,
    tail fan high."""
    f = -facing
    path = [Vector((x + f * 0.5 * s, y, z + 0.5 * s)), Vector((x + f * 0.2 * s, y, z + 1.4 * s)),
            Vector((x - f * 0.25 * s, y, z + 2.2 * s)), Vector((x - f * 0.55 * s, y, z + 2.8 * s)),
            Vector((x - f * 0.6 * s, y, z + 3.3 * s))]
    radii = [0.55 * s, 0.6 * s, 0.45 * s, 0.26 * s, 0.1 * s]
    tube(b, path, radii, 8, 'Gold_Leaf', up=Vector((0, 1, 0)), squash=0.8)
    lathe(b, (x + f * 0.55 * s, y, z), [(0.45 * s, 0.0), (0.6 * s, 0.35 * s), (0.5 * s, 0.75 * s), (0.0, 0.9 * s)], 8, 'Gold_Leaf')
    for sy in (-1, 1):   # eyes + pectoral fins
        b.cylinder((x + f * 0.8 * s, y + sy * 0.38 * s, z + 0.55 * s), (x + f * 0.8 * s, y + sy * 0.5 * s, z + 0.55 * s), 0.12 * s, 6, 'Black_Lacquer')
        fin = [(0.0, 0.0), (0.7 * s, -0.2 * s), (0.5 * s, 0.35 * s)]
        b.prism(fin, (x, y + sy * 0.5 * s, z + 1.0 * s), (-f, 0, 0), (0, 0, 1), (0, sy, 0), 0.06 * s, 'Gold_Leaf')
    tail = [(0.0, 0.0), (-0.8 * s, 0.9 * s), (-0.1 * s, 0.6 * s), (0.3 * s, 1.1 * s), (0.5 * s, 0.4 * s)]
    b.prism(tail, (x - f * 0.6 * s, y - 0.05 * s, z + 3.2 * s), (-f, 0, 0), (0, 0, 1), (0, 1, 0), 0.1 * s, 'Gold_Leaf')
    b.box((x - 0.3 * s, y - 0.35 * s, z - 0.1), (x + 0.3 * s, y + 0.35 * s, z + 0.15), 'Gold_Leaf')


# ================================================================================================= KEEP (TENSHU)
KEEP_TIERS = [(40, 32), (36, 28), (32, 24), (28, 20), (24, 16)]
KEEP_BASE_H = 16.0


def castle_wall_bay(tier, top_tier=False):
    """Bay rule for keep walls: lattice windows with plaster between; tier 1 gets loophole-like small windows."""
    def fn(m, i, c):
        n = m // 4
        if tier == 0:
            bays = ['plaster' if k % 2 == 0 else 'lattice' for k in range(n)]
        else:
            bays = ['lattice' if (k % 2 == 1 or top_tier) else 'plaster' for k in range(n)]
        return wk.wall(m, bays)
    return fn


def keep():
    """Five-tier keep on a tall ishigaki base. Returns (objects, tier_groups) where tier_groups maps export
    names (Base, Tier1..Tier5) to the mesh objects that belong to them."""
    random.seed(21)
    asm = Assembly('HO_Castle_Keep')
    Wt, Dt = KEEP_TIERS[0][0] + 4, KEEP_TIERS[0][1] + 4
    for name, sb in ishigaki_platform(Wt, Dt, H=KEEP_BASE_H, B=3.0).items():
        asm.add(f'Base_{name}', sb)
    z = KEEP_BASE_H + 0.06
    for i, (W, D) in enumerate(KEEP_TIERS):
        grp = f'Tier{i + 1}'
        top_tier = i == len(KEEP_TIERS) - 1
        fn = castle_wall_bay(i, top_tier)
        for side, L in (('front', W), ('back', W), ('right', D), ('left', D)):
            bk.wall_run(asm, grp + '_Walls', L, z, side, W, D, fn, seed=10 * i + len(side))
        for sx in (1, -1):
            for sy in (1, -1):
                asm.add(grp + '_Walls', wk.corner_post(), M(sx * (W / 2 - 0.5), sy * (D / 2 - 0.5), z))
        # floor slab closing the tier (seen through windows)
        fl = Builder(CASTLE_MATS)
        fl.box((-W / 2 + 1, -D / 2 + 1, z), (W / 2 - 1, D / 2 - 1, z + 0.5), 'Wood_Planks')
        asm.add(grp + '_Walls', fl)
        top = z + FLOOR
        if not top_tier:
            sk = Skirt(W, D, inset=2.0, overhang=2.6 if i < 2 else 2.2)
            asm.add(grp + '_Roof', sk.build(), M(0, 0, top))
            ze = sk.H(1.0)
            # gables on the skirt: karahafu front on tier 1, chidori on tier 2 (front/back) and tier 3 (sides)
            if i == 0:
                for pb in karahafu(0.0, D / 2 - 2.0, top + ze + 0.2, w=12.0, depth=4.4, rise=2.6):
                    asm.add(grp + '_Gable', pb)
            elif i == 1:
                for fsg in (1, -1):
                    for pb in chidori(0.0, fsg * (D / 2 - 2.0), top + ze - 0.2, w=10.0, depth=4.2, rise=3.8, facing=fsg):
                        asm.add(grp + '_Gable', pb)
            elif i == 2:
                for fsg in (1, -1):
                    for pb in chidori(0.0, fsg * (W / 2 - 2.0), top + ze - 0.2, w=8.0, depth=4.0, rise=3.2, facing=fsg):
                        asm.add(grp + '_Gable', pb, Matrix.Rotation(-math.pi / 2, 4, 'Z'))
        else:
            # top floor: balcony (mawari-en) with railing sitting on the tier-4 skirt, irimoya roof, shachihoko
            bb = Builder(CASTLE_MATS)
            zb = z + 2.7
            for sg in (1, -1):
                bb.box((-W / 2 - 1.6, sg * (D / 2) - (0 if sg > 0 else 1.6), zb - 0.3), (W / 2 + 1.6, sg * (D / 2) + (1.6 if sg > 0 else 0), zb), 'Wood_Planks')
                bb.box((sg * (W / 2) - (0 if sg > 0 else 1.6), -D / 2, zb - 0.3), (sg * (W / 2) + (1.6 if sg > 0 else 0), D / 2, zb), 'Wood_Planks')
            for (p0, p1) in (((-W / 2 - 1.4, D / 2 + 1.4, zb), (W / 2 + 1.4, D / 2 + 1.4, zb)),
                             ((-W / 2 - 1.4, -D / 2 - 1.4, zb), (W / 2 + 1.4, -D / 2 - 1.4, zb)),
                             ((W / 2 + 1.4, -D / 2 - 1.4, zb), (W / 2 + 1.4, D / 2 + 1.4, zb)),
                             ((-W / 2 - 1.4, -D / 2 - 1.4, zb), (-W / 2 - 1.4, D / 2 + 1.4, zb))):
                railing(bb, p0, p1, h=2.6)
            remap(bb, {'Timber_Dark': 'Red_Lacquer'})
            asm.add(grp + '_Balcony', bb)
            r = Irimoya(W, D, overhang=3.2, gable_overhang=1.0, pitch=0.7, t_gable=0.56, castle=True)
            r.soffit = 'Plaster_White'
            rb = r.build()
            remap(rb, {'Timber_Dark': 'Plaster_White', 'Timber_Light': 'Plaster_White'})
            asm.add(grp + '_Roof', rb, M(0, 0, top))
            shb = Builder(CASTLE_MATS)
            xr = r.Xg + r.kb
            zr = top + r.H(0.0) + 1.3
            for sg in (1, -1):
                shachihoko(shb, sg * (xr - 0.2), 0.0, zr, facing=sg, s=1.2)
            asm.add(grp + '_Gable', shb)
        z = top
    objs = bk.finish(asm)
    groups = {}
    for o in objs:
        key = o.name.replace('HO_Castle_Keep_', '').split('_')[0]
        groups.setdefault(key, []).append(o)
    return objs, groups


def castle_roof(W, D, top, asm, group, shachi=0.0, overhang=2.8, pitch=0.68):
    """White-plastered castle irimoya roof on walls ending at z = top (+ optional shachihoko)."""
    r = Irimoya(W, D, overhang=overhang, gable_overhang=0.8, pitch=pitch, t_gable=0.56, castle=True)
    r.soffit = 'Plaster_White'
    rb = r.build()
    remap(rb, {'Timber_Dark': 'Plaster_White', 'Timber_Light': 'Plaster_White'})
    asm.add(group, rb, M(0, 0, top))
    if shachi:
        shb = Builder(CASTLE_MATS)
        for sg in (1, -1):
            shachihoko(shb, sg * (r.Xg + r.kb - 0.2), 0.0, top + r.H(0.0) + 1.1, facing=sg, s=shachi)
        asm.add(group, shb)
    return r


def banner(b, x, y, z=0.0, h=12.0, facing=1):
    """Nobori banner: lacquered pole + navy cloth with a white circle crest (cloth hangs on the -X side)."""
    b.cylinder((x, y, z), (x, y, z + h), 0.14, 8, 'Black_Lacquer')
    b.beam_box((x - 2.2, y - 0.05, z + h - 0.35), (x, y + 0.05, z + h - 0.2), 'Black_Lacquer', along='x')
    b.box((x - 2.1, y - 0.04, z + h - 7.5), (x - 0.2, y + 0.04, z + h - 0.35), 'Cloth_Navy')
    ring = [(0.62 * math.cos(2 * math.pi * i / 16), 0.62 * math.sin(2 * math.pi * i / 16)) for i in range(16)]
    hole = [(0.4 * math.cos(2 * math.pi * i / 16), 0.4 * math.sin(2 * math.pi * i / 16)) for i in range(16)]
    for side in (1, -1):
        c = Vector((x - 1.15, y + side * 0.04, z + h - 2.4))
        b.prism(ring, c, (1, 0, 0), (0, 0, 1), (0, side, 0), 0.02, 'Cloth_White')
        b.prism(hole, c + Vector((0, side * 0.02, 0)), (1, 0, 0), (0, 0, 1), (0, side, 0), 0.01, 'Cloth_Navy')


def yagura():
    """Two-tier corner watchtower, 16 x 12, white walls, lattice windows, skirt roof with chidori gable,
    castle irimoya top roof with small shachihoko."""
    random.seed(31)
    W, D = 16, 12
    asm = Assembly('HO_Castle_Yagura')
    bk.plinths(asm, W, D)
    z = PLINTH
    for side, L in (('front', W), ('back', W), ('right', D), ('left', D)):
        bk.wall_run(asm, 'Tier1', L, z, side, W, D,
                    lambda m, i, c: wk.wall(m, ['plaster' if k in (0, m // 4 - 1) else 'lattice' for k in range(m // 4)]), seed=len(side))
    for sx in (1, -1):
        for sy in (1, -1):
            asm.add('Tier1', wk.corner_post(), M(sx * (W / 2 - 0.5), sy * (D / 2 - 0.5), z))
    top = z + FLOOR
    sk = Skirt(W, D, inset=2.0, overhang=2.2)
    asm.add('Tier1_Roof', sk.build(), M(0, 0, top))
    for pb in chidori(0.0, D / 2 - 2.0, top + sk.H(1.0) - 0.2, w=7.0, depth=3.6, rise=3.0, facing=1):
        asm.add('Tier1_Roof', pb)
    W2, D2 = W - 4, D - 4
    for side, L in (('front', W2), ('back', W2), ('right', D2), ('left', D2)):
        bk.wall_run(asm, 'Tier2', L, top, side, W2, D2, lambda m, i, c: wk.wall(m, ['lattice'] * (m // 4)), seed=7 + len(side))
    for sx in (1, -1):
        for sy in (1, -1):
            asm.add('Tier2', wk.corner_post(), M(sx * (W2 / 2 - 0.5), sy * (D2 / 2 - 0.5), top))
    castle_roof(W2, D2, top + FLOOR, asm, 'Tier2_Roof', shachi=0.7, overhang=2.6)
    return bk.finish(asm)


def gatehouse():
    """Yagura-mon gate, 28 x 12: stone gate towers either side of a 12-wide passage, massive lintel beams,
    white upper floor with lattice windows, castle roof, two iron-strapped gate doors (separate meshes),
    navy crest banners."""
    random.seed(32)
    W, D = 28, 12
    asm = Assembly('HO_Castle_Gatehouse')
    hb = 10.0
    for sx in (1, -1):
        for name, sb in ishigaki_platform(8, D, H=hb, B=1.2, T=3.0, seed=40 + sx).items():
            asm.add('Base', sb, M(sx * 10.0, 0, 0))
    fb = Builder(CASTLE_MATS)
    for yy in (D / 2 - 0.9, -D / 2 + 0.9):                         # kabuki lintel beams
        fb.beam_box((-8.0, yy - 0.8, hb - 1.6), (8.0, yy + 0.8, hb), 'Timber_Dark', along='x')
    for x in range(-5, 6, 2):                                        # joists under the upper floor
        fb.beam_box((x - 0.35, -D / 2 + 1, hb - 1.2), (x + 0.35, D / 2 - 1, hb - 0.4), 'Timber_Dark', along='y')
    fb.box((-6.0, -D / 2 + 1, hb - 0.4), (6.0, D / 2 - 1, hb), 'Wood_Planks')
    for sx in (1, -1):                                               # hinge posts + threshold
        fb.beam_box((sx * 6.0 - 0.7, -0.7, 0.0), (sx * 6.0 + 0.7, 0.7, hb - 1.6), 'Timber_Dark', along='z')
    fb.box((-6.0, -0.5, 0.0), (6.0, 0.5, 0.35), 'Stone_Granite')
    fb.box((-6.0, -D / 2, -0.02), (6.0, D / 2, 0.05), 'Stone_Fitted', skip=('-z',))
    asm.add('Structure', fb)
    # gate doors: vertical planks, iron straps with studs, ring handles
    for k, sx in enumerate((-1, 1)):
        d = Builder(CASTLE_MATS)
        x0, x1 = (-5.3, 0.0) if sx < 0 else (0.0, 5.3)
        n = 5
        for i in range(n):
            a = x0 + (x1 - x0) * i / n; c = x0 + (x1 - x0) * (i + 1) / n
            d.beam_box((a + 0.02, -0.35, 0.4), (c - 0.02, 0.35, hb - 1.8), 'Timber_Dark', along='z', uv_seed=i * 0.37)
        for zz in (1.6, 4.4, 7.2):
            d.box((x0, -0.42, zz - 0.25), (x1, 0.42, zz + 0.25), 'Iron_Wrought')
            for i in range(9):
                xx = x0 + 0.3 + (x1 - x0 - 0.6) * i / 8
                for side in (1, -1):
                    d.box((xx - 0.09, min(side * 0.42, side * 0.5), zz - 0.09), (xx + 0.09, max(side * 0.42, side * 0.5), zz + 0.09), 'Iron_Wrought')
        hx = x1 - 0.8 if sx < 0 else x0 + 0.8
        for side in (1, -1):
            d.cylinder((hx, side * 0.42, 3.8), (hx, side * 0.62, 3.8), 0.32, 10, 'Iron_Wrought')   # ring pull
        asm.add(f'Door{k + 1}', d)
    # upper floor
    for side, L in (('front', W), ('back', W), ('right', D), ('left', D)):
        bk.wall_run(asm, 'Upper', L, hb, side, W, D,
                    lambda m, i, c: wk.wall(m, ['plaster' if k % 2 == 0 else 'lattice' for k in range(m // 4)]), seed=len(side) + 3)
    for sx in (1, -1):
        for sy in (1, -1):
            asm.add('Upper', wk.corner_post(), M(sx * (W / 2 - 0.5), sy * (D / 2 - 0.5), hb))
    castle_roof(W, D, hb + FLOOR, asm, 'Roof', shachi=0.9, overhang=3.0)
    bn = Builder(CASTLE_MATS)
    for sx in (1, -1):
        banner(bn, sx * 7.2, D / 2 + 2.5, 0.0, h=12.0)
    asm.add('Banners', bn)
    return bk.finish(asm)


def academy_hall():
    """Sword Academy dojo, 44 x 28 on a raised floor with a veranda all round, front steps, sliding shoji
    doors in the centre bays, big irimoya roof with brackets. Interior: polished wood floor, kamidana shrine
    shelf, weapon racks, practice sword racks, taiko drum, lanterns."""
    random.seed(33)
    W, D = 44, 28
    asm = Assembly('HO_Castle_AcademyHall')
    bk.plinths(asm, W, D)
    zf = 3.0                                 # floor level
    sk = Builder(CASTLE_MATS)                # under-floor lattice skirting between plinth and floor
    for sg in (1, -1):
        sk.box((-W / 2, sg * D / 2 - (0.6 if sg > 0 else 0), PLINTH), (W / 2, sg * D / 2 + (0 if sg > 0 else 0.6), zf), 'Timber_Dark')
        sk.box((sg * W / 2 - (0.6 if sg > 0 else 0), -D / 2, PLINTH), (sg * W / 2 + (0 if sg > 0 else 0.6), D / 2, zf), 'Timber_Dark')
    sk.box((-W / 2 + 0.6, -D / 2 + 0.6, 0.0), (W / 2 - 0.6, D / 2 - 0.6, zf - 0.12), 'Timber_Dark', skip=('-z',))
    sk.box((-W / 2 + 0.6, -D / 2 + 0.6, zf - 0.12), (W / 2 - 0.6, D / 2 - 0.6, zf), 'Wood_Planks', skip=('-z',))
    # veranda (engawa) ring + support posts + front steps
    ev = 2.6
    for sg in (1, -1):
        sk.box((-W / 2 - ev, sg * D / 2 - (0 if sg > 0 else ev), zf - 0.3), (W / 2 + ev, sg * D / 2 + (ev if sg > 0 else 0), zf), 'Wood_Planks')
        sk.box((sg * W / 2 - (0 if sg > 0 else ev), -D / 2, zf - 0.3), (sg * W / 2 + (ev if sg > 0 else 0), D / 2, zf), 'Wood_Planks')
    for x in [-W / 2 - ev + 0.4 + (W + 2 * ev - 0.8) * i / 12 for i in range(13)]:
        for yy in (D / 2 + ev - 0.4, -D / 2 - ev + 0.4):
            sk.beam_box((x - 0.2, yy - 0.2, 0.0), (x + 0.2, yy + 0.2, zf - 0.3), 'Timber_Dark', along='z')
    for i in range(4):
        zt = zf * (i + 1) / 4 - 0.3 * (i == 3)
        sk.box((-3.0, D / 2 + ev + (3 - i) * 0.9, 0.0), (3.0, D / 2 + ev + (4 - i) * 0.9, zt), 'Stone_Fitted' if i == 0 else 'Wood_Planks')
    asm.add('Structure', sk)
    front = lambda m, i, c: wk.wall(m, ['shoji'] * (m // 4)) if m == 12 else wk.wall(m, ['plaster', 'lattice', 'lattice', 'plaster'])
    for side, L, fn, mods in (('front', W, front, [16, 12, 16]),
                              ('back', W, lambda m, i, c: wk.wall(m, ['plaster' if k % 2 == 0 else 'lattice' for k in range(m // 4)]), None),
                              ('right', D, lambda m, i, c: wk.wall(m, ['lattice' if k % 2 == 0 else 'plaster' for k in range(m // 4)]), None),
                              ('left', D, lambda m, i, c: wk.wall(m, ['lattice' if k % 2 == 0 else 'plaster' for k in range(m // 4)]), None)):
        bk.wall_run(asm, 'Structure', L, zf, side, W, D, fn, seed=len(side), mods=mods)
    for sx in (1, -1):
        for sy in (1, -1):
            asm.add('Structure', wk.corner_post(), M(sx * (W / 2 - 0.5), sy * (D / 2 - 0.5), zf))
    # interior
    b = pk.B(); g = Builder(pk.GLOW_MATS)
    x0, x1, y0, y1 = -W / 2 + 1, W / 2 - 1, -D / 2 + 1, D / 2 - 1
    # kamidana shrine shelf on the back wall
    b.box((-3.0, y0, zf + 6.2), (3.0, y0 + 1.4, zf + 6.45), 'Timber_Light')
    b.box((-1.2, y0 + 0.2, zf + 6.45), (1.2, y0 + 1.1, zf + 7.8), 'Timber_Light')
    b.sweep([Vector((-1.5, y0 + 0.65, zf + 7.8)), Vector((1.5, y0 + 0.65, zf + 7.8))],
            [(-0.75, 0.0), (0.75, 0.0), (0.0, 0.55)], 'RoofTile_Clay')
    for sx in (-1, 1):
        b.beam_box((sx * 2.6 - 0.08, y0 + 0.2, zf + 5.2), (sx * 2.6 + 0.08, y0 + 0.36, zf + 6.2), 'Timber_Light', along='z')
    pk.ofuda(b, 0.0, y0 + 1.3, zf + 6.15, n=5, w=4.0)
    # weapon racks along the side walls, practice sword stands, spear racks
    for k, yy in enumerate((-7.0, 0.0, 7.0)):
        for sgn, xw, rot in ((1, x1, -math.pi / 2), (-1, x0, math.pi / 2)):
            wr = pk.B(); pk.wall_sword_rack(wr, 0, 0, 0, swords=3, w=4.0)
            asm.add('Interior', wr, M(xw, yy, zf + 2.2, rot))
    for sgn in (1, -1):
        sr = pk.B(); pk.spear_rack(sr, 0, 0, 0, spears=5, w=5.0)
        asm.add('Interior', sr, M(sgn * 14.0, y0 + 0.8, zf))
    pk.sword_rack(b, -8.0, y0 + 1.4, zf, swords=3); pk.sword_rack(b, 8.0, y0 + 1.4, zf, swords=3)
    # taiko drum on a stand (front right corner)
    tx, ty = x1 - 3.0, y1 - 3.0
    for sx in (-1, 1):
        b.beam_box((tx + sx * 1.3 - 0.15, ty - 0.15, zf), (tx + sx * 1.3 + 0.15, ty + 0.15, zf + 3.4), 'Black_Lacquer', along='z')
    b.beam_box((tx - 1.45, ty - 0.2, zf + 0.3), (tx + 1.45, ty + 0.2, zf + 0.55), 'Black_Lacquer', along='x')
    prof = [(1.0, -0.7), (1.15, -0.35), (1.2, 0.0), (1.15, 0.35), (1.0, 0.7)]
    drum = Builder(CASTLE_MATS)
    lathe(drum, (0, 0, 0), [(r_, z_) for r_, z_ in prof], 14, 'Red_Lacquer', cap_bottom=True, cap_top=True)
    asm.add('Interior', drum, Matrix.Translation((tx, ty, zf + 2.2)) @ Matrix.Rotation(math.pi / 2, 4, 'X'))
    # lanterns in the corners
    for (lx, ly) in ((x0 + 1.2, y0 + 1.2), (x1 - 1.2, y0 + 1.2), (x0 + 1.2, y1 - 1.2)):
        pk.andon(b, g, lx, ly, zf)
    asm.add('Interior', b); asm.add('Glow', g)
    r = Irimoya(W, D, overhang=3.4, gable_overhang=1.2, pitch=0.66, t_gable=0.56)
    asm.add('Roof', r.build(), M(0, 0, zf + FLOOR))
    return bk.finish(asm)
