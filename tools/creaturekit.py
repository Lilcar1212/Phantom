"""Hero creature: ancient Eastern water dragon (Roblox-ready, rigged).

Long, straight bind pose: four clawed legs planted, body and very long tail on one straight line, neck reaching
forward to a large sculpted head, crystalline water fins at the tail tip.

Pieces (each its own mesh, each split per texture set on export, each < 20k tris):
  Head, Jaw, Horns, Eyes, Whiskers, Mane, Neck, Body, Tail, Limbs, Claws, Fins, WaterFX
Solid creature materials: Dragon_Scales, Dragon_Belly, Dragon_Horn, Dragon_Fin (crystal), Dragon_Claw, Dragon_Eye.
Only WaterFX uses the translucent Water_Flame set.

Rig (bones): Root; Spine01-04 (hips -> shoulders); Neck01-04; Head; Jaw; Tail01-16 (hips -> tip);
FL/FR/RL/RR _Upper/_Lower/_Foot.  Skin weights are computed from each vertex's position along the spine
(neck/body/tail/fins/water/mane), rigidly for head pieces and the jaw, and by nearest segment for limbs and claws.

Blender axes: front = +Y (Roblox -Z), up = +Z, feet on z = 0, origin between the front feet.
"""
import math, random
from mathutils import Vector, Matrix, noise
from geo import Builder, tube
from harborkit import blob
from dragonkit import ribbon, cone

MATS = ['Dragon_Scales', 'Dragon_Belly', 'Dragon_Horn', 'Dragon_Fin', 'Dragon_Claw', 'Dragon_Eye', 'Water_Flame']
Z = Vector((0, 0, 1))
PIECES = ['Head', 'Jaw', 'Horns', 'Eyes', 'Whiskers', 'Mane', 'Neck', 'Body', 'Tail', 'Limbs', 'Claws', 'Fins', 'WaterFX']


def B():
    return Builder(MATS)


# ------------------------------------------------------------------------------------------------ spine
# control points tail tip -> head base: (x, y, z, radius)
# long, straight bind pose: body and tail on one line along Y, neck reaching forward with a gentle rise
CTRL = [(0.0, -62.0, 6.9, 0.14), (0.0, -56.0, 7.0, 0.36), (0.0, -50.0, 7.1, 0.56), (0.0, -44.0, 7.2, 0.78),
        (0.0, -38.0, 7.3, 1.0), (0.0, -32.0, 7.4, 1.25), (0.0, -26.0, 7.5, 1.55), (0.0, -21.0, 7.55, 1.85),
        (0.0, -16.0, 7.6, 2.25), (0.0, -10.0, 7.7, 2.55), (0.0, -4.0, 7.8, 2.72), (0.0, 2.0, 7.8, 2.8),
        (0.0, 6.0, 8.2, 2.6), (0.0, 10.0, 8.9, 2.25), (0.0, 14.0, 9.8, 1.95), (0.0, 17.5, 10.6, 1.75),
        (0.0, 21.0, 11.2, 1.62)]
HIP_I, SHOULDER_I = 8, 11          # control indices of the hips (rear legs) and shoulders (front legs)


class Spine:
    def __init__(self, ctrl=CTRL, dense=3000):
        P = [Vector(c[:3]) for c in ctrl]
        R = [c[3] for c in ctrl]
        P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
        segs = len(ctrl) - 1
        self.pts, self.rad, self.g = [], [], []
        for k in range(dense + 1):
            g = k / dense * segs
            i = min(int(g), segs - 1); t = g - i
            p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
            self.pts.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                                   (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
            s = t * t * (3 - 2 * t)
            self.rad.append(R[i] * (1 - s) + R[i + 1] * s)
            self.g.append(g)
        self.arc = [0.0]
        for i in range(1, len(self.pts)): self.arc.append(self.arc[-1] + (self.pts[i] - self.pts[i - 1]).length)
        self.length = self.arc[-1]

    def idx(self, s):
        lo, hi = 0, len(self.arc) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.arc[mid] < s: lo = mid
            else: hi = mid
        return lo, (s - self.arc[lo]) / max(self.arc[hi] - self.arc[lo], 1e-9)

    def at(self, s):
        s = max(0.0, min(self.length, s))
        i, w = self.idx(s)
        j = min(i + 1, len(self.pts) - 1)
        p = self.pts[i].lerp(self.pts[j], w)
        r = self.rad[i] * (1 - w) + self.rad[j] * w
        a, b = self.pts[max(i - 2, 0)], self.pts[min(i + 3, len(self.pts) - 1)]
        return p, r, (b - a).normalized()

    def s_of_ctrl(self, ci):
        for k, g in enumerate(self.g):
            if g >= ci: return self.arc[k]
        return self.length

    def nearest_s(self, p, step=4):
        best, bs = 1e18, 0.0
        for k in range(0, len(self.pts), step):
            d = (self.pts[k] - p).length_squared
            if d < best: best, bs = d, self.arc[k]
        return bs

    def frames(self, ss):
        """Parallel-transport frames (T, S, U) at arc positions ss (steered back to belly-down where level)."""
        out, prevS = [], None
        for s in ss:
            p, r, T = self.at(s)
            Sd = T.cross(Z)
            if prevS is None:
                S = Sd.normalized()
            else:
                S = (prevS - T * prevS.dot(T)).normalized()
                if Sd.length > 0.4 and Sd.normalized().dot(S) > 0:
                    S = S.lerp(Sd.normalized(), 0.15 * min(1.0, (Sd.length - 0.4) / 0.4)).normalized()
            prevS = S
            out.append((p, r, T, S, S.cross(T).normalized()))
        return out


# ------------------------------------------------------------------------------------------------ body loft
BELLY_HALF = math.radians(56)


def loft_section(b, sp, s0, s1, ds=0.24, m=56, cap_start=False, laps=4):
    """Scaled tube for the arc range [s0, s1]: dorsal scales (3 laps of the scale texture around), belly plates
    as real geometry bulges every 0.8 stud, slightly flattened belly."""
    n = max(2, int((s1 - s0) / ds))
    ss = [s0 + (s1 - s0) * i / n for i in range(n + 1)]
    fr = sp.frames(ss)
    rings = []
    for (p, r, T, S, U), s in zip(fr, ss):
        ring = []
        k = (s / 0.8) % 1.0
        plate = math.sin(math.pi * k) ** 0.6
        for j in range(m):
            a = 2 * math.pi * j / m
            rr = r * (1.0 + 0.035 * math.cos(2 * a))           # a little wider than tall
            db = abs(a - math.pi)
            if db < BELLY_HALF:
                w = math.cos(db / BELLY_HALF * math.pi / 2)
                rr *= 0.975 + 0.025 * plate * w
            ring.append(b.bm.verts.new(p + (S * math.sin(a) + U * math.cos(a) * 0.95) * rr))
        rings.append(ring)
    for i in range(n):
        u0s, u1s = ss[i] / 4.0, ss[i + 1] / 4.0
        u0b, u1b = ss[i] / 6.4, ss[i + 1] / 6.4
        for j in range(m):
            j2 = (j + 1) % m
            ac = 2 * math.pi * (j + 0.5) / m
            belly = abs(ac - math.pi) < BELLY_HALF
            q = [rings[i][j], rings[i + 1][j], rings[i + 1][j2], rings[i][j2]]
            if belly:
                v0 = (2 * math.pi * j / m - (math.pi - BELLY_HALF)) / (2 * BELLY_HALF)
                v1 = v0 + (2 * math.pi / m) / (2 * BELLY_HALF)
                uv = [(u0b, v0), (u1b, v0), (u1b, v1), (u0b, v1)]
            else:
                v0, v1 = laps * j / m, laps * (j + 1) / m
                uv = [(u0s, v0), (u1s, v0), (u1s, v1), (u0s, v1)]
            c = (fr[i][0] + fr[i + 1][0]) / 2
            b.face(q, 'Dragon_Belly' if belly else 'Dragon_Scales', uv, out=sum((v.co for v in q), Vector()) / 4 - c, smooth=True)
    if cap_start:
        p, r, T, S, U = fr[0]
        tip = b.bm.verts.new(p - T * 0.2)
        for j in range(m):
            b.face([rings[0][(j + 1) % m], rings[0][j], tip], 'Dragon_Scales', [(0, j / m), (0, (j + 1) / m), (-0.03, 0.5)],
                   out=-T, smooth=True)
    return fr


def dorsal_scutes(b, sp, s0, s1, step=0.75):
    """Raised keeled ridge plates along the top of the spine (real geometry)."""
    s = s0
    while s < s1:
        (p, r, T, S, U), = sp.frames([s])
        w, h = 0.2 * r + 0.05, 0.34 * r + 0.06
        base = p + U * r * 0.93
        q = [base - T * w * 1.3 - S * w, base - T * w * 1.3 + S * w, base + T * w * 0.9 + S * w * 0.6, base + T * w * 0.9 - S * w * 0.6]
        apex = base + U * h - T * h * 0.55
        vs = [b.bm.verts.new(x) for x in q]; va = b.bm.verts.new(apex)
        for k in range(4):
            tri = [vs[k], vs[(k + 1) % 4], va]
            b.face(tri, 'Dragon_Fin', [(0, 0), (1, 0), (0.5, 1)], out=(sum((v.co for v in tri), Vector()) / 3 - base) + U * 0.2, smooth=False)
        s += step


# ------------------------------------------------------------------------------------------------ head
HEAD_SCALE = 1.8
HEAD_PROF = [(-0.8, 1.0, 0.95, 0.9, 0.0), (-0.3, 1.15, 1.1, 0.8, 0.1), (0.3, 1.3, 1.2, 0.72, 0.2), (0.9, 1.36, 1.2, 0.64, 0.22),
             (1.45, 1.28, 1.1, 0.58, 0.2), (2.0, 1.12, 0.94, 0.54, 0.14), (2.5, 1.0, 0.8, 0.5, 0.1), (3.0, 0.94, 0.72, 0.47, 0.08),
             (3.5, 0.9, 0.68, 0.45, 0.1), (3.9, 0.78, 0.62, 0.42, 0.12), (4.15, 0.46, 0.42, 0.34, 0.12)]


def _prof(x):
    P = HEAD_PROF
    if x <= P[0][0]: return P[0][1:]
    for a, b in zip(P, P[1:]):
        if a[0] <= x <= b[0]:
            t = (x - a[0]) / (b[0] - a[0]); t = t * t * (3 - 2 * t)
            return tuple(a[k] * (1 - t) + b[k] * t for k in range(1, 5))
    return P[-1][1:]


class HeadFrame:
    def __init__(self, P, f, k=HEAD_SCALE):
        self.P, self.k = P, k
        self.f = f.normalized()
        self.u = (Z - self.f * Z.dot(self.f)).normalized()
        self.s = self.f.cross(self.u).normalized()

    def L(self, x, y, z):
        return self.P + (self.f * x + self.s * y + self.u * z) * self.k

    def vec(self, x, y, z):
        return (self.f * x + self.s * y + self.u * z)


def skull_point(x, a):
    w, ht, hb, c = _prof(x)
    sa, ca = math.sin(a), math.cos(a)
    e = 2.5 if x > 2.4 else 2.2
    y = math.copysign(abs(sa) ** (2 / e), sa) * w
    z = math.copysign(abs(ca) ** (2 / e), ca) * (ht if ca > 0 else hb * 0.9)
    aa = abs(a) if a <= math.pi else 2 * math.pi - a
    # brow ridges over the eyes, eye sockets, cheekbones, nose ridge, nostrils
    brow = 0.16 * math.exp(-((x - 1.6) / 0.45) ** 2) * math.exp(-((aa - 0.62) / 0.2) ** 2)
    sock = -0.08 * math.exp(-((x - 1.95) / 0.3) ** 2) * math.exp(-((aa - 1.0) / 0.16) ** 2)
    cheek = 0.1 * math.exp(-((x - 0.8) / 0.5) ** 2) * math.exp(-((aa - 1.65) / 0.35) ** 2)
    ridge = 0.05 * (x > 2.0) * math.exp(-(aa / 0.14) ** 2)
    nost = 0.12 * math.exp(-((x - 3.7) / 0.22) ** 2) * math.exp(-((aa - 0.5) / 0.16) ** 2)
    y *= 1 + cheek
    z += (brow + ridge + nost) * (1 if ca > 0 else 0)
    y += math.copysign(sock, sa) * 0.6; z += sock * 0.4 * (1 if ca > 0 else 0)
    return y, z + c


def build_head(pieces, H):
    b = pieces['Head']
    xs = [-0.8 + 4.95 * i / 25 for i in range(26)]
    m = 48
    rings = []
    for x in xs:
        rings.append([b.bm.verts.new(H.L(x, *skull_point(x, 2 * math.pi * j / m))) for j in range(m)])
    for i in range(len(xs) - 1):
        for j in range(m):
            j2 = (j + 1) % m
            q = [rings[i][j], rings[i + 1][j], rings[i + 1][j2], rings[i][j2]]
            ac = 2 * math.pi * (j + 0.5) / m
            mat = 'Dragon_Belly' if abs(ac - math.pi) < math.radians(48) else 'Dragon_Scales'
            b.face(q, mat, [(xs[i] / 2.2, j / m * 2), (xs[i + 1] / 2.2, j / m * 2), (xs[i + 1] / 2.2, (j + 1) / m * 2), (xs[i] / 2.2, (j + 1) / m * 2)],
                   out=sum((v.co for v in q), Vector()) / 4 - H.L((xs[i] + xs[i + 1]) / 2, 0, _prof(xs[i])[3]), smooth=True)
    tip = b.bm.verts.new(H.L(4.28, 0, 0.12))
    for j in range(m):
        b.face([rings[-1][j], rings[-1][(j + 1) % m], tip], 'Dragon_Scales', [(2.2, j / m), (2.2, (j + 1) / m), (2.25, 0.5)], out=H.f, smooth=True)
    # brow crests and upper teeth
    for side in (1, -1):
        tube(b, [H.L(1.0, side * 0.9, 0.95), H.L(1.7, side * 1.05, 1.12), H.L(2.4, side * 0.86, 0.88)],
             [0.1 * H.k, 0.13 * H.k, 0.05 * H.k], 8, 'Dragon_Scales')
        for kk, x in enumerate([1.3, 1.65, 2.0, 2.35, 2.7, 3.05, 3.4, 3.7, 3.95]):
            w = _prof(x)[0] * 0.92
            fang = kk == 6
            base = H.L(x, side * w, -0.28)
            cone(b, base, base - H.u * (0.55 if fang else 0.24) * H.k + H.f * 0.03 * H.k, (0.075 if fang else 0.05) * H.k)
    # eyes: narrow glowing almonds set in the sockets, slanted
    e = pieces['Eyes']
    for side in (1, -1):
        c = H.L(1.95, side * 1.12, 0.5)
        tmp = Builder(MATS)
        blob(tmp, (0, 0, 0), (0.34, 0.08, 0.085), 'Dragon_Eye', subdiv=2, amp=0.0, smooth=True)   # long, shallow, narrow
        rot = Matrix((H.f, H.s * side, H.u)).transposed() @ Matrix.Rotation(math.radians(16 * side), 3, 'X')
        for v in tmp.bm.verts:
            v.co = c + (rot @ v.co) * H.k
        from castlekit import mesh_join
        mesh_join(e, tmp)


def build_jaw(pieces, H):
    b = pieces['Jaw']
    hinge = H.L(0.35, 0, -0.5)
    R = Matrix.Rotation(math.radians(-13), 4, H.s)

    def J(x, y, z):
        return hinge + (R @ (H.L(x, y, z) - hinge).to_4d()).to_3d()
    prof = [(0.3, 1.15, 0.48), (1.0, 1.08, 0.44), (1.7, 0.98, 0.38), (2.4, 0.86, 0.32), (3.1, 0.74, 0.26), (3.6, 0.6, 0.2), (3.9, 0.3, 0.12)]
    m = 24
    rings = []
    for x, w, h in prof:
        rings.append([b.bm.verts.new(J(x, math.sin(2 * math.pi * j / m) * w, -0.6 + math.cos(2 * math.pi * j / m) * h * (1 if math.cos(2 * math.pi * j / m) > 0 else 1.2)))
                      for j in range(m)])
    for i in range(len(prof) - 1):
        for j in range(m):
            j2 = (j + 1) % m
            q = [rings[i][j], rings[i + 1][j], rings[i + 1][j2], rings[i][j2]]
            under = abs(2 * math.pi * (j + 0.5) / m - math.pi) < math.radians(62)
            b.face(q, 'Dragon_Belly' if under else 'Dragon_Scales',
                   [(i / 3, j / m * 1.5), ((i + 1) / 3, j / m * 1.5), ((i + 1) / 3, (j + 1) / m * 1.5), (i / 3, (j + 1) / m * 1.5)],
                   out=sum((v.co for v in q), Vector()) / 4 - J(prof[i][0], 0, -0.6), smooth=True)
    chin = b.bm.verts.new(J(3.98, 0, -0.62))
    for j in range(m):
        b.face([rings[-1][j], rings[-1][(j + 1) % m], chin], 'Dragon_Belly', [(2, j / m), (2, (j + 1) / m), (2.1, 0.5)], out=H.f, smooth=True)
    for side in (1, -1):
        for x in [1.3, 1.9, 2.5, 3.0, 3.45]:
            base = J(x, side * (1.0 - 0.12 * x), -0.36)
            cone(b, base, base + H.u * 0.24 * H.k, 0.05 * H.k)
        for k in range(4):                                     # chin / jaw-line spikes pointing back and down
            base = J(1.0 + 0.55 * k, side * (1.0 - 0.1 * k), -0.8)
            cone(b, base, base - H.f * 0.7 * H.k - H.u * 0.35 * H.k + H.s * side * 0.2 * H.k, 0.07 * H.k)
    tube(b, [J(1.0, 0, -0.45), J(2.2, 0, -0.42), J(3.2, 0, -0.34)], [0.2 * H.k, 0.15 * H.k, 0.06 * H.k], 8, 'Dragon_Belly')   # tongue


def build_horns(pieces, H):
    b = pieces['Horns']
    for side in (1, -1):
        # main horns: long, ridged, sweeping back and slightly out and up
        n = 16
        base = H.L(0.55, side * 0.62, 1.05)
        pts, rad = [], []
        for i in range(n + 1):
            t = i / n
            pts.append(base + (H.vec(-5.2 * t, side * (0.5 * t + 0.25 * t * t), 1.1 * t - 0.25 * t * t)) * H.k)
            rad.append((0.3 * (1 - t) ** 0.9 + 0.012) * (1 + 0.1 * math.sin(t * 44)) * H.k)
        tube(b, pts, rad, 10, 'Dragon_Horn')
        # secondary horns below and behind
        base2 = H.L(0.1, side * 0.95, 0.55)
        tube(b, [base2 + H.vec(-3.0 * t, side * 0.7 * t, 0.2 * t - 0.3 * t * t) * H.k for t in [i / 8 for i in range(9)]],
             [(0.17 * (1 - i / 8) + 0.01) * H.k for i in range(9)], 8, 'Dragon_Horn')
        # cheek frills: row of spines along the jaw hinge sweeping back
        for k in range(5):
            r0 = H.L(0.7 - 0.28 * k, side * (1.12 - 0.05 * k), -0.05 - 0.14 * k)
            cone(b, r0, r0 + H.vec(-1.3 - 0.2 * k, side * (0.45 + 0.05 * k), -0.15 - 0.05 * k) * H.k, 0.08 * H.k)
        # brow spikes
        for k in range(3):
            r0 = H.L(1.5 - 0.35 * k, side * 1.02, 1.0 - 0.05 * k)
            cone(b, r0, r0 + H.vec(-0.7, side * 0.25, 0.35) * H.k, 0.05 * H.k)
    for k in range(5):                                         # crown spines on top of the skull
        r0 = H.L(0.9 - 0.4 * k, 0, 1.18 - 0.05 * k)
        cone(b, r0, r0 + H.vec(-0.9, 0, 0.55) * H.k, 0.08 * H.k)


def build_whiskers(pieces, H):
    b = pieces['Whiskers']
    for side in (1, -1):
        w0 = H.L(3.7, side * 0.62, 0.05)
        n = 34
        pts = [w0 + H.vec(-12.0 * t, side * (2.6 * t ** 0.6), -2.4 * t + 0.9 * math.sin(t * 8.0)) * H.k for t in [i / n for i in range(n + 1)]]
        tube(b, pts, [(0.07 * (1 - i / n) + 0.008) * H.k for i in range(n + 1)], 6, 'Dragon_Fin')
        w1 = H.L(2.3, side * 1.02, 0.95)
        n = 16
        pts = [w1 + H.vec(-4.5 * t, side * 1.6 * t, 1.2 * t - 1.4 * t * t) * H.k for t in [i / n for i in range(n + 1)]]
        tube(b, pts, [(0.045 * (1 - i / n) + 0.006) * H.k for i in range(n + 1)], 5, 'Dragon_Fin')


def build_mane(pieces, H, sp, s_sh):
    """Flowing, water-like but solid crystalline mane: strands from the back of the skull and cheeks, continuing
    as a crest down both sides of the neck to the shoulders."""
    b = pieces['Mane']
    rnd = random.Random(21)
    for k in range(14):
        a = (k / 13 - 0.5) * 2.6
        root = H.L(0.1 - 0.25 * abs(a), 0.85 * math.sin(a), 0.2 + 0.95 * math.cos(a))
        d = H.vec(-1.0, 0.55 * math.sin(a), 0.35 + 0.3 * math.cos(a))
        ribbon(b, root, d, H.s if abs(math.sin(a)) < 0.5 else H.u, rnd.uniform(4.5, 7.5) * H.k / 1.8, rnd.uniform(0.7, 1.1) * H.k / 1.8,
               bend=-H.u, curl=0.35, wobble=0.12, phase=k * 0.9, n=12, mat='Dragon_Fin')
    s = s_sh + 1.0
    while s < sp.length - 0.5:
        (p, r, T, S, U), = sp.frames([s])
        for side in (1, -1):
            root = p + U * r * 0.8 + S * side * r * 0.45
            ribbon(b, root, U * 0.6 - T * 0.9 + S * side * 0.8, T, rnd.uniform(3.0, 4.6), rnd.uniform(0.8, 1.2), bend=-T,
                   curl=0.35, wobble=0.1, phase=s + side, n=10, mat='Dragon_Fin')
        s += 0.9


# ------------------------------------------------------------------------------------------------ limbs
def leg_chain(sp, ci, side, front):
    s = sp.s_of_ctrl(ci)
    (p, r, T, S, U), = sp.frames([s])
    A = p + S * side * r * 0.55 - U * r * 0.25
    foot = Vector((A.x + side * 2.9, A.y + (1.6 if front else 0.4), 0.0))
    W = foot + Vector((0, -0.3, 1.9))
    mid = (A + W) / 2
    E = mid + Vector((side * 1.5, -1.6 if front else 1.4, 0.3))
    toe = foot + Vector((0, 2.6, 0.0))
    return A, E, W, foot, toe, r


def build_limb(pieces, sp, ci, side, front):
    b, c, fins = pieces['Limbs'], pieces['Claws'], pieces['Fins']
    A, E, W, foot, toe, r = leg_chain(sp, ci, side, front)
    k = r / 2.3 * 1.55
    up = [A, A.lerp(E, 0.3) + (A - W).normalized() * 0.2, A.lerp(E, 0.65), E]
    tube(b, up, [1.35 * k, 1.28 * k, 1.0 * k, 0.78 * k], 14, 'Dragon_Scales')
    lo = [E, E.lerp(W, 0.35) + Vector((0, 0.2 if front else -0.2, 0)), E.lerp(W, 0.75), W]
    tube(b, lo, [0.8 * k, 0.74 * k, 0.6 * k, 0.52 * k], 14, 'Dragon_Scales')
    blob(b, E, (0.85 * k, 0.85 * k, 0.8 * k), 'Dragon_Scales', subdiv=2, amp=0.04, smooth=True)       # elbow
    palm = Vector((W.x, W.y + 0.45, 0.7))
    tube(b, [W, palm], [0.52 * k, 0.62 * k], 12, 'Dragon_Scales')
    blob(b, palm, (1.05, 1.2, 0.62), 'Dragon_Scales', subdiv=2, amp=0.04, smooth=True)
    fwd = Vector((side * 0.12, 1, 0)).normalized()
    for kk, ang in enumerate((-34, -11, 11, 34)):
        d = (Matrix.Rotation(math.radians(ang), 3, 'Z') @ fwd).normalized()
        p0 = palm + d * 0.8 + Vector((0, 0, -0.05))
        pts = [p0, p0 + d * 0.7 + Vector((0, 0, 0.08)), p0 + d * 1.3 - Vector((0, 0, 0.14)), p0 + d * 1.7 - Vector((0, 0, 0.42))]
        tube(b, pts, [0.38, 0.34, 0.28, 0.22], 10, 'Dragon_Scales')
        cp = pts[-1]
        claw = [cp, cp + d * 0.45 + Vector((0, 0, 0.02)), cp + d * 0.8 - Vector((0, 0, 0.14)), cp + d * 0.98 - Vector((0, 0, 0.4))]
        claw[-1].z = max(claw[-1].z, 0.02)
        tube(c, claw, [0.22, 0.17, 0.09, 0.008], 10, 'Dragon_Claw')
    back = palm - fwd * 0.6 + Vector((0, 0, 0.1))                       # dew claw
    tube(c, [back, back - fwd * 0.3 - Vector((0, 0, 0.1)), back - fwd * 0.45 - Vector((0, 0, 0.28))], [0.12, 0.07, 0.005], 8, 'Dragon_Claw')
    # elbow spikes and a crystal elbow fin
    for kk in range(3):
        r0 = E + Vector((side * 0.3, -0.2 if front else 0.2, 0.2 + 0.2 * kk)) * k
        cone(b, r0, r0 + Vector((side * 0.3, -1.1 if front else 1.1, 0.3)) * k, 0.12 * k)
    ribbon(fins, E + Vector((0, 0, 0.2)), Vector((side * 0.5, -1.0 if front else 1.0, 0.8)), Vector((0, 0, 1)), 2.6 * k + 0.6, 1.0 * k,
           bend=Vector((0, -1 if front else 1, 0)), curl=0.4, phase=side, n=10, mat='Dragon_Fin')
    return (A, E, W, toe)


# ------------------------------------------------------------------------------------------------ fins & water
def build_fins(pieces, sp, s_from, s_to):
    b = pieces['Fins']
    rnd = random.Random(31)
    s = s_from
    k = 0
    while s < s_to:
        (p, r, T, S, U), = sp.frames([s])
        L = 1.2 + 1.9 * r
        ribbon(b, p + U * r * 1.05, U * 1.0 - T * 0.75, T, L * (1.0 if k % 2 == 0 else 0.75), 0.55 * r + 0.25, bend=-T, curl=0.4,
               wobble=0.08, phase=k * 0.7, n=10, mat='Dragon_Fin')
        s += 1.25; k += 1
    # crystalline water fins fanning at the tail end
    (p, r, T, S, U), = sp.frames([1.2])
    for k in range(9):
        a = (k / 8 - 0.5) * 2.4
        d = -T * 0.3 + U * math.cos(a) + S * math.sin(a)
        ribbon(b, p, d, T, rnd.uniform(4.0, 6.5), rnd.uniform(1.0, 1.5), bend=-T, curl=0.45, wobble=0.12, phase=k, n=12, mat='Dragon_Fin')
    for s in (4.0, 7.0):                                              # small side fins further up the tail
        (p, r, T, S, U), = sp.frames([s])
        for side in (1, -1):
            ribbon(b, p + S * side * r, S * side + U * 0.4 - T * 0.5, T, 2.2, 0.8, bend=-T, curl=0.4, n=10, mat='Dragon_Fin')


def build_water(pieces, sp, H, feet, s_sh):
    """Translucent elemental water (Water_Flame): tendrils flung from the mane, spine and tail, splash crowns at
    the feet. Kept separate so it can be hidden, animated or swapped for particles."""
    b = pieces['WaterFX']
    rnd = random.Random(41)
    for k in range(18):                                              # around the head / mane
        a = 2 * math.pi * k / 18
        root = H.L(rnd.uniform(-0.5, 0.6), 1.0 * math.sin(a), 0.3 + 0.9 * math.cos(a))
        d = H.vec(-1.0, 0.9 * math.sin(a), 0.9 * math.cos(a) + 0.2)
        ribbon(b, root, d, H.f.cross(d.normalized()), rnd.uniform(3.0, 6.0), rnd.uniform(0.25, 0.45), bend=-H.u, curl=0.5,
               wobble=0.2, phase=k, n=10, mat='Water_Flame')
    s = 2.0
    while s < sp.length - 2:                                        # tendrils off the spine crest
        (p, r, T, S, U), = sp.frames([s])
        side = rnd.choice((1, -1))
        ribbon(b, p + U * r * 1.1 + S * side * r * 0.3, U * 0.9 - T * 0.8 + S * side * 0.7, T, rnd.uniform(2.0, 4.0), rnd.uniform(0.3, 0.55),
               bend=-T, curl=0.55, wobble=0.2, phase=s, n=8, mat='Water_Flame')
        s += rnd.uniform(1.6, 2.6)
    (p, r, T, S, U), = sp.frames([0.5])                              # tail-tip plume
    for k in range(10):
        a = 2 * math.pi * k / 10
        ribbon(b, p, -T * 0.6 + U * math.cos(a) + S * math.sin(a), T, rnd.uniform(3.0, 5.5), rnd.uniform(0.4, 0.8), bend=-T, curl=0.5,
               wobble=0.2, phase=k * 1.3, n=10, mat='Water_Flame')
    for f in feet:                                                   # splash crowns where the feet meet the ground
        c = Vector((f.x, f.y + 0.6, 0.05))
        for k in range(10):
            a = 2 * math.pi * k / 10 + rnd.uniform(-0.2, 0.2)
            out = Vector((math.cos(a), math.sin(a), 0))
            ribbon(b, c + out * 1.4, out * 0.7 + Z * rnd.uniform(0.9, 1.6), Z.cross(out), rnd.uniform(1.2, 2.4), rnd.uniform(0.3, 0.5),
                   bend=out, curl=0.55, wobble=0.15, phase=k, n=8, mat='Water_Flame')


# ------------------------------------------------------------------------------------------------ assembly + rig
def build():
    """Returns (pieces {name: Builder}, rig) where rig describes bones and how to weight each piece."""
    sp = Spine()
    pieces = {n: B() for n in PIECES}
    s_hip, s_sh, L = sp.s_of_ctrl(HIP_I), sp.s_of_ctrl(SHOULDER_I), sp.length
    loft_section(pieces['Tail'], sp, 0.0, s_hip, cap_start=True)
    loft_section(pieces['Body'], sp, s_hip, s_sh)
    loft_section(pieces['Neck'], sp, s_sh, L)
    dorsal_scutes(pieces['Tail'], sp, 1.5, s_hip)
    dorsal_scutes(pieces['Body'], sp, s_hip, s_sh)
    dorsal_scutes(pieces['Neck'], sp, s_sh, L - 1.0)
    pe, re_, Te = sp.at(L)
    H = HeadFrame(pe - Te * 0.6, Vector((0, 1, -0.22)))
    build_head(pieces, H); build_jaw(pieces, H); build_horns(pieces, H); build_whiskers(pieces, H)
    build_mane(pieces, H, sp, s_sh)
    legs = {}
    for ci, front, tag in ((SHOULDER_I, True, 'F'), (HIP_I, False, 'R')):
        for side, lr in ((1, 'R'), (-1, 'L')):
            legs[tag + lr] = build_limb(pieces, sp, ci, side, front)
    build_fins(pieces, sp, 2.5, L - 3.0)
    build_water(pieces, sp, H, [leg_chain(sp, ci, sd, fr)[3] for ci, fr in ((SHOULDER_I, True), (HIP_I, False)) for sd in (1, -1)], s_sh)
    rig = make_rig(sp, H, legs, s_hip, s_sh)
    return pieces, rig


def make_rig(sp, H, legs, s_hip, s_sh):
    """Bones: (name, head, tail, parent) + arc intervals for spine-weighted pieces."""
    L = sp.length
    bones, chain = [], []                      # chain: (name, s0, s1) along the spine arc, tail tip -> head
    bones.append(('Root', Vector((0, 0, 0)), Vector((0, 1.5, 0)), None))
    tail_n, spine_n, neck_n = 16, 4, 4
    for i in range(spine_n):
        s0 = s_hip + (s_sh - s_hip) * i / spine_n; s1 = s_hip + (s_sh - s_hip) * (i + 1) / spine_n
        bones.append((f'Spine{i + 1:02d}', sp.at(s0)[0], sp.at(s1)[0], 'Root' if i == 0 else f'Spine{i:02d}'))
        chain.append((f'Spine{i + 1:02d}', s0, s1))
    for i in range(neck_n):
        s0 = s_sh + (L - s_sh) * i / neck_n; s1 = s_sh + (L - s_sh) * (i + 1) / neck_n
        bones.append((f'Neck{i + 1:02d}', sp.at(s0)[0], sp.at(s1)[0], 'Spine04' if i == 0 else f'Neck{i:02d}'))
        chain.append((f'Neck{i + 1:02d}', s0, s1))
    bones.append(('Head', sp.at(L)[0], H.L(3.0, 0, 0.2), 'Neck04'))
    chain.append(('Head', L, L + 6.0))
    bones.append(('Jaw', H.L(0.35, 0, -0.5), H.L(3.8, 0, -0.9), 'Head'))
    tail = []
    for i in range(tail_n):                    # Tail01 at the hips -> Tail12 at the tip (denser toward the tip)
        f0 = (i / tail_n) ** 0.85; f1 = ((i + 1) / tail_n) ** 0.85
        s0 = s_hip * (1 - f0); s1 = s_hip * (1 - f1)
        bones.append((f'Tail{i + 1:02d}', sp.at(s0)[0], sp.at(s1)[0], 'Spine01' if i == 0 else f'Tail{i:02d}'))
        tail.append((f'Tail{i + 1:02d}', s1, s0))
    chain = tail[::-1] + chain
    leg_bones = {}
    for tag, (A, E, W, toe) in legs.items():
        par = 'Spine04' if tag[0] == 'F' else 'Spine01'
        segs = [(f'{tag}_Upper', A, E), (f'{tag}_Lower', E, W), (f'{tag}_Foot', W, toe)]
        for k, (n, a, b) in enumerate(segs):
            bones.append((n, a, b, par if k == 0 else segs[k - 1][0]))
        leg_bones[tag] = segs
    return dict(bones=bones, chain=chain, legs=leg_bones, spine=sp, head='Head', jaw='Jaw')


def spine_weights(rig, s):
    ch = rig['chain']
    cs = [((a + b) / 2, n) for n, a, b in ch]
    if s <= cs[0][0]: return {cs[0][1]: 1.0}
    if s >= cs[-1][0]: return {cs[-1][1]: 1.0}
    for (c0, n0), (c1, n1) in zip(cs, cs[1:]):
        if c0 <= s <= c1:
            t = (s - c0) / (c1 - c0)
            t = t * t * (3 - 2 * t)
            return {n0: 1 - t, n1: t}
    return {cs[-1][1]: 1.0}


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length


def limb_weights(rig, p, foot_only=False):
    best = None
    for tag, segs in rig['legs'].items():
        d = min(seg_dist(p, a, b) for _, a, b in segs)
        if best is None or d < best[0]: best = (d, segs)
    segs = best[1]
    if foot_only: return {segs[2][0]: 1.0}
    ds = [(seg_dist(p, a, b), n) for n, a, b in segs]
    ws = sorted(((1.0 / (d ** 4 + 1e-4), n) for d, n in ds), reverse=True)[:2]
    tot = sum(w for w, _ in ws)
    return {n: w / tot for w, n in ws}


def weights_for(rig, piece, p):
    if piece in ('Head', 'Horns', 'Eyes', 'Whiskers'): return {'Head': 1.0}
    if piece == 'Jaw': return {'Jaw': 1.0}
    if piece == 'Claws': return limb_weights(rig, p, foot_only=True)
    if piece == 'Limbs': return limb_weights(rig, p)
    if piece in ('Fins',):                          # elbow fins belong to the legs, the rest to the spine
        near_leg = min(seg_dist(p, a, b) for segs in rig['legs'].values() for _, a, b in segs)
        sp = rig['spine']
        s = sp.nearest_s(p)
        if near_leg < (p - sp.at(s)[0]).length * 0.6: return limb_weights(rig, p)
        return spine_weights(rig, s)
    sp = rig['spine']
    s = sp.nearest_s(p)
    if piece in ('Mane', 'WaterFX') and s >= sp.length - 0.3:
        return {'Head': 1.0}
    if piece == 'WaterFX':
        near_leg = min(seg_dist(p, a, b) for segs in rig['legs'].values() for _, a, b in segs)
        if p.z < 3.0 and near_leg < 3.0: return limb_weights(rig, p, foot_only=True)
    return spine_weights(rig, s)
