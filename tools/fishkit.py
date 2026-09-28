"""Fishing: three Edo-period rods, float, hook, bamboo creel, and eight Japanese fish.

Rods: origin = centre of the grip (hand), the rod points FRONT (Blender +Y -> Roblox -Z) and rises with its natural
droop; line tie at the tip (tip position given in the manifest notes for a RopeConstraint/Beam).
Fish: origin = centre of the body, head FRONT (-Z), back up. Body UV: U snout -> tail, V back -> belly (mirrored).
Fins: fan strips, V root -> edge (the fin textures have alpha toward the edge).
"""
import math, random
from mathutils import Vector, Matrix
from geo import Builder, lathe, tube
from harborkit import blob

ROD_MATS = ['Bamboo', 'Rope', 'Cloth_White', 'Black_Lacquer', 'Red_Lacquer', 'Gold_Leaf', 'Tsuka_Wrap', 'Timber_Dark',
            'Timber_Light', 'Iron_Wrought', 'Straw']
FISH_MATS = ['Fish_Ayu', 'Fish_Koi', 'Fish_Koi_Gold', 'Fish_Tai', 'Fish_Saba', 'Fish_Maguro', 'Fish_Fugu', 'Fish_Unagi',
             'Fish_Fin', 'Fish_Fin_Red', 'Fish_Fin_Yellow', 'Fish_Fin_Gold', 'Fish_Eye']


def RB():
    return Builder(ROD_MATS)


def FB():
    return Builder(FISH_MATS)


# ================================================================================================ rods
def rod_axis(y, L, droop):
    """Rod centre line: along +Y from the butt, drooping at the tip."""
    t = max(0.0, y) / L
    return Vector((0.0, y, -droop * t * t))


def rod_tube(b, y0, y1, r0, r1, mat, L, droop, n=None, bumps=()):
    n = n or max(4, int((y1 - y0) / 0.2))
    pts, rad = [], []
    for i in range(n + 1):
        y = y0 + (y1 - y0) * i / n
        r = r0 + (r1 - r0) * i / n
        for yb, h, w in bumps:                                  # bamboo nodes
            r *= 1 + h * math.exp(-((y - yb) / w) ** 2)
        pts.append(rod_axis(y, L, droop)); rad.append(r)
    tube(b, pts, rad, 10, mat, up=Vector((0, 0, 1)))


def ring_at(b, y, r, w, mat, L, droop):
    rod_tube(b, y - w / 2, y + w / 2, r, r, mat, L, droop, n=2)


def rod_radius(y, L, r_butt, r_tip, y0):
    return r_butt + (r_tip - r_butt) * (y - y0) / (L - y0)


def rod_bamboo():
    """Takezao: a single natural bamboo pole, rope-bound grip, line tied at the tip. 7 long."""
    b = RB()
    L, droop, y0 = 6.4, 0.35, -0.6
    nodes = [y0 + 0.2 + 0.85 * k for k in range(9)]
    rod_tube(b, y0, L, 0.08, 0.014, 'Bamboo', L, droop, n=70, bumps=[(yn, 0.12, 0.03) for yn in nodes])
    rod_tube(b, -0.5, 0.5, 0.095, 0.088, 'Rope', L, droop, n=10)                     # rope grip
    for yy in (-0.52, 0.52):
        ring_at(b, yy, 0.1, 0.05, 'Rope', L, droop)
    lathe(b, (0, y0, 0), [(0.0, 0.0), (0.082, 0.0)], 10, 'Bamboo')                   # butt end (cut face)
    ring_at(b, L - 0.12, 0.022, 0.1, 'Cloth_White', L, droop)                        # line tie
    return b, rod_axis(L, L, droop)


def rod_lacquered():
    """Edo wazao: four jointed bamboo sections, black lacquer with red bands and silk-wrapped ferrules. 9 long."""
    b = RB()
    L, droop, y0 = 8.2, 0.45, -0.8
    joints = [y0 + (L - y0) * k / 4 for k in range(1, 4)]
    rod_tube(b, y0, L, 0.085, 0.013, 'Black_Lacquer', L, droop, n=80)
    for yj in joints:
        r = rod_radius(yj, L, 0.085, 0.013, y0)
        rod_tube(b, yj - 0.18, yj + 0.18, r * 1.14, r * 1.12, 'Tsuka_Wrap', L, droop, n=4)
        ring_at(b, yj - 0.2, r * 1.2, 0.04, 'Gold_Leaf', L, droop)
        ring_at(b, yj + 0.2, r * 1.2, 0.04, 'Gold_Leaf', L, droop)
        for k in (-1, 1):
            ring_at(b, yj + k * 0.45, r * 1.06, 0.08, 'Red_Lacquer', L, droop)
    rod_tube(b, -0.7, 0.6, 0.1, 0.094, 'Tsuka_Wrap', L, droop, n=12)                  # braided silk grip
    ring_at(b, 0.62, 0.105, 0.05, 'Gold_Leaf', L, droop)
    cap = Builder(ROD_MATS)
    lathe(cap, (0, 0, 0), [(0.0, 0.0), (0.07, 0.01), (0.1, 0.07), (0.1, 0.14)], 12, 'Gold_Leaf')
    _rotate_into(b, cap, Matrix.Translation((0, y0 - 0.14, 0)) @ Matrix.Rotation(-math.pi / 2, 4, 'X'))
    rod_tube(b, L - 0.5, L, 0.022, 0.014, 'Red_Lacquer', L, droop, n=4)                # red tip
    ring_at(b, L - 0.1, 0.022, 0.06, 'Cloth_White', L, droop)
    return b, rod_axis(L, L, droop)


def rod_master():
    """Master rod: red lacquer with black sections, gold-leaf fittings, guide rings and a wooden hand reel (tebata)."""
    b = RB()
    L, droop, y0 = 9.0, 0.5, -0.9
    rod_tube(b, y0, L, 0.09, 0.014, 'Red_Lacquer', L, droop, n=90)
    for k in range(5):                                                                 # black lacquer bands + gold rings
        yj = 1.2 + k * 1.6
        r = rod_radius(yj, L, 0.09, 0.014, y0)
        rod_tube(b, yj - 0.3, yj + 0.3, r * 1.05, r * 1.04, 'Black_Lacquer', L, droop, n=4)
        for s in (-1, 1):
            ring_at(b, yj + s * 0.32, r * 1.14, 0.04, 'Gold_Leaf', L, droop)
    rod_tube(b, -0.8, 0.5, 0.108, 0.1, 'Timber_Dark', L, droop, n=12)                   # cherry-bark grip
    for yy in (-0.82, 0.52):
        ring_at(b, yy, 0.115, 0.06, 'Gold_Leaf', L, droop)
    cap = Builder(ROD_MATS)
    lathe(cap, (0, 0, 0), [(0.0, 0.0), (0.08, 0.01), (0.115, 0.08), (0.11, 0.16)], 12, 'Gold_Leaf')
    _rotate_into(b, cap, Matrix.Translation((0, y0 - 0.16, 0)) @ Matrix.Rotation(-math.pi / 2, 4, 'X'))
    # guide rings under the rod
    guides = [1.9, 3.5, 5.1, 6.6, 7.9, L - 0.1]
    for yg in guides:
        p = rod_axis(yg, L, droop)
        r = rod_radius(yg, L, 0.09, 0.014, y0)
        rr = 0.035 + r * 0.3
        c = p - Vector((0, 0, r + rr + 0.01))
        ring = [c + Vector((rr * math.cos(2 * math.pi * k / 10), 0, rr * math.sin(2 * math.pi * k / 10))) for k in range(11)]
        tube(b, ring, [0.008] * 11, 5, 'Gold_Leaf', caps=False)
        tube(b, [p - Vector((0, 0, r * 0.8)), c + Vector((0, 0, rr))], [0.01, 0.01], 5, 'Gold_Leaf')
    # wooden hand reel under the grip: two discs, hub, wound line, crank knob, gold bracket
    rc = Vector((0, 0.95, -0.42))
    for sx in (-1, 1):
        tube(b, [rc + Vector((sx * 0.1, 0, 0)), rc + Vector((sx * 0.13, 0, 0))], [0.34, 0.34], 20, 'Timber_Dark', up=Vector((0, 0, 1)))
    tube(b, [rc + Vector((-0.1, 0, 0)), rc + Vector((0.1, 0, 0))], [0.22, 0.22], 20, 'Cloth_White', up=Vector((0, 0, 1)))   # line
    tube(b, [rc + Vector((-0.2, 0, 0)), rc + Vector((0.2, 0, 0))], [0.05, 0.05], 8, 'Timber_Light', up=Vector((0, 0, 1)))
    kb = rc + Vector((0.14, 0.2, 0.18))
    tube(b, [rc + Vector((0.14, 0, 0)), kb], [0.025, 0.025], 6, 'Gold_Leaf')
    tube(b, [kb, kb + Vector((0.14, 0, 0))], [0.04, 0.035], 8, 'Black_Lacquer', up=Vector((0, 0, 1)))
    for sy in (-0.18, 0.18):
        tube(b, [rod_axis(rc.y + sy, L, droop) - Vector((0, 0, 0.09)), rc + Vector((0, sy, 0.3))], [0.018, 0.018], 6, 'Gold_Leaf')
    # line from the reel along the guides to the tip
    line = [rc + Vector((0, 0.05, -0.22))] + [rod_axis(yg, L, droop) - Vector((0, 0, rod_radius(yg, L, 0.09, 0.014, y0) * 1.3 + 0.07))
                                              for yg in guides]
    tube(b, line, [0.006] * len(line), 4, 'Cloth_White')
    return b, rod_axis(L, L, droop)


def _rotate_into(dst, src, M):
    from castlekit import mesh_join
    for v in src.bm.verts: v.co = M @ v.co
    mesh_join(dst, src)


def float_uki():
    """Red-and-white float (uki) with an antenna, 0.55 tall; origin = line eye at the bottom."""
    b = RB()
    lathe(b, (0, 0, 0), [(0.0, 0.0), (0.02, 0.02), (0.07, 0.1), (0.1, 0.2), (0.1, 0.24)], 12, 'Red_Lacquer', cap_top=False)
    lathe(b, (0, 0, 0), [(0.1, 0.24), (0.09, 0.32), (0.05, 0.42), (0.012, 0.46), (0.0, 0.47)], 12, 'Cloth_White', cap_bottom=False)
    tube(b, [Vector((0, 0, 0.45)), Vector((0, 0, 0.62))], [0.008, 0.005], 5, 'Black_Lacquer', up=Vector((0, 1, 0)))
    ring = [Vector((0.02 * math.cos(2 * math.pi * k / 8), 0, -0.02 + 0.02 * math.sin(2 * math.pi * k / 8))) for k in range(9)]
    tube(b, ring, [0.005] * 9, 4, 'Iron_Wrought', caps=False)
    return b


def hook():
    """Hand-forged J hook with barb and eye, plus a round sinker; 0.3 long. Origin = the eye."""
    b = RB()
    pts = [Vector((0, 0, 0)), Vector((0, 0, -0.18))]
    for k in range(9):
        a = math.pi * k / 8
        pts.append(Vector((0, 0.06 - 0.06 * math.cos(a), -0.18 - 0.06 * math.sin(a))))
    pts.append(Vector((0, 0.125, -0.12)))
    tube(b, pts, [0.009] * (len(pts) - 1) + [0.002], 6, 'Iron_Wrought', up=Vector((1, 0, 0)))
    tube(b, [Vector((0, 0.122, -0.15)), Vector((0, 0.095, -0.13))], [0.006, 0.001], 4, 'Iron_Wrought', up=Vector((1, 0, 0)))  # barb
    ring = [Vector((0, 0.018 * math.sin(2 * math.pi * k / 8), 0.018 + 0.018 * math.cos(2 * math.pi * k / 8))) for k in range(9)]
    tube(b, ring, [0.006] * 9, 4, 'Iron_Wrought', caps=False, up=Vector((1, 0, 0)))
    blob(b, (0, 0, 0.18), (0.035, 0.035, 0.035), 'Iron_Wrought', subdiv=2, amp=0.0)
    tube(b, [Vector((0, 0, 0.04)), Vector((0, 0, 0.15))], [0.003, 0.003], 4, 'Cloth_White', up=Vector((1, 0, 0)))
    return b


def creel():
    """Woven bamboo fish creel (biku) with a lid and rope strap, 1.4 tall; origin = bottom centre."""
    b = RB()
    lathe(b, (0, 0, 0), [(0.0, 0.0), (0.42, 0.02), (0.58, 0.3), (0.6, 0.7), (0.5, 1.0), (0.3, 1.18), (0.28, 1.2)], 20, 'Straw', cap_top=False)
    lathe(b, (0, 0, 1.18), [(0.36, 0.0), (0.36, 0.06), (0.2, 0.14), (0.0, 0.16)], 20, 'Bamboo', cap_bottom=True)
    for z in (0.02, 0.62, 1.12):
        rr = {0.02: 0.43, 0.62: 0.61, 1.12: 0.36}[z]
        ring = [Vector((rr * math.cos(2 * math.pi * k / 20), rr * math.sin(2 * math.pi * k / 20), z)) for k in range(21)]
        tube(b, ring, [0.025] * 21, 5, 'Bamboo', caps=False)
    strap = [Vector((0.6 * math.cos(math.pi * k / 12), 0.0, 0.7 + 1.1 * math.sin(math.pi * k / 12))) for k in range(13)]
    tube(b, strap, [0.03] * 13, 6, 'Rope')
    return b


# ================================================================================================ fish
# species: length L, max height H and width W (fractions of L), shape exponents, peduncle ratio, textures
SPECIES = {
    'Ayu':    dict(L=1.1, H=0.19, W=0.1, a=0.55, b=0.8, ped=0.07, mat='Fish_Ayu', fin='Fish_Fin', tail='fork', hump=0.02),
    'Koi':    dict(L=1.8, H=0.25, W=0.16, a=0.6, b=0.7, ped=0.09, mat='Fish_Koi', fin='Fish_Fin_Red', tail='round', hump=0.03, barbels=True),
    'Koi_Gold': dict(L=1.8, H=0.25, W=0.16, a=0.6, b=0.7, ped=0.09, mat='Fish_Koi_Gold', fin='Fish_Fin_Gold', tail='round', hump=0.03, barbels=True),
    'Tai':    dict(L=1.6, H=0.38, W=0.14, a=0.5, b=0.6, ped=0.08, mat='Fish_Tai', fin='Fish_Fin_Red', tail='fork', hump=0.08, spiny=True),
    'Saba':   dict(L=1.4, H=0.2, W=0.13, a=0.55, b=0.9, ped=0.05, mat='Fish_Saba', fin='Fish_Fin', tail='deepfork', hump=0.01, finlets=5),
    'Maguro': dict(L=5.0, H=0.27, W=0.2, a=0.5, b=1.0, ped=0.04, mat='Fish_Maguro', fin='Fish_Fin', tail='crescent', hump=0.02, finlets=8,
                   finlet_mat='Fish_Fin_Yellow'),
    'Fugu':   dict(L=0.9, H=0.46, W=0.42, a=0.55, b=0.45, ped=0.1, mat='Fish_Fugu', fin='Fish_Fin', tail='round', hump=0.0, small_fins=True),
    'Unagi':  dict(L=3.0, H=0.07, W=0.06, a=0.12, b=0.35, ped=0.3, mat='Fish_Unagi', fin='Fish_Fin', tail='eel', hump=0.0, eel=True),
}


def profile(sp, u):
    """Half-height, half-width and centre offset (studs) at u (0 snout .. 1 tail base)."""
    L = sp['L']
    base = math.sin(math.pi * min(1.0, u) ** sp['a']) ** sp['b'] if u > 0 else 0.0
    if sp.get('eel'):
        base = min(1.0, (u / 0.06) ** 0.5) * (1 - 0.7 * u ** 3)
    base = max(base, sp['ped'] * min(1.0, u / 0.1)) if u > 0.5 else base
    h = sp['H'] * L * 0.5 * base
    w = sp['W'] * L * 0.5 * base
    c = sp['hump'] * L * math.sin(math.pi * u) * (1 - u)
    return h, w, c


def fin_fan(b, roots, tips, mat, nrm):
    """Double-sided fin membrane between matching root and edge point lists; UV U along the root, V root -> edge."""
    n = len(roots) - 1
    for side, off in ((1, 0.004), (-1, -0.004)):
        R = [b.bm.verts.new(p + nrm * off) for p in roots]
        T = [b.bm.verts.new(p + nrm * off) for p in tips]
        for i in range(n):
            q = [R[i], R[i + 1], T[i + 1], T[i]]
            b.face(q, mat, [(i / n, 0), ((i + 1) / n, 0), ((i + 1) / n, 1), (i / n, 1)], out=nrm * side, smooth=True)


def fish(name):
    sp = SPECIES[name]
    L = sp['L']
    b = FB()
    n, m = (80 if sp.get('eel') else 36), 24
    ys = [L / 2 - L * i / n for i in range(n + 1)]              # head at +Y
    rings = []
    for i, y in enumerate(ys):
        u = i / n
        h, w, c = profile(sp, u)
        ring = []
        for j in range(m):
            a = 2 * math.pi * j / m                            # 0 = back
            e = 2.2
            sx, cz = math.sin(a), math.cos(a)
            x = math.copysign(abs(sx) ** (2 / e), sx) * w
            z = math.copysign(abs(cz) ** (2 / e), cz) * h * (1.0 if cz > 0 else 0.92) + c
            ring.append(Vector((x, y, z)))
        rings.append(ring)
    if sp.get('eel'):                                          # gentle S-curve for the eel
        for i, ring in enumerate(rings):
            dx = 0.12 * L * math.sin(2 * math.pi * i / n * 1.2)
            for p in ring: p.x += dx
    V = [[b.bm.verts.new(p) for p in ring] for ring in rings]
    for i in range(n):
        for j in range(m):
            j2 = (j + 1) % m
            q = [V[i][j], V[i + 1][j], V[i + 1][j2], V[i][j2]]
            va = lambda jj: (min(jj, m - jj) / (m / 2))        # 0 back -> 1 belly, mirrored
            c = (rings[i][0] + rings[i][m // 2] + rings[i + 1][0] + rings[i + 1][m // 2]) / 4
            b.face(q, sp['mat'], [(i / n, va(j)), ((i + 1) / n, va(j)), ((i + 1) / n, va(j + 1)), (i / n, va(j + 1))],
                   out=sum((v.co for v in q), Vector()) / 4 - c, smooth=True)
    nose = b.bm.verts.new(Vector((rings[0][0].x, L / 2 + 0.01 * L, profile(sp, 0.02)[2])))
    for j in range(m):
        b.face([V[0][(j + 1) % m], V[0][j], nose], sp['mat'], [(0, 0.5), (0, 0.5), (0, 0.5)], out=Vector((0, 1, 0)), smooth=True)
    tail_ring = rings[-1]
    tc = sum(tail_ring, Vector()) / m
    endv = b.bm.verts.new(tc - Vector((0, 0.01 * L, 0)))
    for j in range(m):
        b.face([V[-1][j], V[-1][(j + 1) % m], endv], sp['mat'], [(1, 0.5), (1, 0.5), (1, 0.5)], out=Vector((0, -1, 0)), smooth=True)

    X = Vector((1, 0, 0))
    def top(u): return Vector((0, L / 2 - L * u, profile(sp, u)[2] + profile(sp, u)[0]))
    def bot(u): return Vector((0, L / 2 - L * u, profile(sp, u)[2] - profile(sp, u)[0] * 0.92))
    fin = sp['fin']
    # caudal fin
    ty = -L / 2
    hp = max(profile(sp, 0.98)[0], 0.02 * L)
    shape = sp['tail']
    k = 9
    roots = [Vector((tc.x, ty + 0.01, tc.z - hp + 2 * hp * i / (k - 1))) for i in range(k)]
    span = {'fork': 0.22, 'deepfork': 0.26, 'crescent': 0.3, 'round': 0.2, 'eel': 0.0}[shape] * L
    tips = []
    for i in range(k):
        t = i / (k - 1) * 2 - 1                                # -1 bottom .. 1 top
        if shape == 'round':
            reach = span * (0.75 + 0.25 * math.cos(t * math.pi / 2)); zz = t * span * 0.75
        elif shape in ('fork', 'deepfork'):
            notch = 0.45 if shape == 'fork' else 0.25
            reach = span * (notch + (1 - notch) * abs(t) ** 0.8); zz = t * span * (0.85 if shape == 'fork' else 1.0)
        elif shape == 'crescent':
            reach = span * (0.2 + 0.8 * abs(t) ** 0.6); zz = t * span * 1.2
        else:
            reach, zz = 0.0, 0.0
        tips.append(Vector((tc.x, ty - reach, tc.z + zz)))
    if shape != 'eel':
        fin_fan(b, roots, tips, fin, X)
    if sp.get('eel'):                                          # continuous dorsal / anal ribbon fin, tail fin merged
        rr = [top(u) + Vector((0, 0, -0.002)) for u in [0.35 + 0.65 * i / 20 for i in range(21)]]
        tt = [p + Vector((0, 0, 0.035 * L * (0.4 + 0.6 * i / 20))) for i, p in enumerate(rr)]
        for lst in (rr, tt):
            for i, p in enumerate(lst):
                u = 0.35 + 0.65 * i / 20
                idx = min(int(u * n), n)
                p.x += 0.12 * L * math.sin(2 * math.pi * idx / n * 1.2)
        fin_fan(b, rr, tt, fin, X)
        rb = [bot(u) for u in [0.55 + 0.45 * i / 14 for i in range(15)]]
        tb = [p - Vector((0, 0, 0.03 * L * (0.4 + 0.6 * i / 14))) for i, p in enumerate(rb)]
        for lst in (rb, tb):
            for i, p in enumerate(lst):
                u = 0.55 + 0.45 * i / 14
                idx = min(int(u * n), n)
                p.x += 0.12 * L * math.sin(2 * math.pi * idx / n * 1.2)
        fin_fan(b, rb, tb, fin, X)
    else:
        # dorsal fin(s)
        if sp.get('finlets'):
            d1 = [top(u) for u in [0.28 + 0.12 * i / 6 for i in range(7)]]
            fin_fan(b, d1, [p + Vector((0, -0.02 * L, (0.1 if name == 'Maguro' else 0.09) * L * math.sin(math.pi * (i / 6) ** 0.6 + 0.2)))
                            for i, p in enumerate(d1)], fin, X)
            d2 = [top(u) for u in [0.52 + 0.08 * i / 4 for i in range(5)]]
            fin_fan(b, d2, [p + Vector((0, -0.04 * L, 0.08 * L * (1 - i / 4) + 0.01 * L)) for i, p in enumerate(d2)], fin, X)
            a2 = [bot(u) for u in [0.54 + 0.08 * i / 4 for i in range(5)]]
            fin_fan(b, a2, [p + Vector((0, -0.04 * L, -0.07 * L * (1 - i / 4) - 0.01 * L)) for i, p in enumerate(a2)], fin, X)
            fm = sp.get('finlet_mat', fin)
            for kk in range(sp['finlets']):
                u = 0.68 + 0.26 * kk / max(1, sp['finlets'] - 1)
                for base, sgn in ((top(u), 1), (bot(u), -1)):
                    fin_fan(b, [base + Vector((0, 0.012 * L, 0)), base - Vector((0, 0.012 * L, 0))],
                            [base + Vector((0, -0.01 * L, sgn * 0.025 * L)), base + Vector((0, -0.03 * L, sgn * 0.02 * L))], fm, X)
        else:
            u0, u1 = (0.25, 0.7) if not sp.get('small_fins') else (0.6, 0.75)
            hmax = (0.13 if sp.get('spiny') else 0.09) * L * (0.5 if sp.get('small_fins') else 1.0)
            d = [top(u) for u in [u0 + (u1 - u0) * i / 10 for i in range(11)]]
            tip = []
            for i, p in enumerate(d):
                t = i / 10
                hh = hmax * (math.sin(math.pi * min(1, t * 1.1)) ** 0.5 if not sp.get('spiny') else (1 - 0.5 * t)) + 0.005
                if sp.get('spiny') and i % 2 == 0: hh *= 1.15
                tip.append(p + Vector((0, -0.03 * L, hh)))
            fin_fan(b, d, tip, fin, X)
            a0, a1 = (0.62, 0.8) if not sp.get('small_fins') else (0.62, 0.76)
            an = [bot(u) for u in [a0 + (a1 - a0) * i / 6 for i in range(7)]]
            fin_fan(b, an, [p + Vector((0, -0.03 * L, -hmax * 0.6 * math.sin(math.pi * min(1, (i / 6) * 1.1)) ** 0.5 - 0.005))
                            for i, p in enumerate(an)], fin, X)
        # pectoral + pelvic pairs
        for sgn in (1, -1):
            u = 0.26
            h, w, c = profile(sp, u)
            base = Vector((sgn * w * 0.92, L / 2 - L * u, c - h * 0.25))
            pl = 0.13 * L * (0.7 if sp.get('small_fins') else 1.0)
            roots = [base + Vector((0, 0.015 * L - 0.03 * L * i / 4, 0.01 * L - 0.02 * L * i / 4)) for i in range(5)]
            tips = [r + Vector((sgn * pl * 0.45, -pl * (0.6 + 0.4 * math.sin(math.pi * i / 4)), -pl * 0.25)) for i, r in enumerate(roots)]
            fin_fan(b, roots, tips, fin, Vector((0, 0, 1)))
            if not sp.get('small_fins'):
                u = 0.45
                h, w, c = profile(sp, u)
                base = Vector((sgn * w * 0.5, L / 2 - L * u, c - h * 0.85))
                roots = [base + Vector((0, 0.01 * L - 0.02 * L * i / 3, 0)) for i in range(4)]
                tips = [r + Vector((sgn * 0.03 * L, -0.07 * L * (0.7 + 0.3 * math.sin(math.pi * i / 3)), -0.05 * L)) for i, r in enumerate(roots)]
                fin_fan(b, roots, tips, fin, Vector((0, 0, 1)))
    # eyes
    u = 0.1 if not sp.get('eel') else 0.035
    h, w, c = profile(sp, u)
    er = max(0.02 * L, 0.02) * (1.6 if name == 'Fugu' else 1.0) * (0.55 if name == 'Maguro' else 1.0)
    for sgn in (1, -1):
        ex = sgn * w * 0.85
        blob(b, (ex, L / 2 - L * u, c + h * 0.3), (er * 0.7, er, er), 'Fish_Eye', subdiv=2, amp=0.0, smooth=True)
    if sp.get('barbels'):
        for sgn in (1, -1):
            p0 = Vector((sgn * 0.02 * L, L / 2 - 0.01 * L, profile(sp, 0.03)[2] - 0.01 * L))
            tube(b, [p0, p0 + Vector((sgn * 0.03 * L, -0.02 * L, -0.03 * L)), p0 + Vector((sgn * 0.05 * L, -0.05 * L, -0.04 * L))],
                 [0.006 * L, 0.004 * L, 0.001], 5, sp['mat'])
    # recentre: origin at the middle of the body
    lo = Vector([min(v.co[k] for v in b.bm.verts) for k in range(3)])
    hi = Vector([max(v.co[k] for v in b.bm.verts) for k in range(3)])
    cc = (lo + hi) / 2
    for v in b.bm.verts: v.co -= cc
    return b
