"""Phase 3 flipbooks: 1024x1024 RGBA sprite sheets (8x8 = 64 frames of 128 px, or 4x4 = 16 frames of 256 px).
Greyscale/white sheets are meant to be tinted in Roblox (ParticleEmitter.Color); fire, fireball, embers and the
explosion are pre-coloured. Looping sheets loop seamlessly (noise scrolls exactly one period per cycle).
Frames read left-to-right, top-to-bottom (Roblox ParticleEmitter.FlipbookLayout Grid8x8 / Grid4x4)."""
import os, math, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'Phase3', 'VFX', 'Flipbooks')
os.makedirs(OUT, exist_ok=True)
SHEET = 1024


def tile_noise(n, seed, beta=2.0, aniso=(1.0, 1.0)):
    r = np.random.default_rng(seed)
    w = r.standard_normal((n, n))
    fy = np.fft.fftfreq(n)[:, None] * n * aniso[1]
    fx = np.fft.fftfreq(n)[None, :] * n * aniso[0]
    f = np.sqrt(fx ** 2 + fy ** 2); f[0, 0] = 1
    amp = 1 / f ** (beta / 2); amp[0, 0] = 0
    o = np.real(np.fft.ifft2(np.fft.fft2(w) * amp))
    o -= o.min(); o /= o.max()
    return o


def sample(noise, x, y):
    """Bilinear sample of a tileable noise at float pixel coords (wraps)."""
    n = noise.shape[0]
    x = np.mod(x, n); y = np.mod(y, n)
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    fx, fy = x - x0, y - y0
    x1 = (x0 + 1) % n; y1 = (y0 + 1) % n
    return (noise[y0, x0] * (1 - fx) * (1 - fy) + noise[y0, x1] * fx * (1 - fy) + noise[y1, x0] * (1 - fx) * fy + noise[y1, x1] * fx * fy)


def smooth(e0, e1, x):
    d = np.asarray(e1 - e0, dtype=float)
    d = np.where(np.abs(d) < 1e-6, 1e-6, d)          # guard e0 == e1 (would give NaN pixels)
    t = np.clip((x - e0) / d, 0, 1)
    return t * t * (3 - 2 * t)


def ramp(t, stops):
    """Colour ramp: stops = [(pos, (r,g,b)), ...] -> RGB float array."""
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,))
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = (t >= p0) & (t <= p1)
        k = ((t - p0) / max(1e-6, p1 - p0))[m][:, None]
        out[m] = np.array(c0) * (1 - k) + np.array(c1) * k
    return out


FIRE = [(0.0, (0.25, 0.02, 0.0)), (0.25, (0.85, 0.18, 0.02)), (0.5, (1.0, 0.5, 0.08)), (0.75, (1.0, 0.82, 0.35)), (1.0, (1.0, 1.0, 0.9))]


def sheet(name, grid, frame_fn, loop, tint, desc):
    S = SHEET // grid
    img = np.zeros((SHEET, SHEET, 4))
    n = grid * grid
    for i in range(n):
        rgba = frame_fn(i, n, S)
        r, c = divmod(i, grid)
        img[r * S:(r + 1) * S, c * S:(c + 1) * S] = rgba
    img = np.nan_to_num(np.clip(img, 0, 1))
    Image.fromarray((img * 255 + 0.5).astype(np.uint8), 'RGBA').save(os.path.join(OUT, f'HO_VFX_{name}.png'), optimize=True)
    META.append(dict(name=f'HO_VFX_{name}', file=f'assets/Phase3/VFX/Flipbooks/HO_VFX_{name}.png', layout=f'Grid{grid}x{grid}',
                     frames=n, loop=loop, tint=tint, description=desc))
    print('wrote', name)


META = []


def coords(S):
    yy, xx = np.mgrid[0:S, 0:S] / S
    return xx - 0.5, 0.5 - yy        # u right, v up, centred


def rgba(rgb, a):
    return np.concatenate([rgb, a[..., None]], -1)


def grey(v, a):
    return rgba(np.repeat(v[..., None], 3, -1), a)


N256 = tile_noise(256, 1, 2.2)
N256b = tile_noise(256, 2, 1.6)
N256c = tile_noise(256, 3, 2.6)


# --------------------------------------------------------------------------------------------- fire
def fire_loop(i, n, S):
    u, v = coords(S)
    t = i / n
    vy = v + 0.5                                   # 0 bottom .. 1 top
    sx = (u + 0.5) * 256; sy = (1 - vy) * 256
    n1 = sample(N256, sx * 0.9, sy * 0.9 + t * 256)          # scrolls up exactly one period per loop
    n2 = sample(N256b, sx * 1.7 + 30, sy * 1.7 + t * 512)
    turb = n1 * 0.65 + n2 * 0.35
    width = 0.3 * np.clip(1 - vy, 0, 1) ** 0.85 * smooth(0.0, 0.22, vy) ** 0.45 + 0.02   # rounded base, widest low, tapering tip
    dist = np.abs(u + (turb - 0.5) * 0.4 * vy) / np.maximum(width, 1e-3)
    tongues = smooth(0.25, 0.75, turb + (0.55 - vy) * 0.9)          # licking flame tongues breaking off at the top
    body = smooth(1.0, 0.3, dist) * tongues * smooth(0.0, 0.06, vy)
    heat = np.clip(body * (0.55 + 0.7 * turb) * (1.2 - vy * 0.7), 0, 1)
    a = smooth(0.04, 0.4, heat)
    return rgba(ramp(heat, FIRE), a)


def fire_burst(i, n, S):
    u, v = coords(S)
    t = i / (n - 1)
    r = np.sqrt(u * u + v * v)
    ang = np.arctan2(v, u)
    R = 0.08 + 0.36 * t ** 0.45
    sx = (ang / (2 * np.pi) + 0.5) * 256; sy = r * 256 * 2.2 - t * 180
    turb = sample(N256, sx * 2, sy) * 0.6 + sample(N256b, sx * 4, sy * 1.5) * 0.4
    edge = smooth(R * (1.0 + (turb - 0.5) * 0.7), R * 0.4, r)
    fade = (1 - t) ** 1.2
    heat = np.clip(edge * (0.5 + 0.7 * turb) * (0.35 + 0.9 * fade) * (1.2 - r / max(R, 1e-3) * 0.6), 0, 1)
    smoke = edge * smooth(0.3, 0.9, t) * 0.6
    rgb = ramp(heat, FIRE) * (1 - smoke[..., None] * 0.7) + np.array((0.12, 0.1, 0.09)) * smoke[..., None] * 0.7
    a = np.clip(smooth(0.03, 0.35, heat) + smoke * 0.8, 0, 1) * smooth(1.0, 0.85, t)
    return rgba(rgb, a)


def fireball_core(i, n, S):
    u, v = coords(S)
    t = i / n
    r = np.sqrt(u * u + v * v) * 2
    ang = np.arctan2(v, u) / (2 * np.pi) + 0.5
    sx = ang * 256 + t * 256; sy = r * 160
    turb = sample(N256, sx, sy - t * 128) * 0.6 + sample(N256c, sx * 2, sy * 2 + t * 256) * 0.4
    core = smooth(0.95 + (turb - 0.5) * 0.4, 0.2, r)
    heat = np.clip(core * (0.7 + 0.5 * turb), 0, 1)
    return rgba(ramp(heat, FIRE), smooth(0.02, 0.3, heat))


def embers(i, n, S):
    u, v = coords(S)
    t = i / n
    r = np.sqrt(u * u + (v * 1.2) ** 2)
    flick = 0.65 + 0.35 * math.sin(t * 2 * math.pi * 2) * math.sin(t * 2 * math.pi * 3 + 1)
    core = smooth(0.08, 0.0, r) * flick
    glow = smooth(0.35, 0.0, r) ** 2 * 0.6 * flick
    heat = np.clip(core + glow * 0.7, 0, 1)
    return rgba(ramp(heat * 0.9 + 0.1 * core, FIRE), np.clip(core + glow, 0, 1))


# --------------------------------------------------------------------------------------------- smoke / dust
def puff(i, n, S, dark=False, dust=False):
    u, v = coords(S)
    t = i / (n - 1)
    if dust:
        v = (v + 0.3) * 1.8                          # flattened, sits low
    r = np.sqrt(u * u + v * v)
    R = (0.2 + 0.26 * t ** 0.5) * (1.1 if dark else 1.0)
    ang = np.arctan2(v, u) / (2 * np.pi) + 0.5
    turb = sample(N256b, (u + 0.5) * 256 * 1.3 + t * 40, (v + 0.5) * 256 * 1.3 - t * 60) * 0.6 + sample(N256, ang * 256, r * 200 - t * 90) * 0.4
    dens = smooth(R * (1.05 + (turb - 0.5) * 0.8), R * 0.2, r)
    fade = (1 - t) ** (0.8 if dark else 1.3)
    a = np.clip(dens * (0.7 + 0.7 * turb) * fade * (1.6 if dark else 1.35), 0, 1)
    shade = (0.35 + 0.65 * turb) * (0.45 if dark else 1.0) * (0.85 + 0.15 * v)
    return grey(np.clip(shade, 0, 1), a)


# --------------------------------------------------------------------------------------------- explosion
def explosion(i, n, S):
    u, v = coords(S)
    t = i / (n - 1)
    r = np.sqrt(u * u + v * v)
    ang = np.arctan2(v, u) / (2 * np.pi) + 0.5
    R = 0.1 + 0.38 * t ** 0.35
    turb = sample(N256, ang * 256 * 2, r * 220 - t * 160) * 0.55 + sample(N256b, (u + 0.5) * 300, (v + 0.5) * 300 - t * 100) * 0.45
    ball = smooth(R * (1.0 + (turb - 0.5) * 0.6), R * 0.3, r)
    flash = smooth(0.25, 0.0, t) * smooth(0.5 * (1 - t), 0.0, r)
    heat = np.clip(ball * (0.55 + 0.6 * turb) * (1.25 - t * 1.4) + flash * 1.5, 0, 1)
    smoke_amt = smooth(0.15, 0.7, t)
    smoke_col = np.array((0.16, 0.14, 0.13)) * (0.6 + 0.6 * turb[..., None])
    rgb = ramp(heat, FIRE) * (1 - smoke_amt * (1 - heat[..., None])) + smoke_col * smoke_amt * (1 - heat[..., None])
    a = np.clip(ball * (0.5 + 0.7 * turb) * (1 - smooth(0.7, 1.0, t)) + flash, 0, 1)
    return rgba(np.clip(rgb, 0, 1), a)


# --------------------------------------------------------------------------------------------- particles via PIL
def pil_frame(S, draw_fn, blur=0.0, ss=2):
    im = Image.new('RGBA', (S * ss, S * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    draw_fn(d, S * ss)
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur * ss))
    im = im.resize((S, S), Image.LANCZOS)
    a = np.asarray(im).astype(float) / 255
    return a


def splash(i, n, S):
    t = i / (n - 1)
    rng = np.random.default_rng(5)
    drops = rng.random((46, 4))
    def draw(d, W):
        # crown sheet
        g = 9.0
        for k in range(46):
            ang = math.pi * (0.1 + 0.8 * drops[k, 0])
            sp = 0.5 + 0.7 * drops[k, 1]
            x = 0.5 + math.cos(ang) * sp * t * 0.55
            y = 0.85 - (math.sin(ang) * sp * t * 1.3 - 0.5 * g * 0.18 * t * t)
            rad = (0.012 + 0.02 * drops[k, 2]) * (1 - 0.6 * t) * W
            if 0 < y < 1:
                d.ellipse((x * W - rad, y * W - rad * 1.3, x * W + rad, y * W + rad * 1.3), fill=(255, 255, 255, int(235 * (1 - t ** 2))))
        h = 0.5 * math.sin(math.pi * min(1, t * 1.6)) * W
        d.polygon([(0.44 * W, 0.86 * W), (0.56 * W, 0.86 * W), (0.52 * W, 0.86 * W - h), (0.48 * W, 0.86 * W - h)], fill=(255, 255, 255, int(220 * (1 - t))))
        d.ellipse((0.2 * W, 0.8 * W, 0.8 * W, 0.92 * W), outline=(255, 255, 255, int(200 * (1 - t))), width=int(0.02 * W))
    return pil_frame(S, draw, blur=0.6)


def spray(i, n, S):
    t = i / n
    rng = np.random.default_rng(6)
    pts = rng.random((120, 3))
    def draw(d, W):
        for k in range(120):
            life = (pts[k, 0] + t) % 1.0
            ang = -math.pi / 2 + (pts[k, 1] - 0.5) * 0.9
            x = 0.5 + math.cos(ang) * life * 0.45
            y = 0.95 + math.sin(ang) * life * 0.9 + 0.35 * life * life
            rad = (0.006 + 0.01 * pts[k, 2]) * W * (1 - life * 0.5)
            d.ellipse((x * W - rad, y * W - rad, x * W + rad, y * W + rad), fill=(255, 255, 255, int(200 * (1 - life))))
    return pil_frame(S, draw, blur=0.8)


def droplets(i, n, S):
    rng = np.random.default_rng(100 + i)
    def draw(d, W):
        stretch = 1.0 + rng.random() * 1.6
        rad = W * (0.12 + rng.random() * 0.08)
        cx, cy = W / 2, W * 0.58
        d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=(255, 255, 255, 230))
        d.polygon([(cx - rad * 0.7, cy - rad * 0.6), (cx + rad * 0.7, cy - rad * 0.6), (cx, cy - rad * stretch * 1.8)], fill=(255, 255, 255, 230))
        d.ellipse((cx - rad * 0.45, cy - rad * 0.55, cx - rad * 0.1, cy - rad * 0.15), fill=(255, 255, 255, 255))
    return pil_frame(S, draw, blur=0.5)


def ripple(i, n, S):
    u, v = coords(S)
    t = i / (n - 1)
    r = np.sqrt(u * u + v * v) * 2
    a = np.zeros_like(r)
    for k, dly in enumerate((0.0, 0.18, 0.36)):
        tt = t - dly
        if tt <= 0: continue
        R = tt * 0.95
        w = 0.025 + 0.03 * tt
        a += np.exp(-((r - R) / w) ** 2) * (1 - tt) ** 1.5 * (1 - 0.25 * k)
    return grey(np.ones_like(r), np.clip(a, 0, 1))


def mist(i, n, S):
    u, v = coords(S)
    t = i / n
    x = (u + 0.5) * 256; y = (v + 0.5) * 256
    m = sample(N256b, x + t * 256, y) * 0.6 + sample(N256, x * 0.7 - t * 256, y * 0.7 + 50) * 0.4
    r = np.sqrt(u * u + v * v) * 2
    a = smooth(0.35, 0.85, m) * smooth(1.0, 0.4, r) * 0.55
    return grey(np.ones_like(u) * 0.95, a)


# --------------------------------------------------------------------------------------------- energy
def bolt_points(rng, x0, y0, x1, y1, depth, disp):
    if depth == 0:
        return [(x0, y0), (x1, y1)]
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    off = (rng.random() - 0.5) * disp * L
    mx += -dy / L * off; my += dx / L * off
    return bolt_points(rng, x0, y0, mx, my, depth - 1, disp)[:-1] + bolt_points(rng, mx, my, x1, y1, depth - 1, disp)


def lightning(i, n, S):
    rng = np.random.default_rng(300 + i)
    def draw(d, W):
        pts = bolt_points(rng, 0.02, 0.5, 0.98, 0.5 + (rng.random() - 0.5) * 0.2, 6, 0.55)
        P = [(x * W, y * W) for x, y in pts]
        d.line(P, fill=(255, 255, 255, 90), width=int(0.05 * W))
        d.line(P, fill=(255, 255, 255, 170), width=int(0.022 * W))
        d.line(P, fill=(255, 255, 255, 255), width=max(1, int(0.008 * W)))
        for _ in range(3):
            k = rng.integers(2, len(pts) - 2)
            bx, by = pts[k]
            br = bolt_points(rng, bx, by, bx + (rng.random() - 0.3) * 0.3, by + (rng.random() - 0.5) * 0.4, 4, 0.6)
            d.line([(x * W, y * W) for x, y in br], fill=(255, 255, 255, 200), width=max(1, int(0.006 * W)))
    return pil_frame(S, draw, blur=0.3)


def crackle(i, n, S):
    rng = np.random.default_rng(400 + i)
    def draw(d, W):
        for _ in range(5):
            ang = rng.random() * 2 * math.pi
            L = 0.15 + rng.random() * 0.3
            pts = bolt_points(rng, 0.5, 0.5, 0.5 + math.cos(ang) * L, 0.5 + math.sin(ang) * L, 4, 0.7)
            d.line([(x * W, y * W) for x, y in pts], fill=(255, 255, 255, 230), width=max(1, int(0.01 * W)))
        d.ellipse((0.44 * W, 0.44 * W, 0.56 * W, 0.56 * W), fill=(255, 255, 255, 200))
    a = pil_frame(S, draw, blur=0.4)
    glow = pil_frame(S, draw, blur=4.0)
    a[..., 3] = np.clip(a[..., 3] + glow[..., 3] * 0.8, 0, 1)
    return a


def magic_glow(i, n, S):
    u, v = coords(S)
    t = i / n
    r = np.sqrt(u * u + v * v) * 2
    ang = np.arctan2(v, u)
    pulse = 0.8 + 0.2 * math.sin(t * 2 * math.pi)
    core = np.exp(-(r / (0.35 * pulse)) ** 2)
    ring = np.exp(-((r - 0.62) / 0.03) ** 2) * (0.6 + 0.4 * np.cos(ang * 12 + t * 2 * math.pi))
    ticks = np.exp(-((r - 0.75) / 0.02) ** 2) * (np.cos(ang * 6 - t * 2 * math.pi) > 0.7)
    a = np.clip(core + ring * 0.7 + ticks * 0.8, 0, 1)
    return grey(np.ones_like(r), a)


def sparkle(i, n, S):
    u, v = coords(S)
    t = i / n
    tw = 0.5 + 0.5 * math.sin(t * 2 * math.pi)
    s = 0.6 + 0.4 * tw
    star = np.exp(-(np.abs(u) / 0.012) ** 1.2) * np.exp(-(np.abs(v) / (0.3 * s)) ** 2) + np.exp(-(np.abs(v) / 0.012) ** 1.2) * np.exp(-(np.abs(u) / (0.3 * s)) ** 2)
    diag = (np.exp(-(np.abs(u - v) / 0.01)) + np.exp(-(np.abs(u + v) / 0.01))) * np.exp(-((u * u + v * v) / (0.02 * s)))
    core = np.exp(-((u * u + v * v) / (0.002 + 0.004 * tw)))
    a = np.clip(star + diag * 0.5 + core, 0, 1)
    return grey(np.ones_like(u), a)


# --------------------------------------------------------------------------------------------- impact
def hit_spark(i, n, S):
    t = i / (n - 1)
    rng = np.random.default_rng(7)
    rays = rng.random((14, 3))
    def draw(d, W):
        c = W / 2
        for k in range(14):
            ang = 2 * math.pi * (k / 14 + rays[k, 0] * 0.05)
            L0 = (0.05 + 0.25 * t) * W
            L1 = L0 + (0.12 + 0.25 * rays[k, 1]) * W * (1 - t)
            w = max(1, int((0.02 + 0.02 * rays[k, 2]) * W * (1 - t)))
            d.line([(c + math.cos(ang) * L0, c + math.sin(ang) * L0), (c + math.cos(ang) * L1, c + math.sin(ang) * L1)], fill=(255, 255, 255, 255), width=w)
        R = (0.18 * (1 - t) + 0.02) * W
        d.ellipse((c - R, c - R, c + R, c + R), fill=(255, 255, 255, int(255 * (1 - t) ** 2)))
    a = pil_frame(S, draw, blur=0.4)
    glow = pil_frame(S, draw, blur=3.0)
    a[..., 3] = np.clip(a[..., 3] + glow[..., 3] * 0.6, 0, 1)
    return a


def shockwave(i, n, S):
    u, v = coords(S)
    t = i / (n - 1)
    r = np.sqrt(u * u + v * v) * 2
    R = 0.08 + 0.9 * t ** 0.6
    w = 0.03 + 0.07 * (1 - t)
    ring = np.exp(-((r - R) / w) ** 2)
    inner = smooth(R, R * 0.6, r) * 0.25 * (1 - t)
    a = np.clip((ring + inner) * (1 - t) ** 0.8, 0, 1)
    return grey(np.ones_like(r), a)


def crack_lines(rng, x, y, ang, L, depth, out):
    pts = [(x, y)]
    for _ in range(6):
        ang += (rng.random() - 0.5) * 0.9
        x += math.cos(ang) * L / 6; y += math.sin(ang) * L / 6
        pts.append((x, y))
    out.append((pts, depth))
    if depth > 0:
        for _ in range(2):
            k = rng.integers(2, 6)
            crack_lines(rng, pts[k][0], pts[k][1], ang + (rng.random() - 0.5) * 1.6, L * 0.55, depth - 1, out)


def ground_crack(i, n, S, growth=True):
    rng = np.random.default_rng(9)
    lines = []
    for k in range(7):
        crack_lines(rng, 0.5, 0.5, 2 * math.pi * k / 7 + rng.random() * 0.4, 0.32, 2, lines)
    t = (i + 1) / n if growth else 1.0
    def draw(d, W):
        d.ellipse((0.38 * W, 0.38 * W, 0.62 * W, 0.62 * W), fill=(20, 16, 14, int(210 * min(1, t * 2))))
        for pts, depth in lines:
            m = max(2, int(len(pts) * min(1, t * (1.4 + (2 - depth) * 0.3))))
            P = [(x * W, y * W) for x, y in pts[:m]]
            w = max(1, int(W * (0.018 if depth == 2 else 0.011 if depth == 1 else 0.006)))
            d.line(P, fill=(18, 14, 12, 255), width=w)
    a = pil_frame(S, draw, blur=0.4)
    rim = pil_frame(S, draw, blur=2.2)
    out = np.zeros_like(a)
    out[..., :3] = a[..., :3]
    out[..., 3] = np.clip(a[..., 3] + rim[..., 3] * 0.35, 0, 1)
    return out


def build_all():
    sheet('Fire_Loop', 8, fire_loop, True, False, 'Looping flame (pre-coloured). Rate ~30 fps.')
    sheet('Fire_Burst', 8, fire_burst, False, False, 'Fire burst / flare-up, turns to smoke at the end (pre-coloured).')
    sheet('Fireball_Core', 4, fireball_core, True, False, 'Swirling fireball core (pre-coloured, loop).')
    sheet('Embers', 4, embers, True, False, 'Single flickering ember sprite (pre-coloured, loop) - emit many.')
    sheet('Smoke_Puff', 8, lambda i, n, S: puff(i, n, S), False, True, 'Soft smoke puff expanding and fading (greyscale).')
    sheet('Smoke_DarkBurst', 8, lambda i, n, S: puff(i, n, S, dark=True), False, True, 'Dense dark smoke burst (greyscale, dark).')
    sheet('Dust_Cloud', 8, lambda i, n, S: puff(i, n, S, dust=True), False, True, 'Low, wide dust cloud for earth impacts (tint brown).')
    sheet('Explosion', 8, explosion, False, False, 'Stylized explosion: flash, rolling fire, smoke (pre-coloured).')
    sheet('Water_Splash', 8, splash, False, True, 'Crown splash burst with droplets (white - tint blue).')
    sheet('Water_Spray', 4, spray, True, True, 'Fine upward spray (loop).')
    sheet('Water_Droplets', 4, droplets, False, True, '16 droplet sprite variants (use random frame).')
    sheet('Ripple_Ring', 8, ripple, False, True, 'Expanding triple ripple rings (place flat on the water).')
    sheet('Mist', 4, mist, True, True, 'Soft drifting mist (loop, low alpha).')
    sheet('Lightning_Arc', 4, lightning, True, True, '16 jagged lightning arcs with branches (flicker through frames).')
    sheet('Electric_Crackle', 4, crackle, True, True, 'Small crackling sparks (random frames).')
    sheet('Magic_Glow', 4, magic_glow, True, True, 'Pulsing glow with a rotating rune ring (loop).')
    sheet('Sparkles', 4, sparkle, True, True, 'Twinkling 4-point star (loop).')
    sheet('Hit_Spark', 4, hit_spark, False, True, 'Radial hit spark burst.')
    sheet('Shockwave_Ring', 8, shockwave, False, True, 'Expanding shockwave ring (place flat or facing camera).')
    sheet('Ground_Crack', 4, ground_crack, False, False, 'Ground crack decal growing over 16 frames (dark, use as flipbook or last frame as decal).')
    # static decal (1024, final state)
    a = ground_crack(15, 16, 1024)
    Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), 'RGBA').save(os.path.join(OUT, 'HO_VFX_Ground_Crack_Decal.png'))
    META.append(dict(name='HO_VFX_Ground_Crack_Decal', file='assets/Phase3/VFX/Flipbooks/HO_VFX_Ground_Crack_Decal.png', layout='single',
                     frames=1, loop=False, tint=False, description='Single 1024 ground crack decal (Decal on the ground).'))
    with open(os.path.join(OUT, 'flipbooks.json'), 'w') as f:
        json.dump(META, f, indent=1)


if __name__ == '__main__':
    build_all()
