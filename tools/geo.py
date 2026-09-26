"""Geometry builder helpers (bmesh) with material slots, UVs and robust outward-facing normals."""
import bmesh, math
from mathutils import Vector

UVD = 0.25   # default texel density: 1 UV unit per 4 studs


def newell(cos):
    n = Vector((0, 0, 0))
    for i, a in enumerate(cos):
        b = cos[(i + 1) % len(cos)]
        n.x += (a.y - b.y) * (a.z + b.z); n.y += (a.z - b.z) * (a.x + b.x); n.z += (a.x - b.x) * (a.y + b.y)
    return n


class Builder:
    def __init__(self, mat_names):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new('UVMap')
        self.mats = {m: i for i, m in enumerate(mat_names)}
        self.mat_names = list(mat_names)

    # --------------------------------------------------------------------------------- primitives
    def face(self, verts, mat, uvs=None, out=None, smooth=False):
        cos = [v.co for v in verts]
        if out is not None:
            if newell(cos).dot(out) < 0:
                verts = verts[::-1]
                if uvs is not None: uvs = uvs[::-1]
        try:
            f = self.bm.faces.new(verts)
        except ValueError:
            return None
        f.material_index = self.mats[mat]
        f.smooth = smooth
        if uvs is not None:
            for l, uv in zip(f.loops, uvs):
                l[self.uv].uv = uv
        return f

    def verts(self, cos):
        return [self.bm.verts.new(c) for c in cos]

    def beam(self, p0, p1, w, h, mat, up=Vector((0, 0, 1)), nseg=1, skip=(), uv_off=(0.0, 0.0), anchor='center',
             caps=True, path=None):
        """Rectangular beam from p0 to p1 (or along `path` polyline). anchor: 'center' | 'top' | 'bottom'."""
        pts = path if path is not None else [p0.lerp(p1, i / nseg) for i in range(nseg + 1)]
        prof_z = {'center': (-h / 2, h / 2), 'top': (-h, 0.0), 'bottom': (0.0, h)}[anchor]
        prof = [(-w / 2, prof_z[0]), (w / 2, prof_z[0]), (w / 2, prof_z[1]), (-w / 2, prof_z[1])]
        names = ['bottom', 'right', 'top', 'left']
        return self.sweep(pts, prof, mat, up=up, caps=caps, skip_sides=[names.index(s) for s in skip],
                          uv_off=uv_off, smooth=False)

    def box(self, lo, hi, mat, skip=(), uvd=UVD, uv_off=(0, 0)):
        lo, hi = Vector(lo), Vector(hi)
        c = [Vector((x, y, z)) for z in (lo.z, hi.z) for y in (lo.y, hi.y) for x in (lo.x, hi.x)]
        v = self.verts(c)
        ctr = (lo + hi) / 2
        quads = {'-z': (0, 1, 3, 2), '+z': (4, 5, 7, 6), '-y': (0, 1, 5, 4), '+y': (2, 3, 7, 6), '-x': (0, 2, 6, 4),
                 '+x': (1, 3, 7, 5)}
        out = []
        for k, q in quads.items():
            if k in skip: continue
            vs = [v[i] for i in q]
            ax = 'xyz'.index(k[1])
            uvs = []
            for vv in vs:
                p = vv.co
                if ax == 2: uvs.append((p.x * uvd + uv_off[0], p.y * uvd + uv_off[1]))
                elif ax == 1: uvs.append((p.x * uvd + uv_off[0], p.z * uvd + uv_off[1]))
                else: uvs.append((p.y * uvd + uv_off[0], p.z * uvd + uv_off[1]))
            n = Vector((0, 0, 0)); n[ax] = 1 if k[0] == '+' else -1
            out.append(self.face(vs, mat, uvs, out=n))
        return out

    def sweep(self, path, profile, mat, up=Vector((0, 0, 1)), caps=True, skip_sides=(), uv_off=(0.0, 0.0),
              smooth=False, smooth_sides=None, uvd=UVD, cap_mat=None, twist_up=None):
        """Sweep closed 2D profile [(x_across, y_up)] along a 3D polyline. Faces point away from the path."""
        path = [Vector(p) for p in path]
        n = len(path)
        frames = []
        for i in range(n):
            if i == 0: d = path[1] - path[0]
            elif i == n - 1: d = path[-1] - path[-2]
            else: d = (path[i + 1] - path[i - 1])
            d.normalize()
            u = twist_up(i) if twist_up else up
            side = d.cross(u)
            if side.length < 1e-6: side = d.cross(Vector((0, 1, 0)))
            side.normalize()
            upv = side.cross(d).normalized()
            frames.append((d, side, upv))
        rings = []
        for p, (d, s, u) in zip(path, frames):
            rings.append(self.verts([p + s * x + u * y for x, y in profile]))
        # perimeter distance for U
        m = len(profile)
        per = [0.0]
        for j in range(m):
            a, b = Vector(profile[j]), Vector(profile[(j + 1) % m])
            per.append(per[-1] + (b - a).length)
        along = [0.0]
        for i in range(1, n): along.append(along[-1] + (path[i] - path[i - 1]).length)
        pc = Vector((sum(x for x, _ in profile) / m, sum(y for _, y in profile) / m))
        for i in range(n - 1):
            for j in range(m):
                if j in skip_sides: continue
                a, b = rings[i][j], rings[i][(j + 1) % m]
                c, dd = rings[i + 1][(j + 1) % m], rings[i + 1][j]
                d0, s0, u0 = frames[i]
                mid2 = (Vector(profile[j]) + Vector(profile[(j + 1) % m])) / 2 - pc
                # outward = 2D edge normal of the profile, mapped into 3D
                e = Vector(profile[(j + 1) % m]) - Vector(profile[j])
                en = Vector((e.y, -e.x))
                if en.dot(mid2) < 0: en = -en
                outv = s0 * en.x + u0 * en.y
                uvs = [(along[i] * uvd + uv_off[0], per[j] * uvd + uv_off[1]),
                       (along[i] * uvd + uv_off[0], per[j + 1] * uvd + uv_off[1]),
                       (along[i + 1] * uvd + uv_off[0], per[j + 1] * uvd + uv_off[1]),
                       (along[i + 1] * uvd + uv_off[0], per[j] * uvd + uv_off[1])]
                sm = smooth if smooth_sides is None else (j in smooth_sides)
                self.face([a, b, c, dd], mat, uvs, out=outv, smooth=sm)
        if caps:
            for idx, sign in ((0, -1), (n - 1, 1)):
                d = frames[idx][0]
                uvs = [(x * uvd, y * uvd) for x, y in profile]
                self.face(list(rings[idx]), cap_mat or mat, uvs, out=d * sign)
        return rings

    def prism(self, outline, origin, ax_u, ax_v, ax_n, depth, mat, uvd=UVD, front_mat=None, back=True):
        """Extrude a 2D outline [(u,v)] (any winding) along ax_n by depth (from 0 to depth)."""
        origin = Vector(origin); ax_u, ax_v, ax_n = Vector(ax_u), Vector(ax_v), Vector(ax_n)
        # force CCW
        area = sum(outline[i][0] * outline[(i + 1) % len(outline)][1] - outline[(i + 1) % len(outline)][0] * outline[i][1]
                   for i in range(len(outline)))
        if area < 0: outline = outline[::-1]
        f0 = self.verts([origin + ax_u * u + ax_v * v for u, v in outline])
        f1 = self.verts([origin + ax_u * u + ax_v * v + ax_n * depth for u, v in outline])
        uvs = [(u * uvd, v * uvd) for u, v in outline]
        if back:
            self.face(f0, mat, uvs, out=-ax_n)
        self.face(f1, front_mat or mat, uvs, out=ax_n)
        m = len(outline)
        acc = 0.0
        for i in range(m):
            j = (i + 1) % m
            e = Vector(outline[j]) - Vector(outline[i])
            en = Vector((e.y, -e.x))       # outward for CCW
            outv = ax_u * en.x + ax_v * en.y
            L = e.length
            self.face([f0[i], f0[j], f1[j], f1[i]], mat,
                      [(acc * uvd, 0), ((acc + L) * uvd, 0), ((acc + L) * uvd, depth * uvd), (acc * uvd, depth * uvd)],
                      out=outv)
            acc += L
        return f0, f1

    def cylinder(self, c0, c1, r, segs, mat, caps=True, smooth=True, uvd=UVD):
        prof = [(r * math.cos(2 * math.pi * i / segs), r * math.sin(2 * math.pi * i / segs)) for i in range(segs)]
        d = (Vector(c1) - Vector(c0))
        up = Vector((0, 0, 1)) if abs(d.normalized().z) < 0.9 else Vector((1, 0, 0))
        return self.sweep([c0, c1], prof, mat, up=up, caps=caps, smooth=smooth, uvd=uvd)

    # --------------------------------------------------------------------------------- finishing
    def mark_sharp(self):
        """Edges between smooth and flat faces (or across material boundaries) -> sharp, for clean exported normals."""
        for e in self.bm.edges:
            fs = e.link_faces
            if len(fs) == 2 and (fs[0].smooth != fs[1].smooth or fs[0].material_index != fs[1].material_index):
                e.smooth = False
            elif len(fs) == 2 and not (fs[0].smooth and fs[1].smooth):
                e.smooth = False

    def deform(self, fn):
        for v in self.bm.verts:
            v.co = fn(v.co)
