"""Building assembler: combines the wall kit, roofs and interior pieces into complete buildings.

Building space: footprint x in [-W/2, W/2], y in [-D/2, D/2], front = +Y (-> Roblox -Z), ground = z 0.
Stack: stone plinth z 0..1, ground floor walls z 1..10, 2nd floor walls z 10..19, roof on top.
"""
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix
import ho
import wallkit as wk
from geo import Builder
from roofkit import Kirizuma, Hisashi, Irimoya, MATS as ROOF_MATS

PLINTH = 1.0
FLOOR = 9.0
ALL_MATS = ['Plaster_White', 'Timber_Dark', 'Timber_Light', 'Shoji_Paper', 'Stone_Granite', 'Wood_Planks',
            'Iron_Wrought', 'Tatami', 'Earth_Packed', 'RoofTile_Clay', 'Gold_Leaf']


class Assembly:
    def __init__(self, name):
        self.name = name
        self.parts = {}          # group name -> list of objects

    def add(self, group, builder, matrix=Matrix.Identity(4), weld=True):
        ob = ho.builder_obj(f'{self.name}_{group}_{len(self.parts.get(group, []))}', builder, weld=weld)
        ob.matrix_world = matrix
        ho.apply_transforms(ob)
        ob.data.transform(Matrix.Translation(ob.location)); ob.location = (0, 0, 0)
        self.parts.setdefault(group, []).append(ob)
        return ob

    def objects(self):
        """Join each group into one object named <name>_<Group>."""
        out = []
        for g, objs in self.parts.items():
            ob = ho.join(objs, f'{self.name}_{g}')
            out.append(ob)
        return out


def M(x=0.0, y=0.0, z=0.0, rot=0.0):
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(rot, 4, 'Z')


def split_len(L):
    """Split a wall run into kit lengths (16/12/8/4)."""
    out = []
    for m in (16, 12, 8, 4):
        while L - m >= 0 and (L - m == 0 or L - m >= 4):
            out.append(m); L -= m
            if L == 0: break
    return out


def wall_run(asm, group, L, z, side, W, D, bay_fn, seed=0, mods=None):
    """Place a run of wall modules along one side. bay_fn(module_len, index, x_offset) -> WallBuilder.
    `mods` overrides the module lengths (must sum to L), listed left to right as seen from outside."""
    mods = mods or split_len(L)
    assert abs(sum(mods) - L) < 1e-6, (mods, L)
    pos = -L / 2
    rot = {'front': 0.0, 'back': math.pi, 'right': -math.pi / 2, 'left': math.pi / 2}[side]
    for i, m in enumerate(mods):
        c = pos + m / 2
        random.seed(seed * 31 + i)
        w = bay_fn(m, i, c)
        if side == 'front': mat = M(c, D / 2 - 0.5, z, rot)
        elif side == 'back': mat = M(-c, -D / 2 + 0.5, z, rot)
        elif side == 'right': mat = M(W / 2 - 0.5, -c, z, rot)
        else: mat = M(-W / 2 + 0.5, c, z, rot)
        asm.add(group, w.b, mat)
        for dn, db in w.doors:
            asm.add(f'Door{len([k for k in asm.parts if k.startswith("Door")]) + 1}', db, mat)
        pos += m


def plinths(asm, W, D):
    for side, L in (('front', W), ('back', W), ('right', D), ('left', D)):
        pos = -L / 2
        for m in split_len(L):
            c = pos + m / 2
            b = wk.plinth(m, seed=int(c * 7 + L))
            rot = {'front': 0.0, 'back': math.pi, 'right': -math.pi / 2, 'left': math.pi / 2}[side]
            mat = {'front': M(c, D / 2 - 0.5, 0, rot), 'back': M(-c, -D / 2 + 0.5, 0, rot),
                   'right': M(W / 2 - 0.5, -c, 0, rot), 'left': M(-W / 2 + 0.5, c, 0, rot)}[side]
            asm.add('Structure', b, mat)
            pos += m
    for sx in (1, -1):
        for sy in (1, -1):
            asm.add('Structure', wk.plinth(1.6, corner=True), M(sx * (W / 2 - 0.5), sy * (D / 2 - 0.5), 0))


def corner_posts(asm, W, D, z, h=FLOOR):
    for sx in (1, -1):
        for sy in (1, -1):
            asm.add('Structure', wk.corner_post(h), M(sx * (W / 2 - 0.5), sy * (D / 2 - 0.5), z))


def floor_slab(asm, W, D, z, top='Wood_Planks', beams=True):
    b = Builder(ALL_MATS)
    x0, x1, y0, y1 = -W / 2 + 1, W / 2 - 1, -D / 2 + 1, D / 2 - 1
    b.box((x0, y0, z - 0.5), (x1, y1, z), 'Timber_Light', skip=('+z',))
    # top surface as its own quad so it can take the plank texture
    b.box((x0, y0, z - 0.1), (x1, y1, z), top, skip=('-z',))
    if beams:
        n = int((x1 - x0) / 4)
        for i in range(1, n + 1):
            x = x0 + (x1 - x0) * i / (n + 1)
            b.beam_box((x - 0.35, y0, z - 1.2), (x + 0.35, y1, z - 0.5), 'Timber_Dark', along='y')
    asm.add('Interior', b)


def signboard_hanging(b, face, x, y, z, side=1):
    """Iron bracket from the wall face (y) with a hanging board perpendicular to the wall (faces +-X)."""
    arm = 1.9
    b.beam_box((x - 0.06, y, z + 3.0), (x + 0.06, y + arm, z + 3.14), 'Iron_Wrought', along='y')
    b.beam(Vector((x, y, z + 1.9)), Vector((x, y + arm * 0.55, z + 3.0)), 0.1, 0.1, 'Iron_Wrought', up=Vector((1, 0, 0)))
    b.beam_box((x - 0.2, y - 0.02, z + 1.7), (x + 0.2, y + 0.12, z + 3.3), 'Iron_Wrought', along='z')     # wall plate
    yc = y + arm - 0.7
    for dy in (-0.45, 0.45):
        b.beam_box((x - 0.03, yc + dy - 0.03, z + 2.7), (x + 0.03, yc + dy + 0.03, z + 3.0), 'Iron_Wrought', along='z')
    # board: frame + (separate) faces
    b.beam_box((x - 0.14, yc - 0.65, z + 0.0), (x + 0.14, yc + 0.65, z + 0.18), 'Timber_Dark', along='y')
    b.beam_box((x - 0.14, yc - 0.65, z + 2.52), (x + 0.14, yc + 0.65, z + 2.7), 'Timber_Dark', along='y')
    b.beam_box((x - 0.14, yc - 0.65, z + 0.18), (x + 0.14, yc - 0.5, z + 2.52), 'Timber_Dark', along='z')
    b.beam_box((x - 0.14, yc + 0.5, z + 0.18), (x + 0.14, yc + 0.65, z + 2.52), 'Timber_Dark', along='z')
    face.box((x - 0.1, yc - 0.5, z + 0.18), (x + 0.1, yc + 0.5, z + 2.52), 'Timber_Light', uvd=0.38)


def interior_machiya(asm, W, D, storeys, front):
    """Ground floor: earthen doma along the left, raised plank shop floor at the front, tatami room at the back,
    shoji partition, shelves, kamado stove, stair chest (2-storey)."""
    b = Builder(ALL_MATS)
    x0, x1, y0, y1 = -W / 2 + 1, W / 2 - 1, -D / 2 + 1, D / 2 - 1
    dw = 4.0                                      # doma width
    xd = x0 + dw
    zr = 2.6                                      # raised floor height
    # doma: earth floor (top at plinth level)
    b.box((x0, y0, 0.0), (xd, y1, PLINTH), 'Earth_Packed', skip=('-z',))
    # raised floor body
    b.box((xd, y0, 0.0), (x1, y1, zr - 0.1), 'Timber_Dark', skip=('-z',))
    ymid = y0 + (y1 - y0) * 0.45
    b.box((xd, ymid, zr - 0.1), (x1, y1, zr), 'Wood_Planks', skip=('-z',))           # shop floor
    tb = Builder(['Tatami', 'Timber_Dark'])
    tb.box((xd, y0, zr - 0.1), (x1, ymid, zr + 0.05), 'Tatami', skip=('-z',), uvd=1 / 3.0)  # tatami room
    asm.add('Interior', tb)
    # edge beam (agari-kamachi) along the doma
    b.beam_box((xd - 0.25, y0, zr - 0.4), (xd + 0.05, y1, zr + 0.06), 'Timber_Dark', along='y')
    # step stone into the raised floor
    b.box((xd - 1.1, y1 - 5.0, PLINTH), (xd - 0.25, y1 - 3.8, PLINTH + 0.7), 'Stone_Granite')
    asm.add('Interior', b)
    # shoji partition between shop and back room (on the raised floor)
    wb = wk.WallBuilder(x1 - xd)
    L = x1 - xd
    nparts = max(2, int(round(L / 2)))
    for i in range(nparts):
        a = -L / 2 + L * i / nparts
        c = -L / 2 + L * (i + 1) / nparts
        wk.WallBuilder.shoji(wb, a, c, 0.0, 5.4, y=0.08 if i % 2 else -0.08, cols=2, rows=4)
    wb.b.beam_box((-L / 2, -0.25, 5.4), (L / 2, 0.25, 5.8), 'Timber_Dark', along='x')        # kamoi rail
    wb.plaster(-L / 2, L / 2, 5.8, FLOOR - 0.6 - zr + 1, -0.15, 0.15)
    asm.add('Interior', wb.b, M((xd + x1) / 2, ymid, zr))
    # kamado stove in the doma (back)
    kb = Builder(ALL_MATS)
    kb.box((x0 + 0.3, y0 + 0.4, PLINTH), (x0 + 3.4, y0 + 2.2, PLINTH + 2.2), 'Plaster_White', uvv=1 / 9)
    for cx in (x0 + 1.1, x0 + 2.6):
        kb.cylinder((cx, y0 + 1.3, PLINTH + 2.2), (cx, y0 + 1.3, PLINTH + 2.45), 0.55, 10, 'Iron_Wrought')
        kb.cylinder((cx, y0 + 1.3, PLINTH + 2.45), (cx, y0 + 1.3, PLINTH + 2.6), 0.2, 8, 'Timber_Dark')
        kb.box((cx - 0.35, y0 + 2.19, PLINTH + 0.4), (cx + 0.35, y0 + 2.25, PLINTH + 1.1), 'Iron_Wrought')
    asm.add('Interior', kb)
    # shop shelves against the right wall, front half
    sb = Builder(ALL_MATS)
    sx0, sx1 = x1 - 1.4, x1
    for i, yy in enumerate(range(int(ymid + 1), int(y1 - 1), 3)):
        sb.beam_box((sx0, yy, zr), (sx1, yy + 0.2, zr + 5.0), 'Timber_Dark', along='z')
    for k in range(4):
        z = zr + 0.5 + k * 1.3
        sb.box((sx0, ymid + 1, z), (sx1, y1 - 1, z + 0.14), 'Timber_Light')
        # goods: stacked boxes / bundles
        yy = ymid + 1.4
        while yy < y1 - 1.6:
            w = random.uniform(0.5, 1.0)
            h = random.uniform(0.4, 0.9)
            mat = random.choice(['Timber_Light', 'Shoji_Paper', 'Timber_Dark'])
            sb.box((sx0 + 0.2, yy, z + 0.14), (sx1 - 0.2, yy + w, z + 0.14 + h), mat, uv_off=(random.random(), 0))
            yy += w + random.uniform(0.2, 0.5)
    asm.add('Interior', sb)
    # low table + andon lantern in the tatami room
    lb = Builder(ALL_MATS)
    tx, ty = (xd + x1) / 2, (y0 + ymid) / 2
    lb.box((tx - 1.2, ty - 0.8, zr + 1.0), (tx + 1.2, ty + 0.8, zr + 1.2), 'Timber_Dark')
    for sx in (-1, 1):
        for sy in (-1, 1):
            lb.box((tx + sx * 1.0 - 0.1, ty + sy * 0.6 - 0.1, zr + 0.05), (tx + sx * 1.0 + 0.1, ty + sy * 0.6 + 0.1, zr + 1.0),
                   'Timber_Dark')
    ax, ay = x1 - 1.0, y0 + 1.0
    lb.box((ax - 0.45, ay - 0.45, zr + 0.05), (ax + 0.45, ay + 0.45, zr + 0.25), 'Timber_Dark')
    wbl = wk.WallBuilder(1)
    for (px, py, rot) in ((ax, ay - 0.4, 0), (ax, ay + 0.4, 0), (ax - 0.4, ay, 1), (ax + 0.4, ay, 1)):
        if rot: lb.box((px - 0.03, py - 0.4, zr + 0.3), (px + 0.03, py + 0.4, zr + 1.9), 'Shoji_Paper')
        else: lb.box((px - 0.4, py - 0.03, zr + 0.3), (px + 0.4, py + 0.03, zr + 1.9), 'Shoji_Paper')
    for sx in (-1, 1):
        for sy in (-1, 1):
            lb.box((ax + sx * 0.42 - 0.05, ay + sy * 0.42 - 0.05, zr + 0.25), (ax + sx * 0.42 + 0.05, ay + sy * 0.42 + 0.05, zr + 2.0),
                   'Timber_Dark')
    asm.add('Interior', lb)
    # stair chest (hako-kaidan) up to the 2nd floor, against the left edge of the raised floor, back room
    if storeys > 1:
        cb = Builder(ALL_MATS)
        n = 7
        sw = 2.4
        run = 5.0
        for i in range(n):
            zt = zr + (FLOOR + PLINTH - zr) * (i + 1) / n
            ya = y0 + 0.2 + run * i / n
            cb.box((xd + 0.1, ya, zr), (xd + 0.1 + sw, y0 + 0.2 + run, zt), 'Timber_Dark', uv_off=(0.1 * i, 0))
            cb.box((xd + 0.1, ya - 0.06, zt - 0.14), (xd + 0.1 + sw, ya + run / n, zt), 'Timber_Light')
            # drawer fronts with iron pulls
            for k in range(int((zt - zr) / 1.2)):
                zz = zr + 0.2 + k * 1.2
                if zz + 0.9 > zt - 0.2: break
                cb.box((xd + 0.1 + sw, ya + 0.1, zz), (xd + 0.14 + sw, ya + run / n - 0.1, zz + 0.9), 'Timber_Light')
                cb.box((xd + 0.14 + sw, ya + run / n / 2 - 0.1, zz + 0.4), (xd + 0.2 + sw, ya + run / n / 2 + 0.1, zz + 0.5),
                       'Iron_Wrought')
        asm.add('Interior', cb)


def machiya(name, W, D, storeys=2, front='koshi', noren='Navy', sign=True, seed=0):
    random.seed(seed)
    asm = Assembly(name)
    plinths(asm, W, D)
    z1 = PLINTH
    # ---------------- ground floor
    def gf_front(m, i, c):
        if front == 'open':
            return wk.open_shop(m)
        if front == 'mixed':
            return wk.open_shop(m) if i == 0 else wk.wall(m, ['koshi', 'door'] + ['koshi'] * (m // 4 - 2))
        bays = ['koshi'] * (m // 4)
        if i == 0: bays[min(1, len(bays) - 1)] = 'door'
        return wk.wall(m, bays)
    wall_run(asm, 'Structure', W, z1, 'front', W, D, gf_front, seed + 1)
    wall_run(asm, 'Structure', W, z1, 'back', W, D,
             lambda m, i, c: wk.wall(m, ['shoji' if (i == 0 and k == 0) else 'window' for k in range(m // 4)]), seed + 2)
    for side in ('right', 'left'):
        wall_run(asm, 'Structure', D, z1, side, W, D,
                 lambda m, i, c: wk.wall(m, ['plaster'] * (m // 4)), seed + 3)
    corner_posts(asm, W, D, z1)
    interior_machiya(asm, W, D, storeys, front)
    top = z1 + FLOOR
    # ---------------- upper floor
    if storeys > 1:
        floor_slab(asm, W, D, top)
        wall_run(asm, 'Structure', W, top, 'front', W, D,
                 lambda m, i, c: wk.wall(m, ['mushiko'] * (m // 4)), seed + 4)
        wall_run(asm, 'Structure', W, top, 'back', W, D,
                 lambda m, i, c: wk.wall(m, ['window' if k % 2 == 0 else 'plaster' for k in range(m // 4)]), seed + 5)
        for side in ('right', 'left'):
            wall_run(asm, 'Structure', D, top, side, W, D, lambda m, i, c: wk.wall(m, ['plaster'] * (m // 4)), seed + 6)
        corner_posts(asm, W, D, top)
        top += FLOOR
    # ---------------- front awning (hisashi) above the ground floor openings
    if storeys > 1 or front != 'open':
        hb = Hisashi(W, P=3.0).build()
        asm.add('Front', hb, M(0, D / 2, z1 + 7.55))
    # ---------------- noren + sign
    fb = Builder(['Timber_Dark', 'Cloth_' + noren])
    door_x = -W / 2 + 6.0 if front != 'open' else 0.0
    nw = 4 if front != 'open' else min(8, W - 4)
    nb = wk.noren(nw, mat='Cloth_' + noren)
    asm.add('Front', nb, M(door_x, D / 2 + 0.3, z1 + 7.0 - 3.55))
    hk = Builder(ALL_MATS)                        # iron hooks holding the noren rod off the wall
    for hx in (door_x - nw / 2 - 0.1, door_x + nw / 2 + 0.1):
        hk.beam_box((hx - 0.05, D / 2 - 0.02, z1 + 6.72), (hx + 0.05, D / 2 + 0.34, z1 + 6.84), 'Iron_Wrought', along='y')
        hk.beam_box((hx - 0.05, D / 2 + 0.3, z1 + 6.72), (hx + 0.05, D / 2 + 0.42, z1 + 7.02), 'Iron_Wrought', along='z')
    asm.add('Front', hk)
    if sign:
        sb = Builder(ALL_MATS); face = Builder(['Timber_Light'])
        signboard_hanging(sb, face, W / 2 - 1.6, D / 2, z1 + 4.4)
        asm.add('Front', sb)
        asm.add('SignFace', face)
    # ---------------- roof
    r = Kirizuma(W, D, overhang=2.0 if W < 20 else 2.4, gable_overhang=0.3)
    rb = r.build()
    asm.add('Roof', rb, M(0, 0, top))
    objs = asm.objects()
    # split the roof into tiles/frame (and further if big)
    out = []
    for o in objs:
        if o.name.endswith('_Roof'):
            parts = ho.split_by_material(o, {'_Tiles': ['RoofTile_Clay'], '_Frame': None})
            for p in parts: p.name = p.data.name = p.name.replace('_Roof_', '_Roof')
            out += parts
        else:
            out.append(o)
    ho.finalize_group(out, pivot=(0, 0, 0))     # pivot = footprint centre at ground level
    for o in out:
        if ho.tri_count(o) > 18000:
            raise RuntimeError(f'{o.name} has {ho.tri_count(o)} tris')
    return out


def finish(asm, limit=18000):
    """Join groups, split roofs into tiles/frame, auto-split any mesh over `limit` tris, pivot at footprint centre."""
    objs = asm.objects()
    out = []
    for o in objs:
        if o.name.endswith('_Roof'):
            parts = ho.split_by_material(o, {'_Tiles': ['RoofTile_Clay'], '_Frame': None})
            for p in parts: p.name = p.data.name = p.name.replace('_Roof_', '_Roof')
            out += parts
        else:
            out.append(o)
    changed = True
    while changed:
        changed = False
        for o in list(out):
            if ho.tri_count(o) > limit:
                out.remove(o)
                lo, hi = ho.world_bbox([o])
                axis = 0 if (hi.x - lo.x) >= (hi.y - lo.y) else 1
                # split through the object's own centre on its longest horizontal axis
                c = (lo + hi) / 2
                o.data.transform(Matrix.Translation(-Vector((c.x if axis == 0 else 0, c.y if axis == 1 else 0, 0))))
                parts = ho.split_by_axis(o, axis, ('A', 'B'))
                for p in parts:
                    p.data.transform(Matrix.Translation(Vector((c.x if axis == 0 else 0, c.y if axis == 1 else 0, 0))))
                out += parts
                changed = True
    ho.finalize_group(out, pivot=(0, 0, 0))
    return out
