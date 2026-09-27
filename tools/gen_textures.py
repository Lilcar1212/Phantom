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


def save(name, color, height, rough, metal, nstrength=4.0, normal=None):
    d = os.path.join(OUT, name); os.makedirs(d, exist_ok=True)
    c = np.clip(color, 0, 255).astype(np.uint8)
    Image.fromarray(c, 'RGB').save(os.path.join(d, f'HO_T_{name}_Color.png'), optimize=True)
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


if __name__ == '__main__':
    which = sys.argv[1:] or ['roof_tile', 'timber_dark', 'timber_light', 'plaster', 'granite', 'fitted_stone',
                             'cobble', 'planks', 'gold', 'iron', 'shoji', 'uv_check']
    for w in which:
        if w == 'timber_dark':
            timber('Timber_Dark', (34, 24, 18), (80, 58, 42), 101, 0.62)
        elif w == 'timber_light':
            timber('Timber_Light', (128, 96, 64), (196, 160, 116), 111, 0.68)
        elif w == 'cloths':
            cloth('Cloth_White', (236, 232, 222), 121); cloth('Cloth_Navy', (30, 44, 82), 122)
            cloth('Cloth_Indigo', (44, 62, 108), 123); cloth('Cloth_Crimson', (140, 32, 34), 124)
            cloth('Cloth_Ochre', (176, 124, 46), 125)
        else:
            globals()[w]()
