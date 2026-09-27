"""Special (gameplay) buildings: Tidewatch Inn, Blacksmith, Armory, General Store, Magic Stall, Kura.

Same conventions as buildkit: footprint centred on the origin, front = +Y (Roblox -Z), ground z = 0,
plinth 0..1, floors of 9 studs. Glowing parts (lanterns, embers, orbs) go to a separate '_Glow' mesh
so they can be made Neon / given PointLights in Roblox; sliding doors are separate '_Door*' meshes.
"""
import math, random
from mathutils import Vector, Matrix
import ho
import wallkit as wk
import propkit as pk
import buildkit as bk
from buildkit import Assembly, M, PLINTH, FLOOR, ALL_MATS
from geo import Builder, lathe
from roofkit import Kirizuma, Irimoya, Hisashi

PROP_MATS = pk.MATS


def P():
    return Builder(PROP_MATS)


def G():
    return Builder(pk.GLOW_MATS)


def plank_floor(asm, group, x0, x1, y0, y1, ztop, mat='Wood_Planks', base=0.0, side='Timber_Dark'):
    b = Builder(ALL_MATS)
    b.box((x0, y0, base), (x1, y1, ztop - 0.12), side, skip=('-z', '+z'))
    b.box((x0, y0, ztop - 0.12), (x1, y1, ztop), mat, skip=('-z',), uvd=(1 / 3.0 if mat == 'Tatami' else 0.25))
    asm.add(group, b)


def slab_with_hole(asm, group, W, D, z, hole=None, top='Wood_Planks'):
    """Upper-floor slab (top at z) covering the interior, optionally leaving a rectangular stair hole."""
    x0, x1, y0, y1 = -W / 2 + 1, W / 2 - 1, -D / 2 + 1, D / 2 - 1
    rects = [(x0, x1, y0, y1)]
    if hole:
        hx0, hx1, hy0, hy1 = hole
        rects = [(x0, x1, y0, hy0), (x0, x1, hy1, y1), (x0, hx0, hy0, hy1), (hx1, x1, hy0, hy1)]
    b = Builder(ALL_MATS)
    for (a0, a1, c0, c1) in rects:
        if a1 - a0 < 0.05 or c1 - c0 < 0.05: continue
        b.box((a0, c0, z - 0.6), (a1, c1, z - 0.1), 'Timber_Light')
        b.box((a0, c0, z - 0.1), (a1, c1, z), top, skip=('-z',))
    n = int((x1 - x0) / 5)
    for i in range(1, n + 1):
        x = x0 + (x1 - x0) * i / (n + 1)
        if hole and hole[0] - 0.4 < x < hole[1] + 0.4: continue
        b.beam_box((x - 0.35, y0, z - 1.3), (x + 0.35, y1, z - 0.6), 'Timber_Dark', along='y')
    asm.add(group, b)


def stair(asm, group, x0, x1, ya, yb, z0, z1, steps=None):
    """Straight wooden stair rising from y=ya (z0) to y=yb (z1), between x0..x1, with stringers."""
    b = Builder(ALL_MATS)
    n = steps or max(4, int(round(abs(z1 - z0) / 0.7)))
    run = (yb - ya) / n
    for i in range(n):
        zt = z0 + (z1 - z0) * (i + 1) / n
        yA, yB = sorted((ya + run * i, ya + run * (i + 1)))
        b.box((x0 + 0.3, yA, zt - 0.2), (x1 - 0.3, yB + (0.1 if run > 0 else 0), zt), 'Wood_Planks')
    for xs in (x0, x1 - 0.3):
        path_lo = Vector((xs + 0.15, ya, z0 - 0.3)); path_hi = Vector((xs + 0.15, yb, z1 - 0.3))
        b.beam(path_lo, path_hi, 0.3, 0.8, 'Timber_Dark', up=Vector((0, 0, 1)))
    asm.add(group, b)


def railing(b, p0, p1, h=3.0, n=None):
    p0, p1 = Vector(p0), Vector(p1)
    L = (p1 - p0).length
    n = n or max(2, int(L / 1.2) + 1)
    for i in range(n):
        q = p0.lerp(p1, i / (n - 1))
        b.beam_box((q.x - 0.12, q.y - 0.12, q.z), (q.x + 0.12, q.y + 0.12, q.z + h), 'Timber_Dark', along='z')
    b.beam(p0 + Vector((0, 0, h)), p1 + Vector((0, 0, h)), 0.22, 0.2, 'Timber_Dark')
    b.beam(p0 + Vector((0, 0, h * 0.45)), p1 + Vector((0, 0, h * 0.45)), 0.14, 0.14, 'Timber_Dark')


def chochin(b, g, x, y, z, r=0.55, h=1.5):
    """Hanging paper lantern: black caps (b) + ribbed paper body (g, glowing)."""
    prof = [(r * 0.55, 0.0), (r * 0.9, h * 0.15), (r, h * 0.5), (r * 0.9, h * 0.85), (r * 0.55, h)]
    lathe(g, (x, y, z), prof, 10, 'Shoji_Paper')
    lathe(b, (x, y, z - 0.12), [(r * 0.6, 0.0), (r * 0.6, 0.14)], 10, 'Black_Lacquer')
    lathe(b, (x, y, z + h - 0.02), [(r * 0.6, 0.0), (r * 0.6, 0.14)], 10, 'Black_Lacquer')
    b.cylinder((x, y, z + h + 0.12), (x, y, z + h + 0.9), 0.03, 4, 'Cloth_Crimson')


def shell(asm, W, D, floors, seed=0, front_mods=None):
    """Plinth + per-floor walls + corner posts. floors = [{'front': fn, 'back': fn, 'side': fn}, ...] where each fn is
    (module_len, index, centre) -> WallBuilder. Groups: Structure_GF / Structure_2F ... Returns the wall-top height."""
    bk.plinths(asm, W, D)
    z = PLINTH
    for k, fl in enumerate(floors):
        grp = 'Structure_GF' if k == 0 else f'Structure_{k + 1}F'
        bk.wall_run(asm, grp, W, z, 'front', W, D, fl['front'], seed + 10 * k + 1, mods=fl.get('front_mods'))
        bk.wall_run(asm, grp, W, z, 'back', W, D, fl['back'], seed + 10 * k + 2)
        for side in ('right', 'left'):
            bk.wall_run(asm, grp, D, z, side, W, D, fl['side'], seed + 10 * k + 3)
        for sx in (1, -1):
            for sy in (1, -1):
                asm.add(grp, wk.corner_post(), M(sx * (W / 2 - 0.5), sy * (D / 2 - 0.5), z))
        z += FLOOR
    return z


def W_(bays):
    """Helper: make a bay function from a per-module bay list rule."""
    return lambda m, i, c: wk.wall(m, bays(m, i))


# ================================================================================================= TIDEWATCH INN
def tidewatch_inn(name='HO_Bldg_TidewatchInn'):
    """40 x 24, two storeys. GF: genkan, lobby with reception counter & key board, dining hall, stair.
    2F: corridor, 6 guest rooms (tatami, futon, low table + cushions, andon, tansu, sliding door) and a stair hall."""
    random.seed(11)
    W, D = 40, 24
    asm = Assembly(name)
    zf2 = PLINTH + FLOOR
    top = shell(asm, W, D, [
        dict(front=lambda m, i, c: wk.wall(m, ['door', 'door'] if m == 8 else ['koshi'] * (m // 4)), front_mods=[16, 8, 16],
             back=W_(lambda m, i: ['window' if k % 2 else 'plaster' for k in range(m // 4)]),
             side=W_(lambda m, i: ['plaster', 'window'] + ['plaster'] * (m // 4 - 2) if m >= 8 else ['plaster'])),
        dict(front=W_(lambda m, i: ['lattice'] * (m // 4)),
             back=W_(lambda m, i: ['window'] * (m // 4)),
             side=W_(lambda m, i: ['plaster', 'window'] + ['plaster'] * (m // 4 - 2) if m >= 8 else ['plaster'])),
    ])
    x0, x1, y0, y1 = -W / 2 + 1, W / 2 - 1, -D / 2 + 1, D / 2 - 1
    zr = PLINTH + 1.3                      # raised ground-floor level
    zu = zf2 + 0.5                         # upper floor level (top of tatami / planks)
    # ---------------- ground floor
    gi = Builder(ALL_MATS)
    gi.box((-4.5, 7.0, 0.0), (4.5, y1, PLINTH), 'Earth_Packed', skip=('-z',))          # genkan (earthen entry)
    gi.box((-2.0, 6.0, PLINTH), (2.0, 7.0, PLINTH + 0.65), 'Stone_Granite')              # step stone
    asm.add('Interior_GF', gi)
    for (a0, a1, c0, c1) in ((x0, -4.5, 0.0, y1), (4.5, x1, 0.0, y1), (-4.5, 4.5, 0.0, 7.0)):
        plank_floor(asm, 'Interior_GF', a0, a1, c0, c1, zr)
    plank_floor(asm, 'Interior_GF', x0, x1, y0, 0.0, zr + 0.05, mat='Tatami')             # dining hall
    b = P(); g = G()
    b.beam_box((-4.6, 6.9, zr - 0.35), (4.6, 7.15, zr + 0.05), 'Timber_Dark', along='x')  # agari-kamachi edge
    # reception counter (choba) with lattice screen, key board, chest, lantern
    pk.counter(b, -10.0, 4.5, zr, w=7.0, d=1.8, h=2.6)
    for i in range(8):
        xx = -13.3 + i * 0.95
        b.beam_box((xx - 0.05, 3.9, zr + 2.6), (xx + 0.05, 4.05, zr + 4.2), 'Timber_Dark', along='z')
    b.beam_box((-13.5, 3.85, zr + 4.2), (-6.5, 4.1, zr + 4.35), 'Timber_Dark', along='x')
    kb = Builder(PROP_MATS)
    kb.box((-13.5, 0.2, zr + 3.2), (-8.5, 0.35, zr + 5.6), 'Wood_Planks')                  # key board on the partition
    for r in range(2):
        for c in range(3):
            kx = -12.8 + c * 1.6; kz = zr + 4.8 - r * 1.2
            kb.beam_box((kx - 0.03, 0.35, kz), (kx + 0.03, 0.55, kz + 0.06), 'Iron_Wrought', along='y')
            kb.box((kx - 0.22, 0.4, kz - 0.75), (kx + 0.22, 0.5, kz - 0.05), 'Timber_Light')
    asm.add('Interior_GF', kb)
    pk.tansu(b, -16.8, 1.2, zr, w=3.0, d=1.4, h=3.6, rows=4)
    pk.andon(b, g, -6.8, 5.8, zr)
    pk.barrel(b, 7.0, 9.5, zr, r=0.7, h=1.9, straw=True)                                 # welcome sake cask
    pk.jar(b, -7.5, 9.8, zr, h=1.8, r=0.8)
    # partition between lobby and dining hall (shoji panels, open middle)
    part = wk.WallBuilder(1)
    for k in range(10):
        a = x0 + k * 3.1
        if k in (4, 5): continue                      # open passage into the dining hall
        wk.WallBuilder.shoji(part, a, a + 3.1, 0.0, 6.2, y=0.08 if k % 2 else -0.08, cols=2, rows=4)
    part.b.beam_box((x0, -0.25, 6.2), (x1 - 7.0, 0.25, 6.6), 'Timber_Dark', along='x')
    part.plaster(x0, x1 - 7.0, 6.6, zf2 - 0.6 - zr, -0.15, 0.15)
    asm.add('Interior_GF', part.b, M(0, 0, zr))
    # dining tables
    for tx in (-15.0, -8.0, -1.0, 6.0):
        pk.low_table(b, tx, -5.5, zr + 0.05, w=3.6, d=2.2)
    for tx in (-15.0, -8.0, -1.0):
        pk.andon(b, g, tx + 3.2, -9.8, zr + 0.05)
    asm.add('Interior_GF', b); asm.add('Glow', g)
    # stair: east side, rising toward the back, arriving in the upper stair hall
    sx0, sx1 = 14.5, 18.6
    stair(asm, 'Interior_GF', sx0, sx1, 4.5, -7.5, zr, zu)
    # ---------------- upper floor
    slab_with_hole(asm, 'Interior_2F', W, D, zf2, hole=(sx0, sx1, -7.5, 4.5))
    rooms_x = [x0 + (12.0 - x0) * k / 3 for k in range(4)]     # 3 rooms per side between x0 and x = 12
    hall_x = 12.0
    ci = Builder(ALL_MATS)
    ci.box((x0, -2.0, zf2), (hall_x, 2.0, zu), 'Wood_Planks', skip=('-z',))                 # corridor
    ci.box((hall_x, y0, zf2), (sx0, y1, zu), 'Wood_Planks', skip=('-z',))                   # stair hall walkway
    ci.box((sx0, y0, zf2), (x1, -7.5, zu), 'Wood_Planks', skip=('-z',))                     # top landing
    ci.box((sx0, 4.5, zf2), (x1, y1, zu), 'Wood_Planks', skip=('-z',))
    railing(ci, (sx0 - 0.1, -7.3, zu), (sx0 - 0.1, 4.6, zu), h=2.8)
    railing(ci, (sx0, 4.6, zu), (x1 - 0.2, 4.6, zu), h=2.8)
    asm.add('Interior_2F', ci)
    rb = P(); rg = G()
    room = 0
    for side, (ya, yb) in (('front', (2.0, y1)), ('back', (y0, -2.0))):
        for k in range(3):
            room += 1
            ra, rb_x = rooms_x[k], rooms_x[k + 1]
            plank_floor(asm, 'Interior_2F', ra, rb_x, ya, yb, zu, mat='Tatami', base=zf2)
            # partition walls between rooms / to the hall (plaster on a timber frame)
            xw = rb_x
            wp = Builder(ALL_MATS)
            wp.box((xw - 0.3, ya, zu), (xw + 0.3, yb, top - 0.7), 'Plaster_White', uvv=1 / 9.0)
            wp.beam_box((xw - 0.4, ya, top - 0.7), (xw + 0.4, yb, top), 'Timber_Dark', along='y')
            wp.beam_box((xw - 0.4, ya, zu + 6.6), (xw + 0.4, yb, zu + 7.0), 'Timber_Dark', along='y')
            asm.add('Interior_2F', wp)
            # corridor wall with a sliding shoji door (door = separate mesh)
            yw = 2.0 if side == 'front' else -2.0
            Lr = rb_x - ra
            cw = wk.WallBuilder(Lr)
            n = 4
            for j in range(n):
                a = -Lr / 2 + Lr * j / n; c = -Lr / 2 + Lr * (j + 1) / n
                if j == 1:
                    d = Builder(wk.MATS)
                    wk.WallBuilder.shoji(cw, a, c, 0.0, 6.6, y=0.1, b=d, cols=2, rows=5, frame_w=0.16, depth=0.16)
                    cw.doors.append((f'Room{room}', d))
                else:
                    wk.WallBuilder.shoji(cw, a, c, 0.0, 6.6, y=-0.1, cols=2, rows=5)
            cw.b.beam_box((-Lr / 2, -0.3, 6.6), (Lr / 2, 0.3, 7.0), 'Timber_Dark', along='x')
            cw.plaster(-Lr / 2, Lr / 2, 7.0, top - zu, -0.2, 0.2)
            cw.b.beam_box((-Lr / 2, -0.3, -0.05), (Lr / 2, 0.3, 0.12), 'Timber_Dark', along='x')   # threshold track
            rot = 0.0 if side == 'front' else math.pi
            mtx = M((ra + rb_x) / 2, yw, zu, rot)
            asm.add('Interior_2F', cw.b, mtx)
            for dn, db in cw.doors:
                asm.add(f'Door_{dn}', db, mtx)
            # room number plate beside the door
            plate = Builder(ALL_MATS)
            py = yw + (-0.25 if side == 'front' else 0.25)
            plate.box((ra + Lr * 0.5 - 0.35, py - 0.05, zu + 7.2), (ra + Lr * 0.5 + 0.35, py + 0.05, zu + 8.0), 'Timber_Light')
            asm.add('Interior_2F', plate)
            # furniture (mirrored for back rooms so the futon lies along the outer wall)
            s = 1 if side == 'front' else -1
            yo = yb if side == 'front' else ya                   # outer wall line
            cx = (ra + rb_x) / 2
            pk.futon(rb, cx - 1.2, yo - s * 2.2, zu, cover=random.choice(['Cloth_Indigo', 'Cloth_Navy', 'Cloth_Crimson']))
            pk.low_table(rb, cx + 2.2, (ya + yb) / 2, zu, w=2.4, d=1.6, h=1.0, cushions=2)
            pk.andon(rb, rg, ra + 1.0, yo - s * 1.0, zu)
            tb = P()
            pk.tansu(tb, 0, 0, 0, w=2.6, d=1.2, h=3.0, rows=3)
            asm.add('Interior_2F', tb, M(rb_x - 1.2, (ya + yb) / 2 - s * 0.5, zu, -math.pi / 2))
    asm.add('Interior_2F', rb); asm.add('Glow', rg)
    # ---------------- front: awning, noren, lanterns, standing sign
    asm.add('Front', Hisashi(W, P=3.0).build(), M(0, D / 2, PLINTH + 7.55))
    asm.add('Front', wk.noren(8, mat='Cloth_Navy'), M(0, D / 2 + 0.3, PLINTH + 7.0 - 3.55))
    hk = Builder(ALL_MATS)
    for hx in (-4.1, 4.1):
        hk.beam_box((hx - 0.05, D / 2 - 0.02, PLINTH + 6.72), (hx + 0.05, D / 2 + 0.34, PLINTH + 6.84), 'Iron_Wrought', along='y')
        hk.beam_box((hx - 0.05, D / 2 + 0.3, PLINTH + 6.72), (hx + 0.05, D / 2 + 0.42, PLINTH + 7.02), 'Iron_Wrought', along='z')
    asm.add('Front', hk)
    fb = P(); fg = G()
    for lx in (-6.0, 6.0):
        chochin(fb, fg, lx, D / 2 + 1.6, PLINTH + 5.2)
        fb.beam_box((lx - 0.05, D / 2 + 1.55, PLINTH + 7.6), (lx + 0.05, D / 2 + 1.65, PLINTH + 8.6), 'Iron_Wrought', along='z')
    asm.add('Front', fb); asm.add('Glow', fg)
    sb = Builder(ALL_MATS); face = Builder(['Timber_Light'])
    bk.signboard_hanging(sb, face, W / 2 - 1.6, D / 2, PLINTH + 4.4)
    asm.add('Front', sb); asm.add('SignFace', face)
    # ---------------- roof
    asm.add('Roof', Irimoya(W, D, overhang=3.0, gable_overhang=1.0, pitch=0.66, t_gable=0.56).build(), M(0, 0, top))
    return bk.finish(asm)


# ================================================================================================= BLACKSMITH
def blacksmith(name='HO_Bldg_Blacksmith'):
    """20 x 24, tall single storey with an open front: forge + chimney, bellows, anvil, quench trough,
    sword racks, tool rack, coal and goods."""
    random.seed(12)
    W, D = 20, 24
    asm = Assembly(name)
    top = shell(asm, W, D, [dict(front=W_(lambda m, i: ['open'] * (m // 4)),
                                 back=W_(lambda m, i: ['plaster', 'lattice'] + ['plaster'] * (m // 4 - 2) if m >= 8 else ['plaster']),
                                 side=W_(lambda m, i: ['plaster', 'lattice'] + ['plaster'] * (m // 4 - 2) if m >= 8 else ['plaster']))])
    x0, x1, y0, y1 = -W / 2 + 1, W / 2 - 1, -D / 2 + 1, D / 2 - 1
    fl = Builder(ALL_MATS)
    fl.box((x0, y0, 0.0), (x1, y1 + 1.0, PLINTH + 0.02), 'Earth_Packed', skip=('-z',))
    asm.add('Interior_GF', fl)
    b = P(); g = G()
    fx, fy = -4.0, -8.0
    pk.forge(b, g, fx, fy, PLINTH, w=4.8, d=3.6, h=2.6)
    # hood + chimney through the roof
    roof = Kirizuma(W, D, overhang=2.4, gable_overhang=0.8)
    ridge_z = top + roof.H(0.0) + 1.2
    hz = PLINTH + 2.6 + 3.0
    lathe(b, (fx, fy, hz), [(2.9, 0.0), (2.9, 0.3), (1.4, 2.2), (1.4, 2.25)], 4, 'Iron_Wrought', cap_bottom=True, cap_top=False)
    b.box((fx - 1.1, fy - 1.1, hz + 2.2), (fx + 1.1, fy + 1.1, ridge_z + 3.0), 'Stone_Fitted')
    b.box((fx - 1.35, fy - 1.35, ridge_z + 3.0), (fx + 1.35, fy + 1.35, ridge_z + 3.5), 'Stone_Granite')
    for sx in (-1, 1):
        b.beam_box((fx + sx * 2.6 - 0.12, fy - 0.12, PLINTH + 2.6), (fx + sx * 2.6 + 0.12, fy + 0.12, hz), 'Iron_Wrought', along='z')
    bl = P(); pk.bellows(bl); asm.add('Interior_GF', bl, M(fx - 5.2, fy + 0.2, PLINTH, math.pi))
    pk.anvil(b, 0.5, -3.0, PLINTH)
    pk.quench_trough(b, 3.5, -8.5, PLINTH)
    wr = P(); pk.wall_sword_rack(wr, 0, 0, 0, swords=4, w=4.6); asm.add('Interior_GF', wr, M(x1, 2.0, PLINTH + 2.2, -math.pi / 2))
    tr = P(); pk.tool_rack(tr, 0, 0, 0, w=4.0); asm.add('Interior_GF', tr, M(4.0, y0, PLINTH + 3.0))
    pk.sword_rack(b, 3.0, 6.5, PLINTH, swords=3)
    for i, (xx, yy) in enumerate(((x0 + 1.0, -2.0), (x0 + 1.0, -0.4), (x0 + 2.4, -1.2))):
        pk.sack(b, xx, yy, PLINTH, h=1.6, r=0.6, mat='Cloth_White')
    pk.barrel(b, x1 - 1.2, y0 + 1.2, PLINTH)
    pk.crate(b, x1 - 1.2, y0 + 3.2, PLINTH); pk.crate(b, x1 - 1.2, y0 + 3.2, PLINTH + 1.2, w=1.4, d=1.2, h=1.0)
    # workbench
    b.box((-8.5, 5.0, PLINTH + 2.8), (-5.0, 7.0, PLINTH + 3.1), 'Wood_Planks')
    for xx in (-8.3, -5.2):
        for yy in (5.2, 6.8):
            b.beam_box((xx - 0.12, yy - 0.12, PLINTH), (xx + 0.12, yy + 0.12, PLINTH + 2.8), 'Timber_Dark', along='z')
    pk.katana(b, (-8.2, 6.0, PLINTH + 3.15), (1, 0, 0), (0, 1, 0), length=3.0, sheathed=False)
    asm.add('Interior_GF', b); asm.add('Glow', g)
    # front: standing sign + crimson noren band across the open front
    sb = P(); face = Builder(['Timber_Light'])
    sb.box((-0.9, -0.5, 0), (0.9, 0.5, 0.5), 'Timber_Dark')
    for x in (-0.7, 0.7):
        sb.beam_box((x - 0.12, -0.12, 0.5), (x + 0.12, 0.12, 4.0), 'Timber_Dark', along='z')
    sb.box((-0.58, -0.08, 0.9), (0.58, 0.08, 3.6), 'Timber_Dark')
    face.box((-0.58, 0.08, 0.9), (0.58, 0.14, 3.6), 'Timber_Light', uvd=0.3)
    face.box((-0.58, -0.14, 0.9), (0.58, -0.08, 3.6), 'Timber_Light', uvd=0.3)
    sb.beam_box((-0.85, -0.14, 3.6), (0.85, 0.14, 3.8), 'Timber_Dark', along='x')
    asm.add('Front', sb, M(W / 2 - 2.0, D / 2 + 2.0, 0.0, math.pi / 2))
    asm.add('SignFace', face, M(W / 2 - 2.0, D / 2 + 2.0, 0.0, math.pi / 2))
    asm.add('Front', wk.noren(8, mat='Cloth_Crimson'), M(-4.0, D / 2 + 0.3, PLINTH + 7.0 - 3.55))
    hk = Builder(ALL_MATS)
    for hx in (-8.1, 0.1):
        hk.beam_box((hx - 0.05, D / 2 - 0.02, PLINTH + 6.72), (hx + 0.05, D / 2 + 0.34, PLINTH + 6.84), 'Iron_Wrought', along='y')
        hk.beam_box((hx - 0.05, D / 2 + 0.3, PLINTH + 6.72), (hx + 0.05, D / 2 + 0.42, PLINTH + 7.02), 'Iron_Wrought', along='z')
    asm.add('Front', hk)
    asm.add('Roof', roof.build(), M(0, 0, top))
    return bk.finish(asm)


# ================================================================================================= ARMORY
def armory(name='HO_Bldg_Armory'):
    """16 x 20, two storeys: lattice front with sliding doors; lacquered samurai armour on stands, spear rack,
    katana stands and wall racks, a counter; storage crates upstairs."""
    random.seed(13)
    W, D = 16, 20
    asm = Assembly(name)
    top = shell(asm, W, D, [
        dict(front=W_(lambda m, i: ['koshi', 'door', 'door', 'koshi']),
             back=W_(lambda m, i: ['plaster', 'window', 'window', 'plaster']),
             side=W_(lambda m, i: ['plaster'] * (m // 4))),
        dict(front=W_(lambda m, i: ['mushiko'] * (m // 4)),
             back=W_(lambda m, i: ['window', 'plaster', 'plaster', 'window']),
             side=W_(lambda m, i: ['plaster'] * (m // 4))),
    ])
    x0, x1, y0, y1 = -W / 2 + 1, W / 2 - 1, -D / 2 + 1, D / 2 - 1
    zr = PLINTH + 0.55
    plank_floor(asm, 'Interior_GF', x0, x1, y0, y1, zr)
    b = P(); g = G()
    for i, (ax, ay, lac, trim) in enumerate(((x0 + 1.6, 4.5, 'Red_Lacquer', 'Black_Lacquer'), (x0 + 1.6, -1.5, 'Black_Lacquer', 'Red_Lacquer'),
                                              (x1 - 1.6, 4.5, 'Black_Lacquer', 'Gold_Leaf'), (x1 - 1.6, -1.5, 'Red_Lacquer', 'Black_Lacquer'))):
        ab = P(); pk.samurai_armour(ab, 0, 0, 0, lacquer=lac, trim=trim)
        asm.add('Interior_GF', ab, M(ax, ay, zr, -math.pi / 2 if ax < 0 else math.pi / 2))
    pk.sword_rack(b, 0.0, 2.0, zr, swords=3)
    sr = P(); pk.spear_rack(sr, 0, 0, 0, spears=5, w=5.0); asm.add('Interior_GF', sr, M(0.0, y0 + 0.8, zr))
    for yy in (-6.0,):
        wr = P(); pk.wall_sword_rack(wr, 0, 0, 0, swords=3, w=4.0)
        asm.add('Interior_GF', wr, M(x0, yy, zr + 2.0, math.pi / 2))
        wr2 = P(); pk.wall_sword_rack(wr2, 0, 0, 0, swords=3, w=4.0)
        asm.add('Interior_GF', wr2, M(x1, yy, zr + 2.0, -math.pi / 2))
    pk.counter(b, 0.0, -4.0, zr, w=5.0, d=1.6, h=3.0)
    pk.tansu(b, 4.5, y0 + 0.9, zr, w=2.4, d=1.2, h=3.4, rows=4)
    pk.andon(b, g, -2.6, -4.0, zr + 3.0, h=1.4)
    asm.add('Interior_GF', b); asm.add('Glow', g)
    # upstairs storage + stair
    slab_with_hole(asm, 'Interior_2F', W, D, PLINTH + FLOOR, hole=(x0, x0 + 3.2, -8.0, 0.5))
    stair(asm, 'Interior_GF', x0, x0 + 3.2, 0.5, -8.0, zr, PLINTH + FLOOR)
    ub = P()
    for i in range(6):
        pk.crate(ub, 1.0 + (i % 3) * 1.9, -6.0 + (i // 3) * 1.8, PLINTH + FLOOR)
    pk.tawara(ub, 3.0, 4.0, PLINTH + FLOOR, rot=0.3); pk.tawara(ub, 3.3, 5.4, PLINTH + FLOOR, rot=-0.2)
    asm.add('Interior_2F', ub)
    # front
    asm.add('Front', Hisashi(W, P=3.0).build(), M(0, D / 2, PLINTH + 7.55))
    asm.add('Front', wk.noren(8, mat='Cloth_Navy'), M(0, D / 2 + 0.3, PLINTH + 7.0 - 3.55))
    hk = Builder(ALL_MATS)
    for hx in (-4.1, 4.1):
        hk.beam_box((hx - 0.05, D / 2 - 0.02, PLINTH + 6.72), (hx + 0.05, D / 2 + 0.34, PLINTH + 6.84), 'Iron_Wrought', along='y')
        hk.beam_box((hx - 0.05, D / 2 + 0.3, PLINTH + 6.72), (hx + 0.05, D / 2 + 0.42, PLINTH + 7.02), 'Iron_Wrought', along='z')
    asm.add('Front', hk)
    sb = Builder(ALL_MATS); face = Builder(['Timber_Light'])
    bk.signboard_hanging(sb, face, W / 2 - 1.6, D / 2, PLINTH + 4.4)
    asm.add('Front', sb); asm.add('SignFace', face)
    asm.add('Roof', Kirizuma(W, D, overhang=2.2, gable_overhang=0.3).build(), M(0, 0, top))
    return bk.finish(asm)


# ================================================================================================= GENERAL STORE
def general_store(name='HO_Bldg_GeneralStore'):
    """20 x 16, two storeys, open shop front with counter; shelves of jars, rice bales, sacks, barrels, crates."""
    random.seed(14)
    W, D = 20, 16
    asm = Assembly(name)
    top = shell(asm, W, D, [
        dict(front=lambda m, i, c: wk.open_shop(m), front_mods=[16, 4],
             back=W_(lambda m, i: ['plaster', 'window'] + ['plaster'] * (m // 4 - 2) if m >= 8 else ['plaster']),
             side=lambda m, i, c: wk.wall(m, ['shoji'] + ['plaster'] * (m // 4 - 1)) if i == 0 else wk.wall(m, ['plaster'] * (m // 4))),
        dict(front=W_(lambda m, i: ['mushiko'] * (m // 4)),
             back=W_(lambda m, i: ['window'] * (m // 4)),
             side=W_(lambda m, i: ['plaster'] * (m // 4))),
    ])
    x0, x1, y0, y1 = -W / 2 + 1, W / 2 - 1, -D / 2 + 1, D / 2 - 1
    zr = PLINTH + 0.55
    plank_floor(asm, 'Interior_GF', x0, x1, y0, y1, zr)
    b = P(); g = G()
    # back wall shelving full of jars
    for sxc in (-5.0, 0.0, 5.0):
        sh, tops = pk.shelf_unit(b, sxc, y0 + 0.7, zr, w=4.6, d=1.3, h=6.2, levels=4)
        for t in tops[:3]:
            for k in range(3):
                jx = sxc - 1.4 + k * 1.4
                if random.random() < 0.85:
                    pk.jar(b, jx, y0 + 0.75, t, h=random.uniform(0.9, 1.3), r=random.uniform(0.38, 0.5),
                           mat=random.choice(['Earth_Packed', 'RoofTile_Clay', 'Black_Lacquer']), lid=random.random() < 0.6)
        for k in range(2):
            pk.sack(b, sxc - 0.9 + k * 1.8, y0 + 0.75, tops[3], h=1.1, r=0.45, mat=random.choice(['Cloth_White', 'Cloth_Ochre']))
    # rice bales stacked on the left
    for i in range(3):
        pk.tawara(b, x0 + 2.0, -2.0 + i * 1.3, zr, L=2.6, r=0.62)
    for i in range(2):
        pk.tawara(b, x0 + 2.0, -1.35 + i * 1.3, zr + 1.15, L=2.6, r=0.62)
    pk.tawara(b, x0 + 2.0, -0.7, zr + 2.3, L=2.6, r=0.62)
    # sake casks + barrels on the right
    for i, (bx, by) in enumerate(((x1 - 1.3, -2.5), (x1 - 1.3, -0.4), (x1 - 3.2, -1.4))):
        pk.barrel(b, bx, by, zr, r=0.85, h=2.2, straw=(i != 2))
    pk.barrel(b, x1 - 1.3, 1.8, zr, r=0.7, h=1.8)
    # sacks and crates near the counter
    for i in range(4):
        pk.sack(b, -3.0 + i * 1.3, 3.2 + (i % 2) * 0.4, zr, h=1.5, r=0.55, mat=random.choice(['Cloth_White', 'Cloth_Ochre', 'Straw']))
    pk.crate(b, 3.5, 3.4, zr); pk.crate(b, 3.5, 3.4, zr + 1.2, w=1.4, d=1.2, h=1.0); pk.crate(b, 5.3, 3.3, zr)
    # abacus + scale on the counter (counter comes with the open shop front)
    zc = PLINTH + 2.85
    b.box((-6.0, D / 2 - 0.9, zc), (-4.4, D / 2 - 0.3, zc + 0.12), 'Timber_Dark')
    for k in range(6):
        b.cylinder((-5.9 + k * 0.28, D / 2 - 0.85, zc + 0.2), (-5.9 + k * 0.28, D / 2 - 0.35, zc + 0.2), 0.04, 4, 'Timber_Dark')
    b.cylinder((-1.0, D / 2 - 0.6, zc), (-1.0, D / 2 - 0.6, zc + 1.4), 0.06, 6, 'Timber_Dark')
    b.beam_box((-1.9, D / 2 - 0.66, zc + 1.4), (-0.1, D / 2 - 0.54, zc + 1.5), 'Timber_Dark', along='x')
    for sx in (-1, 1):
        lathe(b, (-1.0 + sx * 0.8, D / 2 - 0.6, zc + 0.8), [(0.3, 0.0), (0.3, 0.06), (0.0, 0.06)], 8, 'Iron_Wrought')
    pk.andon(b, g, x1 - 1.2, y0 + 3.5, zr)
    asm.add('Interior_GF', b); asm.add('Glow', g)
    slab_with_hole(asm, 'Interior_2F', W, D, PLINTH + FLOOR, hole=(x1 - 3.2, x1, -6.5, 1.5))
    stair(asm, 'Interior_GF', x1 - 3.2, x1, 1.5, -6.5, zr, PLINTH + FLOOR)
    asm.add('Front', Hisashi(W, P=3.0).build(), M(0, D / 2, PLINTH + 7.55))
    asm.add('Front', wk.noren(8, mat='Cloth_Ochre'), M(-4.0, D / 2 + 0.75, PLINTH + 7.0 - 3.55))
    asm.add('Front', wk.noren(8, mat='Cloth_Ochre'), M(4.0, D / 2 + 0.75, PLINTH + 7.0 - 3.55))
    hk = Builder(ALL_MATS)
    for hx in (-8.2, 0.0, 8.2):
        hk.beam_box((hx - 0.05, D / 2 - 0.02, PLINTH + 6.72), (hx + 0.05, D / 2 + 0.79, PLINTH + 6.84), 'Iron_Wrought', along='y')
        hk.beam_box((hx - 0.05, D / 2 + 0.75, PLINTH + 6.72), (hx + 0.05, D / 2 + 0.87, PLINTH + 7.02), 'Iron_Wrought', along='z')
    asm.add('Front', hk)
    sb = Builder(ALL_MATS); face = Builder(['Timber_Light'])
    bk.signboard_hanging(sb, face, W / 2 - 1.2, D / 2, PLINTH + 4.4)
    asm.add('Front', sb); asm.add('SignFace', face)
    asm.add('Roof', Kirizuma(W, D, overhang=2.4, gable_overhang=0.3).build(), M(0, 0, top))
    return bk.finish(asm)


# ================================================================================================= MAGIC STALL
def magic_stall(name='HO_Bldg_MagicStall'):
    """8 x 12 open market stall: lacquered posts, plank deck, cloth canopy with scalloped valance, counter,
    tiered shelves with glowing orbs and crystals, paper lanterns, charms."""
    random.seed(15)
    W, D = 8, 12
    asm = Assembly(name)
    b = P(); g = G()
    # deck
    b.box((-W / 2, -D / 2, 0.0), (W / 2, D / 2, 0.8), 'Timber_Dark', skip=('+z',))
    b.box((-W / 2, -D / 2, 0.8), (W / 2, D / 2, 1.0), 'Wood_Planks', skip=('-z',))
    b.box((-1.2, D / 2, 0.0), (1.2, D / 2 + 1.0, 0.5), 'Stone_Granite')           # step
    # posts (red lacquer), back posts taller
    ph = {1: 8.0, -1: 9.6}
    for sx in (-1, 1):
        for sy in (-1, 1):
            h = ph[sy]
            b.beam_box((sx * (W / 2 - 0.3) - 0.25, sy * (D / 2 - 0.3) - 0.25, 1.0), (sx * (W / 2 - 0.3) + 0.25, sy * (D / 2 - 0.3) + 0.25, h),
                       'Red_Lacquer', along='z')
        b.beam_box((sx * (W / 2 - 0.3) - 0.2, -D / 2, 7.0), (sx * (W / 2 - 0.3) + 0.2, D / 2, 7.4), 'Red_Lacquer', along='y')
    b.beam_box((-W / 2, D / 2 - 0.55, 7.6), (W / 2, D / 2 - 0.05, 8.0), 'Red_Lacquer', along='x')
    b.beam_box((-W / 2, -D / 2 + 0.05, 9.2), (W / 2, -D / 2 + 0.55, 9.6), 'Red_Lacquer', along='x')
    # canopy: cloth sheet from the back beam over the front beam, overhanging and sagging; scalloped valance
    cl = Builder(['Cloth_Indigo', 'Cloth_Navy'])
    nu, nv = 8, 8
    def cp(u, v, off):
        x = -W / 2 - 0.4 + (W + 0.8) * u
        y = -D / 2 + (D + 1.6) * v
        z = 9.7 - 2.0 * v - 0.35 * math.sin(math.pi * u) * math.sin(math.pi * min(1, v * 1.1)) + off
        return Vector((x, y, z))
    for off, out in ((0.0, 1), (-0.06, -1)):
        vs = [[cl.bm.verts.new(cp(i / nu, j / nv, off)) for i in range(nu + 1)] for j in range(nv + 1)]
        for j in range(nv):
            for i in range(nu):
                cl.face([vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]], 'Cloth_Indigo',
                        [(i / nu * 2.2, j / nv * 3.4), ((i + 1) / nu * 2.2, j / nv * 3.4), ((i + 1) / nu * 2.2, (j + 1) / nv * 3.4), (i / nu * 2.2, (j + 1) / nv * 3.4)],
                        out=Vector((0, 0.4, out)), smooth=True)
        if off == 0.0: top = vs
        else: bot = vs
    for j in range(nv):
        for col, o in ((0, -1), (nu, 1)):
            cl.face([top[j][col], top[j + 1][col], bot[j + 1][col], bot[j][col]], 'Cloth_Indigo', [(0, 0)] * 4, out=Vector((o, 0, 0)))
    for i in range(nu):
        cl.face([top[0][i], top[0][i + 1], bot[0][i + 1], bot[0][i]], 'Cloth_Indigo', [(0, 0)] * 4, out=Vector((0, -1, 0)))
    # valance with scallops along the front edge
    ve = cp(0, 1, 0).y
    zv = cp(0.5, 1, 0).z
    ns = 7
    for i in range(ns):
        xa = -W / 2 - 0.4 + (W + 0.8) * i / ns
        xb = -W / 2 - 0.4 + (W + 0.8) * (i + 1) / ns
        outline = [(xa, 0.0), (xb, 0.0), (xb, -0.7), ((xa + xb) / 2, -1.3), (xa, -0.7)]
        cl.prism(outline, (0, ve - 0.03, zv + 0.25), (1, 0, 0), (0, 0, 1), (0, 1, 0), 0.06, 'Cloth_Navy')
    asm.add('Canopy', cl)
    # counter at the front + tiered back shelves with orbs/crystals
    pk.counter(b, 0.0, D / 2 - 1.6, 1.0, w=W - 1.4, d=1.6, h=3.0)
    for k, (zz, yy) in enumerate(((1.0, -D / 2 + 1.0), (2.6, -D / 2 + 1.0), (4.2, -D / 2 + 1.0))):
        b.box((-W / 2 + 0.6, yy - 0.6, 1.0 + k * 1.6), (W / 2 - 0.6, yy + 0.6, 1.0 + k * 1.6 + 0.2), 'Black_Lacquer')
        for sx in (-1, 1):
            b.beam_box((sx * (W / 2 - 0.8) - 0.1, yy - 0.5, 1.0), (sx * (W / 2 - 0.8) + 0.1, yy - 0.3, 1.2 + k * 1.6), 'Black_Lacquer', along='z')
        for i in range(4):
            ox = -2.4 + i * 1.6
            if (i + k) % 3 == 0:
                pk.crystal(g, ox, yy, 1.2 + k * 1.6, h=0.9, r=0.18, tilt=(random.uniform(-0.2, 0.2), 0))
                pk.crystal(g, ox + 0.3, yy + 0.1, 1.2 + k * 1.6, h=0.6, r=0.12, tilt=(0.3, 0.1))
            else:
                pk.orb(b, g, ox, yy, 1.2 + k * 1.6, r=random.choice([0.3, 0.36, 0.42]))
    # orbs + a big crystal cluster on the counter
    for ox in (-2.0, 1.2):
        pk.orb(b, g, ox, D / 2 - 1.6, 4.0, r=0.4)
    for t in ((0, 0), (0.25, 0.1), (-0.25, -0.05)):
        pk.crystal(g, 2.6 + t[0], D / 2 - 1.6, 4.0, h=1.1 - abs(t[0]), r=0.16, tilt=t)
    # paper lanterns hanging at the front, charm strips
    for lx in (-W / 2 + 0.3, W / 2 - 0.3):
        chochin(b, g, lx, D / 2 + 0.2, 4.6, r=0.45, h=1.2)
    pk.ofuda(b, 0.0, D / 2 - 0.3, 7.5, n=7, w=W - 1.2)
    # jars and a stool behind the counter
    pk.jar(b, -2.8, 1.0, 1.0, h=1.2, r=0.5, mat='Black_Lacquer'); pk.jar(b, 2.9, 0.5, 1.0, h=1.0, r=0.45)
    lathe(b, (0.0, 1.5, 1.0), [(0.5, 0.0), (0.45, 1.8), (0.6, 1.9), (0.6, 2.0)], 8, 'Timber_Dark')
    asm.add('Structure_GF', b); asm.add('Glow', g)
    return bk.finish(asm)


# ================================================================================================= KURA
def kura(name='HO_Bldg_Kura'):
    """20 x 24 fire-proof storehouse: thick (1.6) plaster walls on a tall stone base, namako (black tile /
    white lattice) lower walls, heavy plaster doors, barred windows with shutters, crest on the gables."""
    random.seed(16)
    W, D = 20, 24
    asm = Assembly(name)
    b = Builder(ALL_MATS + ['Namako_Wall', 'Black_Lacquer', 'Stone_Fitted'])
    t = 1.6
    zb = 2.0                      # stone base height
    Hw = 17.0                     # wall height above the base
    ztop = zb + Hw
    # stone base (fitted stone faces) - full footprint, the floor inside sits on top
    b.box((-W / 2 - 0.3, -D / 2 - 0.3, 0.0), (W / 2 + 0.3, D / 2 + 0.3, zb), 'Stone_Fitted')
    # walls: solid plaster ring with openings (door front centre, windows 2F front/back, side vents)
    door_w, door_h = 5.0, 7.5
    win = [(-5.0, 11.0), (5.0, 11.0)]
    def wall_side(L, depth_axis, sgn, openings):
        """Build one wall as vertical/horizontal plaster blocks around rectangular openings (u0,u1,z0,z1)."""
        us = sorted({-L / 2, L / 2} | {o[0] for o in openings} | {o[1] for o in openings})
        zs = sorted({zb, ztop} | {o[2] for o in openings} | {o[3] for o in openings})
        for ua, ub in zip(us, us[1:]):
            for za, zc in zip(zs, zs[1:]):
                um, zm = (ua + ub) / 2, (za + zc) / 2
                if any(o[0] <= um <= o[1] and o[2] <= zm <= o[3] for o in openings):
                    continue
                if depth_axis == 'y':
                    y0, y1 = (D / 2 - t, D / 2) if sgn > 0 else (-D / 2, -D / 2 + t)
                    b.box((ua, y0, za), (ub, y1, zc), 'Plaster_White', uvv=1 / 9.0)
                else:
                    x0, x1 = (W / 2 - t, W / 2) if sgn > 0 else (-W / 2, -W / 2 + t)
                    b.box((x0, ua, za), (x1, ub, zc), 'Plaster_White', uvv=1 / 9.0)
    front_open = [(-door_w / 2, door_w / 2, zb, zb + door_h)] + [(wx - 1.2, wx + 1.2, wz, wz + 2.2) for wx, wz in win]
    back_open = [(wx - 1.2, wx + 1.2, wz, wz + 2.2) for wx, wz in win]
    side_open = [(-1.0, 1.0, 13.5, 15.0)]
    wall_side(W, 'y', 1, front_open)
    wall_side(W, 'y', -1, back_open)
    wall_side(D - 2 * t, 'x', 1, [(o[0], o[1], o[2], o[3]) for o in side_open])
    wall_side(D - 2 * t, 'x', -1, [(o[0], o[1], o[2], o[3]) for o in side_open])
    # namako (tile-lattice) cladding on the lower walls, slightly proud, around the door
    zn = zb + 5.5
    for sgn in (1, -1):
        yy = sgn * (D / 2 + 0.06)
        spans = [(-W / 2 - 0.06, -door_w / 2 - 0.9), (door_w / 2 + 0.9, W / 2 + 0.06)] if sgn > 0 else [(-W / 2 - 0.06, W / 2 + 0.06)]
        for a, c in spans:
            b.box((a, min(yy, sgn * D / 2), zb), (c, max(yy, sgn * D / 2), zn), 'Namako_Wall')
        xx = sgn * (W / 2 + 0.06)
        b.box((min(xx, sgn * W / 2), -D / 2 - 0.06, zb), (max(xx, sgn * W / 2), D / 2 + 0.06, zn), 'Namako_Wall')
    # plaster cap band over the namako + thick cornice (hachimaki) under the eaves
    for sgn in (1, -1):
        b.box((-W / 2 - 0.15, sgn * D / 2 - (0.0 if sgn > 0 else 0.15), zn), (W / 2 + 0.15, sgn * D / 2 + (0.15 if sgn > 0 else 0.0), zn + 0.4), 'Plaster_White')
        b.box((sgn * W / 2 - (0.0 if sgn > 0 else 0.15), -D / 2 - 0.15, zn), (sgn * W / 2 + (0.15 if sgn > 0 else 0.0), D / 2 + 0.15, zn + 0.4), 'Plaster_White')
    for k, (off, hh) in enumerate(((0.35, 0.5), (0.6, 0.45))):
        z0 = ztop - 1.6 + k * 0.5
        b.box((-W / 2 - off, -D / 2 - off, z0), (W / 2 + off, D / 2 + off, z0 + hh), 'Plaster_White')
    # door: stepped plaster surround + two thick plaster leaves swung open + inner lattice door (separate)
    for k in range(3):
        o = 0.35 * (k + 1)
        b.box((-door_w / 2 - o, D / 2, zb - 0.0), (-door_w / 2 - o + 0.35, D / 2 + 0.25 * (3 - k), zb + door_h + o), 'Plaster_White')
        b.box((door_w / 2 + o - 0.35, D / 2, zb), (door_w / 2 + o, D / 2 + 0.25 * (3 - k), zb + door_h + o), 'Plaster_White')
        b.box((-door_w / 2 - o, D / 2, zb + door_h + o - 0.35), (door_w / 2 + o, D / 2 + 0.25 * (3 - k), zb + door_h + o), 'Plaster_White')
    for sx in (-1, 1):
        lx = sx * (door_w / 2 + 1.4)
        b.box((min(lx, lx + sx * 0.8), D / 2 + 0.75, zb + 0.1), (max(lx, lx + sx * 0.8), D / 2 + 0.75 + door_w / 2, zb + door_h - 0.1), 'Plaster_White')
        for zz in (zb + 1.5, zb + door_h - 1.5):
            b.beam_box((min(lx, lx + sx * 0.8) - 0.05, D / 2 + 0.7, zz), (max(lx, lx + sx * 0.8) + 0.05, D / 2 + 0.95 + door_w / 2, zz + 0.3),
                       'Iron_Wrought', along='y')
    b.box((-door_w / 2, D / 2 - t, zb), (door_w / 2, D / 2, zb + 0.3), 'Stone_Granite')           # threshold
    dd = Builder(wk.MATS)
    dd.beam_box((-door_w / 2, D / 2 - 1.0, zb + 0.3), (door_w / 2, D / 2 - 0.8, zb + 0.6), 'Timber_Dark', along='x')
    dd.beam_box((-door_w / 2, D / 2 - 1.0, zb + door_h - 0.3), (door_w / 2, D / 2 - 0.8, zb + door_h), 'Timber_Dark', along='x')
    for k in range(9):
        xx = -door_w / 2 + 0.15 + (door_w - 0.3) * k / 8
        dd.beam_box((xx - 0.1, D / 2 - 1.0, zb + 0.6), (xx + 0.1, D / 2 - 0.8, zb + door_h - 0.3), 'Timber_Dark', along='z')
    # windows: iron bars + open plaster shutters
    for sgn, ys in ((1, D / 2), (-1, -D / 2)):
        for wx, wz in win:
            for k in range(4):
                xx = wx - 0.9 + 1.8 * k / 3
                b.cylinder((xx, ys - sgn * 0.8, wz), (xx, ys - sgn * 0.8, wz + 2.2), 0.08, 6, 'Iron_Wrought')
            for sx in (-1, 1):
                lx = wx + sx * 1.2
                b.box((min(lx, lx + sx * 1.3), min(ys, ys + sgn * 0.5), wz - 0.1), (max(lx, lx + sx * 1.3), max(ys, ys + sgn * 0.5), wz + 2.3),
                      'Plaster_White')
            b.box((wx - 1.6, min(ys, ys + sgn * 0.6), wz + 2.2), (wx + 1.6, max(ys, ys + sgn * 0.6), wz + 2.6), 'Plaster_White')
    # side vents with bars
    for sgn in (1, -1):
        xs = sgn * W / 2
        for k in range(3):
            yy = -0.6 + 0.6 * k
            b.cylinder((xs - sgn * 0.8, yy, 13.5), (xs - sgn * 0.8, yy, 15.0), 0.07, 6, 'Iron_Wrought')
    # interior: earth floor, a mezzanine shelf level, goods
    b.box((-W / 2 + t, -D / 2 + t, zb), (W / 2 - t, D / 2 - t, zb + 0.05), 'Earth_Packed', skip=('-z',))
    asm.add('Structure_GF', b)
    ib = P()
    for i in range(4):
        pk.tawara(ib, -5.5, -8.0 + i * 1.3, zb + 0.05, L=2.6, r=0.62)
    for i in range(3):
        pk.tawara(ib, -5.5, -7.35 + i * 1.3, zb + 1.2, L=2.6, r=0.62)
    for i in range(3):
        pk.barrel(ib, 5.5, -8.0 + i * 2.0, zb + 0.05, straw=True)
    for i in range(4):
        pk.crate(ib, 2.0 + (i % 2) * 1.8, 3.0 + (i // 2) * 1.6, zb + 0.05)
    for i in range(3):
        pk.jar(ib, -6.0 + i * 1.5, 6.0, zb + 0.05, h=1.6, r=0.7)
    pk.tansu(ib, 0.0, -D / 2 + t + 0.8, zb + 0.05, w=3.0, d=1.4, h=4.2, rows=4)
    asm.add('Interior_GF', ib)
    asm.add('Door1', dd)
    # roof with the crest on both gables
    roof = Kirizuma(W, D, overhang=1.6, gable_overhang=0.6, pitch=0.6)
    asm.add('Roof', roof.build(), M(0, 0, ztop))
    cb = Builder(['Black_Lacquer', 'Plaster_White'])
    zc = ztop + roof.zu(0.0) + (roof.H(0.0) - roof.T - roof.zu(0.0)) * 0.45
    for sgn in (1, -1):
        xs = sgn * (W / 2 + 0.01)
        ring = [(1.1 * math.cos(2 * math.pi * i / 16), 1.1 * math.sin(2 * math.pi * i / 16)) for i in range(16)]
        cb.prism(ring, (xs, 0, zc), (0, 1, 0), (0, 0, 1), (sgn, 0, 0), 0.12, 'Black_Lacquer')
        inner = [(0.7 * math.cos(2 * math.pi * i / 3 + math.pi / 2), 0.7 * math.sin(2 * math.pi * i / 3 + math.pi / 2)) for i in range(3)]
        cb.prism(inner, (xs + sgn * 0.12, 0, zc), (0, 1, 0), (0, 0, 1), (sgn, 0, 0), 0.06, 'Plaster_White')
    asm.add('Structure_GF', cb)
    return bk.finish(asm)
