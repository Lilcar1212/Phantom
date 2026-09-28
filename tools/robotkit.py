"""Hero unit: HO_Mech_Raijin - an original anime "real robot" style giant (~46 studs to the crest).

White panelled armour with blue and red accents over a dark mechanical frame: faceted helmet with a three-blade gold
crest, twin glowing eyes and a red chin, yellow chest vents, a cannon in the middle of the chest, broad angular
shoulders with upswept fins, front/side skirt armour, heavy knees and feet, four wing plates on the back, and a huge
katana in the right hand (pale blue glowing edge).  Rigid rig (every piece on one bone).
Blender axes: front = +Y (Roblox -Z), up = +Z, feet on z = 0, origin between the feet.
"""
import math
from mathutils import Vector, Matrix
from geo import Builder, tube
from harborkit import blob
from castlekit import mesh_join
from mechkit import place, seg_frame

MATS = ['Mech_White', 'Mech_Blue', 'Mech_Red', 'Mech_Grey', 'Mech_Frame', 'Mech_Vent', 'Gold_Leaf', 'Glow_Yellow',
        'Glow_Blue', 'Glow_Amber', 'Shadow_Black', 'Steel_Blade', 'Steel_Dark', 'Iron_Wrought', 'Tsuka_Wrap', 'Navy_Lacquer',
        'Black_Lacquer']
UVD = 0.1


def B():
    return Builder(MATS)


# ------------------------------------------------------------------------------------------------ primitives
def hull(b, pts, mat):
    """Convex 8-point block: pts = bottom quad (4) + top quad (4), same winding. Planar UVs per face."""
    P = [Vector(p) for p in pts]
    c = sum(P, Vector()) / 8
    vs = [b.bm.verts.new(p) for p in P]
    faces = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    for f in faces:
        q = [vs[i] for i in f]
        fc = sum((v.co for v in q), Vector()) / 4
        n = (q[1].co - q[0].co).cross(q[2].co - q[0].co)
        ax = max(range(3), key=lambda k: abs(n[k]))
        a, bb = [k for k in range(3) if k != ax]
        b.face(q, mat, [(v.co[a] * UVD, v.co[bb] * UVD) for v in q], out=fc - c)


def tbox(b, z0, z1, bot, top, mat):
    """Tapered box along Z: bot/top = (cx, cy, width, depth)."""
    def quad(z, cx, cy, w, d):
        return [(cx - w / 2, cy - d / 2, z), (cx + w / 2, cy - d / 2, z), (cx + w / 2, cy + d / 2, z), (cx - w / 2, cy + d / 2, z)]
    hull(b, quad(z0, *bot) + quad(z1, *top), mat)


def plate(b, outline, origin, u, v, n, th, mat):
    """Flat armour plate: 2D outline extruded by th along n."""
    b.prism(outline, origin, u, v, n, th, mat, uvd=UVD)


# ------------------------------------------------------------------------------------------------ layout
J = dict(
    pelvis=Vector((0, 0, 25.0)), waist=Vector((0, 0, 27.5)), neck=Vector((0, 0, 38.6)),
    R_sh=Vector((8.8, 0, 35.2)), L_sh=Vector((-8.8, 0, 35.2)),
    R_el=Vector((10.6, 1.2, 27.6)), L_el=Vector((-10.9, 0.4, 27.4)),
    R_wr=Vector((11.0, 4.6, 21.0)), L_wr=Vector((-11.6, 1.6, 20.2)),
    R_hip=Vector((3.3, 0, 24.0)), L_hip=Vector((-3.3, 0, 24.0)),
    R_kn=Vector((3.8, 0.8, 15.2)), L_kn=Vector((-3.8, 0.8, 15.2)),
    R_an=Vector((3.8, 0.0, 3.4)), L_an=Vector((-3.8, 0.0, 3.4)),
    cannon=Vector((0, 3.7, 33.0)),
)
SWORD_DIR = Vector((0.05, 0.9, -0.43)).normalized()


# ------------------------------------------------------------------------------------------------ parts
def torso(p):
    b = p['Torso']
    tbox(b, 28.0, 31.0, (0, 0, 7.0, 5.6), (0, 0.2, 8.4, 6.4), 'Mech_Blue')                          # abdomen
    for k in range(3):                                                                               # ab plates
        tbox(b, 28.2 + k * 0.95, 29.0 + k * 0.95, (0, 2.9, 5.0 - k * 0.3, 0.5), (0, 3.1, 5.2 - k * 0.3, 0.5), 'Mech_Frame')
    tbox(b, 31.0, 38.6, (0, 0.2, 10.5, 7.0), (0, -0.3, 13.0, 7.6), 'Mech_White')                   # chest
    hull(b, [(-5.6, 3.3, 31.2), (5.6, 3.3, 31.2), (5.9, 4.1, 31.4), (-5.9, 4.1, 31.4),
             (-6.2, 3.2, 37.6), (6.2, 3.2, 37.6), (6.4, 3.8, 37.2), (-6.4, 3.8, 37.2)], 'Mech_Blue')    # chest front plate
    for sx in (-1, 1):                                                                               # yellow intake vents
        hull(b, [(sx * 1.9, 3.9, 34.0), (sx * 5.2, 3.9, 34.0), (sx * 5.2, 4.3, 34.2), (sx * 1.9, 4.3, 34.2),
                 (sx * 1.9, 3.9, 37.0), (sx * 5.5, 3.9, 37.0), (sx * 5.5, 4.3, 36.8), (sx * 1.9, 4.3, 36.8)], 'Mech_Vent')
        hull(b, [(sx * 6.3, -3.2, 31.4), (sx * 6.9, -3.2, 31.4), (sx * 6.9, 3.4, 31.4), (sx * 6.3, 3.4, 31.4),
                 (sx * 6.6, -3.6, 38.2), (sx * 7.2, -3.6, 38.2), (sx * 7.2, 3.6, 38.2), (sx * 6.6, 3.6, 38.2)], 'Mech_White')
    hull(b, [(-3.8, -1.5, 37.8), (3.8, -1.5, 37.8), (3.4, 3.9, 37.6), (-3.4, 3.9, 37.6),
             (-2.6, -1.2, 39.2), (2.6, -1.2, 39.2), (2.2, 3.1, 38.9), (-2.2, 3.1, 38.9)], 'Mech_Red')        # red collar
    # backpack + four wing plates (angular, white with blue inner and red tips)
    tbox(b, 30.0, 37.5, (0, -4.6, 7.0, 3.0), (0, -4.4, 7.8, 3.4), 'Mech_Grey')
    for sx in (-1, 1):
        tag = 'R' if sx > 0 else 'L'
        w = p[tag + '_Wing']
        for k, (ang, L, W) in enumerate(((44, 14.5, 4.0), (18, 12.5, 3.4))):
            base = Vector((sx * 2.4, -5.6 - 0.8 * k, 35.5 - 1.5 * k))
            a = math.radians(ang)
            dirv = Vector((sx * math.cos(a), -0.25, math.sin(a))).normalized()
            side = Vector((0, 1, 0)).cross(dirv).normalized()
            tip = base + dirv * L
            hull(w, [base - side * W / 2, base + side * W / 2, base + side * W / 2 + Vector((0, -0.5, 0)), base - side * W / 2 + Vector((0, -0.5, 0)),
                     tip - side * W * 0.3, tip + side * W * 0.45, tip + side * W * 0.45 + Vector((0, -0.4, 0)), tip - side * W * 0.3 + Vector((0, -0.4, 0))],
                 'Mech_White')
            hull(w, [base - side * W * 0.3 + Vector((0, 0.05, 0)), base + side * W * 0.3 + Vector((0, 0.05, 0)),
                     base + side * W * 0.3 + Vector((0, 0.15, 0)), base - side * W * 0.3 + Vector((0, 0.15, 0)),
                     tip - side * W * 0.15 - dirv * 2 + Vector((0, 0.05, 0)), tip + side * W * 0.2 - dirv * 2 + Vector((0, 0.05, 0)),
                     tip + side * W * 0.2 - dirv * 2 + Vector((0, 0.15, 0)), tip - side * W * 0.15 - dirv * 2 + Vector((0, 0.15, 0))], 'Mech_Blue')
            t2 = tip + dirv * 0.01
            hull(w, [t2 - dirv * 1.6 - side * W * 0.3, t2 - dirv * 1.6 + side * W * 0.45, t2 - dirv * 1.6 + side * W * 0.45 + Vector((0, -0.45, 0)),
                     t2 - dirv * 1.6 - side * W * 0.3 + Vector((0, -0.45, 0)),
                     t2 + dirv * 0.8 + side * W * 0.1, t2 + dirv * 0.8 + side * W * 0.2, t2 + dirv * 0.8 + side * W * 0.2 + Vector((0, -0.45, 0)),
                     t2 + dirv * 0.8 + side * W * 0.1 + Vector((0, -0.45, 0))], 'Mech_Red')
        w.cylinder(Vector((sx * 2.0, -5.2, 35.0)), Vector((sx * 3.0, -5.2, 35.0)), 1.0, 12, 'Mech_Frame')


def cannon(p):
    b = p['Cannon']
    c = J['cannon']
    b.cylinder(c + Vector((0, -0.4, 0)), c + Vector((0, 0.9, 0)), 1.9, 20, 'Mech_Grey')
    ring = [c + Vector((1.55 * math.cos(a), 0.95, 1.55 * math.sin(a))) for a in [2 * math.pi * k / 24 for k in range(25)]]
    tube(b, ring, [0.16] * 25, 8, 'Glow_Amber', caps=False)
    b.cylinder(c + Vector((0, 0.8, 0)), c + Vector((0, 6.4, 0)), 1.05, 16, 'Mech_White')
    b.cylinder(c + Vector((0, 2.6, 0)), c + Vector((0, 3.0, 0)), 1.2, 16, 'Mech_Blue')
    b.cylinder(c + Vector((0, 5.6, 0)), c + Vector((0, 6.8, 0)), 1.3, 8, 'Mech_Red')                   # muzzle
    b.cylinder(c + Vector((0, 6.3, 0)), c + Vector((0, 6.82, 0)), 0.7, 12, 'Shadow_Black', caps=False)
    b.cylinder(c + Vector((0, 5.8, 0)), c + Vector((0, 6.3, 0)), 0.7, 12, 'Glow_Amber')


def pelvis(p):
    b = p['Pelvis']
    b.cylinder(Vector((0, 0, 25.2)), Vector((0, 0, 28.4)), 2.9, 16, 'Mech_Frame')                      # waist
    tbox(b, 22.2, 25.8, (0, 0.4, 3.0, 4.0), (0, 0.2, 7.0, 5.8), 'Mech_Blue')                           # crotch
    hull(b, [(-1.0, 2.2, 21.6), (1.0, 2.2, 21.6), (1.2, 2.8, 21.8), (-1.2, 2.8, 21.8),
             (-1.6, 2.6, 25.0), (1.6, 2.6, 25.0), (1.8, 3.2, 24.9), (-1.8, 3.2, 24.9)], 'Mech_Red')
    for sx in (-1, 1):
        # front skirt plates: hang forward and slightly out, red tab + yellow caution
        hull(b, [(sx * 0.6, 3.0, 25.6), (sx * 4.6, 3.0, 25.6), (sx * 4.6, 3.8, 25.6), (sx * 0.6, 3.8, 25.6),
                 (sx * 1.2, 3.9, 18.6), (sx * 4.8, 3.6, 19.4), (sx * 4.8, 4.3, 19.4), (sx * 1.2, 4.6, 18.6)], 'Mech_White')
        hull(b, [(sx * 2.2, 3.85, 21.0), (sx * 3.6, 3.85, 21.2), (sx * 3.6, 4.35, 21.2), (sx * 2.2, 4.4, 21.0),
                 (sx * 2.2, 3.9, 22.4), (sx * 3.6, 3.9, 22.6), (sx * 3.6, 4.3, 22.6), (sx * 2.2, 4.35, 22.4)], 'Mech_Red')
        # side skirts: tall plates hanging on the hips
        hull(b, [(sx * 4.6, -2.8, 26.0), (sx * 5.2, -2.8, 26.0), (sx * 5.2, 2.8, 26.0), (sx * 4.6, 2.8, 26.0),
                 (sx * 5.4, -2.4, 17.8), (sx * 6.0, -2.4, 17.8), (sx * 6.0, 2.2, 17.8), (sx * 5.4, 2.2, 17.8)], 'Mech_White')
        hull(b, [(sx * 5.3, -0.8, 23.6), (sx * 5.5, -0.8, 23.6), (sx * 5.5, 1.2, 23.6), (sx * 5.3, 1.2, 23.6),
                 (sx * 5.6, -0.6, 20.8), (sx * 5.8, -0.6, 20.8), (sx * 5.8, 1.0, 20.8), (sx * 5.6, 1.0, 20.8)], 'Mech_Red')
    hull(b, [(-4.0, -3.4, 25.8), (4.0, -3.4, 25.8), (4.0, -2.6, 25.8), (-4.0, -2.6, 25.8),
             (-3.4, -4.2, 20.2), (3.4, -4.2, 20.2), (3.4, -3.5, 20.2), (-3.4, -3.5, 20.2)], 'Mech_White')     # back skirt


def head(p):
    b = p['Head']
    n = J['neck']
    b.cylinder(n, n + Vector((0, 0, 1.4)), 1.2, 12, 'Mech_Frame')
    tbox(b, 39.4, 42.6, (0, 0.2, 3.4, 3.6), (0, 0.0, 2.8, 3.4), 'Mech_White')                           # helmet
    hull(b, [(-1.5, -1.8, 42.5), (1.5, -1.8, 42.5), (1.3, 1.6, 42.5), (-1.3, 1.6, 42.5),
             (-0.9, -1.4, 43.4), (0.9, -1.4, 43.4), (0.6, 1.2, 43.2), (-0.6, 1.2, 43.2)], 'Mech_White')        # crown
    hull(b, [(-1.3, 1.5, 39.4), (1.3, 1.5, 39.4), (1.0, 2.35, 39.6), (-1.0, 2.35, 39.6),
             (-1.4, 1.6, 41.5), (1.4, 1.6, 41.5), (1.2, 2.2, 41.4), (-1.2, 2.2, 41.4)], 'Mech_Grey')           # faceplate
    for sx in (-1, 1):                                                                                   # twin eyes
        hull(b, [(sx * 0.2, 2.2, 40.95), (sx * 1.15, 2.1, 41.05), (sx * 1.15, 2.3, 41.05), (sx * 0.2, 2.4, 40.95),
                 (sx * 0.2, 2.2, 41.25), (sx * 1.2, 2.05, 41.45), (sx * 1.2, 2.25, 41.45), (sx * 0.2, 2.4, 41.25)], 'Glow_Yellow')
        b.cylinder(Vector((sx * 1.8, 0.8, 41.6)), Vector((sx * 1.8, 1.9, 41.6)), 0.28, 10, 'Mech_Grey')     # vulcan pods
        hull(b, [(sx * 1.6, -1.6, 39.6), (sx * 1.85, -1.6, 39.6), (sx * 1.85, 1.2, 39.6), (sx * 1.6, 1.2, 39.6),
                 (sx * 1.5, -1.4, 42.2), (sx * 1.75, -1.4, 42.2), (sx * 1.75, 0.9, 42.2), (sx * 1.5, 0.9, 42.2)], 'Mech_Blue')
    hull(b, [(-0.7, 1.8, 39.1), (0.7, 1.8, 39.1), (0.4, 2.7, 39.3), (-0.4, 2.7, 39.3),
             (-0.6, 1.8, 40.2), (0.6, 1.8, 40.2), (0.4, 2.5, 40.2), (-0.4, 2.5, 40.2)], 'Mech_Red')           # chin
    blob(b, (0, 1.9, 42.3), (0.28, 0.12, 0.28), 'Glow_Blue', subdiv=2, amp=0.0)                           # forehead sensor
    # original three-blade crest: two gold blades sweeping up/out and a short red centre spike
    for sx in (-1, 1):
        base = Vector((sx * 0.25, 1.9, 42.2))
        tipp = base + Vector((sx * 3.6, 0.6, 3.4))
        hull(b, [base + Vector((0, 0, -0.25)), base + Vector((sx * 0.3, 0, 0.25)), base + Vector((sx * 0.3, 0.25, 0.25)), base + Vector((0, 0.25, -0.25)),
                 tipp + Vector((0, 0, -0.05)), tipp + Vector((sx * 0.08, 0, 0.05)), tipp + Vector((sx * 0.08, 0.1, 0.05)), tipp + Vector((0, 0.1, -0.05))],
             'Gold_Leaf')
    base = Vector((0, 2.0, 42.4))
    hull(b, [base + Vector((-0.2, 0, 0)), base + Vector((0.2, 0, 0)), base + Vector((0.2, 0.3, 0)), base + Vector((-0.2, 0.3, 0)),
             base + Vector((-0.03, 0.4, 1.6)), base + Vector((0.03, 0.4, 1.6)), base + Vector((0.03, 0.5, 1.6)), base + Vector((-0.03, 0.5, 1.6))], 'Mech_Red')
    for v in b.bm.verts:                                                     # scale the whole head up about the neck
        v.co = n + (v.co - n) * 1.4


def arm(p, side):
    tag = 'R' if side > 0 else 'L'
    S, E, W = J[tag + '_sh'], J[tag + '_el'], J[tag + '_wr']
    X = Vector((side, 0, 0))
    u = p[tag + '_UpperArm']
    blob(u, S, (2.0, 2.0, 2.0), 'Mech_Frame', subdiv=2, amp=0.0)
    # shoulder armour: big angular block with a red upswept fin
    sx = side
    hull(u, [(S.x + sx * -1.6, -3.2, 31.8), (S.x + sx * 3.6, -3.0, 31.8), (S.x + sx * 3.6, 3.0, 31.8), (S.x + sx * -1.6, 3.2, 31.8),
             (S.x + sx * -1.2, -2.8, 38.6), (S.x + sx * 3.0, -2.6, 38.2), (S.x + sx * 3.0, 2.6, 38.2), (S.x + sx * -1.2, 2.8, 38.6)], 'Mech_White')
    hull(u, [(S.x + sx * 3.6, -2.6, 32.4), (S.x + sx * 3.9, -2.6, 32.4), (S.x + sx * 3.9, 2.6, 32.4), (S.x + sx * 3.6, 2.6, 32.4),
             (S.x + sx * 3.1, -2.2, 37.6), (S.x + sx * 3.4, -2.2, 37.6), (S.x + sx * 3.4, 2.2, 37.6), (S.x + sx * 3.1, 2.2, 37.6)], 'Mech_Blue')
    hull(u, [(S.x + sx * -1.0, -2.6, 38.5), (S.x + sx * 3.0, -2.4, 38.1), (S.x + sx * 3.0, -1.8, 38.1), (S.x + sx * -1.0, -2.0, 38.5),
             (S.x + sx * 0.8, -2.6, 39.6), (S.x + sx * 5.6, -2.2, 41.4), (S.x + sx * 5.6, -1.7, 41.4), (S.x + sx * 0.8, -2.0, 39.6)], 'Mech_Red')
    seg = B()
    L = (E - S).length
    seg.cylinder((0, 0, 0.4), (0, 0, L - 0.6), 1.5, 12, 'Mech_Frame')
    tbox(seg, 1.6, L - 0.9, (0, 0, 3.9, 3.9), (0, 0, 3.6, 3.6), 'Mech_White')
    place(u, seg, seg_frame(S, E, X))
    f = p[tag + '_Forearm']
    f.cylinder(E - X * 1.4, E + X * 1.4, 1.35, 14, 'Mech_Frame')
    seg = B()
    L = (W - E).length
    seg.cylinder((0, 0, 0.3), (0, 0, L - 0.3), 1.4, 12, 'Mech_Frame')
    tbox(seg, 0.8, L - 0.6, (0, 0, 4.0, 4.0), (0, 0, 5.0, 4.6), 'Mech_White')
    hull(seg, [(-2.25, -1.0, 2.2), (-2.1, -1.0, 2.2), (-2.1, 1.0, 2.2), (-2.25, 1.0, 2.2),
               (-2.6, -1.4, L - 1.0), (-2.45, -1.4, L - 1.0), (-2.45, 1.4, L - 1.0), (-2.6, 1.4, L - 1.0)], 'Mech_Red')
    tbox(seg, L - 0.9, L - 0.3, (0, 0, 5.1, 4.7), (0, 0, 4.6, 4.2), 'Mech_Blue')
    place(f, seg, seg_frame(E, W, X))
    h = p[tag + '_Hand']
    hd = (W - E).normalized()
    hb = B()
    tbox(hb, 0.0, 1.9, (0, 0, 2.2, 1.3), (0, 0, 2.4, 1.4), 'Mech_Frame')
    for k in range(4):
        x = -0.85 + 0.57 * k
        if side > 0:
            tbox(hb, 1.9, 2.6, (x, 0.5, 0.42, 0.8), (x, 0.8, 0.42, 0.9), 'Mech_Grey')
            tbox(hb, 1.0, 1.9, (x, 1.25, 0.42, 0.6), (x, 1.2, 0.42, 0.6), 'Mech_Grey')
        else:
            tbox(hb, 1.9, 3.1, (x, 0.0, 0.42, 0.5), (x, 0.2, 0.42, 0.45), 'Mech_Grey')
            tbox(hb, 3.1, 3.9, (x, 0.2, 0.4, 0.45), (x, 0.6, 0.36, 0.4), 'Mech_Grey')
    tbox(hb, 0.6, 1.8, (1.25, 0.6, 0.5, 0.6), (1.35, 1.0, 0.45, 0.55), 'Mech_Grey')
    for v in hb.bm.verts: v.co *= 1.35
    place(h, hb, seg_frame(W, W + (hd if side < 0 else Vector((0, 0.2, -1.0)).normalized()), X))
    return S, E, W


def leg(p, side):
    tag = 'R' if side > 0 else 'L'
    Hp, K, A = J[tag + '_hip'], J[tag + '_kn'], J[tag + '_an']
    X = Vector((side, 0, 0))
    t = p[tag + '_Thigh']
    blob(t, Hp, (2.0, 2.0, 2.0), 'Mech_Frame', subdiv=2, amp=0.0)
    seg = B()
    L = (Hp - K).length
    seg.cylinder((0, 0, 0.4), (0, 0, L - 0.4), 1.6, 12, 'Mech_Frame')
    tbox(seg, 1.0, L - 1.0, (0, 0.2, 5.2, 5.2), (0, 0, 5.8, 5.4), 'Mech_White')
    tbox(seg, 2.0, 3.2, (side * -2.3, 0, 0.3, 3.0), (side * -2.3, 0, 0.3, 3.0), 'Mech_Grey')
    place(t, seg, seg_frame(K, Hp, X))
    s = p[tag + '_Shin']
    blob(s, K, (1.7, 1.8, 1.7), 'Mech_Frame', subdiv=2, amp=0.0)
    # knee armour: big wedge with a red stripe and a grey vent
    hull(s, [(K.x - 2.3, K.y + 1.0, K.z - 3.2), (K.x + 2.3, K.y + 1.0, K.z - 3.2), (K.x + 2.2, K.y + 3.0, K.z - 2.6), (K.x - 2.2, K.y + 3.0, K.z - 2.6),
             (K.x - 2.0, K.y + 1.2, K.z + 1.8), (K.x + 2.0, K.y + 1.2, K.z + 1.8), (K.x + 1.7, K.y + 2.4, K.z + 1.5), (K.x - 1.7, K.y + 2.4, K.z + 1.5)],
         'Mech_White')
    hull(s, [(K.x - 0.4, K.y + 2.9, K.z - 2.4), (K.x + 0.4, K.y + 2.9, K.z - 2.4), (K.x + 0.4, K.y + 3.15, K.z - 2.3), (K.x - 0.4, K.y + 3.15, K.z - 2.3),
             (K.x - 0.4, K.y + 2.3, K.z + 1.2), (K.x + 0.4, K.y + 2.3, K.z + 1.2), (K.x + 0.4, K.y + 2.55, K.z + 1.2), (K.x - 0.4, K.y + 2.55, K.z + 1.2)],
         'Mech_Red')
    seg = B()
    L = (K - A).length
    seg.cylinder((0, 0, 0.3), (0, 0, L - 0.3), 1.4, 12, 'Mech_Frame')
    tbox(seg, 0.4, L - 2.8, (0, -0.3, 6.6, 6.2), (0, 0.1, 5.2, 5.2), 'Mech_White')                     # flared shin
    tbox(seg, 2.0, 5.0, (side * 3.35, -0.8, 0.25, 2.2), (side * 3.0, -0.8, 0.25, 2.0), 'Mech_Vent')       # side vent
    tbox(seg, 0.2, 1.0, (0, -0.3, 6.8, 6.4), (0, -0.3, 6.6, 6.2), 'Mech_Blue')                             # ankle rim
    place(s, seg, seg_frame(A, K, X))
    ft = p[tag + '_Foot']
    ft.cylinder(A - X * 1.3, A + X * 1.3, 1.2, 12, 'Mech_Frame')
    tbox(ft, 0.0, 1.0, (A.x, A.y + 1.2, 5.4, 10.0), (A.x, A.y + 1.2, 5.2, 9.8), 'Mech_Frame')              # sole
    hull(ft, [(A.x - 2.5, A.y - 3.2, 1.0), (A.x + 2.5, A.y - 3.2, 1.0), (A.x + 2.5, A.y + 5.4, 1.0), (A.x - 2.5, A.y + 5.4, 1.0),
              (A.x - 1.8, A.y - 2.4, 3.2), (A.x + 1.8, A.y - 2.4, 3.2), (A.x + 1.6, A.y + 2.0, 3.0), (A.x - 1.6, A.y + 2.0, 3.0)], 'Mech_White')
    hull(ft, [(A.x - 2.4, A.y + 4.2, 0.2), (A.x + 2.4, A.y + 4.2, 0.2), (A.x + 2.2, A.y + 6.2, 0.2), (A.x - 2.2, A.y + 6.2, 0.2),
              (A.x - 2.2, A.y + 4.0, 1.9), (A.x + 2.2, A.y + 4.0, 1.9), (A.x + 1.8, A.y + 5.6, 1.2), (A.x - 1.8, A.y + 5.6, 1.2)], 'Mech_Blue')
    hull(ft, [(A.x - 1.4, A.y - 4.4, 0.2), (A.x + 1.4, A.y - 4.4, 0.2), (A.x + 1.6, A.y - 3.0, 0.2), (A.x - 1.6, A.y - 3.0, 0.2),
              (A.x - 1.2, A.y - 4.0, 1.6), (A.x + 1.2, A.y - 4.0, 1.6), (A.x + 1.4, A.y - 3.0, 2.0), (A.x - 1.4, A.y - 3.0, 2.0)], 'Mech_Red')


def sword(p):
    """Huge katana: the Moonlit Edge scaled x9.5 (steel blade, pale blue glowing edge, navy fittings)."""
    import herokit
    kb, saya, g = herokit.katana('MoonlitEdge')
    s = p['Sword']
    grip = J['R_wr'] + Vector((0, 0.2, -1.0)).normalized() * 1.2
    R = Vector((0, 1, 0)).rotation_difference(SWORD_DIR).to_matrix().to_4x4()
    M = Matrix.Translation(grip) @ R @ Matrix.Scale(9.5, 4)
    for src in (kb, g):
        tmp = B()
        mesh_join(tmp, src)
        place(s, tmp, M)
    return grip


# ------------------------------------------------------------------------------------------------ build + rig
PIECES = ['Head', 'Torso', 'Cannon', 'Pelvis', 'R_Wing', 'L_Wing', 'R_UpperArm', 'R_Forearm', 'R_Hand', 'L_UpperArm',
          'L_Forearm', 'L_Hand', 'Sword', 'R_Thigh', 'R_Shin', 'R_Foot', 'L_Thigh', 'L_Shin', 'L_Foot']


def build():
    p = {n: B() for n in PIECES}
    torso(p); cannon(p); pelvis(p); head(p)
    for sd in (1, -1):
        arm(p, sd); leg(p, sd)
    grip = sword(p)
    tip = grip + SWORD_DIR * 9.5 * (0.95 / 2 + 0.12 + 2.7)
    bones = [('Root', Vector((0, 0, 0)), Vector((0, 2, 0)), None),
             ('Pelvis', J['pelvis'], J['waist'], 'Root'),
             ('Torso', J['waist'], J['neck'], 'Pelvis'),
             ('Head', J['neck'], J['neck'] + Vector((0, 0, 5.6)), 'Torso'),
             ('Cannon', J['cannon'], J['cannon'] + Vector((0, 6.8, 0)), 'Torso'),
             ('R_Wing', Vector((2.4, -5.4, 35.0)), Vector((9.0, -6.5, 44.0)), 'Torso'),
             ('L_Wing', Vector((-2.4, -5.4, 35.0)), Vector((-9.0, -6.5, 44.0)), 'Torso')]
    for tag in ('R', 'L'):
        bones += [(f'{tag}_UpperArm', J[tag + '_sh'], J[tag + '_el'], 'Torso'),
                  (f'{tag}_Forearm', J[tag + '_el'], J[tag + '_wr'], f'{tag}_UpperArm'),
                  (f'{tag}_Hand', J[tag + '_wr'], J[tag + '_wr'] + (J[tag + '_wr'] - J[tag + '_el']).normalized() * 2.4, f'{tag}_Forearm'),
                  (f'{tag}_Thigh', J[tag + '_hip'], J[tag + '_kn'], 'Pelvis'),
                  (f'{tag}_Shin', J[tag + '_kn'], J[tag + '_an'], f'{tag}_Thigh'),
                  (f'{tag}_Foot', J[tag + '_an'], J[tag + '_an'] + Vector((0, 5.5, -2.5)), f'{tag}_Shin')]
    bones.append(('Sword', grip, tip, 'R_Hand'))
    return p, dict(bones=bones, bone_of={n: n for n in PIECES}, muzzle=J['cannon'] + Vector((0, 6.8, 0)), tip=tip)


def weights_for(rig, piece, pos):
    return {rig['bone_of'][piece]: 1.0}
