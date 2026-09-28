"""Detailed Eastern water dragon (Twin Dragons VFX / showpiece).

Serpentine scaled body with a plated belly, horned head with open jaws, teeth, glowing eyes, long whiskers and a
water-flame mane; flowing water fins along the spine, four clawed legs with water tufts at the elbows, a splashing
tail plume, loose droplets, and a separate whirlpool.

Blender axes: front = +Y (Roblox -Z), up = +Z. Materials: Dragon_Scales, Dragon_Belly, Dragon_Horn, Water_Flame,
Glow_Yellow (eyes), VFX_Water (whirlpool).
UVs: body/legs U along the body (11 studs per tile, tail -> head), V around. Water_Flame ribbons: V root -> tip.
"""
import math, random
from mathutils import Vector, Matrix, noise
from geo import Builder, tube
from harborkit import blob

MATS = ['Dragon_Scales', 'Dragon_Belly', 'Dragon_Horn', 'Water_Flame', 'Glow_Yellow', 'VFX_Water']
Z = Vector((0, 0, 1))


def B():
    return Builder(MATS)


# ------------------------------------------------------------------------------------------------ helpers
def ribbon(b, root, d, wdir, L, W, bend=None, curl=0.35, wobble=0.12, phase=0.0, n=12, mat='Water_Flame'):
    """Double-sided flame-shaped plume from `root` along `d` (length L, base width W across `wdir`), bending
    toward `bend` and curling at the tip. UV: U across (0..1), V root -> tip."""
    d = d.normalized()
    wdir = (wdir - d * wdir.dot(d)).normalized()
    nrm = d.cross(wdir).normalized()
    bend = (bend if bend is not None else nrm)
    bend = (bend - d * bend.dot(d)).normalized() if (bend - d * bend.dot(d)).length > 1e-4 else nrm
    rows_f, rows_b = [], []
    for i in range(n + 1):
        t = i / n
        c = root + d * L * t + bend * curl * L * t ** 2.4 + wdir * wobble * L * math.sin(3.0 * math.pi * t + phase) * t
        w = W * (0.75 + 1.3 * t) * (1 - t) ** 0.85 + 0.01
        tw = (wdir + bend * 0.35 * t).normalized()
        pts = [c - tw * w / 2, c + nrm * w * 0.08, c + tw * w / 2]
        rows_f.append([b.bm.verts.new(p) for p in pts])
        rows_b.append([b.bm.verts.new(p - nrm * 0.012) for p in pts])
    for i in range(n):
        for j in range(2):
            uv = [(j / 2, i / n), ((j + 1) / 2, i / n), ((j + 1) / 2, (i + 1) / n), (j / 2, (i + 1) / n)]
            q = [rows_f[i][j], rows_f[i][j + 1], rows_f[i + 1][j + 1], rows_f[i + 1][j]]
            b.face(q, mat, uv, out=nrm, smooth=True)
            q = [rows_b[i][j], rows_b[i][j + 1], rows_b[i + 1][j + 1], rows_b[i + 1][j]]
            b.face(q, mat, uv, out=-nrm, smooth=True)


def cone(b, base, tip, r, mat='Dragon_Horn', segs=6):
    tube(b, [base, base.lerp(tip, 0.55), tip], [r, r * 0.55, 0.004], segs, mat, up=_up_for(tip - base))


def _up_for(d):
    d = d.normalized()
    return Vector((0, 1, 0)) if abs(d.z) > 0.9 else Z


def frame(T):
    T = T.normalized()
    S = T.cross(Z)
    if S.length < 1e-4: S = Vector((1, 0, 0))
    S.normalize()
    return T, S, S.cross(T).normalized()


# ------------------------------------------------------------------------------------------------ body
L_BODY = 38.0


def spine(t):
    """Body centre line, t = 0 tail tip .. 1 neck. Big sinuous S (lateral + vertical waves), head end raised."""
    y = -L_BODY / 2 + L_BODY * t
    x = 5.5 * math.sin(2 * math.pi * 1.0 * t + 0.3) * (1 - 0.4 * t)
    z = 5.0 + 4.3 * math.sin(2 * math.pi * 0.8 * t - 1.6) + 8.0 * t ** 3
    if t < 0.14:                                           # tail curls up at the end
        k = (0.14 - t) / 0.14
        z += 2.2 * k ** 2; x -= 1.2 * k ** 2
    return Vector((x, y, z))


def radius(t):
    if t < 0.55:
        return 0.08 + 1.27 * math.sin(math.pi / 2 * t / 0.55) ** 0.95
    return 1.35 - 0.33 * (t - 0.55) / 0.45


def body(b, n=220, m=28):
    pts = [spine(i / n) for i in range(n + 1)]
    arc = [0.0]
    for i in range(1, n + 1): arc.append(arc[-1] + (pts[i] - pts[i - 1]).length)
    rings, frames = [], []
    for i in range(n + 1):
        t = i / n
        T = pts[min(i + 1, n)] - pts[max(i - 1, 0)]
        T, S, U = frame(T)
        r = radius(t)
        ring = []
        for j in range(m):
            a = 2 * math.pi * j / m                        # 0 = top, pi = belly
            bulge = 1.0 + 0.04 * math.cos(4 * a)
            ring.append(b.bm.verts.new(pts[i] + (S * math.sin(a) * r + U * math.cos(a) * r * 0.9) * bulge))
        rings.append(ring); frames.append((T, S, U, r))
    belly_half = math.radians(58)
    for i in range(n):
        u0, u1 = arc[i] / 11.0, arc[i + 1] / 11.0
        for j in range(m):
            j2 = (j + 1) % m
            ac = 2 * math.pi * (j + 0.5) / m
            belly = abs(ac - math.pi) < belly_half
            if belly:
                v0 = (2 * math.pi * j / m - (math.pi - belly_half)) / (2 * belly_half)
                v1 = v0 + (2 * math.pi / m) / (2 * belly_half)
            else:
                v0, v1 = j / m, (j + 1) / m
            q = [rings[i][j], rings[i + 1][j], rings[i + 1][j2], rings[i][j2]]
            c = (pts[i] + pts[i + 1]) / 2
            b.face(q, 'Dragon_Belly' if belly else 'Dragon_Scales', [(u0, v0), (u1, v0), (u1, v1), (u0, v1)],
                   out=sum((v.co for v in q), Vector()) / 4 - c, smooth=True)
    tip = b.bm.verts.new(pts[0] - frames[0][0] * 0.15)       # close the tail tip
    for j in range(m):
        q = [rings[0][(j + 1) % m], rings[0][j], tip]
        b.face(q, 'Dragon_Scales', [(0, j / m), (0, (j + 1) / m), (-0.02, (j + 0.5) / m)], out=-frames[0][0], smooth=True)
    return pts, frames


# ------------------------------------------------------------------------------------------------ head
def head(b, P, T):
    f = (T.normalized() + Vector((0, 0, 0.05))).normalized()
    u = (Z - f * Z.dot(f)).normalized()
    s = f.cross(u).normalized()

    def Lc(x, y, zz):
        return P + f * x + s * y + u * zz

    # upper head: loft of superelliptic sections, flatter underneath (the mouth line)
    prof = [(-0.6, 1.0, 0.92, 0.0), (0.3, 1.2, 1.15, 0.14), (1.1, 1.16, 1.08, 0.18), (1.9, 1.0, 0.86, 0.1),
            (2.6, 0.82, 0.66, 0.03), (3.3, 0.72, 0.56, 0.05), (3.85, 0.6, 0.5, 0.08), (4.15, 0.34, 0.32, 0.06)]
    m = 24
    rings = []
    for x, w, h, zc in prof:
        ring = []
        for j in range(m):
            a = 2 * math.pi * j / m
            cy, cz = math.sin(a), math.cos(a)
            e = 2.6
            yy = math.copysign(abs(cy) ** (2 / e), cy) * w
            zz = math.copysign(abs(cz) ** (2 / e), cz) * h
            if zz < 0: zz *= 0.62                          # flat palate
            ring.append(b.bm.verts.new(Lc(x, yy, zc + zz)))
        rings.append(ring)
    for i in range(len(prof) - 1):
        for j in range(m):
            j2 = (j + 1) % m
            q = [rings[i][j], rings[i + 1][j], rings[i + 1][j2], rings[i][j2]]
            ac = 2 * math.pi * (j + 0.5) / m
            mat = 'Dragon_Belly' if abs(ac - math.pi) < math.radians(50) else 'Dragon_Scales'
            b.face(q, mat, [(prof[i][0] / 5.5, j / m * 0.6), (prof[i + 1][0] / 5.5, j / m * 0.6),
                            (prof[i + 1][0] / 5.5, (j + 1) / m * 0.6), (prof[i][0] / 5.5, (j + 1) / m * 0.6)],
                   out=sum((v.co for v in q), Vector()) / 4 - Lc((prof[i][0] + prof[i + 1][0]) / 2, 0, prof[i][3]), smooth=True)
    nose = b.bm.verts.new(Lc(4.25, 0, 0.06))
    for j in range(m):
        b.face([rings[-1][j], rings[-1][(j + 1) % m], nose], 'Dragon_Scales', [(1.8, j / m), (1.8, (j + 1) / m), (1.85, 0.5)],
               out=f, smooth=True)

    # lower jaw, hinged at x=0.5 and dropped open by 16 deg
    hinge = Lc(0.5, 0, -0.45)
    rot = Matrix.Rotation(math.radians(-16), 4, s)

    def J(x, y, zz):
        p = Lc(x, y, zz) - hinge
        return hinge + (rot @ p.to_4d()).to_3d()
    jprof = [(0.5, 0.95, 0.42), (1.3, 0.84, 0.36), (2.2, 0.7, 0.3), (2.8, 0.56, 0.24), (3.25, 0.4, 0.18), (3.5, 0.18, 0.09)]
    jr = []
    for x, w, h in jprof:
        ring = []
        for j in range(16):
            a = 2 * math.pi * j / 16
            ring.append(b.bm.verts.new(J(x, math.sin(a) * w, -0.55 + math.cos(a) * h)))
        jr.append(ring)
    for i in range(len(jprof) - 1):
        for j in range(16):
            j2 = (j + 1) % 16
            q = [jr[i][j], jr[i + 1][j], jr[i + 1][j2], jr[i][j2]]
            under = abs(2 * math.pi * (j + 0.5) / 16 - math.pi) < math.radians(60)
            b.face(q, 'Dragon_Belly' if under else 'Dragon_Scales',
                   [(i / 5, j / 16 * 0.6), ((i + 1) / 5, j / 16 * 0.6), ((i + 1) / 5, (j + 1) / 16 * 0.6), (i / 5, (j + 1) / 16 * 0.6)],
                   out=sum((v.co for v in q), Vector()) / 4 - J(jprof[i][0], 0, -0.55), smooth=True)
    chin = b.bm.verts.new(J(3.57, 0, -0.55))
    for j in range(16):
        b.face([jr[-1][j], jr[-1][(j + 1) % 16], chin], 'Dragon_Belly', [(2, j / 16), (2, (j + 1) / 16), (2.1, 0.5)],
               out=f, smooth=True)

    # teeth: upper row pointing down (fangs near the front), lower row pointing up
    for side in (1, -1):
        for k, x in enumerate([1.6, 2.0, 2.4, 2.8, 3.2, 3.6, 3.95]):
            w = 0.62 if x > 3.3 else 0.7
            fang = k in (5,)
            base = Lc(x, side * w * 0.95, -0.22)
            cone(b, base, base - u * (0.42 if fang else 0.2), 0.07 if fang else 0.045)
        for x in [1.6, 2.1, 2.6, 3.05]:
            base = J(x, side * (0.62 - 0.08 * x), -0.36)
            cone(b, base, base + u * 0.2 - f * 0.03, 0.045)
    # tongue (forked) - scales tinted by the belly set
    tube(b, [J(1.2, 0, -0.42), J(2.4, 0, -0.38), J(2.8, 0, -0.3), J(3.2, 0.08, -0.2)], [0.16, 0.12, 0.07, 0.01], 8, 'Dragon_Belly')

    # eyes, brows, nostrils
    for side in (1, -1):
        blob(b, Lc(1.8, side * 0.9, 0.46), (0.2, 0.24, 0.17), 'Glow_Yellow', subdiv=2, amp=0.0, smooth=True)
        tube(b, [Lc(1.2, side * 0.8, 0.66), Lc(1.8, side * 1.0, 0.8), Lc(2.4, side * 0.86, 0.62)], [0.12, 0.17, 0.08], 8,
             'Dragon_Scales')                                                               # brow ridge
        blob(b, Lc(3.9, side * 0.3, 0.46), (0.14, 0.14, 0.11), 'Dragon_Scales', subdiv=2, amp=0.0)  # nostril knob
        # antler horns: main beam back / up / out, one forward tine
        h0 = Lc(0.75, side * 0.52, 0.95)
        pts = [h0, h0 - f * 1.0 + s * side * 0.35 + u * 0.7, h0 - f * 2.3 + s * side * 0.65 + u * 1.15,
               h0 - f * 3.7 + s * side * 0.8 + u * 1.25]
        tube(b, pts, [0.24, 0.18, 0.1, 0.02], 8, 'Dragon_Horn')
        tube(b, [pts[1], pts[1] - f * 0.25 + u * 0.8 + s * side * 0.1, pts[1] - f * 0.1 + u * 1.25], [0.1, 0.06, 0.01], 6, 'Dragon_Horn')
        tube(b, [pts[2], pts[2] - f * 0.2 + u * 0.55, pts[2] - f * 0.05 + u * 0.9 + s * side * 0.1], [0.07, 0.04, 0.008], 6, 'Dragon_Horn')
        # long whiskers from the snout, flowing back and down in waves
        w0 = Lc(3.7, side * 0.55, 0.05)
        wp = [w0 + s * side * (1.3 * (k / 24) ** 0.6) - f * (8.0 * k / 24) - u * (2.2 * k / 24) + u * 0.6 * math.sin(k / 24 * 7.0)
              for k in range(25)]
        tube(b, wp, [0.075 - 0.0028 * k for k in range(25)], 6, 'Water_Flame', up=Vector((0, 0, 1)))
        # short brow whiskers
        w1 = Lc(2.1, side * 1.0, 0.7)
        tube(b, [w1 + s * side * 0.3 * k - f * 0.5 * k + u * (0.25 * k - 0.05 * k * k) for k in range(6)],
             [0.05, 0.045, 0.035, 0.025, 0.015, 0.005], 5, 'Water_Flame')
        # cheek / jaw frills (water flames) sweeping back
        for k in range(3):
            ribbon(b, Lc(0.9 - 0.3 * k, side * 1.0, -0.1 - 0.25 * k), -f + s * side * 0.6 - u * 0.15 * k, u, 2.0 + 0.4 * k,
                   0.7, bend=u, curl=0.4, phase=k + side)
    # water mane: crest along the back of the skull and nape, sweeping back and up
    for k in range(9):
        a = (k - 4) / 4.0
        root = Lc(0.5 - 0.3 * abs(a) - 0.15 * k, 0.75 * a, 1.0 - 0.25 * abs(a))
        ribbon(b, root, -f * 1.0 + u * 0.55 + s * a * 0.7, s, 2.8 + 1.0 * (1 - abs(a)), 1.0, bend=u, curl=0.45, phase=k * 0.9)
    for k in range(6):                                     # long flowing nape mane down the neck
        side = 1 if k % 2 else -1
        root = Lc(-0.4 - 0.2 * k, side * 0.5, 0.75)
        ribbon(b, root, -f * 1.0 + u * 0.25 + s * side * 0.6, s, 3.4 + 0.3 * k, 0.9, bend=-u, curl=0.3, phase=k * 1.4)
    # beard under the chin
    for k in range(3):
        ribbon(b, J(2.6 + 0.4 * k, (k - 1) * 0.2, -0.75), -u * 1.0 - f * 0.6, s, 1.4, 0.4, bend=-f, curl=0.35, phase=k)
    return f, s, u


# ------------------------------------------------------------------------------------------------ limbs & fins
def leg(b, P, T, S, U, r, side, front):
    A = P + S * side * r * 0.72 - U * r * 0.35
    if front:
        E = A + S * side * 1.3 - U * 1.0 + T * 0.5
        Wr = E + T * 1.2 - U * 0.8 + S * side * 0.15
    else:
        E = A + S * side * 1.2 - U * 0.9 - T * 0.6
        Wr = E + T * 0.4 - U * 1.2 + S * side * 0.2
    tube(b, [A, A.lerp(E, 0.5) + U * 0.15, E], [0.48 * min(1.0, r), 0.4, 0.3], 10, 'Dragon_Scales')
    tube(b, [E, E.lerp(Wr, 0.5), Wr], [0.3, 0.26, 0.22], 10, 'Dragon_Scales')
    blob(b, Wr, (0.28, 0.3, 0.2), 'Dragon_Scales', subdiv=2, amp=0.05, smooth=True)          # palm
    fw = (T + S * side * 0.2).normalized()
    for k, ang in enumerate((-42, -14, 14, 42)):
        dvec = (Matrix.Rotation(math.radians(ang), 3, U) @ fw).normalized()
        p0 = Wr + dvec * 0.18
        pts = [p0, p0 + dvec * 0.3 - U * 0.05, p0 + dvec * 0.52 - U * 0.22, p0 + dvec * 0.64 - U * 0.42]
        tube(b, pts, [0.1, 0.085, 0.07, 0.055], 6, 'Dragon_Scales')
        cone(b, pts[-1], pts[-1] + dvec * 0.12 - U * 0.36, 0.06)
    back = Wr - fw * 0.2
    cone(b, back, back - fw * 0.32 - U * 0.25, 0.05)                                         # dew claw
    for k in range(3):                                                                       # elbow water tufts
        ribbon(b, E + U * 0.1, -T + U * (0.5 + 0.3 * k) + S * side * 0.3, S, 1.2 + 0.35 * k, 0.45, bend=U, curl=0.45, phase=k * 1.7)


def dorsal_fins(b, pts, frames, t0=0.07, t1=0.965, step=0.026):
    n = len(pts) - 1
    t = t0; k = 0
    while t < t1:
        i = int(t * n)
        T, S, U, r = frames[i]
        big = 1.0 if k % 2 == 0 else 0.7
        root = pts[i] + U * r * 0.82
        ribbon(b, root, U * 1.0 - T * 0.85 + S * 0.12 * math.sin(k * 1.7), T, (0.9 + 1.9 * r) * big, 1.05 * r + 0.15,
               bend=-T, curl=0.5, wobble=0.1, phase=k * 0.8)
        t += step; k += 1


def tail_plume(b, pts, frames):
    T, S, U, r = frames[2]
    root = pts[1]
    dirs = [(-T + U * 0.9, 4.2), (-T + U * 0.3 + S * 0.5, 3.6), (-T + U * 0.3 - S * 0.5, 3.6), (-T - U * 0.4 + S * 0.35, 3.0),
            (-T - U * 0.4 - S * 0.35, 3.0), (-T + U * 1.4 + S * 0.2, 3.2), (-T * 0.4 + U * 1.0 - S * 0.4, 2.6)]
    for k, (d, L) in enumerate(dirs):
        ribbon(b, root, d, S if abs(d.normalized().dot(S)) < 0.7 else U, L, 1.1, bend=U, curl=0.5, phase=k * 1.3)


def droplets(b, pts, frames, count=46, seed=7):
    rnd = random.Random(seed)
    n = len(pts) - 1
    for k in range(count):
        i = rnd.randrange(4, n - 4)
        T, S, U, r = frames[i]
        off = U * (r + rnd.uniform(1.2, 3.2)) + S * rnd.uniform(-2.2, 2.2) - T * rnd.uniform(0, 1.5)
        sz = rnd.uniform(0.07, 0.2)
        blob(b, pts[i] + off, (sz, sz, sz * 1.25), 'Water_Flame', subdiv=1, amp=0.05, seed=k, smooth=True)


HEAD_SCALE = 1.4
LEG_SCALE = 1.35


def scaled(b, fn, pivot, k, *args):
    from castlekit import mesh_join
    tmp = B()
    out = fn(tmp, *args)
    for v in tmp.bm.verts: v.co = pivot + (v.co - pivot) * k
    mesh_join(b, tmp)
    return out


def water_dragon():
    """Returns (dragon builder, droplets builder). Head points to +Y (front); centred on its bounding box."""
    b = B()
    pts, frames = body(b)
    scaled(b, head, pts[-1], HEAD_SCALE, pts[-1], frames[-1][0])
    for tl, front in ((0.8, True), (0.42, False)):
        i = int(tl * (len(pts) - 1))
        T, S, U, r = frames[i]
        for side in (1, -1):
            A = pts[i] + S * side * r * 0.72 - U * r * 0.35
            scaled(b, leg, A, LEG_SCALE, pts[i], T, S, U, r, side, front)
    dorsal_fins(b, pts, frames)
    tail_plume(b, pts, frames)
    d = B()
    droplets(d, pts, frames)
    # centre everything on the dragon's bounding box
    lo = Vector([min(v.co[a] for v in b.bm.verts) for a in range(3)])
    hi = Vector([max(v.co[a] for v in b.bm.verts) for a in range(3)])
    c = (lo + hi) / 2
    for bb in (b, d):
        for v in bb.bm.verts: v.co -= c
    return b, d


def whirlpool(R=10.0, depth=2.6, nu=64, nv=14):
    """Funnel-shaped whirlpool disc (VFX_Water). U spirals around (scroll it to spin), V centre (0) -> rim (1)."""
    b = B()
    rows = []
    for j in range(nv + 1):
        v = j / nv
        rr = R * (0.06 + 0.94 * v)
        zz = -depth * (1 - v) ** 2.2
        rows.append([b.bm.verts.new(Vector((rr * math.cos(2 * math.pi * i / nu), rr * math.sin(2 * math.pi * i / nu), zz)))
                     for i in range(nu)])
    for j in range(nv):
        for i in range(nu):
            i2 = (i + 1) % nu
            q = [rows[j][i], rows[j][i2], rows[j + 1][i2], rows[j + 1][i]]
            sw = lambda ii, jj: (ii / nu * 3 + jj / nv * 1.6, jj / nv)
            b.face(q, 'VFX_Water', [sw(i, j), sw(i + 1, j), sw(i + 1, j + 1), sw(i, j + 1)], out=Vector((0, 0, 1)), smooth=True)
    return b
