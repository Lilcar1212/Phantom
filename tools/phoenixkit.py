"""Hero creature: phoenix (fire bird), Roblox-ready and rigged.

Soaring pose: wings spread wide (~40 studs), long streamer tail plumes with eye spots and a fan of tail feathers,
crowned head with curling crest plumes, hooked gold beak, glowing amber eyes, legs and talons tucked for flight.
Pieces (each split per texture set, < 20k tris): Head, Beak, Crest, Eyes, Neck, Body, Wings, Tail, Legs, Talons, FireFX.
Solid materials: Phoenix_Body, Phoenix_Breast, Phoenix_Feather, Phoenix_Plume, Phoenix_Beak, Glow_Amber (eyes).
FireFX uses the translucent Fire_Flame set (AlphaMode Transparency / Neon-ish glow).

Rig: Root, Spine01-03, Neck01-02, Head, Beak, L/R_Wing1-3 (shoulder, forearm, hand), Tail01-06, L/R_Thigh/Shin/Foot.
Blender axes: front = +Y (Roblox -Z), up = +Z. Origin = centre of the body (it's a flyer).
"""
import math, random
from mathutils import Vector, Matrix
from geo import Builder, tube
from harborkit import blob
from dragonkit import ribbon, cone
from creaturekit import Spine

MATS = ['Phoenix_Body', 'Phoenix_Breast', 'Phoenix_Feather', 'Phoenix_Plume', 'Phoenix_Beak', 'Glow_Amber', 'Fire_Flame']
PIECES = ['Head', 'Beak', 'Crest', 'Eyes', 'Neck', 'Body', 'Wings', 'Tail', 'Legs', 'Talons', 'FireFX']
Z = Vector((0, 0, 1))


def B():
    return Builder(MATS)


# body spine: tail base -> head base (x, y, z, radius)
CTRL = [(0.0, -7.0, -0.6, 0.5), (0.0, -5.2, -0.4, 1.3), (0.0, -3.0, -0.1, 2.2), (0.0, -0.6, 0.2, 2.6), (0.0, 1.8, 0.6, 2.35),
        (0.0, 3.6, 1.3, 1.6), (0.0, 5.0, 2.4, 1.15), (0.0, 6.2, 3.6, 1.0), (0.0, 7.2, 4.4, 0.95)]
NECK_I = 5


# ------------------------------------------------------------------------------------------------ helpers
def feather(b, root, d, side, L, W, bend=0.12, mat='Phoenix_Feather', n=10, twist=0.0):
    """Double-sided lanceolate feather with a raised shaft, curving along `side x d` normal by `bend`.
    UV: U across the vane (0..1), V root -> tip."""
    d = d.normalized()
    side = (side - d * side.dot(d)).normalized()
    nrm = d.cross(side).normalized()
    F, K = [], []
    for i in range(n + 1):
        t = i / n
        c = root + d * L * t + nrm * bend * L * t * t
        w = W * math.sin(math.pi * min(1.0, 0.12 + t * 0.95)) ** 0.7 * (1 - 0.35 * t) + 0.01
        sd = (side * math.cos(twist * t) + nrm * math.sin(twist * t))
        pts = [c - sd * w / 2, c + nrm * w * 0.05, c + sd * w / 2]
        F.append([b.bm.verts.new(p) for p in pts])
        K.append([b.bm.verts.new(p - nrm * 0.015) for p in pts])
    for i in range(n):
        for j in range(2):
            uv = [(j / 2, i / n), ((j + 1) / 2, i / n), ((j + 1) / 2, (i + 1) / n), (j / 2, (i + 1) / n)]
            b.face([F[i][j], F[i][j + 1], F[i + 1][j + 1], F[i + 1][j]], mat, uv, out=nrm, smooth=True)
            b.face([K[i][j], K[i][j + 1], K[i + 1][j + 1], K[i + 1][j]], mat, uv, out=-nrm, smooth=True)


def streamer(b, pts, W, mat='Phoenix_Plume'):
    """Long tail plume along a polyline: thin shaft that widens into a teardrop eye near the tip. V root -> tip."""
    n = len(pts) - 1
    F, K = [], []
    for i, p in enumerate(pts):
        t = i / n
        d = (pts[min(i + 1, n)] - pts[max(i - 1, 0)]).normalized()
        side = d.cross(Z).normalized() if abs(d.z) < 0.95 else Vector((1, 0, 0))
        nrm = d.cross(side).normalized()
        w = W * (0.18 + 0.1 * t) + W * 1.1 * math.exp(-((t - 0.86) / 0.08) ** 2) * (1 if t < 0.97 else 0.4)
        if t > 0.96: w *= (1 - t) / 0.04 * 0.6 + 0.05
        row = [p - side * w / 2, p + nrm * w * 0.05, p + side * w / 2]
        F.append([b.bm.verts.new(q) for q in row])
        K.append([b.bm.verts.new(q - nrm * 0.015) for q in row])
        if i == 0: n0 = nrm
    for i in range(n):
        p = pts[i]
        d = (pts[i + 1] - p).normalized()
        side = d.cross(Z).normalized() if abs(d.z) < 0.95 else Vector((1, 0, 0))
        nrm = d.cross(side).normalized()
        for j in range(2):
            uv = [(j / 2, i / n), ((j + 1) / 2, i / n), ((j + 1) / 2, (i + 1) / n), (j / 2, (i + 1) / n)]
            b.face([F[i][j], F[i][j + 1], F[i + 1][j + 1], F[i + 1][j]], mat, uv, out=nrm, smooth=True)
            b.face([K[i][j], K[i][j + 1], K[i + 1][j + 1], K[i + 1][j]], mat, uv, out=-nrm, smooth=True)


# ------------------------------------------------------------------------------------------------ body
def body_loft(pieces, sp, s_neck):
    for pname, s0, s1 in (('Body', 0.0, s_neck), ('Neck', s_neck, sp.length)):
        b = pieces[pname]
        n, m = max(4, int((s1 - s0) / 0.2)), 40
        ss = [s0 + (s1 - s0) * i / n for i in range(n + 1)]
        fr = sp.frames(ss)
        rings = []
        for (p, r, T, S, U), s in zip(fr, ss):
            ring = []
            for j in range(m):
                a = 2 * math.pi * j / m
                rr = r * (1.0 + 0.06 * math.cos(2 * a)) * (1.08 if math.cos(a) < 0 else 1.0)   # fuller breast
                ring.append(b.bm.verts.new(p + (S * math.sin(a) * 1.05 + U * math.cos(a) * 0.95) * rr))
            rings.append(ring)
        for i in range(n):
            for j in range(m):
                j2 = (j + 1) % m
                ac = 2 * math.pi * (j + 0.5) / m
                breast = abs(ac - math.pi) < math.radians(70)
                q = [rings[i][j], rings[i + 1][j], rings[i + 1][j2], rings[i][j2]]
                u0, u1 = ss[i] / 3.0, ss[i + 1] / 3.0
                v0, v1 = 3 * j / m, 3 * (j + 1) / m
                b.face(q, 'Phoenix_Breast' if breast else 'Phoenix_Body', [(u0, v0), (u1, v0), (u1, v1), (u0, v1)],
                       out=sum((v.co for v in q), Vector()) / 4 - (fr[i][0] + fr[i + 1][0]) / 2, smooth=True)
        if pname == 'Body':
            p, r, T, S, U = fr[0]
            tip = b.bm.verts.new(p - T * 0.3)
            for j in range(m):
                b.face([rings[0][(j + 1) % m], rings[0][j], tip], 'Phoenix_Body', [(0, 0), (0, 1), (-0.1, 0.5)], out=-T, smooth=True)
        # contour feathers ruffled over the back and neck (solid, give a feathered silhouette)
        rnd = random.Random(hash(pname) & 0xff)
        for k in range(int((s1 - s0) / 0.45)):
            s = s0 + (k + 0.5) * 0.45
            (p, r, T, S, U), = sp.frames([s])
            for side in (-1, 0, 1):
                a = side * 0.6
                root = p + (U * math.cos(a) + S * math.sin(a)) * r * 0.95
                feather(b, root, -T * 1.0 + U * 0.25 + S * side * 0.3, S, (0.9 + 0.5 * r) * rnd.uniform(0.85, 1.15), 0.5 + 0.18 * r,
                        bend=0.08, n=6)


def head(pieces, P, f):
    f = f.normalized(); u = (Z - f * Z.dot(f)).normalized(); s = f.cross(u).normalized()
    L = lambda x, y, z: P + f * x + s * y + u * z
    hb = pieces['Head']
    # skull: small loft
    prof = [(-0.4, 0.95, 0.95), (0.3, 1.1, 1.08), (0.9, 1.0, 0.98), (1.5, 0.78, 0.76), (1.9, 0.5, 0.52)]
    m = 28
    rings = [[hb.bm.verts.new(L(x, math.sin(2 * math.pi * j / m) * w, math.cos(2 * math.pi * j / m) * h + 0.1)) for j in range(m)]
             for x, w, h in prof]
    for i in range(len(prof) - 1):
        for j in range(m):
            j2 = (j + 1) % m
            q = [rings[i][j], rings[i + 1][j], rings[i + 1][j2], rings[i][j2]]
            under = abs(2 * math.pi * (j + 0.5) / m - math.pi) < math.radians(60)
            hb.face(q, 'Phoenix_Breast' if under else 'Phoenix_Body', [(i / 2, j / m * 1.5), ((i + 1) / 2, j / m * 1.5),
                    ((i + 1) / 2, (j + 1) / m * 1.5), (i / 2, (j + 1) / m * 1.5)], out=sum((v.co for v in q), Vector()) / 4 - L(prof[i][0], 0, 0.1),
                    smooth=True)
    # hooked beak: upper (in the head piece), lower mandible (Beak piece, hinged)
    up = [L(1.6, 0, 0.35), L(2.4, 0, 0.3), L(3.0, 0, 0.1), L(3.25, 0, -0.25), L(3.1, 0, -0.5)]
    tube(hb, up, [0.5, 0.36, 0.22, 0.1, 0.01], 12, 'Phoenix_Beak', squash=0.75)
    bk = pieces['Beak']
    lo = [L(1.6, 0, -0.2), L(2.3, 0, -0.32), L(2.8, 0, -0.35)]
    tube(bk, lo, [0.4, 0.24, 0.02], 10, 'Phoenix_Beak', squash=0.7)
    # eyes
    for side in (1, -1):
        blob(pieces['Eyes'], L(0.95, side * 0.9, 0.35), (0.22, 0.12, 0.16), 'Glow_Amber', subdiv=2, amp=0.0)
        tube(hb, [L(0.5, side * 0.92, 0.6), L(1.0, side * 1.02, 0.66), L(1.5, side * 0.85, 0.52)], [0.08, 0.1, 0.04], 8, 'Phoenix_Beak')  # gold brow
        for k in range(4):                                      # cheek feathers sweeping back
            feather(hb, L(0.4 - 0.25 * k, side * 1.0, -0.1 - 0.15 * k), -f + s * side * 0.5 - u * 0.1, u, 1.6 + 0.2 * k, 0.4,
                    bend=0.1, n=6)
    # crest: curling plumes crowning the head, plus a comb of short feathers
    cr = pieces['Crest']
    for k in range(7):                                          # sweeping crest plumes curling back over the head
        a = (k - 3) * 0.22
        base = L(0.3 - 0.12 * abs(k - 3), a * 1.1, 0.95)
        feather(cr, base, -f * 0.9 + u * 0.8 + s * a * 0.6, s, 3.6 - 0.35 * abs(k - 3), 0.75, bend=-0.35, n=12,
                mat='Phoenix_Plume', twist=0.2 * (k - 3))
    for k in range(6):
        feather(cr, L(0.9 - 0.25 * k, 0, 1.0), u * 1.0 - f * 0.6, s, 0.9 + 0.1 * k, 0.35, bend=-0.15, n=6)
    return f, s, u, L


# ------------------------------------------------------------------------------------------------ wings
def wing_chain(side):
    S = Vector((side * 1.8, 1.4, 1.3))
    E = Vector((side * 7.5, 1.2, 2.6))
    W = Vector((side * 13.0, 1.8, 3.3))
    H = Vector((side * 18.5, 0.6, 3.6))
    return S, E, W, H


def wing(pieces, side):
    b = pieces['Wings']
    S, E, W, H = wing_chain(side)
    arm = [S, S.lerp(E, 0.5) + Vector((0, 0.2, 0.2)), E, E.lerp(W, 0.5) + Vector((0, 0.2, 0.1)), W, W.lerp(H, 0.5), H]
    tube(b, arm, [0.95, 0.7, 0.55, 0.45, 0.4, 0.3, 0.12], 12, 'Phoenix_Body')
    down = Vector((0, 0, 1))
    # primaries: fanned from the hand, longest at the tip, sweeping back toward the wrist
    for k in range(11):
        t = k / 10
        root = W.lerp(H, t)
        ang = math.radians(-12 - 70 * (1 - t))                  # 0 = straight out
        d = Vector((side * math.cos(ang), math.sin(ang), -0.05))
        L = 6.5 + 4.5 * t ** 0.8
        feather(b, root, d, Vector((0, 1, 0)) if abs(d.y) < 0.7 else Vector((1, 0, 0)), L, 1.25, bend=0.06, n=10)
    # secondaries along the forearm, pointing back
    for k in range(14):
        t = k / 13
        root = E.lerp(W, t)
        d = Vector((side * 0.25 * t, -1.0, -0.05))
        feather(b, root, d, Vector((1, 0, 0)), 6.2 - 0.4 * t, 1.35, bend=0.05, n=9)
    # tertials near the body
    for k in range(6):
        t = k / 5
        root = S.lerp(E, 0.3 + 0.7 * t)
        feather(b, root, Vector((side * 0.1, -1.0, -0.05)), Vector((1, 0, 0)), 5.0 + 0.8 * t, 1.3, bend=0.05, n=8)
    # coverts: two overlapping rows on top of the wing
    for row, (Lc, off) in enumerate(((3.2, 0.12), (2.0, 0.22))):
        for k in range(18):
            t = k / 17
            root = (S.lerp(E, t * 2) if t < 0.5 else E.lerp(H, (t - 0.5) * 2)) + Vector((0, 0.1, off))
            feather(b, root, Vector((side * 0.2, -1.0, -0.1)), Vector((1, 0, 0)), Lc * (1.0 - 0.3 * t), 1.0, bend=0.04, n=6,
                    mat='Phoenix_Body' if row == 1 else 'Phoenix_Feather')
    return (S, E, W, H)


# ------------------------------------------------------------------------------------------------ tail, legs, fire
def tail(pieces, base):
    b = pieces['Tail']
    for k in range(9):                                          # fan of broad tail feathers
        a = (k / 8 - 0.5) * 1.3
        d = Vector((math.sin(a), -math.cos(a), -0.12))
        feather(b, base, d, Vector((math.cos(a), math.sin(a), 0)), 8.5 - 2.0 * abs(a), 1.7, bend=0.05, n=10)
    for k, (dx, L, lift) in enumerate(((0.0, 27.0, 1.0), (-1.6, 23.0, -0.6), (1.6, 23.0, -0.6), (-3.2, 19.0, 0.4), (3.2, 19.0, 0.4))):
        pts = []
        for i in range(31):
            t = i / 30
            pts.append(base + Vector((dx * t * 1.6 + 0.8 * dx * math.sin(t * 3), -L * t, lift * 3.0 * math.sin(t * math.pi * 1.3) - 2.5 * t * t)))
        streamer(b, pts, 1.6 if k == 0 else 1.35)
    return base


def leg_chain(side):
    hip = Vector((side * 1.1, -1.2, -1.6))
    knee = hip + Vector((side * 0.2, -1.2, -1.0))
    ankle = knee + Vector((0, -1.6, 0.2))
    toe = ankle + Vector((0, -1.0, -0.1))
    return hip, knee, ankle, toe


def legs(pieces, side):
    b, c = pieces['Legs'], pieces['Talons']
    hip, knee, ankle, toe = leg_chain(side)
    tube(b, [hip, knee], [0.7, 0.45], 10, 'Phoenix_Breast')
    tube(b, [knee, ankle], [0.25, 0.2], 8, 'Phoenix_Beak')
    for k, ang in enumerate((-30, 0, 30, 180)):                 # toes curled under, gold talons
        d = Matrix.Rotation(math.radians(ang), 3, 'Z') @ Vector((0, -1, 0))
        p0 = ankle
        p1 = p0 + d * 0.5 - Vector((0, 0, 0.1))
        p2 = p1 + d * 0.3 - Vector((0, 0, 0.35))
        tube(b, [p0, p1, p2], [0.14, 0.11, 0.09], 6, 'Phoenix_Beak')
        tube(c, [p2, p2 + d * 0.08 - Vector((0, 0, 0.25)), p2 - d * 0.12 - Vector((0, 0, 0.42))], [0.08, 0.05, 0.004], 6, 'Phoenix_Beak')
    return hip, knee, ankle, toe


def fire(pieces, wings, tail_base, head_L):
    b = pieces['FireFX']
    rnd = random.Random(9)
    for (S, E, W, H), side in wings:                           # flames trailing off the flight-feather tips
        for k in range(16):
            t = k / 15
            root = (E.lerp(W, t * 2) if t < 0.5 else W.lerp(H, (t - 0.5) * 2)) + Vector((side * 1.6 * t, -5.2 - 2.2 * t, -0.35))
            ribbon(b, root, Vector((side * 0.3 * t, -1.0, 0.08)), Vector((1, 0, 0)), rnd.uniform(2.5, 5.0), rnd.uniform(0.6, 1.1),
                   bend=Z, curl=0.35, wobble=0.18, phase=k, n=10, mat='Fire_Flame')
        tip = H + Vector((side * 3.5, -2.0, 0))
        for k in range(5):
            ribbon(b, tip, Vector((side * 0.8, -1.0, 0.1 * k - 0.2)), Z, rnd.uniform(3.0, 5.5), 0.9, bend=Z, curl=0.4, phase=k,
                   n=10, mat='Fire_Flame')
    for k in range(14):                                        # tail fire
        a = (k / 13 - 0.5) * 1.6
        root = tail_base + Vector((math.sin(a) * 5, -7.0 - 2 * math.cos(a), -0.3))
        ribbon(b, root, Vector((math.sin(a) * 0.5, -1.0, 0.25)), Vector((1, 0, 0)), rnd.uniform(3.0, 6.0), rnd.uniform(0.7, 1.2),
               bend=Z, curl=0.4, wobble=0.2, phase=k, n=10, mat='Fire_Flame')
    for k in range(9):                                         # crown of flame over the crest
        a = (k / 8 - 0.5) * 1.8
        root = head_L(0.0 - 0.3 * abs(a), a * 0.6, 1.4)
        ribbon(b, root, Vector((math.sin(a) * 0.4, -0.8, 1.0)), Vector((1, 0, 0)), rnd.uniform(2.0, 3.6), 0.6, bend=Vector((0, -1, 0)),
               curl=0.4, phase=k, n=8, mat='Fire_Flame')


# ------------------------------------------------------------------------------------------------ build + rig
def build():
    sp = Spine(CTRL, dense=1500)
    pieces = {n: B() for n in PIECES}
    s_neck = sp.s_of_ctrl(NECK_I)
    body_loft(pieces, sp, s_neck)
    pe, re_, Te = sp.at(sp.length)
    f, s, u, L = head(pieces, pe - Te * 0.3, Vector((0, 1, -0.15)))
    wings = [(wing(pieces, side), side) for side in (1, -1)]
    tail_base = sp.at(0.4)[0]
    tail(pieces, tail_base)
    leg_data = {('R' if side > 0 else 'L'): legs(pieces, side) for side in (1, -1)}
    fire(pieces, wings, tail_base, L)
    rig = make_rig(sp, s_neck, L, wings, tail_base, leg_data)
    return pieces, rig


def make_rig(sp, s_neck, L, wings, tail_base, leg_data):
    bones = [('Root', Vector((0, 0, 0)), Vector((0, 1.5, 0)), None)]
    chain = []
    for i in range(3):
        s0, s1 = s_neck * i / 3, s_neck * (i + 1) / 3
        bones.append((f'Spine{i + 1:02d}', sp.at(s0)[0], sp.at(s1)[0], 'Root' if i == 0 else f'Spine{i:02d}')); chain.append((f'Spine{i + 1:02d}', s0, s1))
    for i in range(2):
        s0 = s_neck + (sp.length - s_neck) * i / 2; s1 = s_neck + (sp.length - s_neck) * (i + 1) / 2
        bones.append((f'Neck{i + 1:02d}', sp.at(s0)[0], sp.at(s1)[0], 'Spine03' if i == 0 else 'Neck01')); chain.append((f'Neck{i + 1:02d}', s0, s1))
    bones.append(('Head', sp.at(sp.length)[0], L(2.0, 0, 0.1), 'Neck02')); chain.append(('Head', sp.length, sp.length + 4))
    bones.append(('Beak', L(1.6, 0, -0.2), L(2.8, 0, -0.35), 'Head'))
    wing_b = {}
    for (S, E, W, H), side in wings:
        tag = 'R' if side > 0 else 'L'
        segs = [(f'{tag}_Wing1', S, E), (f'{tag}_Wing2', E, W), (f'{tag}_Wing3', W, H)]
        for k, (n, a, c) in enumerate(segs):
            bones.append((n, a, c, 'Spine03' if k == 0 else segs[k - 1][0]))
        wing_b[tag] = segs
    tail_b = []
    for i in range(6):
        y0, y1 = tail_base.y - 27.0 * (i / 6) ** 1.2, tail_base.y - 27.0 * ((i + 1) / 6) ** 1.2
        bones.append((f'Tail{i + 1:02d}', Vector((0, y0, tail_base.z)), Vector((0, y1, tail_base.z)), 'Spine01' if i == 0 else f'Tail{i:02d}'))
        tail_b.append((f'Tail{i + 1:02d}', y0, y1))
    leg_b = {}
    for tag, (hip, knee, ankle, toe) in leg_data.items():
        segs = [(f'{tag}_Thigh', hip, knee), (f'{tag}_Shin', knee, ankle), (f'{tag}_Foot', ankle, toe)]
        for k, (n, a, c) in enumerate(segs):
            bones.append((n, a, c, 'Spine01' if k == 0 else segs[k - 1][0]))
        leg_b[tag] = segs
    return dict(bones=bones, chain=chain, spine=sp, wings=wing_b, tail=tail_b, legs=leg_b, tail_base=tail_base)


def _chain_blend(cs, x):
    """cs: list of (centre, name) sorted by centre; linear blend between neighbours."""
    if x <= cs[0][0]: return {cs[0][1]: 1.0}
    if x >= cs[-1][0]: return {cs[-1][1]: 1.0}
    for (c0, n0), (c1, n1) in zip(cs, cs[1:]):
        if c0 <= x <= c1:
            t = (x - c0) / (c1 - c0); t = t * t * (3 - 2 * t)
            return {n0: 1 - t, n1: t}


def _seg(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length


def weights_for(rig, piece, p):
    if piece in ('Head', 'Crest', 'Eyes'): return {'Head': 1.0}
    if piece == 'Beak': return {'Beak': 1.0}
    if piece in ('Legs', 'Talons'):
        best = min(((min(_seg(p, a, b) for _, a, b in segs), segs) for segs in rig['legs'].values()), key=lambda x: x[0])[1]
        if piece == 'Talons': return {best[2][0]: 1.0}
        ds = sorted(((1.0 / (_seg(p, a, b) ** 4 + 1e-4), n) for n, a, b in best), reverse=True)[:2]
        tot = sum(w for w, _ in ds)
        return {n: w / tot for w, n in ds}
    ax = abs(p.x)
    if piece == 'Wings' or (piece == 'FireFX' and ax > 2.4 and p.y > rig['tail_base'].y - 6):
        segs = rig['wings']['R' if p.x > 0 else 'L']
        cs = [(abs((a.x + b.x) / 2), n) for n, a, b in segs]
        w = _chain_blend(cs, ax)
        if ax < abs(segs[0][1].x) + 0.8:                       # blend the wing root into the chest
            k = max(0.0, (abs(segs[0][1].x) + 0.8 - ax) / 1.6)
            w = {n: v * (1 - k) for n, v in w.items()}; w['Spine03'] = w.get('Spine03', 0) + k
        return w
    if piece in ('Tail', 'FireFX') and p.y < rig['tail_base'].y + 0.3:
        cs = [(-(y0 + y1) / 2, n) for n, y0, y1 in rig['tail']]
        w = _chain_blend(cs, -p.y)
        return w
    sp = rig['spine']
    s = sp.nearest_s(p, step=2)
    if piece == 'FireFX' and s >= sp.length - 0.3: return {'Head': 1.0}
    cs = [((a + b) / 2, n) for n, a, b in rig['chain']]
    return _chain_blend(cs, s)
