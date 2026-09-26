"""Parametric Japanese roof generator (irimoya hip-and-gable, kirizuma gable ...).

Design space (Blender): ridge runs along X, building footprint W (X) x D (Y), wall top at z = 0.
Front of the building = +Y (-> Roblox -Z). The roof module sits directly on the wall top: its lowest
point (frieze/plate) is z = 0 and it covers exactly the W x D footprint (outer wall faces), so it snaps
onto any wall assembly of the same footprint.
"""
import math
from mathutils import Vector
from geo import Builder

MATS = ['RoofTile_Clay', 'Timber_Dark', 'Timber_Light', 'Plaster_White', 'Gold_Leaf']


def smoothstep(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


class Irimoya:
    def __init__(self, W, D, overhang=3.0, gable_overhang=1.2, pitch=0.58, concave=0.35, t_gable=0.5,
                 tile_pitch=1.0, course=0.9, lift=None, flare=None, frieze_color='Plaster_White', castle=False,
                 rafter_spacing=0.9, bracket_spacing=4.0):
        self.W, self.D, self.o = W, D, overhang
        self.kb = gable_overhang
        self.Xe, self.Ye = W / 2 + overhang, D / 2 + overhang
        self.tg = t_gable
        self.Xg = self.Xe - self.Ye + t_gable * self.Ye
        self.pitch, self.c = pitch, concave
        self.rise = pitch * self.Ye
        self.T = 0.55                      # slab thickness (tiles + boards)
        self.tp, self.course = tile_pitch, course
        self.A = lift if lift is not None else 0.085 * self.Ye
        self.B = flare if flare is not None else 0.05 * self.Ye
        self.R = 0.6 * self.Ye
        self.rh = 0.32                     # rafter height
        self.rw = 0.26
        self.castle = castle
        self.rafter_spacing = rafter_spacing
        self.bracket_spacing = bracket_spacing
        self.frieze_mat = frieze_color
        self.L = math.hypot(self.Ye, self.rise)
        # choose eave height so the bracket arms sit comfortably above the wall top
        self.ze = 0.0
        arm_bottom = self._purlin_top(1.0) - 0.5 - 0.25 - 0.5
        self.ze = 1.05 - arm_bottom
        self.b = Builder(MATS)

    # ------------------------------------------------------------------------------ surface functions
    def H(self, t):
        """Tile surface height at slope parameter t (0 ridge .. 1 eave)."""
        u = 1 - t
        return self.ze + self.rise * (u * (1 - self.c) + self.c * u * u)

    def t_of_d(self, d):
        """Slope parameter at horizontal distance d outside the footprint line (long side)."""
        return (self.D / 2 + d) / self.Ye

    def zu(self, d):
        return self.H(self.t_of_d(d)) - self.T

    def _purlin_top(self, d):
        return self.zu(d) - self.rh

    def saw(self, t):
        """Tile-course step offset (0 .. step), courses aligned to the eave."""
        s = (1 - t) * self.L
        f = (s / self.course) % 1.0
        return 0.07 * (1 - f)

    def long(self, a, t, sign=1):
        return Vector((a, sign * t * self.Ye, self.H(t)))

    def hip(self, a, t, sign=1):
        return Vector((sign * (self.Xe - self.Ye + t * self.Ye), a, self.H(t)))

    def lift_fn(self, co):
        W2, D2, o = self.W / 2, self.D / 2, self.o
        dout = max(abs(co.x) - W2, abs(co.y) - D2)
        w = smoothstep(dout / o)
        if w <= 0: return co
        sx = min(1, max(0, (abs(co.x) - (self.Xe - self.R)) / self.R))
        sy = min(1, max(0, (abs(co.y) - (self.Ye - self.R)) / self.R))
        k = (sx * sy) ** 1.5 * w
        return Vector((co.x + math.copysign(self.B * k, co.x), co.y + math.copysign(self.B * k, co.y),
                       co.z + self.A * k))

    # ------------------------------------------------------------------------------ slabs (tile sheets)
    def slab(self, mapping, t0, t1, a_ext, n_across):
        """Closed tile slab. mapping(a,t)->Vector; a_ext(t)->(amin,amax). Top = stepped tile courses, bottom = boards."""
        b = self.b
        c, step = self.course, 0.07
        s_lo, s_hi = (1 - t1) * self.L, (1 - t0) * self.L        # distance up-slope from the eave
        marks = [s_lo]
        k = math.floor(s_lo / c + 1e-6) + 1
        while k * c < s_hi - 1e-4:
            marks.append(k * c); k += 1
        marks.append(s_hi)

        def off_start(sv):
            f = (sv / c) % 1.0
            if f > 1 - 1e-6: f = 0.0
            return step * (1 - f)

        def off_end(sv):
            f = (sv / c) % 1.0
            if f < 1e-6: f = 1.0
            return step * (1 - f)
        samples = []
        for i in range(len(marks) - 1):
            samples.append((1 - marks[i] / self.L, off_start(marks[i])))
            samples.append((1 - marks[i + 1] / self.L, off_end(marks[i + 1])))
        tv, bv, info = [], [], []
        for t, ov in samples:
            amin, amax = a_ext(t)
            arow = [amin + (amax - amin) * j / n_across for j in range(n_across + 1)]
            tv.append([b.bm.verts.new(mapping(a, t) + Vector((0, 0, ov))) for a in arow])
            bv.append([b.bm.verts.new(mapping(a, t) - Vector((0, 0, self.T))) for a in arow])
            info.append((t, arow))
        up = Vector((0, 0, 1))
        amid = 0.5 * sum(a_ext(0.5 * (t0 + t1)))
        eave_dir = mapping(amid, t1) - mapping(amid, t0); eave_dir.z = 0; eave_dir.normalize()
        for i in range(len(tv) - 1):
            ta, tb = info[i][0], info[i + 1][0]
            same = abs(ta - tb) < 1e-7
            for j in range(n_across):
                q = [tv[i][j], tv[i][j + 1], tv[i + 1][j + 1], tv[i + 1][j]]
                uv = [(info[i][1][j] * 0.25, (1 - ta) * self.L * 0.25), (info[i][1][j + 1] * 0.25, (1 - ta) * self.L * 0.25),
                      (info[i + 1][1][j + 1] * 0.25, (1 - tb) * self.L * 0.25 + (0.018 if same else 0)),
                      (info[i + 1][1][j] * 0.25, (1 - tb) * self.L * 0.25 + (0.018 if same else 0))]
                b.face(q, 'RoofTile_Clay', uv, out=eave_dir if same else up)
                if not same:
                    qb = [bv[i][j], bv[i][j + 1], bv[i + 1][j + 1], bv[i + 1][j]]
                    b.face(qb, 'Timber_Light', uv, out=-up)
        # eave edge + ridge edge
        for row, out, mat in ((0, eave_dir, 'RoofTile_Clay'), (len(tv) - 1, -eave_dir, 'Timber_Dark')):
            for j in range(n_across):
                q = [tv[row][j], tv[row][j + 1], bv[row][j + 1], bv[row][j]]
                a0, a1 = info[row][1][j] * 0.25, info[row][1][j + 1] * 0.25
                b.face(q, mat, [(a0, 0.14), (a1, 0.14), (a1, 0), (a0, 0)], out=out)
        # sides
        for col in (0, n_across):
            for k in range(len(tv) - 1):
                ta, tb = info[k][0], info[k + 1][0]
                if abs(ta - tb) < 1e-7:
                    f = [tv[k][col], tv[k + 1][col], bv[k][col]]
                    bv[k + 1][col].co = bv[k][col].co.copy()
                else:
                    f = [tv[k][col], tv[k + 1][col], bv[k + 1][col], bv[k][col]]
                ctr = sum((v.co for v in f), Vector()) / len(f)
                o = ctr - mapping(0.5 * (info[k][1][0] + info[k][1][-1]), ta); o.z = 0
                s0 = (1 - ta) * self.L * 0.25
                s1 = (1 - tb) * self.L * 0.25
                uvs = [(s0, 0.14), (s1, 0.14), (s1, 0), (s0, 0)][:len(f)] if len(f) == 4 else [(s0, 0.14), (s1, 0.14), (s0, 0)]
                b.face(f, 'Timber_Dark', uvs, out=o)

    # ------------------------------------------------------------------------------ tile rows
    def cover_row(self, mapping, a, t0, t1, eave_disc=True):
        """Round cover-tile row (marugawara): half-round profile on the pan courses, disc end tile at the eave."""
        b = self.b
        if t1 - t0 < 0.02: return
        r = 0.22
        n = max(2, int(math.ceil((t1 - t0) * self.L / 2.2)))
        ts = [t0 + (t1 - t0) * i / n for i in range(n + 1)]
        path = [mapping(a, t) + Vector((0, 0, 0.04)) for t in ts]
        prof = [(r * math.cos(math.pi * i / 3), r * math.sin(math.pi * i / 3)) for i in range(4)]
        prof = prof + [(-r, -0.07), (r, -0.07)]
        # sides 0..2 = arc (smooth), 3 = left lip, 4 = bottom (hidden, skipped), 5 = right lip
        b.sweep(path, prof, 'RoofTile_Clay', smooth=True, smooth_sides={0, 1, 2}, skip_sides=(4,), caps=True)
        if eave_disc and t1 > 0.999:
            d = (path[-1] - path[-2]).normalized()
            c0, c1 = path[-1] - d * 0.02, path[-1] + d * 0.12
            rr = 0.3
            prof = [(rr * math.cos(2 * math.pi * i / 6 + math.pi / 6), rr * math.sin(2 * math.pi * i / 6 + math.pi / 6) + 0.02)
                    for i in range(6)]
            b.sweep([c0, c1], prof, 'RoofTile_Clay', smooth=True)

    # ------------------------------------------------------------------------------ ridges
    def ridge_profile(self, s=1.0, cap=True):
        w = 0.46 * s
        pts = [(w, -0.35 * s)]
        y = 0.0
        for k in range(3):
            x = w - 0.035 * k * s
            pts += [(x, y + 0.2 * s)]
            if k < 2: pts += [(x - 0.035 * s, y + 0.2 * s)]
            y += 0.2 * s
        rc = 0.3 * s
        top = y
        for i in range(0, 7):
            ang = math.pi * i / 6
            pts.append((rc * math.cos(ang), top + rc * math.sin(ang)))
        right = pts[:]
        left = [(-x, y) for x, y in reversed(right[1:-7])]
        prof = right + left + [(-w, -0.35 * s)]
        # dedupe consecutive
        out = []
        for p in prof:
            if not out or (abs(out[-1][0] - p[0]) > 1e-6 or abs(out[-1][1] - p[1]) > 1e-6):
                out.append(p)
        return out

    def ridge(self, path, s=1.0):
        prof = self.ridge_profile(s)
        n = len(prof)
        arc = set(range(n - 1))
        self.b.sweep(path, prof, 'RoofTile_Clay', smooth=False, caps=True)

    def onigawara(self, base, facing, s=1.0, tilt=0.0):
        """Demon end tile: arched plate with flared wings, raised rim and a boss, facing `facing` (horizontal)."""
        b = self.b
        f = Vector(facing).normalized()
        up = Vector((0, 0, 1))
        if tilt:
            f = (f * math.cos(tilt) + up * math.sin(tilt)).normalized()
        side = f.cross(Vector((0, 0, 1))).normalized()
        upv = side.cross(f).normalized()
        outline = [(-0.95, 0), (0.95, 0), (0.95, 0.28), (0.62, 0.5), (0.62, 1.05)]
        for i in range(1, 8):
            ang = math.pi * i / 8
            outline.append((0.62 * math.cos(ang), 1.05 + 0.62 * math.sin(ang)))
        outline += [(-0.62, 1.05), (-0.62, 0.5), (-0.95, 0.28)]
        outline = [(u * s, v * s) for u, v in outline]
        base = Vector(base)
        # plate body (depth along -f from front face)
        b.prism(outline, base - f * 0.5 * s, side, upv, f, 0.5 * s, 'RoofTile_Clay')
        # raised inner rim/face
        inner = [(u * 0.72, v * 0.72 + 0.14 * s) for u, v in outline[3:-2]]
        inner = [(outline[3][0] * 0.72, 0.36 * s)] + inner + [(outline[-3][0] * 0.72, 0.36 * s)]
        b.prism(inner, base, side, upv, f, 0.1 * s, 'RoofTile_Clay', back=False)
        # boss
        c = base + upv * 1.02 * s + f * 0.1 * s
        b.cylinder(c, c + f * 0.14 * s, 0.24 * s, 8, 'RoofTile_Clay')
        # small horns
        for sg in (-1, 1):
            p = base + side * (sg * 0.3 * s) + upv * 1.62 * s - f * 0.1 * s
            b.sweep([p, p + upv * 0.35 * s + side * sg * 0.18 * s], [(-0.08 * s, -0.08 * s), (0.08 * s, -0.08 * s),
                    (0.08 * s, 0.08 * s), (-0.08 * s, 0.08 * s)], 'RoofTile_Clay', up=f)

    # ------------------------------------------------------------------------------ build
    def build(self):
        b = self.b
        W2, D2, Xe, Ye, Xg, kb, tg = self.W / 2, self.D / 2, self.Xe, self.Ye, self.Xg, self.kb, self.tg
        XgK = Xg + kb
        # ---------------- tile slabs
        for sg in (1, -1):
            m_long = lambda a, t, sg=sg: self.long(a, t, sg)
            m_hip = lambda a, t, sg=sg: self.hip(a, t, sg)
            # long side, upper (gable roof part incl. kera overhang)
            self.slab(m_long, 0.0, tg, lambda t: (-XgK, XgK), max(4, int(2 * XgK / 1.6)))
            # long side, lower trapezoid (hip-cut)
            self.slab(m_long, tg, 1.0, lambda t: (-(Xe - Ye + t * Ye), Xe - Ye + t * Ye), max(6, int(2 * Xe / 1.4)))
            # hip end
            self.slab(m_hip, tg, 1.0, lambda t: (-t * Ye, t * Ye), max(4, int(2 * Ye / 1.4)))
        # ---------------- cover tile rows
        p = self.tp
        n_long = int(Xe / p) + 1
        for sg in (1, -1):
            m_long = lambda a, t, sg=sg: self.long(a, t, sg)
            m_hip = lambda a, t, sg=sg: self.hip(a, t, sg)
            for i in range(-n_long, n_long):
                a = (i + 0.5) * p
                A = abs(a)
                if A <= Xg - 0.1:
                    self.cover_row(m_long, a, 0.0, 1.0)
                else:
                    if A <= XgK - 0.3:
                        self.cover_row(m_long, a, 0.0, tg, eave_disc=False)
                    th = (A - (Xe - Ye)) / Ye
                    if th < 0.97:
                        self.cover_row(m_long, a, th + 0.02, 1.0)
            n_hip = int(Ye / p) + 1
            for i in range(-n_hip, n_hip):
                a = (i + 0.5) * p
                t0 = max(tg + 0.03, abs(a) / Ye + 0.02)
                if t0 < 0.97:
                    self.cover_row(m_hip, a, t0, 1.0)
        # ---------------- ridges
        rs = 1.0 + 0.15 * (self.Ye / 11 - 1)
        top = [Vector((x, 0, self.H(0) + 0.02)) for x in [-(XgK + 0.15) + (2 * (XgK + 0.15)) * i / 8 for i in range(9)]]
        self.ridge(top, s=rs * 1.25)
        for sg in (1, -1):
            for sy in (1, -1):
                # descending gable-edge ridge along the kera edge
                path = [Vector((sg * (XgK - 0.25), sy * t * Ye, self.H(t) + 0.02)) for t in [0.04 + (tg + 0.03 - 0.04) * i / 5 for i in range(6)]]
                self.ridge(path, s=rs * 0.9)
                # corner hip ridge along the hip line
                path = [Vector((sg * (Xe - Ye + t * Ye), sy * t * Ye, self.H(t) + 0.02)) for t in [tg + (1.0 - tg) * i / 10 for i in range(11)]]
                path[-1] += (path[-1] - path[-2]).normalized() * 0.3
                self.ridge(path, s=rs * 0.85)
            # ridge along the pediment base
            path = [Vector((sg * (Xg + 0.3), y, self.H(tg) - 0.05)) for y in [-tg * Ye + 2 * tg * Ye * i / 6 for i in range(7)]]
            self.ridge(path, s=rs * 0.75)
        # ---------------- onigawara
        for sg in (1, -1):
            self.onigawara(Vector((sg * (XgK + 0.3), 0, self.H(0) - 0.1)), (sg, 0, 0), s=rs * 1.05)
            for sy in (1, -1):
                t = 1.0
                pe = Vector((sg * (Xe + 0.15), sy * (Ye + 0.15), self.H(1.0) + 0.05))
                self.onigawara(pe, (sg, sy, 0), s=rs * 0.6, tilt=math.radians(12))
                pk = Vector((sg * (XgK - 0.25), sy * (tg + 0.05) * Ye, self.H(tg + 0.05) - 0.05))
                self.onigawara(pk, (0, sy, 0), s=rs * 0.5)
        # ---------------- pediment (plaster + timber lattice), hafu boards, gegyo
        for sg in (1, -1):
            zb = self.H(tg)
            ys = [-tg * Ye + 2 * tg * Ye * i / 12 for i in range(13)]
            outline = [(y, zb) for y in (-tg * Ye, tg * Ye)]
            outline += [(y, self.H(abs(y) / Ye) - self.T + 0.02) for y in reversed(ys)]
            origin = Vector((sg * (Xg - 0.4) if sg > 0 else -(Xg - 0.4), 0, 0))
            b.prism(outline, Vector((sg * (Xg - 0.45), 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)),
                    Vector((sg, 0, 0)), 0.45, 'Plaster_White', uvd=0.25)
            # timber members on the gable face
            xf = sg * Xg
            def zt(y): return self.H(abs(y) / Ye) - self.T
            yw = tg * Ye
            b.box((min(xf, xf + sg * 0.12), -yw, zb), (max(xf, xf + sg * 0.12), yw, zb + 0.45), 'Timber_Dark')
            for zl in (zb + 2.0,):
                if zl + 0.35 > self.H(0) - self.T - 0.4: continue
                # width available at that height
                tt = 1 - ((zl + 0.35 - self.ze + self.T) / self.rise)
                # solve H(t)-T = zl+0.35 numerically
                lo_, hi_ = 0.0, tg
                for _ in range(30):
                    mid = (lo_ + hi_) / 2
                    if self.H(mid) - self.T > zl + 0.35: lo_ = mid
                    else: hi_ = mid
                yy = lo_ * Ye - 0.05
                b.box((min(xf, xf + sg * 0.12), -yy, zl), (max(xf, xf + sg * 0.12), yy, zl + 0.35), 'Timber_Dark')
            nst = max(2, int(2 * yw / 2.2))
            for i in range(1, nst):
                y = -yw + 2 * yw * i / nst
                b.box((min(xf, xf + sg * 0.1), y - 0.12, zb + 0.45), (max(xf, xf + sg * 0.1), y + 0.12, zt(y) - 0.02),
                      'Timber_Dark')
            # hafu (barge) boards under the kera edges, both slopes
            for sy in (1, -1):
                ts = [0.0 + (tg + 0.04) * i / 8 for i in range(9)]
                path = [Vector((sg * (XgK - 0.18), sy * t * Ye, self.H(t))) for t in ts]
                path[0] = Vector((sg * (XgK - 0.18), 0, self.H(0)))
                b.sweep(path, [(-0.18, -self.T - 0.42), (0.18, -self.T - 0.42), (0.18, 0.06), (-0.18, 0.06)],
                        'Timber_Dark', caps=True)
                # gold nail covers (kugikakushi)
                for t in (0.12, 0.24, 0.36):
                    c = Vector((sg * (XgK - 0.18 + 0.2), sy * t * Ye, self.H(t) - self.T - 0.1))
                    b.box((min(c.x, c.x + sg * 0.07), c.y - 0.18, c.z - 0.22), (max(c.x, c.x + sg * 0.07), c.y + 0.18, c.z + 0.02),
                          'Gold_Leaf')
            # gegyo (hanging gable ornament), gold
            zt0 = self.H(0) - self.T
            out = [(-0.55, 0.0), (-0.9, -0.35), (-0.65, -0.75), (-0.3, -0.6), (0.0, -1.1), (0.3, -0.6), (0.65, -0.75),
                   (0.9, -0.35), (0.55, 0.0)]
            out = [(u, v * 1.1 + 0.05) for u, v in out]
            b.prism([(u, v + zt0 - 0.55) for u, v in out], Vector((sg * (XgK - 0.02), 0, 0)), Vector((0, 1, 0)),
                    Vector((0, 0, 1)), Vector((sg, 0, 0)), 0.16, 'Gold_Leaf')
        # ---------------- eave structure: fascia, rafters, corner beams, purlin, brackets, frieze, ceiling
        o = self.o
        rh, rw = self.rh, self.rw
        # fascia board ring under the slab edge
        zf = self.H(1.0) - self.T
        for sg in (1, -1):
            b.beam(Vector((-Xe, sg * (Ye - 0.2), zf)), Vector((Xe, sg * (Ye - 0.2), zf)), 0.3, 0.34, 'Timber_Dark',
                   nseg=16, anchor='top')
            b.beam(Vector((sg * (Xe - 0.2), -Ye, zf)), Vector((sg * (Xe - 0.2), Ye, zf)), 0.3, 0.34, 'Timber_Dark',
                   nseg=12, anchor='top')
        # rafters
        sp = self.rafter_spacing
        def rafter(mapping, a, tA, tB, nseg):
            pts = []
            for i in range(nseg + 1):
                t = tA + (tB - tA) * i / nseg
                q = mapping(a, t); q.z -= self.T
                pts.append(q)
            b.beam(None, None, rw, rh, 'Timber_Dark', path=pts, anchor='top', skip=('top',))
        t_in = (D2 - 0.6) / Ye
        t_out = 1 - 0.3 / Ye
        for sg in (1, -1):
            n = int(Xe / sp) + 1
            for i in range(-n, n + 1):
                a = i * sp
                A = abs(a)
                ts = max(t_in, (A - (W2 - D2)) / Ye + 0.03)   # hip diagonal in plan
                if ts < t_out - 0.02:
                    self.rafter_fn = rafter(lambda aa, t, sg=sg: self.long(aa, t, sg), a, ts, t_out, 3)
            n = int(Ye / sp) + 1
            for i in range(-n, n + 1):
                a = i * sp
                ts = max(t_in, abs(a) / Ye + 0.03)
                if ts < t_out - 0.02:
                    rafter(lambda aa, t, sg=sg: self.hip(aa, t, sg), a, ts, t_out, 3)
        # corner beams (sumigi) along the hip diagonal
        for sg in (1, -1):
            for sy in (1, -1):
                pts = []
                for i in range(7):
                    t = t_in + (1.0 + 0.04 - t_in) * i / 6
                    q = Vector((sg * (Xe - Ye + t * Ye), sy * t * Ye, self.H(t) - self.T))
                    pts.append(q)
                b.beam(None, None, 0.5, 0.62, 'Timber_Dark', path=pts, anchor='top')
                if self.castle:
                    d = (pts[-1] - pts[-2]).normalized()
                    c = pts[-1]
                    side = d.cross(Vector((0, 0, 1))).normalized()
                    upv = side.cross(d)
                    b.sweep([c - d * 0.02, c + d * 0.1],
                            [(-0.28, -0.66), (0.28, -0.66), (0.28, 0.04), (-0.28, 0.04)], 'Gold_Leaf')
        # eave purlin (dashigeta) at d = 1.0
        zp = self._purlin_top(1.0)
        for sg in (1, -1):
            b.beam(Vector((-(W2 + 1.25), sg * (D2 + 1.0), zp)), Vector((W2 + 1.25, sg * (D2 + 1.0), zp)), 0.5, 0.5,
                   'Timber_Dark', nseg=14, anchor='top')
            b.beam(Vector((sg * (W2 + 1.0), -(D2 + 1.25), zp)), Vector((sg * (W2 + 1.0), D2 + 1.25, zp)), 0.5, 0.5,
                   'Timber_Dark', nseg=10, anchor='top')
        # frieze ring on the wall top (plaster between plate beams), top flush with slab underside
        zfr = self.zu(0.0)
        th = 1.0
        for sg in (1, -1):
            b.box((-W2, sg * D2 - (th if sg > 0 else 0), 0), (W2, sg * D2 + (0 if sg > 0 else th), zfr), self.frieze_mat,
                  uvd=0.25)
            b.box((sg * W2 - (th if sg > 0 else 0), -D2 + th, 0), (sg * W2 + (0 if sg > 0 else th), D2 - th, zfr),
                  self.frieze_mat, uvd=0.25)
            # plate beam (keta) band, slightly proud, at the bottom and top of the frieze
            for z0, z1 in ((0.0, 0.6), (zfr - 0.45, zfr - 0.02)):
                b.box((-W2 - 0.1, sg * D2 - (0.2 if sg > 0 else -0.1) - (0 if sg > 0 else 0.3), z0),
                      (W2 + 0.1, sg * D2 + (0.1 if sg > 0 else 0.2) - (0 if sg > 0 else 0.0), z1), 'Timber_Dark')
                b.box((sg * W2 - (0.2 if sg > 0 else -0.1) - (0 if sg > 0 else 0.3), -D2, z0),
                      (sg * W2 + (0.1 if sg > 0 else 0.2), D2, z1), 'Timber_Dark')
        # ceiling closing the module from below
        b.box((-W2 + th - 0.01, -D2 + th - 0.01, 0.35), (W2 - th + 0.01, D2 - th + 0.01, 0.6), 'Timber_Light')
        # brackets: post-head blocks + boat-shaped arms carrying the purlin (every bracket_spacing studs)
        zpb = zp - 0.5       # purlin bottom
        def bracket(pos, out_dir, along):
            out_dir = Vector(out_dir); along = Vector(along)
            arm = [(-0.3, zpb - 0.72), (0.75, zpb - 0.72), (1.45, zpb - 0.42), (1.45, zpb - 0.25), (-0.3, zpb - 0.25)]
            b.prism([(u, v) for u, v in arm], Vector(pos) - along * 0.2, out_dir, Vector((0, 0, 1)), along, 0.4,
                    'Timber_Dark')
            # masu bearing block under purlin
            c = Vector(pos) + out_dir * 1.0
            lo = c - out_dir * 0.32 - along * 0.32
            hi = c + out_dir * 0.32 + along * 0.32
            b.box((min(lo.x, hi.x), min(lo.y, hi.y), zpb - 0.25), (max(lo.x, hi.x), max(lo.y, hi.y), zpb), 'Timber_Dark')
            # post-head block on the frieze
            lo = Vector(pos) - along * 0.35
            hi = Vector(pos) + along * 0.35 + out_dir * 0.18
            b.box((min(lo.x, hi.x), min(lo.y, hi.y), zpb - 1.1), (max(lo.x, hi.x), max(lo.y, hi.y), zpb - 0.72),
                  'Timber_Dark')
        bs = self.bracket_spacing
        for sg in (1, -1):
            nx = int(round(self.W / bs))
            for i in range(1, nx):
                x = -W2 + i * bs
                bracket((x, sg * D2, 0), (0, sg, 0), (1, 0, 0))
            ny = int(round(self.D / bs))
            for i in range(1, ny):
                y = -D2 + i * bs
                bracket((sg * W2, y, 0), (sg, 0, 0), (0, 1, 0))
        # ---------------- corner upturn (sori) + flare
        b.deform(self.lift_fn)
        b.mark_sharp()
        return b


class Kirizuma(Irimoya):
    """Plain gable roof (machiya style): eaves on the long (front/back) sides only, straight eaves,
    full plaster gable walls on the ends, barge boards, no brackets (rafters sit on the wall plate)."""

    def __init__(self, W, D, overhang=2.0, gable_overhang=1.0, pitch=0.62, concave=0.25, **kw):
        super().__init__(W, D, overhang=overhang, gable_overhang=gable_overhang, pitch=pitch, concave=concave,
                         lift=0.0, flare=0.0, **kw)
        # machiya: low frieze, eave underside ~0.5 above the wall top at the eave line
        self.ze = 0.0
        self.ze = 0.55 - (self.H(1.0) - self.T) + 0.34 + 0.35

    def build(self):
        b = self.b
        W2, D2, Ye, kb = self.W / 2, self.D / 2, self.Ye, self.kb
        XK = W2 + kb
        for sg in (1, -1):
            m = lambda a, t, sg=sg: self.long(a, t, sg)
            self.slab(m, 0.0, 1.0, lambda t: (-XK, XK), max(4, int(2 * XK / 1.6)))
            n = int(XK / self.tp)
            for i in range(-n, n):
                a = (i + 0.5) * self.tp
                if abs(a) <= XK - 0.35:
                    self.cover_row(m, a, 0.0, 1.0)
        rs = 1.0 + 0.15 * (Ye / 11 - 1)
        self.ridge([Vector((x, 0, self.H(0) + 0.02)) for x in [-(XK + 0.1) + 2 * (XK + 0.1) * i / 8 for i in range(9)]],
                   s=rs * 1.1)
        for sg in (1, -1):
            self.onigawara(Vector((sg * (XK + 0.25), 0, self.H(0) - 0.1)), (sg, 0, 0), s=rs * 0.9)
            for sy in (1, -1):
                path = [Vector((sg * (XK - 0.25), sy * t * Ye, self.H(t) + 0.02)) for t in [0.04 + 0.96 * i / 8 for i in range(9)]]
                path[-1] += (path[-1] - path[-2]).normalized() * 0.15
                self.ridge(path, s=rs * 0.75)
                self.onigawara(path[-1] + Vector((0, sy * 0.05, -0.1)), (0, sy, 0), s=rs * 0.45)
                # barge board
                ts = [1.0 * i / 8 for i in range(9)]
                bp = [Vector((sg * (XK - 0.18), sy * t * Ye, self.H(t))) for t in ts]
                b.sweep(bp, [(-0.16, -self.T - 0.38), (0.16, -self.T - 0.38), (0.16, 0.05), (-0.16, 0.05)],
                        'Timber_Dark')
        # gable end walls (plaster triangle on the end walls) with tie beam + king post
        zu0 = self.zu(0.0)
        for sg in (1, -1):
            ys = [-D2 + self.D * i / 10 for i in range(11)]
            outline = [(-D2, 0.0), (D2, 0.0)] + [(y, self.H(abs(y) / Ye) - self.T + 0.02) for y in reversed(ys)]
            b.prism(outline, Vector((sg * (W2 - 1.0) if sg > 0 else -(W2 - 1.0), 0, 0)) if False else
                    Vector((sg * W2 - (1.0 if sg > 0 else -1.0), 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)),
                    Vector((sg, 0, 0)), 1.0, 'Plaster_White')
            xf = sg * W2
            lo = lambda y0, z0: (min(xf, xf + sg * 0.12), y0, z0)
            hi = lambda y1, z1: (max(xf, xf + sg * 0.12), y1, z1)
            b.box(lo(-D2 - 0.05, 0.0), hi(D2 + 0.05, 0.55), 'Timber_Dark')            # wall plate
            b.box(lo(-D2 * 0.72, zu0 + 0.6), hi(D2 * 0.72, zu0 + 0.95), 'Timber_Dark')  # tie beam
            b.box(lo(-0.18, 0.55), hi(0.18, self.H(0) - self.T - 0.02), 'Timber_Dark')  # king post
            for sy in (1, -1):
                b.box(lo(sy * D2 - (0.36 if sy > 0 else 0), 0.55) if sy > 0 else lo(-D2, 0.55),
                      hi(D2, zu0) if sy > 0 else hi(-D2 + 0.36, zu0), 'Timber_Dark')   # corner posts
        # long-side wall plate + frieze (short) under the eaves
        for sg in (1, -1):
            y0, y1 = (D2 - 1.0, D2) if sg > 0 else (-D2, -D2 + 1.0)
            b.box((-W2 + 1.0, y0, 0), (W2 - 1.0, y1, zu0), 'Plaster_White')
            yo0, yo1 = (D2 - 0.2, D2 + 0.12) if sg > 0 else (-D2 - 0.12, -D2 + 0.2)
            b.box((-W2 - 0.1, yo0, 0.0), (W2 + 0.1, yo1, 0.6), 'Timber_Dark')
        b.box((-W2 + 1.0, -D2 + 1.0, 0.3), (W2 - 1.0, D2 - 1.0, 0.55), 'Timber_Light')   # ceiling
        # rafters + fascia on the long sides
        t_in, t_out = (D2 - 0.6) / Ye, 1 - 0.3 / Ye
        zf = self.H(1.0) - self.T
        for sg in (1, -1):
            m = lambda a, t, sg=sg: self.long(a, t, sg)
            n = int(XK / self.rafter_spacing)
            for i in range(-n, n + 1):
                a = i * self.rafter_spacing
                pts = []
                for k in range(3):
                    t = t_in + (t_out - t_in) * k / 2
                    q = m(a, t); q.z -= self.T; pts.append(q)
                b.beam(None, None, self.rw, self.rh, 'Timber_Dark', path=pts, anchor='top', skip=('top',))
            b.beam(Vector((-XK + 0.2, sg * (Ye - 0.2), zf)), Vector((XK - 0.2, sg * (Ye - 0.2), zf)), 0.3, 0.32,
                   'Timber_Dark', anchor='top')
        b.mark_sharp()
        return b


class Hisashi(Irimoya):
    """Pent roof / shop awning (hisashi). Back edge (Blender -Y) mounts flush against a wall face;
    tiles slope down toward the front (+Y). Supported by cantilever beams (dashibari) every 4 studs."""

    def __init__(self, W, P=3.0, pitch=0.45, concave=0.15, end_ridges=True, **kw):
        super().__init__(W, 2 * P, overhang=0.0, gable_overhang=0.0, pitch=pitch, concave=concave, lift=0.0,
                         flare=0.0, **kw)
        self.P = P
        self.Ye = P
        self.rise = pitch * P
        self.L = math.hypot(P, self.rise)
        self.T = 0.45
        self.ze = 0.0
        self.end_ridges = end_ridges

    def long(self, a, t, sign=1):
        return Vector((a, t * self.P, self.ze + self.rise * (1 - t) * (1 - self.c * t) + 1.1))

    def build(self):
        b = self.b
        W2, P = self.W / 2, self.P
        m = lambda a, t: self.long(a, t)
        self.slab(m, 0.0, 1.0, lambda t: (-W2, W2), max(3, int(self.W / 1.6)))
        n = int(W2 / self.tp)
        for i in range(-n, n):
            a = (i + 0.5) * self.tp
            if abs(a) <= W2 - 0.3:
                self.cover_row(m, a, 0.02, 1.0)
        # wall flashing ridge along the back edge
        top = m(0, 0)
        self.ridge([Vector((x, 0.25, top.z - 0.05)) for x in [-W2 + self.W * i / 6 for i in range(7)]], s=0.62)
        # back board (closes the module against the wall)
        zt = top.z
        b.box((-W2, -0.02, 0.0), (W2, 0.2, zt + 0.25), 'Timber_Dark')
        # end ridges + barge boards
        for sg in (1, -1):
            if self.end_ridges:
                path = [m(sg * (W2 - 0.22), t) + Vector((0, 0, 0.02)) for t in [0.06 + 0.94 * i / 5 for i in range(6)]]
                self.ridge(path, s=0.55)
            bp = [m(sg * (W2 - 0.12), t) for t in [i / 5 for i in range(6)]]
            b.sweep(bp, [(-0.12, -self.T - 0.25), (0.12, -self.T - 0.25), (0.12, 0.04), (-0.12, 0.04)], 'Timber_Dark')
        # rafters, fascia
        zf = m(0, 1).z - self.T
        for i in range(int(self.W / self.rafter_spacing) + 1):
            a = -W2 + 0.3 + (self.W - 0.6) * i / int(self.W / self.rafter_spacing)
            pts = [m(a, t) - Vector((0, 0, self.T)) for t in (0.04, 0.5, 1 - 0.25 / P)]
            b.beam(None, None, self.rw * 0.9, self.rh * 0.85, 'Timber_Dark', path=pts, anchor='top', skip=('top',))
        b.beam(Vector((-W2, P - 0.18, zf)), Vector((W2, P - 0.18, zf)), 0.26, 0.3, 'Timber_Dark', anchor='top')
        # eave beam + cantilever beams (dashibari) every 4 studs, incl. the ends
        zb = m(0, 0.72).z - self.T - self.rh
        b.beam(Vector((-W2, 0.72 * P, zb)), Vector((W2, 0.72 * P, zb)), 0.38, 0.38, 'Timber_Dark', anchor='top')
        k = int(round(self.W / 4))
        for i in range(k + 1):
            x = -W2 + 0.25 + (self.W - 0.5) * i / k
            arm = [(0.0, zb - 1.0), (0.4, zb - 1.0), (0.72 * P + 0.35, zb - 0.62), (0.72 * P + 0.35, zb - 0.38),
                   (0.0, zb - 0.38 + 0.0)]
            b.prism(arm, Vector((x - 0.17, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)), Vector((1, 0, 0)), 0.34,
                    'Timber_Dark')
            # arm top reaches the eave beam: small bearing block
            b.box((x - 0.2, 0.72 * P - 0.2, zb - 0.38), (x + 0.2, 0.72 * P + 0.2, zb), 'Timber_Dark')
        # drop the whole module so its lowest point is z = 0
        zmin = min(v.co.z for v in b.bm.verts)
        for v in b.bm.verts: v.co.z -= zmin
        b.mark_sharp()
        return b
