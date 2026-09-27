"""Phase 4 hero models: katanas + scabbards, R6 armour sets, floating stone fists, Earth Golem, the Hollow.

Weapons: pivot at the grip centre; blade points FRONT (Blender +Y -> Roblox -Z), cutting edge DOWN.
Armour: one mesh per R6 part, built in that part's local space (part centre = origin) so it welds on with an
identity offset. Golem / Hollow: part meshes named like R6 parts, placed in character space with an invisible
HumanoidRootPart box; roblox/HO_RigBuilder.lua builds the Motor6Ds so the Phase 2 animations play on them.
"""
import math, random
import bmesh
from mathutils import Vector, Matrix, noise
from geo import Builder, lathe, loft, tube
from harborkit import blob

MATS = ['Steel_Blade', 'Steel_Dark', 'Tsuka_Wrap', 'Black_Lacquer', 'Red_Lacquer', 'Navy_Lacquer', 'Gold_Leaf', 'Iron_Wrought',
        'Cloth_Crimson', 'Cloth_Navy', 'Cloth_White', 'Stone_Granite', 'Stone_Fitted', 'Shadow_Black', 'Timber_Dark',
        'Glow_Red', 'Glow_Blue', 'Glow_Amber', 'Glow_Yellow']
GLOW = ['Glow_Red', 'Glow_Blue', 'Glow_Amber', 'Glow_Yellow']


def B():
    return Builder(MATS)


def G():
    return Builder(GLOW)


# ================================================================================================ WEAPONS
KATANAS = {
    #            blade len, height, sori, steel, tsuba shape, tsuba mat, saya mat, glow, fittings
    'IronKatana': dict(L=2.5, h=0.2, sori=0.12, steel='Steel_Blade', tsuba='round', tmat='Iron_Wrought', saya='Black_Lacquer', glow=None, fit='Iron_Wrought'),
    'TemperedKatana': dict(L=2.6, h=0.21, sori=0.16, steel='Steel_Blade', tsuba='square', tmat='Iron_Wrought', saya='Black_Lacquer', glow=None, fit='Gold_Leaf'),
    'AshfallSword': dict(L=2.8, h=0.3, sori=0.07, steel='Steel_Dark', tsuba='heavy', tmat='Iron_Wrought', saya='Black_Lacquer', glow='Glow_Amber', fit='Iron_Wrought'),
    'CrimsonOath': dict(L=2.7, h=0.22, sori=0.18, steel='Steel_Blade', tsuba='flower', tmat='Gold_Leaf', saya='Red_Lacquer', glow='Glow_Red', fit='Gold_Leaf'),
    'MoonlitEdge': dict(L=2.7, h=0.2, sori=0.15, steel='Steel_Blade', tsuba='moon', tmat='Iron_Wrought', saya='Navy_Lacquer', glow='Glow_Blue', fit='Iron_Wrought'),
}
GRIP = 0.95


def blade_curve(t, L, sori):
    """Blade centre line: y along the blade, z curving up toward the spine (tip rises by `sori`)."""
    return Vector((0.0, GRIP / 2 + 0.12 + L * t, sori * t * t))


def blade(b, spec, g=None):
    L, h, sori, steel = spec['L'], spec['h'], spec['sori'], spec['steel']
    n = 20
    secs = []
    for i in range(n + 1):
        t = i / n
        c = blade_curve(t, L, sori)
        taper = 1.0 - 0.3 * t
        hh = h * taper
        if t > 0.88:                                       # kissaki: edge sweeps up to the point
            k = (t - 0.88) / 0.12
            hh *= max(0.02, 1 - k ** 1.6)
            c = c + Vector((0, 0, h * taper * 0.5 * k ** 1.3))
        th = 0.07 * taper * (1 - 0.8 * max(0.0, (t - 0.88) / 0.12))
        e = c + Vector((0, 0, -hh / 2))                    # cutting edge
        sh = c + Vector((0, 0, hh * 0.15))                 # shinogi (ridge line)
        sp = c + Vector((0, 0, hh / 2))                    # spine (mune)
        secs.append([e, sh + Vector((th / 2, 0, 0)), sp + Vector((th * 0.3, 0, 0)), sp + Vector((-th * 0.3, 0, 0)),
                     sh + Vector((-th / 2, 0, 0))])
    rings = loft(b, secs, steel, caps=True)
    for i, ring in enumerate(rings):                       # UV: U along the blade, V edge (0) -> spine (1)
        for j, v in enumerate(ring):
            vv = [0.0, 0.62, 1.0, 1.0, 0.62][j]
            for l in v.link_loops:
                l[b.uv].uv = (i / n * L * 0.35, vv)
    if spec['glow'] and g is not None:
        if spec['glow'] == 'Glow_Amber':                   # Ashfall: ember cracks along both flats
            r = random.Random(3)
            for side in (1, -1):
                pts = []
                for k in range(9):
                    t = 0.08 + 0.72 * k / 8
                    c = blade_curve(t, L, sori)
                    pts.append(c + Vector((side * 0.037 * (1 - 0.3 * t), 0, h * (1 - 0.3 * t) * (0.05 + 0.18 * math.sin(k * 1.7 + side)))))
                tube(g, pts, [0.018] * len(pts), 4, 'Glow_Amber', smooth=True)
        else:                                              # Crimson / Moonlit: glowing edge aura
            secs2 = []
            for i in range(n + 1):
                t = i / n
                c = blade_curve(t, L, sori)
                hh = h * (1.0 - 0.3 * t)
                if t > 0.88:
                    k = (t - 0.88) / 0.12
                    hh *= max(0.02, 1 - k ** 1.6); c = c + Vector((0, 0, h * (1 - 0.3 * t) * 0.5 * k ** 1.3))
                e = c + Vector((0, 0, -hh / 2))
                w = 0.03 * (1 - 0.5 * t)
                secs2.append([e + Vector((0, 0, -0.02)), e + Vector((w, 0, hh * 0.3)), e + Vector((-w, 0, hh * 0.3))])
            loft(g, secs2, spec['glow'])


def tsuba(b, spec, y):
    shape, mat = spec['tsuba'], spec['tmat']
    if shape == 'round':
        out = [(0.34 * math.cos(2 * math.pi * k / 20), 0.3 * math.sin(2 * math.pi * k / 20)) for k in range(20)]
    elif shape == 'square':
        out = []
        for k in range(24):
            a = 2 * math.pi * k / 24
            c, s = math.cos(a), math.sin(a)
            r = 0.34 / max(abs(c), abs(s)) ** 0.35
            out.append((r * c * 0.95, r * s * 0.85))
    elif shape == 'heavy':
        out = [(0.42 * math.cos(2 * math.pi * k / 8 + math.pi / 8), 0.36 * math.sin(2 * math.pi * k / 8 + math.pi / 8)) for k in range(8)]
    elif shape == 'flower':                                 # 8-lobed mokko
        out = [((0.36 + 0.06 * math.cos(8 * 2 * math.pi * k / 48)) * math.cos(2 * math.pi * k / 48),
                (0.33 + 0.06 * math.cos(8 * 2 * math.pi * k / 48)) * math.sin(2 * math.pi * k / 48)) for k in range(48)]
    else:                                                   # moon: disc with a crescent notch
        out = []
        for k in range(28):
            a = 2 * math.pi * k / 28
            r = 0.34 - (0.1 if math.cos(a - 0.8) > 0.8 else 0.0)
            out.append((r * math.cos(a), r * 0.9 * math.sin(a)))
    th = 0.09 if shape == 'heavy' else 0.06
    b.prism(out, (0, y, 0), (1, 0, 0), (0, 0, 1), (0, 1, 0), th, mat)
    if shape in ('flower', 'moon'):                         # raised rim ring
        rim = [(x * 1.02, z * 1.02) for x, z in out]
        b.prism(rim, (0, y + th, 0), (1, 0, 0), (0, 0, 1), (0, 1, 0), 0.012, 'Gold_Leaf' if shape == 'flower' else 'Iron_Wrought')
    return y + th


def katana(name):
    """Returns (weapon builder, scabbard builder, glow builder or None)."""
    spec = KATANAS[name]
    b = B(); g = G() if spec['glow'] else None
    # grip (oval, silk-wrapped), pommel, collar
    prof = [(0.075 * math.cos(2 * math.pi * k / 12), 0.095 * math.sin(2 * math.pi * k / 12)) for k in range(12)]
    b.sweep([Vector((0, -GRIP / 2, 0)), Vector((0, GRIP / 2, 0.01))], prof, 'Tsuka_Wrap', up=Vector((0, 0, 1)), uvd=2.2, smooth=True,
            smooth_sides=set(range(12)))
    lathe_y(b, -GRIP / 2, [(0.085, 0.0), (0.09, -0.05), (0.06, -0.1), (0.0, -0.11)], spec['fit'])
    lathe_y(b, GRIP / 2 - 0.02, [(0.09, 0.0), (0.092, 0.06), (0.0, 0.06)], spec['fit'])
    y = tsuba(b, spec, GRIP / 2 + 0.04)
    lathe_y(b, y, [(0.06, 0.0), (0.05, 0.08), (0.0, 0.08)], 'Gold_Leaf')                     # habaki
    blade(b, spec, g)
    # scabbard (saya) following the blade curve, with koiguchi mouth and kojiri tip, sageo cord
    s = B()
    L, sori = spec['L'], spec['sori']
    n = 16
    secs = []
    for i in range(n + 1):
        t = i / n
        c = blade_curve(t * 0.97, L, sori) + Vector((0, 0.02, 0))
        hw = 0.11 * (1 - 0.25 * t) + 0.02; hh = spec['h'] * (1 - 0.25 * t) * 0.62 + 0.05
        secs.append([c + Vector((hw * math.cos(2 * math.pi * k / 10), 0, hh * math.sin(2 * math.pi * k / 10))) for k in range(10)])
    rings = loft(s, secs, spec['saya'], caps=True)
    for i, ring in enumerate(rings):
        for k, v in enumerate(ring):
            for l in v.link_loops: l[s.uv].uv = (i / n * L * 0.3, k / 10)
    c0 = blade_curve(0.0, L, sori)
    s.box((-0.14, c0.y - 0.02, -spec['h'] * 0.62 - 0.06), (0.14, c0.y + 0.1, spec['h'] * 0.62 + 0.06), spec['fit'])
    ce = blade_curve(0.97, L, sori)
    lathe_y(s, ce.y + 0.02, [(0.1, 0.0), (0.08, 0.12), (0.0, 0.16)], spec['fit'], z=ce.z)
    k0 = blade_curve(0.12, L, sori)
    s.cylinder((0.13, k0.y, k0.z + 0.12), (-0.13, k0.y, k0.z + 0.12), 0.05, 8, spec['fit'])
    tube(s, [k0 + Vector((0.12, 0, 0.12)), k0 + Vector((0.2, 0.3, -0.25)), k0 + Vector((0.18, 0.7, -0.45)), k0 + Vector((0.14, 1.1, -0.5))],
         [0.03] * 4, 5, 'Cloth_Crimson' if spec['saya'] != 'Red_Lacquer' else 'Gold_Leaf')
    return b, s, g


def lathe_y(b, y, prof, mat, z=0.0):
    """Lathe around the Y axis (profile: (radius, offset along +Y))."""
    tmp = Builder(MATS)
    lathe(tmp, (0, 0, 0), prof, 12, mat)
    rotm = Matrix.Translation((0, y, z)) @ Matrix.Rotation(-math.pi / 2, 4, 'X')
    for v in tmp.bm.verts: v.co = rotm @ v.co
    bmesh.ops.recalc_face_normals(tmp.bm, faces=tmp.bm.faces)     # profiles may run either way along Y
    from castlekit import mesh_join
    mesh_join(b, tmp)


# ================================================================================================ ARMOUR (R6 pieces)
ARMOUR = {
    'Ashigaru': dict(plate='Black_Lacquer', lame='Black_Lacquer', lace='Cloth_Navy', trim='Iron_Wrought', crest=None, helmet='jingasa'),
    'Samurai': dict(plate='Red_Lacquer', lame='Black_Lacquer', lace='Cloth_Crimson', trim='Gold_Leaf', crest='kuwagata', helmet='kabuto'),
    'Oathguard': dict(plate='Navy_Lacquer', lame='Navy_Lacquer', lace='Cloth_White', trim='Gold_Leaf', crest='ring', helmet='kabuto'),
}
# Blender part space: X width, Y depth (front = +Y), Z height. R6 torso = 2 x 1 x 2, arm/leg = 1 x 1 x 2, head ~1.2.


def band(b, x0, x1, z0, z1, y_front, depth_back, mat, curve=0.12):
    """A curved plate/lame wrapping the front of a part: profile swept along X with a gentle curve."""
    n = 8
    secs = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        bulge = curve * (1 - ((2 * (x - x0) / (x1 - x0)) - 1) ** 2)
        yf = y_front + bulge
        secs.append([Vector((x, yf - 0.12, z0)), Vector((x, yf, z0 + 0.02)), Vector((x, yf, z1)), Vector((x, yf - 0.12, z1 - 0.02))])
    loft(b, secs, mat)


def armour_torso(set_name):
    s = ARMOUR[set_name]
    b = B()
    # breastplate (front) and back plate as stacked lames with lacing gaps
    zs = [1.05, 0.62, 0.22, -0.18, -0.58, -1.0]
    for k, (z1, z0) in enumerate(zip(zs, zs[1:])):
        mat = s['plate'] if k % 2 == 0 else s['lame']
        band(b, -1.12, 1.12, z0 + 0.03, z1, 0.64, 0.1, mat, curve=0.16)
        b.box((-1.12, -0.66, z0 + 0.03), (1.12, -0.54, z1), mat)   # back plate
        for x in (-0.7, 0.0, 0.7):                         # lacing cords
            b.box((x - 0.05, 0.62, z0 - 0.02), (x + 0.05, 0.84, z0 + 0.08), s['lace'])
    for sx in (-1, 1):                                     # side plates
        b.box((sx * 1.04 - 0.06, -0.62, -1.0), (sx * 1.04 + 0.06, 0.66, 1.05), s['plate'])
    b.box((-1.14, -0.68, 1.02), (1.14, 0.86, 1.12), s['trim'])                                  # top trim
    for sx in (-1, 1):                                     # shoulder straps
        b.box((sx * 0.75 - 0.18, -0.6, 1.05), (sx * 0.75 + 0.18, 0.7, 1.18), s['lame'])
    # kusazuri skirt: 4 panels of 3 lames hanging below the torso
    for (cx, cy, w, d) in ((0, 0.62, 1.0, 0.1), (0, -0.6, 1.0, 0.1), (1.0, 0.0, 0.1, 0.62), (-1.0, 0.0, 0.1, 0.62)):
        for j in range(3):
            z1 = -1.0 - j * 0.24; z0 = z1 - 0.22
            grow = 1 + j * 0.06
            b.box((cx - w * grow - 0.02, cy - d * grow - 0.02, z0), (cx + w * grow + 0.02, cy + d * grow + 0.02, z1),
                  s['plate'] if j % 2 == 0 else s['lame'])
    if s['crest'] == 'ring':                               # Oathguard crest: gold ring on the chest
        ring = [(0.32 * math.cos(2 * math.pi * k / 20), 0.32 * math.sin(2 * math.pi * k / 20)) for k in range(20)]
        b.prism(ring, (0, 0.82, 0.42), (1, 0, 0), (0, 0, 1), (0, 1, 0), 0.04, s['trim'])
        inner = [(0.2 * math.cos(2 * math.pi * k / 20), 0.2 * math.sin(2 * math.pi * k / 20)) for k in range(20)]
        b.prism(inner, (0, 0.86, 0.42), (1, 0, 0), (0, 0, 1), (0, 1, 0), 0.03, s['plate'])
    elif s['crest'] == 'kuwagata':
        b.cylinder((0, 0.8, 0.42), (0, 0.9, 0.42), 0.14, 10, s['trim'])
    return b


def armour_arm(set_name, side):
    """side = 1 right (+X is outward), -1 left. Shoulder guard (sode) + forearm guard (kote)."""
    s = ARMOUR[set_name]
    b = B()
    for j in range(5):                                     # sode: 5 lames on the outer upper arm
        z1 = 1.12 - j * 0.24; z0 = z1 - 0.22
        x = side * (0.55 + j * 0.02)
        b.box((min(x, x + side * 0.1), -0.62, z0), (max(x, x + side * 0.1), 0.62, z1), s['plate'] if j % 2 == 0 else s['lame'])
        b.box((min(x, x + side * 0.12), -0.1, z0 - 0.04), (max(x, x + side * 0.12), 0.1, z0 + 0.04), s['lace'])
    b.box((-0.58, -0.6, 1.0), (0.58, 0.6, 1.14), s['trim'])
    for j in range(4):                                     # kote: plates wrapping the forearm
        z1 = -0.2 - j * 0.2; z0 = z1 - 0.16
        b.box((-0.56, -0.56, z0), (0.56, 0.56, z1), s['plate'] if j % 2 == 0 else s['lame'])
    b.box((-0.52, -0.54, -1.0), (0.52, 0.54, -0.9), s['trim'])
    return b


def armour_leg(set_name, side):
    s = ARMOUR[set_name]
    b = B()
    for j in range(3):                                     # haidate thigh apron (front)
        z1 = 0.95 - j * 0.26; z0 = z1 - 0.24
        b.box((-0.54, 0.5, z0), (0.54, 0.6, z1), s['plate'] if j % 2 == 0 else s['lame'])
    for j in range(3):                                     # suneate shin guard (front + sides)
        z1 = -0.25 - j * 0.24; z0 = z1 - 0.22
        b.box((-0.56, 0.48, z0), (0.56, 0.6, z1), s['plate'])
        b.box((side * 0.5 - 0.05, -0.3, z0), (side * 0.5 + 0.05, 0.55, z1), s['lame'])
    b.box((-0.58, 0.46, -0.28), (0.58, 0.62, -0.18), s['trim'])
    return b


def armour_helmet(set_name):
    s = ARMOUR[set_name]
    b = B()
    if s['helmet'] == 'jingasa':                           # conical ashigaru hat
        lathe(b, (0, 0, 0.35), [(1.3, 0.0), (1.2, 0.08), (0.4, 0.55), (0.0, 0.7)], 16, s['plate'])
        lathe(b, (0, 0, 0.33), [(1.32, 0.0), (1.32, 0.05), (1.2, 0.05), (1.2, 0.0)], 16, s['trim'], cap_bottom=False, cap_top=False)
        return b
    lathe(b, (0, 0, 0.1), [(0.72, 0.0), (0.74, 0.25), (0.62, 0.55), (0.3, 0.75), (0.0, 0.8)], 16, s['lame'])       # bowl
    for j in range(4):                                     # shikoro neck guard
        r0 = 0.76 + j * 0.1
        lathe(b, (0, 0, 0.12 - j * 0.14), [(r0 + 0.1, 0.0), (r0, 0.14)], 16, s['plate'] if j % 2 == 0 else s['lame'],
              cap_bottom=False, cap_top=False)
    b.box((-0.7, 0.55, 0.2), (0.7, 0.8, 0.3), s['trim'])                                      # visor
    for sx in (-1, 1):                                      # fukigaeshi (turn-backs)
        b.box((sx * 0.9 - 0.2, 0.2, -0.05), (sx * 0.9 + 0.2, 0.45, 0.3), s['plate'])
    if s['crest'] == 'kuwagata':
        for sx in (-1, 1):
            tube(b, [Vector((sx * 0.12, 0.78, 0.35)), Vector((sx * 0.35, 0.85, 0.9)), Vector((sx * 0.45, 0.82, 1.5))], [0.07, 0.06, 0.03], 5, s['trim'])
    elif s['crest'] == 'ring':
        ring = [(0.3 * math.cos(2 * math.pi * k / 20), 0.3 * math.sin(2 * math.pi * k / 20)) for k in range(20)]
        b.prism(ring, (0, 0.8, 0.7), (1, 0, 0), (0, 0, 1), (0, 1, 0), 0.05, s['trim'])
    return b


# ================================================================================================ STONE FIST
def rockbox(b, c, size, mat='Stone_Granite', seed=0, rotm=None, amp=0.12):
    """Chunky carved stone block (noise-softened, faceted)."""
    tmp = Builder(MATS)
    blob(tmp, (0, 0, 0), (size[0] / 2, size[1] / 2, size[2] / 2), mat, subdiv=2, amp=amp, freq=0.8, seed=seed, smooth=False)
    # squarish: push vertices toward a box shape
    for v in tmp.bm.verts:
        p = v.co
        m = max(abs(p.x) / (size[0] / 2), abs(p.y) / (size[1] / 2), abs(p.z) / (size[2] / 2), 1e-6)
        v.co = p.lerp(p / m, 0.55)
        if rotm: v.co = rotm @ v.co
        v.co += Vector(c)
    from castlekit import mesh_join
    mesh_join(b, tmp)


def stone_fist(side=1):
    """Floating carved-stone fist punching toward +Y: palm/back block, 4 curled 3-segment fingers with knuckle
    ridges, wrapped thumb, cracked forearm stump; glowing amber cracks & joints in the glow builder.
    side = 1 right fist, -1 left (mirrored)."""
    b = B(); g = G()
    rockbox(b, (0, -0.3, 0), (2.0, 1.6, 1.6), seed=1)                       # back of hand / palm block
    for k in range(4):                                                      # fingers
        x = (-0.72 + 0.48 * k) * side
        w = 0.42 if k < 3 else 0.36
        base = Vector((x, 0.55, 0.35))
        seg_len = [0.62, 0.5, 0.42]
        ang = 0.0
        p = base
        for j in range(3):
            ang += [15, 80, 85][j]
            d = Vector((0, math.cos(math.radians(ang)), -math.sin(math.radians(ang))))
            c = p + d * seg_len[j] / 2
            rotm = Matrix.Rotation(-math.radians(ang), 3, 'X')
            rockbox(b, c, (w, seg_len[j] + 0.06, w * 0.95), seed=10 + k * 3 + j, rotm=rotm, amp=0.08)
            if j < 2:                                                       # glowing joint between segments
                jp = p + d * seg_len[j]
                g.cylinder((jp.x - w * 0.42, jp.y, jp.z), (jp.x + w * 0.42, jp.y, jp.z), w * 0.26, 6, 'Glow_Amber')
            p = p + d * seg_len[j]
        rockbox(b, base + Vector((0, 0.05, 0.28)), (w * 0.9, 0.35, 0.22), seed=40 + k, amp=0.1)   # knuckle ridge
    # thumb wrapped across the front of the curled fingers
    tb = Vector((1.05 * side, 0.2, -0.1))
    rockbox(b, tb + Vector((0, 0.25, 0)), (0.5, 0.7, 0.5), seed=50, rotm=Matrix.Rotation(math.radians(30 * side), 3, 'Z'))
    rockbox(b, Vector((0.55 * side, 0.95, -0.35)), (0.75, 0.42, 0.42), seed=51, rotm=Matrix.Rotation(math.radians(-10 * side), 3, 'Z'))
    # forearm stump: tapering, broken jagged end
    tmp = Builder(MATS)
    blob(tmp, (0, -1.9, -0.05), (0.85, 1.3, 0.8), 'Stone_Granite', subdiv=3, amp=0.18, freq=0.7, seed=60, smooth=False)
    for v in tmp.bm.verts:
        if v.co.y < -2.6:                                                   # jagged broken end
            v.co.y = -2.6 - (noise.noise(v.co * 3.0) * 0.35 + 0.2)
    from castlekit import mesh_join
    mesh_join(b, tmp)
    # amber cracks over the back of the hand and forearm
    r = random.Random(7 + side)
    for k in range(6):
        pts = []
        y = r.uniform(-2.5, 0.2); a = r.uniform(0, 2 * math.pi)
        for j in range(6):
            y += r.uniform(0.15, 0.35); a += r.uniform(-0.5, 0.5)
            rr = 0.84 if y < -0.9 else 0.83
            pts.append(Vector((math.cos(a) * rr, y, math.sin(a) * rr * 0.95)))
        tube(g, pts, [0.045] * len(pts), 4, 'Glow_Amber', smooth=True)
    return b, g


# ================================================================================================ CHARACTER RIG PARTS
def hrp_box(b, s):
    """Invisible HumanoidRootPart box (2s x 1s x 2s) centred on the character origin (rig reference)."""
    b.box((-s, -0.5 * s, -s), (s, 0.5 * s, s), 'Shadow_Black')


def golem():
    """Earth Golem at rig scale 2.4: returns {part name: (builder, glow builder or None)} in PART-LOCAL space
    (part centre = origin; Blender axes: X right, Y front, Z up)."""
    s = 2.4
    parts = {}
    # torso: core + chest plates + belly segments
    b = B(); g = G()
    rockbox(b, (0, -0.1, 0), (2.0 * s * 0.9, 1.0 * s * 0.9, 2.0 * s * 0.9), seed=101, amp=0.1)
    for sx in (-1, 1):
        rockbox(b, (sx * 1.05, 0.55 * s * 0.8, 1.3), (2.1, 0.9, 1.9), seed=102 + sx, amp=0.1)      # pecs
    for k in range(3):
        rockbox(b, (0, 0.5 * s * 0.8, -0.4 - k * 0.95), (2.6 - k * 0.3, 0.8, 0.8), seed=110 + k, amp=0.08)   # belly segments
    for k in range(4):                                     # amber cracks between plates
        g.box((-1.4 + k * 0.9, 1.05, -1.9 + 0.0), (-1.3 + k * 0.9, 1.12, 0.4), 'Glow_Amber')
    parts['Torso'] = (b, g)
    # head: blocky skull, heavy brow, glowing eyes, jaw
    b = B(); g = G()
    rockbox(b, (0, 0, 0.1), (3.0, 2.4, 2.2), seed=120, amp=0.1)
    rockbox(b, (0, 1.05, 0.75), (3.2, 0.8, 0.7), seed=121, amp=0.08)                             # brow
    rockbox(b, (0, 0.7, -0.75), (2.4, 1.2, 0.8), seed=122, amp=0.08)                             # jaw
    rockbox(b, (0, -0.1, -1.25), (1.9, 1.7, 1.0), seed=123, amp=0.08)                            # neck block
    for sx in (-1, 1):
        g.cylinder((sx * 0.7, 1.05, 0.25), (sx * 0.7, 1.35, 0.25), 0.28, 10, 'Glow_Yellow')
    parts['Head'] = (b, g)
    # arms: boulder shoulder, upper arm, forearm, big block fist
    for name, sx in (('Right Arm', 1), ('Left Arm', -1)):
        b = B()
        blob(b, (sx * 0.2, 0, 1.9), (1.8, 1.7, 1.5), 'Stone_Granite', subdiv=3, amp=0.2, freq=0.6, seed=130 + sx, smooth=False)
        rockbox(b, (0, 0, 0.4), (1.9, 1.9, 2.0), seed=132 + sx, amp=0.1)
        rockbox(b, (0, 0.1, -1.4), (2.3, 2.3, 2.1), seed=134 + sx, amp=0.1)
        rockbox(b, (0, 0.2, -2.9), (2.9, 2.9, 2.2), seed=136 + sx, amp=0.1)                          # fist
        for k in range(4):
            rockbox(b, (-0.9 + k * 0.6, 1.5, -2.8), (0.5, 0.35, 0.6), seed=140 + k + sx, amp=0.1)   # knuckles
        parts[name] = (b, None)
    for name, sx in (('Right Leg', 1), ('Left Leg', -1)):
        b = B()
        rockbox(b, (0, 0, 1.2), (2.2, 2.2, 2.4), seed=150 + sx, amp=0.1)                            # thigh
        rockbox(b, (0, 0.55, 0.05), (1.9, 0.9, 1.0), seed=152 + sx, amp=0.08)                       # knee plate
        rockbox(b, (0, 0, -1.3), (2.0, 2.0, 2.2), seed=154 + sx, amp=0.1)                           # shin
        rockbox(b, (0, 0.5, -2.35), (2.4, 3.0, 0.9), seed=156 + sx, amp=0.08)                       # foot
        parts[name] = (b, None)
    return parts, s


def hollow():
    """The Hollow (R6 scale): black shadow body, glowing red slit-pupil eye in the chest, red cracks, tattered
    shadow wisps, clawed hands. Returns {part: (builder, glow)} in part-local space."""
    s = 1.0
    parts = {}
    b = B(); g = G()
    blob(b, (0, 0.02, 0.3), (1.0, 0.56, 0.78), 'Shadow_Black', subdiv=3, amp=0.12, freq=0.7, seed=201)      # chest
    blob(b, (0, -0.02, -0.55), (0.62, 0.42, 0.55), 'Shadow_Black', subdiv=3, amp=0.12, freq=0.8, seed=202)   # narrow waist
    for k in range(4):                                       # spine ridge spikes on the back
        tube(b, [Vector((0, -0.45, 0.75 - k * 0.35)), Vector((0, -0.8, 0.85 - k * 0.35))], [0.1, 0.005], 5, 'Shadow_Black')
    lathe(g, (0, 0, 0), [(0.0, 0.0), (0.36, 0.02), (0.36, 0.06), (0.0, 0.08)], 16, 'Glow_Red')     # eye (flat lens)
    for v in g.bm.verts:
        v.co = Matrix.Translation((0, 0.52, 0.25)) @ Matrix.Rotation(-math.pi / 2, 4, 'X') @ v.co
    b.box((-0.05, 0.6, 0.02), (0.05, 0.64, 0.48), 'Shadow_Black')                                   # slit pupil
    r = random.Random(3)
    for k in range(7):                                       # red cracks radiating from the eye
        a = 2 * math.pi * k / 7 + r.uniform(-0.2, 0.2)
        pts = []
        x, z = 0.0, 0.25
        for j in range(5):
            x += math.cos(a) * 0.18 + r.uniform(-0.05, 0.05); z += math.sin(a) * 0.18 + r.uniform(-0.05, 0.05)
            yv = 0.5 * math.sqrt(max(0.05, 1 - (x / 1.0) ** 2 - ((z - 0.1) / 1.05) ** 2)) + 0.07
            pts.append(Vector((x, yv, z)))
        tube(g, pts, [0.03 * (1 - j / 6) for j in range(5)], 4, 'Glow_Red')
    for k in range(5):                                       # tattered wisps hanging from the back
        x = -0.8 + 0.4 * k
        wisp(b, Vector((x, -0.55, 0.6)), 1.6 + r.uniform(0, 0.8), r.random())
    parts['Torso'] = (b, g)
    b = B(); g = G()
    blob(b, (0, 0.05, 0.05), (0.62, 0.6, 0.66), 'Shadow_Black', subdiv=3, amp=0.12, freq=0.8, seed=210)
    for sx in (-1, 1):                                       # faint red eye glints
        g.cylinder((sx * 0.22, 0.55, 0.1), (sx * 0.22, 0.62, 0.1), 0.06, 6, 'Glow_Red')
    for sx in (-1, 1):                                       # swept-back horn spikes
        tube(b, [Vector((sx * 0.35, 0.0, 0.5)), Vector((sx * 0.55, -0.4, 0.9)), Vector((sx * 0.6, -0.9, 1.1))], [0.12, 0.07, 0.01], 6, 'Shadow_Black')
    parts['Head'] = (b, g)
    UP = Vector((0, 1, 0))                                   # limbs run along Z: frame 'up' must not be Z
    for name, sx in (('Right Arm', 1), ('Left Arm', -1)):
        b = B(); g = G()
        # long thin arm reaching past the knee, bony elbow, clawed hand
        blob(b, (0, 0, 0.72), (0.5, 0.48, 0.42), 'Shadow_Black', subdiv=2, amp=0.1, freq=0.9, seed=220 + sx)   # shoulder
        tube(b, [Vector((0, 0, 0.8)), Vector((0, -0.05, -0.05)), Vector((0, 0.18, -1.05))], [0.34, 0.24, 0.17], 10,
             'Shadow_Black', up=UP)
        blob(b, (0, -0.07, -0.05), (0.26, 0.28, 0.24), 'Shadow_Black', subdiv=2, amp=0.1, seed=224 + sx)          # elbow
        blob(b, (0, 0.2, -1.12), (0.24, 0.2, 0.2), 'Shadow_Black', subdiv=2, amp=0.1, seed=226 + sx)             # hand
        for k in range(4):                                   # claws
            a = -0.6 + k * 0.4
            base = Vector((math.sin(a) * 0.17, 0.24 + math.cos(a) * 0.06, -1.2))
            tube(b, [base, base + Vector((math.sin(a) * 0.1, 0.12, -0.3)), base + Vector((math.sin(a) * 0.08, 0.32, -0.55))],
                 [0.06, 0.045, 0.005], 5, 'Shadow_Black', up=UP)
        wisp(b, Vector((sx * 0.3, -0.15, 0.3)), 1.2, 0.3 + 0.2 * sx)
        tube(g, [Vector((sx * 0.2, 0.24, 0.6)), Vector((sx * 0.22, 0.2, 0.0)), Vector((sx * 0.15, 0.3, -0.8))], [0.025] * 3, 4,
             'Glow_Red', up=UP)
        parts[name] = (b, g)
    for name, sx in (('Right Leg', 1), ('Left Leg', -1)):
        b = B()
        # digitigrade leg: thigh forward, shin back, raised heel, clawed toes
        blob(b, (0, 0.05, 0.6), (0.44, 0.42, 0.5), 'Shadow_Black', subdiv=2, amp=0.1, seed=230 + sx)            # hip / thigh
        tube(b, [Vector((0, 0.05, 0.5)), Vector((0, 0.25, -0.2)), Vector((0, -0.15, -0.7)), Vector((0, 0.0, -0.95))],
             [0.34, 0.24, 0.16, 0.14], 10, 'Shadow_Black', up=UP)
        blob(b, (0, 0.25, -0.2), (0.25, 0.26, 0.24), 'Shadow_Black', subdiv=2, amp=0.1, seed=232 + sx)          # knee
        blob(b, (0, 0.2, -0.93), (0.22, 0.4, 0.1), 'Shadow_Black', subdiv=2, amp=0.1, seed=234 + sx, flat_bottom=-1.0)  # foot
        for k in range(3):                                   # toe claws
            x = -0.12 + 0.12 * k
            tube(b, [Vector((x, 0.5, -0.95)), Vector((x * 1.3, 0.72, -0.97)), Vector((x * 1.4, 0.86, -1.0))],
                 [0.05, 0.035, 0.005], 5, 'Shadow_Black', up=Vector((0, 0, 1)))
        parts[name] = (b, None)
    return parts, s


def wisp(b, top, length, phase):
    """Tattered shadow ribbon hanging down from `top` (double-sided strip with a ragged end)."""
    n = 6
    pts = []
    for j in range(n + 1):
        t = j / n
        pts.append(top + Vector((math.sin(t * 3 + phase * 6) * 0.15, -0.1 * t, -length * t)))
    w0 = 0.35
    for side in (1, -1):
        for j in range(n):
            wa = w0 * (1 - 0.6 * j / n); wb = w0 * (1 - 0.6 * (j + 1) / n)
            if j == n - 1: wb *= 0.3
            q = [pts[j] + Vector((-wa / 2, side * 0.01, 0)), pts[j] + Vector((wa / 2, side * 0.01, 0)),
                 pts[j + 1] + Vector((wb / 2, side * 0.01, 0)), pts[j + 1] + Vector((-wb / 2, side * 0.01, 0))]
            vs = [b.bm.verts.new(p) for p in q]
            b.face(vs, 'Shadow_Black', [(0, j / n), (1, j / n), (1, (j + 1) / n), (0, (j + 1) / n)], out=Vector((0, side, 0)), smooth=True)
