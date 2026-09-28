"""Hero unit: giant iron samurai mech (HO_Mech_Tetsujin), ~40 studs tall, Roblox-ready and rigged.

Riveted iron war machine dressed as a samurai: kabuto helmet with huge gold kuwagata horns and crest, iron menpo
with a glowing eye slit, layered sode shoulder plates, laced do chest lames, kusazuri skirt plates, armoured
limbs with pistons, a big cannon built into the middle of the chest (glowing core), smoke stacks and a banner on the
back, and a huge dark-steel nodachi with a glowing edge in the right hand.

Every piece is rigid (weighted 100 % to one bone) - it moves like machinery.
Blender axes: front = +Y (Roblox -Z), up = +Z, feet on z = 0, origin between the feet.
"""
import math, random
from mathutils import Vector, Matrix
from geo import Builder, lathe, tube
from harborkit import blob
from castlekit import mesh_join

MATS = ['Mech_Plate', 'Steel_Dark', 'Black_Lacquer', 'Red_Lacquer', 'Gold_Leaf', 'Cloth_Crimson', 'Iron_Wrought',
        'Shadow_Black', 'Glow_Red', 'Glow_Amber', 'Steel_Blade', 'Tsuka_Wrap', 'Navy_Lacquer', 'Timber_Dark', 'Cloth_White']
UVD = 0.125          # Mech_Plate tile = 8 studs (panels of 2 studs)


def B():
    return Builder(MATS)


# ------------------------------------------------------------------------------------------------ helpers
def cbox(b, c, size, mat='Mech_Plate', ch=0.18, axis='y'):
    """Box with chamfered edges around `axis` (prism of a chamfered rectangle)."""
    c = Vector(c); sx, sy, sz = size
    X, Y, Zv = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
    if axis == 'y':
        u, v, n, w, h, d = X, Zv, Y, sx, sz, sy
    elif axis == 'x':
        u, v, n, w, h, d = Y, Zv, X, sy, sz, sx
    else:
        u, v, n, w, h, d = X, Y, Zv, sx, sy, sz
    k = min(ch, w * 0.3, h * 0.3)
    out = [(-w / 2 + k, -h / 2), (w / 2 - k, -h / 2), (w / 2, -h / 2 + k), (w / 2, h / 2 - k), (w / 2 - k, h / 2), (-w / 2 + k, h / 2),
           (-w / 2, h / 2 - k), (-w / 2, -h / 2 + k)]
    b.prism(out, c - n * d / 2, u, v, n, d, mat, uvd=UVD)


def place(dst, src, M):
    for v in src.bm.verts: v.co = M @ v.co
    mesh_join(dst, src)


def seg_frame(a, b, side=Vector((1, 0, 0))):
    """Matrix mapping local +Z to (b - a), local X roughly to `side`, origin at a."""
    z = (b - a).normalized()
    x = (side - z * side.dot(z))
    if x.length < 1e-4: x = Vector((0, 1, 0)) - z * z.y
    x.normalize()
    y = z.cross(x)
    R = Matrix((x, y, z)).transposed().to_4x4()
    return Matrix.Translation(a) @ R


def rivets(b, pts, r=0.12, mat='Iron_Wrought'):
    for p in pts:
        blob(b, p, (r, r, r), mat, subdiv=1, amp=0.0)


def lames(b, x0, x1, z_top, n, h, y, depth, mats, curve=0.25, gap=0.05, tilt=0.12):
    """Stacked horizontal armour lames on a front face at y (facing +Y), slightly bowed and tilted out."""
    for k in range(n):
        z1 = z_top - k * (h + gap); z0 = z1 - h
        mat = mats[k % len(mats)]
        secs = []
        for i in range(9):
            x = x0 + (x1 - x0) * i / 8
            bow = curve * (1 - ((2 * i / 8) - 1) ** 2)
            yy = y + bow + tilt * k * 0.2
            secs.append([Vector((x, yy - depth, z0)), Vector((x, yy + 0.08, z0 - 0.02)), Vector((x, yy, z1)), Vector((x, yy - depth, z1))])
        from geo import loft
        loft(b, secs, mat)


# ------------------------------------------------------------------------------------------------ skeleton layout
J = dict(
    pelvis=Vector((0, 0, 18.5)), waist=Vector((0, 0, 21.0)), neck=Vector((0, 0, 32.5)),
    R_sh=Vector((8.6, 0.0, 30.0)), L_sh=Vector((-8.6, 0.0, 30.0)),
    R_el=Vector((10.6, 3.6, 23.6)), L_el=Vector((-10.8, 0.8, 23.2)),
    R_wr=Vector((10.2, 9.2, 21.0)), L_wr=Vector((-11.4, 2.0, 16.6)),
    R_hip=Vector((3.4, 0.0, 18.0)), L_hip=Vector((-3.4, 0.0, 18.0)),
    R_kn=Vector((3.9, 1.0, 10.0)), L_kn=Vector((-3.9, 1.0, 10.0)),
    R_an=Vector((3.9, 0.0, 2.4)), L_an=Vector((-3.9, 0.0, 2.4)),
    cannon=Vector((0.0, 4.4, 27.2)),
)
SWORD_DIR = Vector((0.08, 0.95, -0.3)).normalized()


# ------------------------------------------------------------------------------------------------ parts
def torso(p):
    b = p['Torso']
    # armoured core: boxy-rounded loft from waist to shoulders
    from geo import loft
    secs = []
    for i in range(9):
        t = i / 8
        z = 21.0 + 11.0 * t
        w = 9.5 + 6.5 * math.sin(math.pi / 2 * t) ** 1.4
        d = 7.0 + 2.2 * math.sin(math.pi * t * 0.8)
        m = 20
        ring = []
        for j in range(m):
            a = 2 * math.pi * j / m
            ca, sa = math.cos(a), math.sin(a)
            e = 4.0
            ring.append(Vector((math.copysign(abs(ca) ** (2 / e), ca) * w / 2, math.copysign(abs(sa) ** (2 / e), sa) * d / 2, z)))
        secs.append(ring)
    rings = loft(b, secs, 'Mech_Plate', caps=True)
    for i, ring in enumerate(rings):                 # planar-ish UVs for the plate texture
        for v in ring:
            for l in v.link_loops: l[b.uv].uv = ((v.co.x + v.co.y) * UVD, v.co.z * UVD)
    # do: laced lames on the belly and flanks (around the cannon)
    lames(b, -4.8, 4.8, 24.6, 4, 0.75, 3.9, 0.35, ['Red_Lacquer', 'Black_Lacquer'], curve=0.4)
    for x0, x1 in ((-7.4, -3.4), (3.4, 7.4)):
        lames(b, x0, x1, 31.0, 6, 0.8, 4.45, 0.35, ['Red_Lacquer', 'Black_Lacquer'], curve=0.3)
    for x in (-3.2, -1.6, 0.0, 1.6, 3.2):            # red lacing cords
        b.box((x - 0.1, 4.1, 21.4), (x + 0.1, 4.45, 24.7), 'Cloth_Crimson')
    for x in (-6.8, -5.2, -3.9, 3.9, 5.2, 6.8):
        b.box((x - 0.1, 4.6, 26.0), (x + 0.1, 4.95, 31.0), 'Cloth_Crimson')
    # gorget + shoulder yoke, gold trim edge
    lathe(b, (0, 0, 31.6), [(4.6, 0.0), (4.4, 0.7), (3.4, 1.2), (2.6, 1.3)], 16, 'Mech_Plate', cap_bottom=False, cap_top=False)
    b.box((-8.2, -4.6, 31.8), (8.2, 4.6, 32.4), 'Gold_Leaf')
    # back: two smoke stacks and a sashimono banner
    for sx in (-1, 1):
        base = Vector((sx * 3.2, -4.4, 29.0))
        b.cylinder(base, base + Vector((sx * 0.6, -1.6, 8.0)), 0.9, 12, 'Steel_Dark')
        b.cylinder(base + Vector((sx * 0.6, -1.6, 8.0)), base + Vector((sx * 0.66, -1.8, 8.8)), 1.15, 12, 'Iron_Wrought')
        cbox(b, (sx * 3.2, -4.8, 28.0), (2.6, 1.6, 3.0), 'Mech_Plate')
    pole0 = Vector((0, -4.9, 24.0)); pole1 = Vector((0, -5.4, 46.0))
    b.cylinder(pole0, pole1, 0.25, 8, 'Timber_Dark')
    b.box((-0.1, -5.5, 36.0), (0.1, -5.3, 45.5), 'Timber_Dark')
    b.prism([(0, 0), (4.2, 0), (4.2, 10.5), (0, 10.5)], (0.15, -5.35, 35.2), (1, 0, 0), (0, 0, 1), (0, 1, 0), 0.08, 'Cloth_Crimson')
    blob(b, (2.1, -5.3, 42.0), (1.3, 0.12, 1.3), 'Gold_Leaf', subdiv=2, amp=0.0)      # gold mon on the banner
    rivets(b, [Vector((x, 4.6, 31.2)) for x in (-7.5, -6.0, 6.0, 7.5)] + [Vector((sx * 7.8, 0, 29.6)) for sx in (-1, 1)])


def cannon(p):
    b = p['Cannon']
    c = J['cannon']
    Y = Vector((0, 1, 0))
    b.cylinder(c + Vector((0, -0.6, 0)), c + Vector((0, 0.8, 0)), 3.1, 24, 'Mech_Plate')           # turret housing
    ring = [c + Vector((2.6 * math.cos(a), 0.85, 2.6 * math.sin(a))) for a in [2 * math.pi * k / 24 for k in range(25)]]
    tube(b, ring, [0.22] * 25, 8, 'Glow_Amber', caps=False)                                         # glowing core ring
    b.cylinder(c + Vector((0, 0.8, 0)), c + Vector((0, 1.3, 0)), 2.0, 20, 'Iron_Wrought')
    b.cylinder(c + Vector((0, 1.2, 0)), c + Vector((0, 7.4, 0)), 1.5, 20, 'Steel_Dark')              # barrel
    for yy in (2.2, 4.0, 5.8):
        b.cylinder(c + Vector((0, yy, 0)), c + Vector((0, yy + 0.45, 0)), 1.72, 20, 'Iron_Wrought')   # reinforcing bands
    b.cylinder(c + Vector((0, 7.2, 0)), c + Vector((0, 8.6, 0)), 1.9, 8, 'Mech_Plate')                # muzzle brake
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        cbox(b, c + Vector((2.0 * math.cos(a), 7.9, 2.0 * math.sin(a))), (0.5, 0.9, 0.5), 'Steel_Dark', axis='y')
    b.cylinder(c + Vector((0, 8.0, 0)), c + Vector((0, 8.62, 0)), 1.05, 16, 'Shadow_Black', caps=False)  # bore
    b.cylinder(c + Vector((0, 7.4, 0)), c + Vector((0, 8.0, 0)), 1.05, 16, 'Glow_Amber')                  # hot glow deep in the bore
    rivets(b, [c + Vector((2.85 * math.cos(a), 0.82, 2.85 * math.sin(a))) for a in [2 * math.pi * k / 12 for k in range(12)]], 0.16)


def pelvis(p):
    b = p['Pelvis']
    cbox(b, (0, 0, 19.4), (8.8, 6.4, 3.6), 'Mech_Plate', ch=0.5)
    lathe(b, (0, 0, 20.6), [(5.6, 0.0), (5.6, 0.8), (5.2, 0.9)], 20, 'Cloth_Crimson', cap_bottom=False, cap_top=False)     # obi
    blob(b, (0, 5.4, 21.0), (0.9, 0.5, 0.7), 'Cloth_Crimson', subdiv=2, amp=0.0)
    # kusazuri: seven hanging panels of lames splayed around the hips
    for theta in (90, 50, 130, 10, 170, -30, 210):                     # front, front sides, sides, back sides
        panel = B()
        for j in range(4):
            z1 = -j * 1.3; z0 = z1 - 1.2
            panel.box((-1.7, -0.25, z0), (1.7, 0.25, z1), 'Red_Lacquer' if j % 2 == 0 else 'Black_Lacquer')
            panel.box((-0.1, 0.24, z0), (0.1, 0.34, z1), 'Cloth_Crimson')
        panel.box((-1.8, -0.3, -5.4), (1.8, 0.3, -5.1), 'Gold_Leaf')
        th = math.radians(theta)
        dirv = Vector((math.cos(th), math.sin(th), 0))
        M = (Matrix.Translation(Vector((dirv.x * 5.0, dirv.y * 3.6, 20.4))) @
             Matrix.Rotation(th - math.pi / 2, 4, 'Z') @ Matrix.Rotation(math.radians(14), 4, 'X'))
        place(b, panel, M)


def head(p):
    b = p['Head']
    base = J['neck']
    b.cylinder(base, base + Vector((0, 0, 1.6)), 1.6, 16, 'Steel_Dark')
    hc = base + Vector((0, 0.3, 3.4))
    lathe(b, hc, [(2.9, -0.2), (3.0, 0.6), (2.7, 1.8), (1.9, 2.8), (0.8, 3.3), (0.0, 3.4)], 24, 'Black_Lacquer')        # kabuto bowl
    for k in range(16):                                                       # riveted ribs
        a = 2 * math.pi * k / 16
        pts = [hc + Vector((r * math.cos(a), r * math.sin(a), z)) for r, z in ((3.02, 0.0), (2.95, 0.8), (2.62, 1.9), (1.8, 2.85), (0.75, 3.34))]
        tube(b, pts, [0.09] * 5, 5, 'Iron_Wrought')
    for j in range(4):                                                        # shikoro neck guard
        r0 = 3.1 + j * 0.55
        lathe(b, hc + Vector((0, -0.4, -0.3 - j * 0.8)), [(r0 + 0.5, 0.0), (r0, 0.75)], 24,
              'Mech_Plate' if j % 2 == 0 else 'Black_Lacquer', cap_bottom=False, cap_top=False)
    for sx in (-1, 1):                                                        # fukigaeshi turn-backs
        cbox(b, hc + Vector((sx * 3.3, 1.6, 0.2)), (0.4, 1.6, 1.9), 'Black_Lacquer')
        cbox(b, hc + Vector((sx * 3.35, 1.7, 0.2)), (0.2, 1.2, 1.4), 'Gold_Leaf')
    # menpo face mask with glowing eye slit and mouth grille
    cbox(b, hc + Vector((0, 2.5, -0.6)), (3.8, 1.4, 2.6), 'Mech_Plate', ch=0.5)
    b.box(tuple(hc + Vector((-1.6, 3.2, -0.1))), tuple(hc + Vector((1.6, 3.28, 0.35))), 'Glow_Red')
    b.box(tuple(hc + Vector((-1.8, 3.18, 0.35))), tuple(hc + Vector((1.8, 3.4, 0.6))), 'Black_Lacquer')   # brow over the slit
    for k in range(5):
        x = -1.0 + 0.5 * k
        b.box(tuple(hc + Vector((x - 0.12, 3.2, -1.7))), tuple(hc + Vector((x + 0.12, 3.35, -0.8))), 'Steel_Dark')
    # kuwagata horns + maedate crest (gold)
    for sx in (-1, 1):
        root = hc + Vector((sx * 0.9, 2.6, 1.3))
        tube(b, [root, root + Vector((sx * 1.4, 0.6, 2.6)), root + Vector((sx * 2.8, 0.4, 5.6)), root + Vector((sx * 3.3, -0.2, 7.6))],
             [0.45, 0.4, 0.28, 0.05], 8, 'Gold_Leaf')
    blob(b, hc + Vector((0, 3.1, 1.8)), (1.0, 0.18, 1.0), 'Gold_Leaf', subdiv=2, amp=0.0)
    blob(b, hc + Vector((0, 3.25, 1.8)), (0.45, 0.1, 0.45), 'Red_Lacquer', subdiv=2, amp=0.0)


def arm(p, side):
    tag = 'R' if side > 0 else 'L'
    S, E, W = J[tag + '_sh'], J[tag + '_el'], J[tag + '_wr']
    X = Vector((side, 0, 0))
    # upper arm + shoulder ball
    u = p[tag + '_UpperArm']
    blob(u, S, (2.1, 2.1, 2.1), 'Steel_Dark', subdiv=2, amp=0.0)
    seg = B()
    L = (E - S).length
    seg.cylinder((0, 0, 0.6), (0, 0, L - 0.8), 1.45, 16, 'Steel_Dark')
    cbox(seg, (0, 0, L * 0.45), (3.4, 3.2, L * 0.62), 'Mech_Plate', ch=0.5, axis='z')
    seg.cylinder((0, 1.7, 1.0), (0, 1.7, L - 1.2), 0.25, 8, 'Iron_Wrought')                              # piston
    place(u, seg, seg_frame(S, E, X))
    # sode: big layered shoulder plates hanging on the outside
    sode = B()
    for k in range(6):
        z1 = 1.4 - k * 1.25; z0 = z1 - 1.15
        sode.box((-0.3 + 0.08 * k, -3.2, z0), (0.3 + 0.08 * k, 3.2, z1), 'Red_Lacquer' if k % 2 == 0 else 'Black_Lacquer')
        for yy in (-2.2, 0.0, 2.2):
            sode.box((0.3 + 0.08 * k, yy - 0.1, z0), (0.4 + 0.08 * k, yy + 0.1, z1), 'Cloth_Crimson')
    sode.box((-0.5, -3.3, 1.35), (0.5, 3.3, 1.7), 'Gold_Leaf')
    M = Matrix.Translation(S + X * 2.4 + Vector((0, 0, -0.4))) @ Matrix.Rotation(math.radians(-12 * side), 4, 'Y')
    if side < 0: M = M @ Matrix.Scale(-1, 4, Vector((1, 0, 0)))
    place(u, sode, M)
    # forearm: elbow hinge, kote plates, gauntlet
    f = p[tag + '_Forearm']
    f.cylinder(E - X * 1.6, E + X * 1.6, 1.4, 16, 'Iron_Wrought')
    seg = B()
    L = (W - E).length
    seg.cylinder((0, 0, 0.4), (0, 0, L - 0.4), 1.25, 16, 'Steel_Dark')
    for k in range(4):
        z0 = 0.6 + k * (L - 1.2) / 4
        cbox(seg, (0, 0, z0 + (L - 1.2) / 8), (3.0, 3.0, (L - 1.2) / 4 - 0.15), 'Black_Lacquer' if k % 2 == 0 else 'Mech_Plate', ch=0.45, axis='z')
    seg.box((-1.62, -0.12, 0.6), (-1.5, 0.12, L - 0.6), 'Gold_Leaf')
    place(f, seg, seg_frame(E, W, X))
    # hand: palm + fingers (right curled around the sword grip, left half-open)
    h = p[tag + '_Hand']
    hd = (W - E).normalized()
    hb = B()
    cbox(hb, (0, 0, 1.2), (2.4, 1.6, 2.2), 'Mech_Plate', ch=0.35, axis='z')
    for k in range(4):
        x = -0.85 + 0.57 * k
        if side > 0:                                             # curled: three segments wrapping forward/down
            hb.box((x - 0.24, 0.8, 2.0), (x + 0.24, 1.6, 2.6), 'Steel_Dark')
            hb.box((x - 0.24, 1.2, 1.1), (x + 0.24, 1.9, 2.0), 'Steel_Dark')
            hb.box((x - 0.24, 0.6, 0.6), (x + 0.24, 1.3, 1.1), 'Steel_Dark')
        else:
            hb.box((x - 0.24, -0.25, 2.3), (x + 0.24, 0.35, 3.4), 'Steel_Dark')
            hb.box((x - 0.24, 0.0, 3.4), (x + 0.24, 0.8, 4.0), 'Steel_Dark')
    hb.box((1.1, 0.2, 0.6), (1.6, 1.4, 1.6), 'Steel_Dark')                                              # thumb
    place(h, hb, seg_frame(W, W + (hd if side < 0 else Vector((0, 0.35, -1.0)).normalized()), X))
    return S, E, W


def leg(p, side):
    tag = 'R' if side > 0 else 'L'
    Hp, K, A = J[tag + '_hip'], J[tag + '_kn'], J[tag + '_an']
    X = Vector((side, 0, 0))
    t = p[tag + '_Thigh']
    blob(t, Hp, (2.2, 2.2, 2.2), 'Steel_Dark', subdiv=2, amp=0.0)
    seg = B()
    L = (K - Hp).length
    seg.cylinder((0, 0, 0.5), (0, 0, L - 0.5), 1.9, 16, 'Steel_Dark')
    cbox(seg, (0, 0.3, L * 0.5), (4.0, 3.8, L * 0.7), 'Mech_Plate', ch=0.6, axis='z')
    for k in range(3):                                                    # haidate lames on the front
        seg.box((-1.9, 2.2, L * 0.25 + k * 1.6), (1.9, 2.55, L * 0.25 + k * 1.6 + 1.4), 'Black_Lacquer' if k % 2 == 0 else 'Mech_Plate')
    place(t, seg, seg_frame(K, Hp, X))
    s = p[tag + '_Shin']
    blob(s, K, (1.9, 2.0, 1.9), 'Iron_Wrought', subdiv=2, amp=0.0)
    blob(s, K + Vector((0, 1.6, 0.2)), (1.4, 0.7, 1.5), 'Mech_Plate', subdiv=2, amp=0.0)                   # knee cap
    seg = B()
    L = (A - K).length
    seg.cylinder((0, 0, 0.3), (0, 0, L - 0.3), 1.6, 16, 'Steel_Dark')
    for k in range(5):                                                    # suneate splints
        x = -1.4 + 0.7 * k
        seg.box((x - 0.3, 1.5, 0.8), (x + 0.3, 1.95, L - 0.6), 'Black_Lacquer')
    cbox(seg, (0, 0.2, L * 0.45), (3.6, 3.4, L * 0.55), 'Mech_Plate', ch=0.5, axis='z')
    seg.cylinder((side * 0.9, -1.8, 1.0), (side * 0.9, -1.8, L - 1.0), 0.3, 8, 'Iron_Wrought')           # calf pistons
    seg.cylinder((-side * 0.9, -1.8, 1.0), (-side * 0.9, -1.8, L - 1.0), 0.3, 8, 'Iron_Wrought')
    place(s, seg, seg_frame(A, K, X))
    ft = p[tag + '_Foot']
    ft.cylinder(A - X * 1.2, A + X * 1.2, 1.3, 14, 'Iron_Wrought')
    cbox(ft, (A.x, A.y + 1.2, 1.1), (4.0, 6.4, 2.2), 'Mech_Plate', ch=0.6)
    cbox(ft, (A.x, A.y + 4.6, 0.7), (4.2, 1.6, 1.4), 'Black_Lacquer', ch=0.4)                             # toe cap
    cbox(ft, (A.x, A.y - 2.5, 0.6), (2.0, 1.6, 1.2), 'Mech_Plate', ch=0.3)                                # heel spur
    for k in range(3):
        ft.box((A.x - 1.9 + 1.3 * k, A.y + 5.3, 0.0), (A.x - 1.1 + 1.3 * k, A.y + 5.9, 0.6), 'Steel_Dark')  # toe claws


def sword(p):
    """Giant nodachi: the Ashfall katana scaled x9 (dark steel, amber glowing edge), gripped in the right hand."""
    import herokit
    kb, saya, g = herokit.katana('AshfallSword')
    s = p['Sword']
    grip = J['R_wr'] + Vector((0, 0.35, -1.0)).normalized() * 1.3
    R = Vector((0, 1, 0)).rotation_difference(SWORD_DIR).to_matrix().to_4x4()
    M = Matrix.Translation(grip) @ R @ Matrix.Scale(9.0, 4)
    for src in (kb, g):
        tmp = B()
        mesh_join(tmp, src)
        place(s, tmp, M)
    return grip


# ------------------------------------------------------------------------------------------------ build + rig
PIECES = ['Head', 'Torso', 'Cannon', 'Pelvis', 'R_UpperArm', 'R_Forearm', 'R_Hand', 'L_UpperArm', 'L_Forearm', 'L_Hand',
          'Sword', 'R_Thigh', 'R_Shin', 'R_Foot', 'L_Thigh', 'L_Shin', 'L_Foot']


def build():
    p = {n: B() for n in PIECES}
    torso(p); cannon(p); pelvis(p); head(p)
    for sd in (1, -1):
        arm(p, sd); leg(p, sd)
    grip = sword(p)
    tip = grip + SWORD_DIR * 9.0 * (0.95 / 2 + 0.12 + 2.8)
    bones = [
        ('Root', Vector((0, 0, 0)), Vector((0, 2, 0)), None),
        ('Pelvis', J['pelvis'], J['waist'], 'Root'),
        ('Torso', J['waist'], J['neck'], 'Pelvis'),
        ('Head', J['neck'], J['neck'] + Vector((0, 0, 4.5)), 'Torso'),
        ('Cannon', J['cannon'], J['cannon'] + Vector((0, 8.6, 0)), 'Torso'),
    ]
    for tag in ('R', 'L'):
        bones += [(f'{tag}_UpperArm', J[tag + '_sh'], J[tag + '_el'], 'Torso'),
                  (f'{tag}_Forearm', J[tag + '_el'], J[tag + '_wr'], f'{tag}_UpperArm'),
                  (f'{tag}_Hand', J[tag + '_wr'], J[tag + '_wr'] + (J[tag + '_wr'] - J[tag + '_el']).normalized() * 2.5, f'{tag}_Forearm'),
                  (f'{tag}_Thigh', J[tag + '_hip'], J[tag + '_kn'], 'Pelvis'),
                  (f'{tag}_Shin', J[tag + '_kn'], J[tag + '_an'], f'{tag}_Thigh'),
                  (f'{tag}_Foot', J[tag + '_an'], J[tag + '_an'] + Vector((0, 5.0, -2.0)), f'{tag}_Shin')]
    bones.append(('Sword', grip, tip, 'R_Hand'))
    bone_of = {n: n for n in PIECES}
    return p, dict(bones=bones, bone_of=bone_of, muzzle=J['cannon'] + Vector((0, 8.6, 0)), tip=tip)


def weights_for(rig, piece, pos):
    return {rig['bone_of'][piece]: 1.0}
