"""Phase 3 VFX meshes (low-poly, UVs laid out for scrolling textures) + their scroll textures.

UV convention for every ribbon / shell: U runs ALONG the effect (arc length, around the ring, along the dragon body),
V runs ACROSS it (0 = inner / bottom edge, 1 = outer / top edge). Scroll the texture along U for motion.
"""
import math, os, random
import numpy as np
from mathutils import Vector, Matrix, noise
from geo import Builder, lathe, tube
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX_OUT = os.path.join(ROOT, 'assets', 'Phase3', 'VFX', 'Textures')
MATS = ['VFX_Slash', 'VFX_Energy', 'VFX_Water', 'VFX_Fire', 'Stone_Granite']


def B():
    return Builder(MATS)


def grid_surface(b, P, nu, nv, mat, double=True, u_scale=1.0):
    """Surface from P(u, v) -> Vector with u, v in [0, 1]; UVs = (u*u_scale, v). Double-sided (two opposing faces)
    so it renders from both sides in Roblox (which culls back faces)."""
    vs = [[b.bm.verts.new(P(i / nu, j / nv)) for i in range(nu + 1)] for j in range(nv + 1)]
    for j in range(nv):
        for i in range(nu):
            q = [vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]]
            uv = [((i / nu) * u_scale, j / nv), (((i + 1) / nu) * u_scale, j / nv), (((i + 1) / nu) * u_scale, (j + 1) / nv), ((i / nu) * u_scale, (j + 1) / nv)]
            b.face(q, mat, uv, smooth=True)
    if double:
        vs2 = [[b.bm.verts.new(P(i / nu, j / nv)) for i in range(nu + 1)] for j in range(nv + 1)]
        for j in range(nv):
            for i in range(nu):
                q = [vs2[j + 1][i], vs2[j + 1][i + 1], vs2[j][i + 1], vs2[j][i]]
                uv = [((i / nu) * u_scale, (j + 1) / nv), (((i + 1) / nu) * u_scale, (j + 1) / nv), (((i + 1) / nu) * u_scale, j / nv), ((i / nu) * u_scale, j / nv)]
                b.face(q, mat, uv, smooth=True)
    return vs


# --------------------------------------------------------------------------------------------- slashes
def slash(kind='medium'):
    """Crescent blade trail in the XY plane (horizontal slash), sweeping ~200 deg around the origin, thick in the
    middle and tapering to points. Thin / medium / heavy differ in radius, width, sweep and a slight tilt."""
    R, W, sweep, tilt = {'thin': (5.0, 0.8, 170, 4), 'medium': (6.5, 1.8, 200, 8), 'heavy': (8.5, 3.4, 230, 12)}[kind]
    b = B()
    a0 = math.radians(90 - sweep / 2 + 90); a1 = math.radians(90 + sweep / 2 + 90)
    def P(u, v):
        a = a0 + (a1 - a0) * u
        w = W * math.sin(math.pi * u) ** 0.7
        r = R - w * 0.35 + v * w
        z = math.sin(math.radians(tilt)) * r * math.cos(a - (a0 + a1) / 2) * 0.3 + (v - 0.5) * 0.05
        return Vector((r * math.cos(a), r * math.sin(a), z))
    grid_surface(b, P, 32, 4, 'VFX_Slash')
    return b


# --------------------------------------------------------------------------------------------- rings / dome
def shock_ring_flat(R=8.0, W=2.0):
    b = B()
    def P(u, v):
        a = 2 * math.pi * u
        r = R - W / 2 + v * W
        return Vector((r * math.cos(a), r * math.sin(a), 0.02 * math.sin(math.pi * v)))
    grid_surface(b, P, 48, 2, 'VFX_Energy', u_scale=4.0)
    return b


def shock_dome(R=6.0):
    b = B()
    def P(u, v):
        a = 2 * math.pi * u
        el = v * math.pi / 2
        return Vector((R * math.cos(a) * math.cos(el), R * math.sin(a) * math.cos(el), R * math.sin(el) * 0.85))
    grid_surface(b, P, 32, 10, 'VFX_Energy', u_scale=3.0)
    return b


def vortex(H=16.0, R0=1.2, R1=6.0, twist=2.5):
    """Tornado: open, flaring, twisted shell (U around, V up)."""
    b = B()
    def P(u, v):
        r = R0 + (R1 - R0) * v ** 1.4
        a = 2 * math.pi * u + twist * 2 * math.pi * v
        wob = 0.4 * math.sin(v * 7 + u * 2 * math.pi) * v
        return Vector(((r + wob) * math.cos(a), (r + wob) * math.sin(a), H * v))
    grid_surface(b, P, 24, 16, 'VFX_Energy', u_scale=2.0)
    return b


def spiral_cone(H=10.0, R=4.0, turns=3.0, W=1.2):
    """Helical ribbon winding up a cone (drill / charge-up swirl)."""
    b = B()
    def P(u, v):
        a = 2 * math.pi * turns * u
        r = R * (1 - u * 0.85)
        z = H * u + (v - 0.5) * W
        return Vector((r * math.cos(a), r * math.sin(a), z))
    grid_surface(b, P, 96, 2, 'VFX_Energy', u_scale=6.0)
    return b


def energy_sphere():
    """Three nested shells (outer 4, middle 2.8, core 1.6) as separate builders -> separate meshes."""
    out = []
    for name, r, segs in (('Outer', 4.0, 24), ('Middle', 2.8, 20), ('Core', 1.6, 16)):
        b = B()
        prof = [(r * math.sin(math.pi * i / 12), r - r * math.cos(math.pi * i / 12)) for i in range(13)]
        prof[0] = (0.0, 0.0); prof[-1] = (0.0, 2 * r)
        lathe(b, (0, 0, 4.0 - r), prof, segs, 'VFX_Energy')
        out.append((name, b))
    return out


# --------------------------------------------------------------------------------------------- water dragon
def water_dragon(L=40.0):
    """Serpentine water dragon: tapering sinuous body (U along the body for flowing water), head with snout,
    jaw, horns, whiskers and a dorsal ridge. Head at +Y (front)."""
    b = B()
    n = 64
    path, radii = [], []
    for i in range(n + 1):
        t = i / n                                       # 0 tail .. 1 neck
        y = -L / 2 + L * t
        x = math.sin(t * math.pi * 3.0) * 3.5 * (1 - t * 0.6)
        z = 4.0 + math.sin(t * math.pi * 2.0 + 1.0) * 2.2 + t * 2.0
        path.append(Vector((x, y, z)))
        radii.append(0.15 + 1.25 * math.sin(math.pi * min(1.0, t * 1.05)) ** 0.6 if t < 0.95 else 1.2)
    rings = tube(b, path, radii, 14, 'VFX_Water', smooth=True, caps=False)
    # re-map UVs: U along the body (0 tail -> 4 neck), V around
    for k, ring in enumerate(rings):
        for j, v in enumerate(ring):
            for l in v.link_loops:
                l[b.uv].uv = (k / n * 4.0, l[b.uv].uv[1] % 1.0)
    head = path[-1]
    d = (path[-1] - path[-2]).normalized()
    # skull, snout, jaw
    tube(b, [head, head + d * 1.6, head + d * 3.2 + Vector((0, 0, -0.2))], [1.3, 1.0, 0.55], 10, 'VFX_Water')
    tube(b, [head + d * 0.6 + Vector((0, 0, -0.7)), head + d * 2.6 + Vector((0, 0, -1.3))], [0.7, 0.35], 8, 'VFX_Water')
    side = d.cross(Vector((0, 0, 1))).normalized()
    for s in (1, -1):
        base = head + side * s * 0.7 + Vector((0, 0, 0.8))
        tube(b, [base, base - d * 1.2 + Vector((0, 0, 1.0)) + side * s * 0.4, base - d * 2.6 + Vector((0, 0, 1.4)) + side * s * 0.8],
             [0.22, 0.14, 0.03], 6, 'VFX_Water')          # horns
        wb = head + d * 2.6 + side * s * 0.45
        tube(b, [wb, wb + side * s * 1.5 - d * 0.5 + Vector((0, 0, -0.3)), wb + side * s * 2.8 - d * 1.8 + Vector((0, 0, 0.2)),
                 wb + side * s * 3.6 - d * 3.5 + Vector((0, 0, -0.2))], [0.08, 0.06, 0.04, 0.01], 5, 'VFX_Water')   # whiskers
    # dorsal ridge fins along the back
    for i in range(6, n - 3, 4):
        p = path[i]; r = radii[i]
        dd = (path[i + 1] - path[i - 1]).normalized()
        upv = Vector((0, 0, 1))
        tip = p + upv * (r + 0.9 * r)
        b.face([b.bm.verts.new(p + upv * r * 0.8 - dd * r * 0.6), b.bm.verts.new(p + upv * r * 0.8 + dd * r * 0.6), b.bm.verts.new(tip)],
               'VFX_Water', [(0, 0), (1, 0), (0.5, 1)])
        b.face([b.bm.verts.new(tip), b.bm.verts.new(p + upv * r * 0.8 + dd * r * 0.6), b.bm.verts.new(p + upv * r * 0.8 - dd * r * 0.6)],
               'VFX_Water', [(0.5, 1), (1, 0), (0, 0)])
    return b


# --------------------------------------------------------------------------------------------- earth
def rock_shard(seed, size=1.0):
    """Angular low-poly rock chunk / shard (flat facets), centred on its own origin."""
    import bmesh
    b = B()
    r = random.Random(seed)
    tmp = bmesh.new()
    bmesh.ops.create_icosphere(tmp, subdivisions=2, radius=1.0)
    elong = Vector((r.uniform(0.6, 1.0), r.uniform(0.6, 1.0), r.uniform(1.0, 2.2) if seed % 2 else r.uniform(0.6, 1.1)))
    vm = {}
    for v in tmp.verts:
        n = v.co.normalized()
        k = 1.0 + noise.noise(n * 2.0 + Vector((seed, seed * 2, 0))) * 0.35
        vm[v] = b.bm.verts.new(Vector((n.x * elong.x, n.y * elong.y, n.z * elong.z)) * k * size)
    for f in tmp.faces:
        vs = [vm[v] for v in f.verts]
        b.face(vs, 'Stone_Granite', [((v.co.x + v.co.y) * 0.3, v.co.z * 0.3) for v in vs], out=sum((v.co for v in vs), Vector()))
    tmp.free()
    return b


def stone_drill(H=6.0, R=1.6, turns=4):
    """Stone drill: cone with raised spiral ridges (lathe cone + helical ridge tube)."""
    b = B()
    lathe(b, (0, 0, 0), [(R, 0.0), (R * 0.95, H * 0.1), (0.0, H)], 12, 'Stone_Granite')
    n = 64
    pts = [Vector((R * (1 - i / n) * 0.98 * math.cos(2 * math.pi * turns * i / n), R * (1 - i / n) * 0.98 * math.sin(2 * math.pi * turns * i / n),
                   H * i / n * 0.97)) for i in range(n + 1)]
    tube(b, pts, [0.22 * (1 - i / n) + 0.03 for i in range(n + 1)], 5, 'Stone_Granite', smooth=False)
    return b


# --------------------------------------------------------------------------------------------- fire
def fire_pillar(H=18.0, R0=3.0, R1=2.2):
    """Open, slightly tapered cylinder with a wobbling top edge (U around, V up; scroll V for rising flames)."""
    b = B()
    def P(u, v):
        a = 2 * math.pi * u
        r = R0 + (R1 - R0) * v + 0.25 * math.sin(a * 5 + v * 6)
        return Vector((r * math.cos(a), r * math.sin(a), H * v + (0.8 * math.sin(a * 7) * v if v > 0.9 else 0)))
    grid_surface(b, P, 24, 8, 'VFX_Fire', u_scale=3.0)
    return b


def fire_ring_segment(R=10.0, arc=45.0, H=5.0):
    """One segment of a ring of fire: curved wall of flame (U along the arc, V up). 8 segments = full circle."""
    b = B()
    a0 = math.radians(-arc / 2); a1 = math.radians(arc / 2)
    def P(u, v):
        a = a0 + (a1 - a0) * u
        h = H * (0.75 + 0.25 * math.sin(u * math.pi * 3))
        return Vector((R * math.cos(a), R * math.sin(a), h * v))
    grid_surface(b, P, 10, 4, 'VFX_Fire')
    return b


# --------------------------------------------------------------------------------------------- scroll textures
def textures():
    """Tileable scroll textures (1024, RGBA): slash gradient, energy flow, water flow, fire flow."""
    os.makedirs(TEX_OUT, exist_ok=True)
    import vfx_flipbooks as vf
    S = 1024
    yy, xx = np.mgrid[0:S, 0:S] / S
    # slash: bright leading edge (v high) fading toward the inner edge, streaks along U
    streak = vf.tile_noise(S, 11, 1.2, aniso=(30.0, 1.0))
    v = 1 - yy
    a = np.clip(vf.smooth(0.0, 0.85, v) * (0.55 + 0.45 * streak) + vf.smooth(0.8, 0.98, v) * 0.6, 0, 1) * vf.smooth(1.0, 0.94, v)
    rgb = np.ones((S, S, 3))
    Image.fromarray((np.dstack([rgb, a]) * 255).astype(np.uint8), 'RGBA').save(os.path.join(TEX_OUT, 'HO_VFXT_Slash.png'))
    # energy: flowing streaks along U, tileable
    n1 = vf.tile_noise(S, 12, 1.4, aniso=(12.0, 1.0)); n2 = vf.tile_noise(S, 13, 2.2)
    a = np.clip(vf.smooth(0.45, 0.85, n1 * 0.7 + n2 * 0.3) * 0.9 + 0.1, 0, 1)
    Image.fromarray((np.dstack([np.ones((S, S, 3)), a]) * 255).astype(np.uint8), 'RGBA').save(os.path.join(TEX_OUT, 'HO_VFXT_Energy.png'))
    # water: foamy flowing water (pre-coloured blue-white)
    n3 = vf.tile_noise(S, 14, 1.6, aniso=(6.0, 1.0)); n4 = vf.tile_noise(S, 15, 2.4)
    t = n3 * 0.6 + n4 * 0.4
    rgb = vf.ramp(t, [(0.0, (0.05, 0.25, 0.5)), (0.5, (0.2, 0.55, 0.85)), (0.8, (0.7, 0.9, 1.0)), (1.0, (1.0, 1.0, 1.0))])
    a = np.clip(0.55 + 0.45 * t, 0, 1)
    Image.fromarray((np.dstack([rgb, a]) * 255).astype(np.uint8), 'RGBA').save(os.path.join(TEX_OUT, 'HO_VFXT_Water.png'))
    # fire flow: rising flame tongues (V up), pre-coloured, alpha fades to the top
    n5 = vf.tile_noise(S, 16, 1.8, aniso=(1.0, 5.0))
    heat = np.clip(n5 * 1.1 - 0.05, 0, 1)
    rgb = vf.ramp(heat, vf.FIRE)
    a = vf.smooth(0.25, 0.6, heat)
    Image.fromarray((np.dstack([rgb, a]) * 255).astype(np.uint8), 'RGBA').save(os.path.join(TEX_OUT, 'HO_VFXT_Fire.png'))

    # the same images as material texture sets (textures/VFX_<X>/HO_T_VFX_<X>_*.png) for the mesh materials
    for src, setname in (('HO_VFXT_Slash', 'VFX_Slash'), ('HO_VFXT_Energy', 'VFX_Energy'), ('HO_VFXT_Water', 'VFX_Water'),
                         ('HO_VFXT_Fire', 'VFX_Fire')):
        d = os.path.join(ROOT, 'textures', setname); os.makedirs(d, exist_ok=True)
        Image.open(os.path.join(TEX_OUT, src + '.png')).save(os.path.join(d, f'HO_T_{setname}_Color.png'))
        Image.new('RGB', (1024, 1024), (128, 128, 255)).save(os.path.join(d, f'HO_T_{setname}_Normal.png'))
        Image.new('L', (1024, 1024), 230).save(os.path.join(d, f'HO_T_{setname}_Roughness.png'))
        Image.new('L', (1024, 1024), 0).save(os.path.join(d, f'HO_T_{setname}_Metalness.png'))
