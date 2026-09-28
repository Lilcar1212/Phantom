"""Generate the shared, tileable PBR texture library for Hollow Oath (1024x1024 PNG sets).

Every set: textures/<Set>/HO_T_<Set>_{Color,Normal,Roughness,Metalness}.png
Normal maps are tangent-space, OpenGL (+Y up) - the format Roblox SurfaceAppearance and Blender expect.

World-scale conventions (the UV density each set is authored for):
  * tileable sets: one tile = 4x4 studs (UV density 0.25 / stud) unless noted
  * Plaster_White: U tiles every 4 studs, V spans exactly one 9-stud floor (dirt band at V=0)
"""
import os, sys
import numpy as np
from PIL import Image
from scipy.spatial import cKDTree

N = 1024
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'textures')
yy, xx = np.mgrid[0:N, 0:N] / N          # yy = V (0 at top row of image), xx = U


def rng(seed):
    return np.random.default_rng(seed)


def fnoise(seed, beta=2.0, lo=0, aniso=(1.0, 1.0), n=N):
    """Tileable fractal noise via spectral synthesis, normalised to 0..1.
    aniso=(sx, sy): sx > 1 stretches features along U, sy > 1 along V."""
    r = rng(seed)
    w = r.standard_normal((n, n))
    fy = np.fft.fftfreq(n)[:, None] * n * aniso[1]
    fx = np.fft.fftfreq(n)[None, :] * n * aniso[0]
    f = np.sqrt(fx ** 2 + fy ** 2)
    f[0, 0] = 1
    amp = 1.0 / f ** (beta / 2)
    if lo:
        amp[f < lo] = 0
    amp[0, 0] = 0
    out = np.real(np.fft.ifft2(np.fft.fft2(w) * amp))
    out -= out.min(); out /= out.max()
    return out


def voronoi(seed, count, jitter=1.0, grid=None):
    """Periodic Voronoi. Returns F1, F2 (in tile units) and cell id per pixel."""
    r = rng(seed)
    if grid:
        gx, gy = grid
        cy, cx = np.mgrid[0:gy, 0:gx]
        pts = np.stack([(cx + 0.5 + (r.random(cx.shape) - 0.5) * jitter) / gx,
                        (cy + 0.5 + (r.random(cy.shape) - 0.5) * jitter) / gy], -1).reshape(-1, 2)
    else:
        pts = r.random((count, 2))
    pts %= 1.0
    tree = cKDTree(pts, boxsize=1.0)
    q = np.stack([xx.ravel(), yy.ravel()], -1)
    d, i = tree.query(q, k=2)
    return d[:, 0].reshape(N, N), d[:, 1].reshape(N, N), i[:, 0].reshape(N, N), pts


def normal_from_height(h, strength):
    """OpenGL tangent-space normal (green = +V up in texture space). Image row 0 is top (V=1)."""
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 0.5 * strength
    dy = (np.roll(h, 1, 0) - np.roll(h, -1, 0)) * 0.5 * strength   # +V is up the image
    nx, ny, nz = -dx, -dy, np.ones_like(h)
    l = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    return np.stack([nx / l, ny / l, nz / l], -1) * 0.5 + 0.5


def lerp(a, b, t):
    t = np.clip(t, 0, 1)[..., None] if np.ndim(t) == 2 else np.clip(t, 0, 1)
    return np.asarray(a, float) * (1 - t) + np.asarray(b, float) * t


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def save(name, color, height, rough, metal, nstrength=4.0, normal=None, alpha=None):
    d = os.path.join(OUT, name); os.makedirs(d, exist_ok=True)
    c = np.clip(color, 0, 255).astype(np.uint8)
    if alpha is not None:                                  # RGBA colour map (SurfaceAppearance AlphaMode)
        c = np.dstack([c, (np.clip(alpha, 0, 1) * 255).astype(np.uint8)])
    Image.fromarray(c, 'RGBA' if alpha is not None else 'RGB').save(os.path.join(d, f'HO_T_{name}_Color.png'), optimize=True)
    nm = normal if normal is not None else normal_from_height(height, nstrength * N / 256)
    Image.fromarray((nm * 255 + 0.5).astype(np.uint8), 'RGB').save(os.path.join(d, f'HO_T_{name}_Normal.png'))
    rough = rough if np.ndim(rough) else np.full((N, N), rough)
    Image.fromarray((np.clip(rough, 0, 1) * 255).astype(np.uint8), 'L').save(os.path.join(d, f'HO_T_{name}_Roughness.png'))
    m = metal if np.ndim(metal) else np.full((N, N), metal)
    Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8), 'L').save(os.path.join(d, f'HO_T_{name}_Metalness.png'))
    print('wrote', name)


def wood_grain(seed, rings=34, warp=6.0):
    """Grain running along U. Returns (grain 0..1 lines, fibre noise)."""
    n1 = fnoise(seed, 2.2, aniso=(8.0, 1.0))
    n2 = fnoise(seed + 1, 1.2, aniso=(20.0, 1.0))
    ring = np.sin((yy * rings + n1 * warp) * 2 * np.pi) * 0.5 + 0.5
    ring = ring ** 3
    return ring, n2


# ----------------------------------------------------------------------------------------------- sets
def roof_tile():
    # Ibushi-gawara: smoked clay, blue-grey with silvery sheen. V runs down-slope.
    m1 = fnoise(11, 2.4); m2 = fnoise(12, 1.0); m3 = fnoise(13, 3.0)
    streak = fnoise(14, 2.0, aniso=(1.0, 12.0))           # vertical rain streaks
    lichen = smooth(0.66, 0.8, fnoise(15, 2.6)) * smooth(0.5, 0.7, m2)
    base = lerp((62, 69, 80), (92, 100, 112), m1 * 0.7 + m2 * 0.3)
    base = lerp(base, (48, 52, 58), smooth(0.55, 0.9, streak) * 0.5)
    base = lerp(base, (104, 112, 82), lichen * 0.55)
    base += (m2[..., None] - 0.5) * 18
    h = m2 * 0.6 + m3 * 0.3 + lichen * 0.3
    rough = 0.52 + m1 * 0.15 + lichen * 0.3 - smooth(0.6, 0.9, streak) * 0.08
    save('RoofTile_Clay', base, h, rough, 0.0, 2.5)


def fibre_lines(seed, width=1.5, warp_amt=0.02):
    """1-D noise across V, broadcast along U and gently warped -> long straight wood fibres."""
    r = rng(seed)
    line = r.standard_normal(N)
    k = np.exp(-0.5 * (np.arange(-8, 9) / width) ** 2); k /= k.sum()
    line = np.convolve(np.concatenate([line[-8:], line, line[:8]]), k, 'same')[8:-8]
    line = (line - line.min()) / (line.max() - line.min())
    warp = (fnoise(seed + 1, 3.0, aniso=(6.0, 1.0)) - 0.5) * warp_amt
    idx = (((yy + warp) % 1.0) * N).astype(int) % N
    return line[idx]


def timber(name, dark, light, seed, rough_base):
    warp = fnoise(seed, 3.0, aniso=(6.0, 1.0))
    ring = np.sin((yy * 9 + warp * 1.6) * 2 * np.pi) * 0.5 + 0.5      # broad growth-ring bands
    ring = smooth(0.25, 0.95, ring)
    fib = fibre_lines(seed + 3, 1.2)
    fib2 = fibre_lines(seed + 5, 4.0, 0.04)
    mott = fnoise(seed + 7, 2.4)
    t = ring * 0.45 + fib * 0.3 + fib2 * 0.2 + mott * 0.15
    col = lerp(light, dark, np.clip(t, 0, 1))
    wear = smooth(0.62, 0.85, fnoise(seed + 9, 2.0))
    col = lerp(col, np.array(dark) * 0.75 + np.array((40, 40, 40)) * 0.25, wear * 0.3)
    h = (1 - fib) * 0.4 + (1 - ring) * 0.3 + mott * 0.1
    rough = rough_base + fib * 0.12 + wear * 0.1
    save(name, col, h, rough, 0.0, 3.0)


def plaster():
    # V spans one 9-stud floor: image bottom (row N-1) = V 0 = ground/base of wall.
    v = 1.0 - yy
    m1 = fnoise(21, 2.6); m2 = fnoise(22, 1.1); m3 = fnoise(23, 2.0, aniso=(1.0, 10.0))
    base = lerp((236, 231, 219), (222, 214, 198), m1)
    base += (m2[..., None] - 0.5) * 8
    # rain streaks from above (vertical), faint
    base = lerp(base, (196, 190, 178), smooth(0.62, 0.95, m3) * 0.35)
    # dirt band at base with a ragged edge + splash
    edge = 0.10 + (fnoise(24, 2.0) - 0.5) * 0.08
    dirt = smooth(edge + 0.06, edge - 0.04, v)
    splash = smooth(0.18, 0.02, v) * smooth(0.55, 0.8, fnoise(25, 1.4))
    base = lerp(base, (150, 138, 118), dirt * 0.75)
    base = lerp(base, (128, 118, 100), splash * 0.4)
    # fine cracks
    f1, f2, _, _ = voronoi(26, 40)
    crack = smooth(0.004, 0.0, f2 - f1) * smooth(0.7, 0.85, fnoise(27, 2.0))
    base = lerp(base, (170, 165, 155), crack * 0.6)
    h = m2 * 0.45 + m1 * 0.2 - crack * 0.6
    rough = 0.86 + dirt * 0.08
    save('Plaster_White', base, h, rough, 0.0, 1.6)


def granite():
    m1 = fnoise(31, 2.5); m2 = fnoise(32, 0.6); m3 = fnoise(33, 1.6)
    spk = fnoise(34, 0.0)
    lichen = smooth(0.68, 0.82, fnoise(35, 2.6))
    moss = smooth(0.74, 0.88, fnoise(36, 2.2))
    col = lerp((128, 122, 110), (168, 160, 146), m1)
    col = lerp(col, (70, 66, 62), smooth(0.8, 0.9, spk) * 0.8)
    col = lerp(col, (205, 200, 190), smooth(0.2, 0.1, spk) * 0.6)
    col += (m3[..., None] - 0.5) * 16
    col = lerp(col, (176, 170, 120), lichen * 0.45)
    col = lerp(col, (78, 92, 52), moss * 0.6)
    h = m3 * 0.5 + m2 * 0.35 + m1 * 0.3 + moss * 0.2
    rough = 0.74 + m2 * 0.12 + moss * 0.12
    save('Stone_Granite', col, h, rough, 0.0, 3.2)


def fitted_stone():
    # Mortarless fitted blocks (for plinths / flat stone faces). 4 studs per tile, ~4x3 stones.
    f1, f2, cid, pts = voronoi(41, 0, jitter=0.85, grid=(4, 5))
    edge = f2 - f1
    r = rng(42)
    tone = r.random(len(pts))[cid]
    m1 = fnoise(43, 2.4); m2 = fnoise(44, 0.8)
    dome = smooth(0.0, 0.07, edge)
    gap = smooth(0.012, 0.0, edge)
    col = lerp((118, 112, 102), (165, 158, 144), tone * 0.7 + m1 * 0.3)
    col += (m2[..., None] - 0.5) * 18
    col = lerp(col, (38, 36, 34), gap)
    moss = smooth(0.012, 0.0, edge - 0.004) * smooth(0.55, 0.75, fnoise(45, 2.2))
    col = lerp(col, (72, 86, 48), moss * 0.7)
    h = dome * 0.8 + m2 * 0.15 + m1 * 0.1
    rough = 0.78 + gap * 0.15
    save('Stone_Fitted', col, h, rough, 0.0, 6.0)


def cobble():
    f1, f2, cid, pts = voronoi(51, 0, jitter=0.9, grid=(9, 9))
    edge = f2 - f1
    r = rng(52)
    tone = r.random(len(pts))[cid]
    m1 = fnoise(53, 2.4); m2 = fnoise(54, 0.8)
    dome = smooth(0.0, 0.05, edge) ** 0.7
    gap = smooth(0.016, 0.004, edge)
    col = lerp((104, 98, 90), (150, 142, 128), tone * 0.6 + m1 * 0.4)
    col += (m2[..., None] - 0.5) * 20
    col = lerp(col, (74, 62, 48), gap)                          # packed dirt between stones
    col = lerp(col, (80, 92, 50), gap * smooth(0.6, 0.8, fnoise(55, 2.2)) * 0.8)
    h = dome * 0.9 + m2 * 0.1
    rough = 0.7 - dome * 0.12 + gap * 0.25
    save('Cobblestone', col, h, rough, 0.0, 7.0)


def planks():
    # Boards run along U; 8 boards per 4-stud tile (0.5-stud boards), staggered butt joints.
    nb = 8
    board = np.floor(yy * nb).astype(int)
    r = rng(61)
    offs = r.random(nb)
    lengths = r.choice([0.5, 1.0], nb)
    seg_u = (xx + offs[board]) / lengths[board]
    seg = np.floor(seg_u).astype(int)
    seg_id = board * 7 + seg
    tone = rng(62).random(nb * 7 + 20)[seg_id % (nb * 7 + 20)]
    fv = (yy * nb) % 1.0
    fu = seg_u % 1.0
    gap = np.maximum(smooth(0.035, 0.0, fv), smooth(0.035, 0.0, 1 - fv))
    butt = np.maximum(smooth(0.006, 0.0, fu), smooth(0.006, 0.0, 1 - fu))
    gap = np.maximum(gap, butt)
    ring, fib = wood_grain(63, rings=60)
    weather = fnoise(64, 2.0)
    col = lerp((150, 124, 92), (98, 80, 60), ring * 0.4 + fib * 0.3 + tone * 0.4)
    col = lerp(col, (132, 126, 116), smooth(0.45, 0.8, weather) * 0.45)       # silvered weathering
    col = lerp(col, (30, 24, 18), gap)
    # nail heads
    nail = np.zeros_like(xx)
    for k in range(nb):
        for s in (0.06, 0.94):
            cu = ((np.arange(8) + s) * lengths[k] - offs[k]) % 1.0
            for c in cu:
                du = np.minimum(abs(xx - c), 1 - abs(xx - c)); dv = abs(yy - (k + 0.5) / nb)
                nail = np.maximum(nail, smooth(0.006, 0.003, np.sqrt(du ** 2 + dv ** 2)))
    col = lerp(col, (48, 44, 42), nail)
    h = (1 - gap) * 0.7 + fib * 0.25 + ring * 0.1 - nail * 0.2
    rough = 0.78 + fib * 0.1 + gap * 0.1 - nail * 0.3
    metal = nail * 0.8
    save('Wood_Planks', col, h, rough, metal, 3.0)


def gold():
    # Gold leaf over lacquer: faint leaf-square seams, hammered micro-dents.
    m1 = fnoise(71, 2.2); m2 = fnoise(72, 1.0)
    f1, f2, _, _ = voronoi(73, 0, jitter=0.12, grid=(8, 8))
    seam = smooth(0.004, 0.0, f2 - f1)
    col = lerp((196, 150, 62), (236, 196, 108), m1)
    col = lerp(col, (160, 116, 46), seam * 0.6)
    rub = smooth(0.8, 0.9, fnoise(74, 2.4))
    col = lerp(col, (70, 30, 24), rub * 0.5)              # red lacquer showing through where worn
    h = m2 * 0.4 + seam * 0.2
    rough = 0.22 + m2 * 0.18 + rub * 0.4
    metal = 1.0 - rub * 0.9
    save('Gold_Leaf', col, h, rough, metal, 1.4)


def iron():
    m1 = fnoise(81, 2.2); m2 = fnoise(82, 0.9)
    dents_f1, dents_f2, _, _ = voronoi(83, 220)
    dent = smooth(0.0, 0.03, dents_f1)
    rust = smooth(0.62, 0.8, fnoise(84, 2.4) * 0.7 + m2 * 0.3)
    col = lerp((52, 50, 50), (86, 84, 82), m1)
    col = lerp(col, (116, 58, 28), rust * 0.85)
    col = lerp(col, (150, 84, 40), rust * smooth(0.6, 0.9, m2) * 0.5)
    h = dent * 0.5 + rust * 0.35 + m2 * 0.2
    rough = 0.5 + m1 * 0.15 + rust * 0.35
    metal = 0.92 - rust * 0.85
    save('Iron_Wrought', col, h, rough, metal, 2.5)


def shoji():
    fib = fnoise(91, 1.4, aniso=(3.0, 1.0)); m1 = fnoise(92, 2.5)
    col = lerp((244, 239, 224), (226, 218, 198), m1 * 0.6 + fib * 0.4)
    h = fib * 0.4
    save('Shoji_Paper', col, h, 0.92, 0.0, 0.7)


def uv_check():
    # Debug grid used by the test cube, with face labels painted by the cube script.
    c = ((np.floor(xx * 8) + np.floor(yy * 8)) % 2)[..., None]
    col = lerp((70, 70, 80), (200, 200, 210), c)
    save('Debug_Grid', col, np.zeros((N, N)), 0.6, 0.0)


def cloth(name, base, seed=121):
    """Woven cotton (noren / banners): fine weave, soft folds, faded edges. base = RGB."""
    wu = (np.sin(xx * N * np.pi * 0.5) * 0.5 + 0.5)
    wv = (np.sin(yy * N * np.pi * 0.5) * 0.5 + 0.5)
    weave = (wu * 0.5 + wv * 0.5)
    m1 = fnoise(seed, 2.4); m2 = fnoise(seed + 1, 1.2)
    fade = smooth(0.55, 0.9, fnoise(seed + 2, 2.0))
    col = np.array(base, float)[None, None, :] * (0.86 + 0.14 * m1[..., None]) * (0.94 + 0.06 * weave[..., None])
    col = lerp(col, np.minimum(np.array(base) * 1.25 + 25, 255), fade * 0.25)
    h = weave * 0.5 + m2 * 0.3
    save(name, col, h, 0.9 - weave * 0.05, 0.0, 1.2)


def tatami():
    """Tatami mat surface: woven igusa rush running along V, 3x6-stud mat = one texture tile (UV 1/3 x 1/6)."""
    rows = (np.sin(yy * N * np.pi / 3.0) * 0.5 + 0.5)
    fib = fnoise(131, 0.8, aniso=(1.0, 30.0))
    m1 = fnoise(132, 2.4)
    col = lerp((168, 164, 104), (198, 190, 128), rows * 0.4 + fib * 0.4 + m1 * 0.2)
    # heri (cloth border) along the long edges: dark indigo band
    band = np.maximum(smooth(0.035, 0.03, xx), smooth(0.965, 0.97, xx))
    col = lerp(col, (38, 44, 58), band)
    h = rows * 0.4 + fib * 0.3 - band * 0.2
    save('Tatami', col, h, 0.75 + band * 0.1, 0.0, 2.2)


def red_lacquer():
    m1 = fnoise(141, 2.4); m2 = fnoise(142, 1.0)
    wear = smooth(0.72, 0.86, fnoise(143, 2.2))
    col = lerp((168, 36, 26), (196, 52, 34), m1)
    col = lerp(col, (60, 34, 26), wear * 0.55)          # dark wood showing through
    col = lerp(col, (120, 110, 98), smooth(0.85, 0.95, fnoise(144, 2.0)) * 0.3)
    h = m2 * 0.3 + wear * 0.2
    save('Red_Lacquer', col, h, 0.34 + m1 * 0.1 + wear * 0.35, 0.0, 1.0)



def earth():
    """Packed earth (doma floors, paths): compacted clay with grit and faint sweep marks."""
    m1 = fnoise(151, 2.6); m2 = fnoise(152, 1.0); grit = fnoise(153, 0.0)
    sweep = fnoise(154, 1.6, aniso=(6.0, 1.0))
    col = lerp((112, 92, 70), (146, 122, 94), m1 * 0.7 + sweep * 0.3)
    col = lerp(col, (84, 70, 56), smooth(0.8, 0.95, grit) * 0.6)
    col = lerp(col, (170, 150, 120), smooth(0.15, 0.05, grit) * 0.4)
    h = m2 * 0.4 + grit * 0.2 + sweep * 0.15
    save('Earth_Packed', col, h, 0.88, 0.0, 1.6)



def black_lacquer():
    m1 = fnoise(161, 2.4); m2 = fnoise(162, 1.0)
    wear = smooth(0.8, 0.9, fnoise(163, 2.2))
    col = lerp((22, 20, 22), (38, 34, 36), m1)
    col = lerp(col, (96, 40, 30), wear * 0.5)            # red undercoat where worn
    h = m2 * 0.25 + wear * 0.15
    save('Black_Lacquer', col, h, 0.22 + m1 * 0.08 + wear * 0.3, 0.0, 0.8)


def namako():
    """Namako-kabe: square black tiles set diagonally, raised white plaster joints. One tile = 1x1 stud,
    texture tile = 4x4 studs (4 diagonal tiles per row)."""
    u = (xx + yy) * 4.0; v = (xx - yy) * 4.0
    fu, fv = u % 1.0, v % 1.0
    d = np.minimum(np.minimum(fu, 1 - fu), np.minimum(fv, 1 - fv))
    joint = smooth(0.09, 0.05, d)
    dome = smooth(0.05, 0.12, d)
    m1 = fnoise(171, 2.4); m2 = fnoise(172, 1.0)
    tid = (np.floor(u) * 7 + np.floor(v) * 13) % 5 / 5.0
    tile = lerp((34, 36, 40), (58, 60, 66), m1 * 0.6 + tid * 0.4)
    plaster = lerp((226, 222, 212), (242, 238, 228), m2)
    col = lerp(tile, plaster, joint)
    h = joint * 1.0 + dome * 0.25 + m2 * 0.05
    save('Namako_Wall', col, h, 0.55 + joint * 0.35, 0.0, 5.0)


def straw():
    """Woven rice straw (tawara bales, sacks, komodaru wrap): fibres along U, binding bands."""
    fib = fnoise(181, 0.6, aniso=(30.0, 1.0)); m1 = fnoise(182, 2.4)
    col = lerp((168, 140, 86), (212, 186, 124), fib * 0.6 + m1 * 0.4)
    col = lerp(col, (120, 96, 56), smooth(0.8, 0.95, fnoise(183, 0.8, aniso=(30.0, 1.0))) * 0.5)
    h = fib * 0.6
    save('Straw', col, h, 0.85, 0.0, 2.5)


def ember():
    """Glowing forge coals (use with Neon or a PointLight in Roblox)."""
    f1, f2, cid, pts = voronoi(191, 0, jitter=0.9, grid=(10, 10))
    edge = f2 - f1
    heat = fnoise(192, 1.8)
    hot = smooth(0.35, 0.8, heat)
    coal = smooth(0.0, 0.04, edge)
    col = lerp((30, 18, 14), (255, 120, 30), hot * coal)
    col = lerp(col, (255, 210, 120), smooth(0.7, 0.95, heat) * coal)
    save('Ember', col, coal * 0.8, 0.9, 0.0, 4.0)


def magic_glow():
    """Soft swirling glow for magic orbs (near-white so Roblox can tint it; use Neon / PointLight)."""
    sw = fnoise(201, 2.2); sw2 = fnoise(202, 1.4, aniso=(4.0, 1.0))
    t = np.sin((xx * 3 + sw * 2.5) * 2 * np.pi) * 0.5 + 0.5
    col = lerp((190, 226, 255), (255, 255, 255), t * 0.6 + sw2 * 0.4)
    save('Magic_Glow', col, sw * 0.2, 0.15, 0.0, 0.5)



def bamboo():
    """Bamboo culm surface along V (culm axis): green-gold with node rings every 1.5 studs (texture tile = 4 studs)."""
    fib = fnoise(211, 0.8, aniso=(1.0, 30.0)); m1 = fnoise(212, 2.4)
    col = lerp((150, 150, 70), (190, 176, 96), fib * 0.5 + m1 * 0.5)
    v = yy * 4 / 1.5
    node = smooth(0.06, 0.0, np.minimum(v % 1.0, 1 - (v % 1.0)))
    col = lerp(col, (110, 100, 50), node * 0.8)
    col = lerp(col, (120, 140, 60), smooth(0.6, 0.85, fnoise(213, 2.0)) * 0.35)
    h = fib * 0.3 + node * 0.8
    save('Bamboo', col, h, 0.4 + node * 0.2, 0.0, 2.0)


def pine_bark():
    """Plated pine bark: reddish-grey plates with deep fissures running along V."""
    f1, f2, cid, pts = voronoi(221, 0, jitter=0.9, grid=(6, 14))
    edge = f2 - f1
    tone = rng(222).random(len(pts))[cid]
    m1 = fnoise(223, 2.4)
    col = lerp((70, 52, 44), (128, 96, 76), tone * 0.5 + m1 * 0.5)
    fiss = smooth(0.025, 0.0, edge)
    col = lerp(col, (30, 24, 20), fiss)
    h = smooth(0.0, 0.05, edge) * 0.9 + m1 * 0.1
    save('Pine_Bark', col, h, 0.85, 0.0, 6.0)


def pine_needles():
    """Dense needle clumps for sculpted foliage pads (solid, no alpha): dark green tufts with lighter tips."""
    f1, f2, cid, pts = voronoi(231, 0, jitter=1.0, grid=(16, 16))
    tuft = smooth(0.06, 0.0, f1)
    streak = fnoise(232, 0.6, aniso=(1.0, 6.0))
    m1 = fnoise(233, 2.2)
    col = lerp((28, 52, 32), (60, 96, 52), streak * 0.6 + m1 * 0.4)
    col = lerp(col, (104, 132, 70), tuft * 0.45)
    h = streak * 0.6 + tuft * 0.4
    save('Pine_Needles', col, h, 0.8, 0.0, 4.0)


def rope():
    """Twisted hemp rope along U: diagonal strands."""
    t = ((xx * 8 + yy * 3) % 1.0)
    strand = np.sin(t * np.pi) ** 0.6
    m1 = fnoise(241, 2.0)
    col = lerp((120, 96, 60), (190, 160, 110), strand * 0.7 + m1 * 0.3)
    save('Rope', col, strand, 0.9, 0.0, 3.0)


def sail_canvas():
    """Sail cloth: off-white cotton with vertical seams every 1 stud (texture 4 studs), weathering."""
    m1 = fnoise(251, 2.4); m2 = fnoise(252, 1.2)
    seam = smooth(0.012, 0.0, np.minimum((xx * 4) % 1.0, 1 - (xx * 4) % 1.0))
    col = lerp((232, 224, 204), (206, 196, 172), m1 * 0.7 + m2 * 0.3)
    col = lerp(col, (170, 160, 140), seam * 0.7)
    col = lerp(col, (180, 170, 150), smooth(0.7, 0.9, fnoise(253, 2.0, aniso=(1.0, 6.0))) * 0.3)
    save('Sail_Canvas', col, m2 * 0.3 + seam * 0.5, 0.9, 0.0, 1.5)



def steel_blade():
    """Polished blade steel. UV: U along the blade, V across (V = 0 cutting edge, 1 spine). Wavy hamon temper line
    separates the bright edge steel from the darker body; fine polishing streaks along U."""
    streak = fnoise(261, 0.8, aniso=(40.0, 1.0)); m1 = fnoise(262, 2.2)
    v = 1 - yy
    wave = 0.32 + 0.06 * np.sin(xx * 2 * np.pi * 9) + 0.03 * np.sin(xx * 2 * np.pi * 23 + 1.3) + (fnoise(263, 2.0) - 0.5) * 0.06
    hamon = smooth(wave + 0.03, wave - 0.03, v)            # 1 on the edge side
    body = lerp((120, 124, 130), (150, 154, 160), streak * 0.6 + m1 * 0.4)
    edge = lerp((200, 204, 210), (232, 236, 240), streak)
    col = lerp(body, edge, hamon)
    col = lerp(col, (250, 250, 252), smooth(0.03, 0.0, np.abs(v - wave)) * 0.5)   # frosty hamon boundary
    rough = 0.28 - hamon * 0.12 + streak * 0.06
    save('Steel_Blade', col, streak * 0.2, rough, 1.0, 0.6)



def steel_dark():
    """Ash-dark blade steel for the Ashfall Sword (same UV layout as Steel_Blade), faint ember-orange hamon."""
    streak = fnoise(265, 0.8, aniso=(40.0, 1.0)); m1 = fnoise(266, 2.2)
    v = 1 - yy
    wave = 0.3 + 0.05 * np.sin(xx * 2 * np.pi * 7) + (fnoise(267, 2.0) - 0.5) * 0.08
    hamon = smooth(wave + 0.04, wave - 0.04, v)
    body = lerp((46, 44, 46), (70, 66, 66), streak * 0.6 + m1 * 0.4)
    edge = lerp((120, 116, 112), (150, 144, 136), streak)
    col = lerp(body, edge, hamon)
    col = lerp(col, (200, 90, 40), smooth(0.025, 0.0, np.abs(v - wave)) * 0.6)
    save('Steel_Dark', col, streak * 0.2, 0.4 - hamon * 0.12, 0.9, 0.6)


def tsuka_wrap():
    """Katana grip: black silk ito wrapped in a diamond pattern over white ray skin (samegawa). Tile = 4 diamonds."""
    u = xx * 4; v = yy * 2
    du = np.abs((u % 1.0) - 0.5); dv = np.abs((v % 1.0) - 0.5)
    diamond = (du + dv) < 0.34
    samegawa = fnoise(271, 0.0)
    fib = fnoise(272, 0.6, aniso=(1.0, 10.0))
    col = np.where(diamond[..., None], lerp((226, 222, 206), (246, 242, 230), samegawa)[...,],
                   lerp((18, 18, 22), (46, 44, 52), fib))
    h = np.where(diamond, samegawa * 0.3, 0.6 + fib * 0.4)
    save('Tsuka_Wrap', col, h, np.where(diamond, 0.7, 0.55), 0.0, 2.5)


def shadow_black():
    """The Hollow's skin: near-black with a slow smoky violet sheen."""
    m1 = fnoise(281, 2.4); m2 = fnoise(282, 1.2, aniso=(1.0, 4.0))
    col = lerp((6, 5, 9), (26, 18, 34), smooth(0.5, 0.95, m1 * 0.6 + m2 * 0.4))
    save('Shadow_Black', col, m2 * 0.4, 0.55 + m1 * 0.3, 0.0, 1.5)


def navy_lacquer():
    m1 = fnoise(291, 2.4); wear = smooth(0.8, 0.9, fnoise(292, 2.2))
    col = lerp((22, 32, 64), (34, 48, 92), m1)
    col = lerp(col, (120, 90, 40), wear * 0.4)
    save('Navy_Lacquer', col, m1 * 0.2, 0.25 + m1 * 0.08 + wear * 0.3, 0.0, 0.8)


def glow(name, rgb, seed):
    """Emissive-style colour (use Material = Neon in Roblox) with a soft hot/cool variation."""
    m1 = fnoise(seed, 2.2)
    col = lerp(np.array(rgb) * 0.75, np.minimum(np.array(rgb) * 1.15 + 30, 255), m1)
    save(name, col, np.zeros((N, N)), 0.3, 0.0)


def dragon_scales():
    """Water-dragon body scales. U runs along the body (tail -> head, 16 rows / tile = 8 studs), V around it
    (16 scales per tile = one lap). Rows nearer the head overlap the ones behind; free rounded edges face the
    tail (-U). Teal-blue with dark navy seams and pale cyan rims, like a glossy wet hide."""
    R, C = 16, 16
    U, V = xx, 1 - yy
    h = np.zeros((N, N)); edge = np.ones((N, N)); cid = np.zeros((N, N)); inner = np.zeros((N, N))
    rad = 0.78 / C * 1.25
    for r in range(R):                                     # painter's order: later (head-ward) rows on top
        cu = (r + 0.5) / R
        du = (U - cu + 0.5) % 1.0 - 0.5
        off = 0.5 * (r % 2)
        cv = np.floor(V * C - off + 0.5)
        dv = (V * C - off - cv) / C
        du_s = du * (R / C) * 1.15                         # scales a bit longer than wide
        d = np.sqrt(du_s ** 2 + dv ** 2) / rad
        dv2 = dv - np.where(dv >= 0, 1.0, -1.0) / C                         # neighbour in the same row (the other nearest)
        d2 = np.sqrt(du_s ** 2 + dv2 ** 2) / rad
        seam = smooth(0.16, 0.0, d2 - d)                    # where two scales of a row meet
        m = (d < 1.0) & (du < 0.35 / R)                    # the head-side end is tucked under the row ahead
        h[m] = (np.sqrt(1 - d[m] ** 2) * 0.8 + 0.2 * (-du[m] * R)) * (1 - 0.7 * seam[m])
        edge[m] = np.maximum(d[m], np.where(seam[m] > 0.3, 0.9 + 0.1 * seam[m], 0.0)); inner[m] = 1 - d[m]
        cid[m] = (r * 131 + cv[m] * 17) % 97
    var = (np.sin(cid * 12.9898) * 43758.5453) % 1.0
    n1 = fnoise(601, 2.2); n2 = fnoise(602, 1.4, aniso=(1.0, 3.0))
    base = lerp((16, 62, 158), (36, 140, 228), var * 0.6 + n1 * 0.4)
    col = lerp(base, (110, 206, 255), smooth(0.35, 0.0, edge) * 0.55)       # sheen toward the scale centre
    col = lerp(col, (205, 246, 255), smooth(0.78, 0.92, edge) * smooth(1.0, 0.95, edge) * 0.85)   # pale rim
    col = lerp(col, (4, 16, 46), smooth(0.93, 1.0, edge))                  # dark seam
    col = lerp(col, (60, 90, 190), n2 * 0.18)                              # violet-blue drift
    micro = fnoise(603, 1.0)
    hh = h + n1 * 0.05 + micro * 0.03
    save('Dragon_Scales', col, hh, 0.12 + 0.3 * smooth(0.9, 1.0, edge) + n1 * 0.06, 0.28, 6.5)


def dragon_belly():
    """Belly scutes: broad plates across the body, 8 per tile along U (1 stud each), pale blue-lavender."""
    U, V = xx, 1 - yy
    k = (U * 8) % 1.0                                      # 0 at the tail edge of a plate, 1 at its head edge
    n1 = fnoise(611, 2.2); n2 = fnoise(612, 1.3, aniso=(1.0, 6.0))
    prof = smooth(0.0, 0.25, k) * smooth(1.0, 0.8, k)      # rounded plate
    ridge = np.abs(np.sin((V + n1 * 0.02) * np.pi * 2)) ** 8 * 0.0
    h = prof * 0.8 + n2 * 0.1 + ridge
    col = lerp((96, 120, 168), (190, 206, 232), prof * 0.8 + n1 * 0.2)                 # silver-blue plates
    col = lerp(col, (70, 92, 136), (smooth(0.07, 0.0, k) + smooth(0.95, 1.0, k)) * 0.8)   # seams between plates
    col = lerp(col, (248, 252, 255), smooth(0.5, 0.75, k) * smooth(0.95, 0.8, k) * 0.45)
    save('Dragon_Belly', col, h, 0.16 + (1 - prof) * 0.25, 0.55, 5.0)


def dragon_horn():
    """Horns, claws, teeth: ivory with a cold blue tint toward the tips (V = 0 base .. 1 tip on tubes)."""
    V = 1 - yy
    n1 = fnoise(621, 1.3, aniso=(1.0, 8.0)); n2 = fnoise(622, 2.4)
    rings = np.sin((V * 22 + n2 * 1.5) * np.pi * 2) * 0.5 + 0.5
    col = lerp((38, 52, 78), (92, 116, 150), n1 * 0.6 + rings * 0.2)                 # dark steel-blue horn
    col = lerp(col, (150, 196, 236), smooth(0.55, 1.0, V) * 0.7)
    col = lerp(col, (90, 94, 110), smooth(0.7, 1.0, rings) * 0.15)
    save('Dragon_Horn', col, rings * 0.4 + n1 * 0.2, 0.35 + n2 * 0.2, 0.0, 3.0)


def water_flame():
    """Stylised living-water fins / mane / splashes: V runs root (0) -> tip (1) along each plume, U across it.
    Deep blue at the root, bright cyan body, white foam at the tips, flowing streaks along V."""
    U, V = xx, 1 - yy
    s1 = fnoise(631, 1.3, aniso=(1.0, 10.0)); s2 = fnoise(632, 2.2, aniso=(1.0, 4.0)); n = fnoise(633, 2.4)
    t = np.clip(V * 0.85 + (s1 - 0.5) * 0.35 + (n - 0.5) * 0.15, 0, 1)
    col = lerp((12, 60, 150), (30, 150, 225), smooth(0.0, 0.45, t))
    col = lerp(col, (120, 220, 250), smooth(0.4, 0.75, t))
    col = lerp(col, (245, 252, 255), smooth(0.78, 0.95, t))
    streak = smooth(0.7, 0.95, s2) * smooth(0.2, 0.6, V)
    col = lerp(col, (220, 246, 255), streak * 0.5)
    alpha = np.clip(0.45 + 0.35 * smooth(0.3, 0.9, t) + streak * 0.3 + smooth(0.8, 0.95, t) * 0.3, 0, 1)
    save('Water_Flame', col, t * 0.3 + streak * 0.3, 0.06, 0.0, 2.0, alpha=alpha)


def dragon_fin():
    """Solid crystalline fins, mane strands and whiskers: deep blue at the root (V=0) to icy cyan at the edge (V=1),
    fine radiating ribs along V, glassy. Opaque - the creature reads as a solid animal."""
    U, V = xx, 1 - yy
    n1 = fnoise(641, 1.2, aniso=(1.0, 12.0)); n2 = fnoise(642, 2.3)
    ribs = np.abs(np.sin((U * 24 + n1 * 1.4) * np.pi)) ** 6
    col = lerp((10, 44, 120), (34, 130, 214), smooth(0.0, 0.55, V + (n2 - 0.5) * 0.2))
    col = lerp(col, (150, 226, 255), smooth(0.55, 1.0, V))
    col = lerp(col, (6, 30, 90), ribs * 0.45 * (1 - V * 0.6))
    col = lerp(col, (230, 250, 255), smooth(0.93, 1.0, V) * 0.8)
    save('Dragon_Fin', col, ribs * 0.5 + n2 * 0.1, 0.08 + ribs * 0.12, 0.2, 4.0)


def dragon_claw():
    """Claws: polished blue-silver, darker at the base, bright at the tip (V along the claw)."""
    V = 1 - yy
    n1 = fnoise(651, 1.3, aniso=(1.0, 10.0)); n2 = fnoise(652, 2.4)
    col = lerp((70, 86, 110), (210, 222, 236), smooth(0.1, 0.9, V) * 0.8 + n1 * 0.2)
    col = lerp(col, (40, 70, 120), n2 * 0.2)
    save('Dragon_Claw', col, n1 * 0.3, 0.12 + n2 * 0.1, 0.85, 2.0)


def dragon_eye():
    """Narrow glowing eye: intense cyan with a white-hot core (use Material Neon / high emission)."""
    r = np.sqrt((xx - 0.5) ** 2 + (yy - 0.5) ** 2) * 2
    n1 = fnoise(661, 2.0)
    col = lerp((20, 160, 230), (120, 240, 255), smooth(1.0, 0.3, r) * 0.8 + n1 * 0.2)
    col = lerp(col, (245, 255, 255), smooth(0.35, 0.0, r))
    save('Dragon_Eye', col, np.zeros((N, N)), 0.05, 0.0)


# ----------------------------------------------------------------------------------------------- fish
# Fish body sets: U = snout (0) -> tail (1) along the fish, V = back (0) -> belly (1), mirrored on both flanks.

def _scale_net(U, V, rows=34, cols=14):
    """Overlapping-scale net (darker scale edges) for fish flanks."""
    a = U * rows
    b = V * cols + 0.5 * (np.floor(a) % 2)
    fu, fv = a % 1.0, b % 1.0
    d = np.sqrt(((fu - 0.15) * 1.0) ** 2 + ((fv - 0.5) * 1.1) ** 2)
    return smooth(0.48, 0.62, d)


def fish(name, back, side, belly, pattern=None, rough=0.3, metal=0.35, scales=True, seed=700):
    U, V = xx, 1 - yy
    n1 = fnoise(seed, 2.2); n2 = fnoise(seed + 1, 1.4, aniso=(4.0, 1.0))
    col = lerp(back, side, smooth(0.08, 0.5, V + (n1 - 0.5) * 0.08))
    col = lerp(col, belly, smooth(0.55, 0.85, V + (n2 - 0.5) * 0.05))
    h = np.zeros((N, N))
    if scales:
        net = _scale_net(U, V)
        col = lerp(col, np.array(back) * 0.55, net * 0.35 * (1 - smooth(0.6, 0.9, V)))
        col = lerp(col, (255, 255, 255), (1 - net) * 0.06)
        h = 1 - net
    if pattern: col = pattern(U, V, col, n1, n2)
    # gill-plate arc and darker snout
    gill = np.exp(-((U - 0.2 - 0.03 * np.sin((V - 0.5) * 3)) / 0.006) ** 2) * smooth(0.95, 0.2, V)
    col = lerp(col, np.array(back) * 0.45, gill * 0.7)
    col = lerp(col, np.array(back) * 0.7, smooth(0.06, 0.0, U) * 0.6)
    save(name, col, h * 0.5 + n1 * 0.1, rough + (1 - smooth(0.4, 0.8, V)) * 0.1, metal * smooth(0.2, 0.7, V) + 0.05, 2.5)


def fish_fin(name, root, edge, alpha_root=0.95, alpha_edge=0.55, seed=760):
    """Fin membrane: rays along V (root 0 -> edge 1), translucent toward the edge (RGBA)."""
    U, V = xx, 1 - yy
    n1 = fnoise(seed, 1.2, aniso=(1.0, 10.0))
    rays = np.abs(np.sin((U * 22 + n1 * 0.8) * np.pi)) ** 8
    col = lerp(root, edge, smooth(0.0, 1.0, V))
    col = lerp(col, np.array(root) * 0.6, rays * 0.5)
    alpha = np.clip(alpha_root + (alpha_edge - alpha_root) * V + rays * 0.25, 0, 1)
    save(name, col, rays * 0.5, 0.35, 0.0, 2.0, alpha=alpha)


def fish_all():
    def ayu(U, V, col, n1, n2):
        spot = np.exp(-(((U - 0.3) / 0.04) ** 2 + ((V - 0.42) / 0.06) ** 2))
        return lerp(col, (230, 196, 60), spot * 0.9)
    fish('Fish_Ayu', (70, 84, 60), (170, 176, 160), (232, 232, 222), ayu, seed=701)

    def koi(U, V, col, n1, n2):
        blot = smooth(0.6, 0.66, fnoise(711, 2.6) * 0.8 + (1 - V) * 0.3)
        return lerp(col, (224, 70, 30), blot * smooth(0.95, 0.5, V))
    fish('Fish_Koi', (236, 232, 222), (240, 236, 228), (244, 242, 236), koi, rough=0.25, metal=0.15, seed=710)
    fish('Fish_Koi_Gold', (196, 140, 30), (236, 190, 60), (250, 224, 130), None, rough=0.18, metal=0.85, seed=715)

    def tai(U, V, col, n1, n2):
        dots = smooth(0.965, 0.99, fnoise(721, 0.3)) * smooth(0.7, 0.2, V)
        return lerp(col, (90, 170, 240), dots)
    fish('Fish_Tai', (196, 60, 70), (226, 120, 120), (244, 214, 210), tai, rough=0.25, metal=0.4, seed=720)

    def saba(U, V, col, n1, n2):
        w = np.sin((U * 26 + np.sin(V * 20 + U * 8) * 0.9 + n1 * 1.5) * np.pi)
        stripes = smooth(0.4, 0.8, w) * smooth(0.42, 0.25, V)
        return lerp(col, (16, 30, 30), stripes * 0.85)
    fish('Fish_Saba', (40, 110, 110), (150, 180, 180), (236, 240, 238), saba, rough=0.22, metal=0.6, seed=730)
    fish('Fish_Maguro', (18, 28, 64), (90, 106, 130), (206, 214, 222), None, rough=0.25, metal=0.55, scales=False, seed=740)

    def fugu(U, V, col, n1, n2):
        spots = smooth(0.6, 0.66, fnoise(751, 2.8)) * smooth(0.6, 0.3, V)
        blotch = np.exp(-(((U - 0.4) / 0.07) ** 2 + ((V - 0.45) / 0.08) ** 2))
        col = lerp(col, (40, 34, 24), spots * 0.8)
        return lerp(col, (22, 18, 14), blotch * 0.9)
    fish('Fish_Fugu', (120, 112, 70), (170, 160, 110), (244, 242, 232), fugu, rough=0.5, metal=0.05, scales=False, seed=750)
    fish('Fish_Unagi', (26, 32, 22), (70, 76, 50), (200, 186, 120), None, rough=0.2, metal=0.1, scales=False, seed=760)

    fish_fin('Fish_Fin', (170, 172, 166), (226, 226, 218), seed=770)
    fish_fin('Fish_Fin_Red', (190, 60, 60), (240, 150, 140), seed=771)
    fish_fin('Fish_Fin_Yellow', (200, 170, 40), (245, 220, 110), alpha_edge=0.8, seed=772)
    fish_fin('Fish_Fin_Gold', (210, 150, 40), (250, 220, 140), alpha_edge=0.75, seed=773)
    r = np.sqrt((xx - 0.5) ** 2 + (yy - 0.5) ** 2) * 2
    col = lerp((6, 6, 8), (40, 34, 24), smooth(0.6, 1.2, r) + fnoise(781, 2.0) * 0.2)          # glossy dark eye
    save('Fish_Eye', col, np.zeros((N, N)), 0.03, 0.2)


# ----------------------------------------------------------------------------------------------- phoenix
def _feather_scales(R=16, C=16, elong=1.3):
    """Overlapping rounded contour feathers (same layout as the dragon scales, softer and longer).
    Returns height, edge distance (0 centre .. 1 rim) and a per-feather random value."""
    U, V = xx, 1 - yy
    h = np.zeros((N, N)); edge = np.ones((N, N)); cid = np.zeros((N, N))
    rad = 0.78 / C * 1.3
    for r in range(R):
        cu = (r + 0.5) / R
        du = (U - cu + 0.5) % 1.0 - 0.5
        off = 0.5 * (r % 2)
        cv = np.floor(V * C - off + 0.5)
        dv = (V * C - off - cv) / C
        du_s = du * (R / C) / elong
        d = np.sqrt(du_s ** 2 + dv ** 2) / rad
        m = (d < 1.0) & (du < 0.35 / R)
        h[m] = np.sqrt(1 - d[m] ** 2) * 0.7 + 0.3 * (-du[m] * R)
        edge[m] = d[m]
        cid[m] = (r * 131 + cv[m] * 17) % 97
    return h, edge, (np.sin(cid * 12.9898) * 43758.5453) % 1.0


def phoenix_body_sets():
    U, V = xx, 1 - yy
    h, edge, var = _feather_scales()
    barbs = np.abs(np.sin((U * 16 * 9 + V * 16 * 3) * np.pi)) ** 4
    n1 = fnoise(801, 2.2)
    for name, c0, c1, rim, seam in (('Phoenix_Body', (150, 18, 20), (206, 44, 26), (255, 150, 40), (60, 6, 8)),
                                    ('Phoenix_Breast', (214, 100, 20), (246, 160, 40), (255, 226, 120), (120, 40, 8))):
        col = lerp(c0, c1, var * 0.6 + n1 * 0.4)
        col = lerp(col, rim, smooth(0.55, 0.95, edge) * 0.85)               # glowing feather tips
        col = lerp(col, seam, smooth(0.96, 1.0, edge))
        col = lerp(col, np.array(c0) * 0.7, barbs * 0.15)
        save(name, col, h * 0.8 + barbs * 0.08, 0.45 - smooth(0.6, 1.0, edge) * 0.15, 0.1, 4.0)


def phoenix_feather():
    """Flight feathers: U across the vane (0..1, rachis at 0.5), V root (0) -> tip (1).
    Crimson root -> orange -> gold -> white-hot tip, with diagonal barbs and a pale shaft."""
    U, V = xx, 1 - yy
    n1 = fnoise(811, 1.6, aniso=(1.0, 6.0))
    a = np.abs(U - 0.5) * 2
    barbs = np.abs(np.sin((V * 60 - a * 18 + n1 * 2) * np.pi)) ** 3
    col = lerp((140, 12, 18), (226, 60, 20), smooth(0.0, 0.4, V))
    col = lerp(col, (252, 150, 30), smooth(0.35, 0.7, V))
    col = lerp(col, (255, 222, 110), smooth(0.68, 0.92, V))
    col = lerp(col, (255, 248, 220), smooth(0.9, 1.0, V) * 0.8)
    col = lerp(col, np.array((90, 8, 10)), barbs * 0.22 * (1 - V * 0.5))
    shaft = smooth(0.035, 0.0, np.abs(U - 0.5))
    col = lerp(col, (255, 236, 190), shaft * 0.8)
    edge = smooth(0.85, 1.0, a)
    col = lerp(col, (255, 200, 90), edge * 0.5)
    save('Phoenix_Feather', col, barbs * 0.3 + shaft * 0.5, 0.4, 0.05, 3.0)


def phoenix_plume():
    """Tail streamer: slender gold-orange shaft that opens into a peacock-style eye spot near the tip (V ~ 0.86)."""
    U, V = xx, 1 - yy
    a = np.abs(U - 0.5) * 2
    n1 = fnoise(821, 1.5, aniso=(1.0, 8.0))
    col = lerp((180, 30, 20), (246, 130, 30), smooth(0.0, 0.6, V))
    col = lerp(col, (255, 200, 70), smooth(0.6, 0.8, V))
    r = np.sqrt((a * 0.55) ** 2 + ((V - 0.86) / 0.1) ** 2)
    col = lerp(col, (255, 236, 150), smooth(1.0, 0.8, r))
    col = lerp(col, (200, 40, 30), smooth(0.75, 0.55, r))
    col = lerp(col, (30, 150, 170), smooth(0.5, 0.35, r))                  # teal eye
    col = lerp(col, (20, 20, 60), smooth(0.28, 0.15, r))
    barbs = np.abs(np.sin((V * 70 - a * 20 + n1 * 2) * np.pi)) ** 3
    col = lerp(col, np.array((110, 20, 10)), barbs * 0.15)
    shaft = smooth(0.03, 0.0, np.abs(U - 0.5))
    col = lerp(col, (255, 230, 180), shaft * 0.7)
    save('Phoenix_Plume', col, barbs * 0.3 + shaft * 0.4, 0.35, 0.1, 3.0)


def phoenix_beak():
    """Beak and talons: polished gold-amber horn, dark at the base, bright at the tip (V along)."""
    V = 1 - yy
    n1 = fnoise(831, 1.3, aniso=(1.0, 8.0)); n2 = fnoise(832, 2.3)
    col = lerp((150, 80, 20), (250, 196, 70), smooth(0.0, 0.9, V) * 0.8 + n1 * 0.2)
    col = lerp(col, (255, 236, 170), smooth(0.85, 1.0, V) * 0.6)
    save('Phoenix_Beak', col, n1 * 0.3, 0.2 + n2 * 0.1, 0.7, 2.0)


def fire_flame():
    """Living fire plumes (translucent): V root (0) -> tip (1): deep red -> orange -> yellow-white, streaks along V."""
    U, V = xx, 1 - yy
    s1 = fnoise(841, 1.3, aniso=(1.0, 10.0)); s2 = fnoise(842, 2.2, aniso=(1.0, 4.0)); n = fnoise(843, 2.4)
    t = np.clip(V * 0.85 + (s1 - 0.5) * 0.35 + (n - 0.5) * 0.15, 0, 1)
    col = lerp((150, 14, 6), (240, 70, 10), smooth(0.0, 0.4, t))
    col = lerp(col, (255, 160, 30), smooth(0.35, 0.7, t))
    col = lerp(col, (255, 246, 190), smooth(0.72, 0.95, t))
    streak = smooth(0.7, 0.95, s2) * smooth(0.2, 0.6, V)
    col = lerp(col, (255, 230, 150), streak * 0.5)
    alpha = np.clip(0.55 + 0.3 * smooth(0.2, 0.8, t) + streak * 0.3 - smooth(0.9, 1.0, V) * 0.4, 0, 1)
    save('Fire_Flame', col, t * 0.3 + streak * 0.3, 0.3, 0.0, 2.0, alpha=alpha)


def phoenix_all():
    phoenix_body_sets(); phoenix_feather(); phoenix_plume(); phoenix_beak(); fire_flame()


def mech_plate():
    """Riveted war-machine iron: 4x4 panels per tile with seams, rivet rows along the seams, scratches, rust
    streaks running down (V), lighter worn edges. Tile = 8 studs."""
    U, V = xx, 1 - yy
    P = 4
    fu, fv = (U * P) % 1.0, (V * P) % 1.0
    du = np.minimum(fu, 1 - fu); dv = np.minimum(fv, 1 - fv)
    seam = smooth(0.012, 0.0, np.minimum(du, dv))
    edge = smooth(0.05, 0.015, np.minimum(du, dv)) * (1 - seam)
    # rivets: every 1/8 panel along both seam directions, 0.03 panel in from the seam
    ru = ((U * P * 8) % 1.0 - 0.5) / 8; rv = ((V * P * 8) % 1.0 - 0.5) / 8
    rivet = np.maximum(smooth(0.011, 0.006, np.sqrt(ru ** 2 + (dv - 0.045) ** 2)),
                       smooth(0.011, 0.006, np.sqrt(rv ** 2 + (du - 0.045) ** 2)))
    n1 = fnoise(901, 2.2); n2 = fnoise(902, 1.1, aniso=(1.0, 12.0)); n3 = fnoise(903, 0.9, aniso=(14.0, 1.0))
    pid = (np.floor(U * P) * 7 + np.floor(V * P) * 3) % 5 / 5.0
    col = lerp((70, 70, 76), (104, 102, 104), n1 * 0.7 + pid * 0.3)
    rust = smooth(0.62, 0.8, n2) * smooth(0.3, 0.7, n1)
    col = lerp(col, (96, 52, 30), rust * 0.55)
    scratch = smooth(0.8, 0.9, n3) * 0.35
    col = lerp(col, (130, 128, 128), scratch + edge * 0.35)
    col = lerp(col, (18, 18, 20), seam * 0.9)
    col = lerp(col, (110, 106, 102), rivet * 0.6)
    h = rivet * 1.0 - seam * 0.8 + n1 * 0.05
    save('Mech_Plate', col, h, 0.42 + rust * 0.3 - edge * 0.15 - scratch * 0.2, 0.85 - rust * 0.6, 6.0)


def _panel_lines(seed, P=4):
    """Hard-surface panelling for anime-style mech armour: irregular panel seams, small access hatches,
    screw dots and occasional caution stripes / decal blocks. Returns (seam, detail, caution) masks."""
    U, V = xx, 1 - yy
    r = rng(seed)
    seam = np.zeros((N, N))
    # main grid + randomly offset secondary cuts
    for k in range(P):
        for coord, other in ((U, V), (V, U)):
            pos = (k + 0.5 + r.uniform(-0.35, 0.35)) / P
            span0, span1 = sorted(r.uniform(0, 1, 2))
            if r.random() < 0.6: span0, span1 = 0.0, 1.0
            m = (other >= span0) & (other <= span1)
            seam = np.maximum(seam, smooth(0.0022, 0.0, np.abs(coord - pos)) * m)
    detail = np.zeros((N, N)); caution = np.zeros((N, N))
    for k in range(10):                                      # hatches (rectangles), screw dots, caution strips
        cx, cy = r.uniform(0.05, 0.95, 2); w, h = r.uniform(0.03, 0.09), r.uniform(0.02, 0.06)
        box = (np.abs(U - cx) < w) & (np.abs(V - cy) < h)
        edge = box & ((np.abs(np.abs(U - cx) - w) < 0.002) | (np.abs(np.abs(V - cy) - h) < 0.002))
        seam = np.maximum(seam, edge * 0.8)
        for sx in (-1, 1):
            for sy in (-1, 1):
                d = np.sqrt((U - cx - sx * (w - 0.008)) ** 2 + (V - cy - sy * (h - 0.008)) ** 2)
                detail = np.maximum(detail, smooth(0.004, 0.002, d))
        if k < 3:
            cx, cy = r.uniform(0.1, 0.9, 2)
            strip = (np.abs(U - cx) < 0.06) & (np.abs(V - cy) < 0.008)
            caution = np.maximum(caution, strip * (np.sin((U + V) * 400) > 0))
    return seam, detail, caution


def mech_panel(name, base, line, seed, rough=0.35, metal=0.15, caution_col=(200, 40, 40)):
    seam, detail, caution = _panel_lines(seed)
    n1 = fnoise(seed + 5, 2.3); n2 = fnoise(seed + 6, 1.2)
    col = lerp(base, np.array(base) * 0.92, n1 * 0.6)
    col = lerp(col, line, seam * 0.85)
    col = lerp(col, np.array(line) * 1.1, detail * 0.7)
    col = lerp(col, caution_col, caution * 0.9)
    col = lerp(col, np.array(base) * 0.8, smooth(0.75, 0.95, n2) * 0.12)          # subtle grime
    h = -seam * 0.9 + detail * 0.5 + n1 * 0.02
    save(name, col, h, rough + n1 * 0.08, metal, 5.0)


def mech_frame():
    """Inner frame: dark gunmetal with machined grooves and bolt heads."""
    U, V = xx, 1 - yy
    grooves = np.abs(np.sin(V * 48 * np.pi)) ** 12
    n1 = fnoise(951, 2.2)
    bolts = smooth(0.012, 0.006, np.sqrt(((U * 8) % 1 - 0.5) ** 2 / 64 + ((V * 8) % 1 - 0.5) ** 2 / 64))
    col = lerp((44, 46, 52), (64, 66, 72), n1)
    col = lerp(col, (22, 22, 26), grooves * 0.7)
    col = lerp(col, (120, 122, 126), bolts)
    save('Mech_Frame', col, bolts - grooves * 0.5, 0.35 + n1 * 0.1, 0.85, 4.0)


def mech_vent():
    """Yellow intake vents: horizontal slats with dark gaps (V across the slats)."""
    U, V = xx, 1 - yy
    k = (V * 10) % 1.0
    slat = smooth(0.15, 0.3, k) * smooth(0.85, 0.7, k)
    col = lerp((30, 26, 16), (236, 186, 40), slat)
    col = lerp(col, (255, 222, 110), smooth(0.4, 0.5, k) * smooth(0.6, 0.5, k) * 0.5)
    save('Mech_Vent', col, slat, 0.3, 0.3, 4.0)


def mech_all():
    mech_panel('Mech_White', (232, 234, 236), (150, 156, 164), 961, caution_col=(170, 172, 180))
    mech_panel('Mech_Blue', (40, 72, 160), (20, 34, 80), 962, caution_col=(240, 240, 240))
    mech_panel('Mech_Red', (200, 38, 48), (110, 18, 24), 963, caution_col=(250, 250, 250))
    mech_panel('Mech_Grey', (120, 126, 136), (70, 74, 82), 964)
    mech_frame(); mech_vent()


if __name__ == '__main__':
    which = sys.argv[1:] or ['roof_tile', 'timber_dark', 'timber_light', 'plaster', 'granite', 'fitted_stone',
                             'cobble', 'planks', 'gold', 'iron', 'shoji', 'uv_check']
    for w in which:
        if w == 'timber_dark':
            timber('Timber_Dark', (34, 24, 18), (80, 58, 42), 101, 0.62)
        elif w == 'timber_light':
            timber('Timber_Light', (128, 96, 64), (196, 160, 116), 111, 0.68)
        elif w == 'glows':
            glow('Glow_Red', (230, 40, 40), 301); glow('Glow_Blue', (150, 200, 255), 302)
            glow('Glow_Amber', (255, 150, 40), 303); glow('Glow_Yellow', (255, 220, 60), 304)
        elif w == 'cloths':
            cloth('Cloth_White', (236, 232, 222), 121); cloth('Cloth_Navy', (30, 44, 82), 122)
            cloth('Cloth_Indigo', (44, 62, 108), 123); cloth('Cloth_Crimson', (140, 32, 34), 124)
            cloth('Cloth_Ochre', (176, 124, 46), 125)
        else:
            globals()[w]()
