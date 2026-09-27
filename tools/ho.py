"""Hollow Oath - shared Blender pipeline (run with `python3`, uses the `bpy` module).

Conventions (see docs/PIPELINE.md):
  * 1 Blender unit == 1 Roblox stud.
  * Asset FRONT faces Blender +Y  -> exported as FBX/Roblox -Z (Roblox LookVector).
  * Up is Blender +Z -> FBX/Roblox +Y.
  * Origin at bottom-centre of the asset's bounding box; transforms applied.
"""
import bpy, bmesh, math, os, json, shutil, sys
from mathutils import Vector, Matrix
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX_DIR = os.path.join(ROOT, 'textures')
ASSET_DIR = os.path.join(ROOT, 'assets')
RENDER_DIR = os.path.join(ROOT, 'renders')
MANIFEST_JSON = os.path.join(ROOT, 'docs', 'manifest.json')
MANIFEST_MD = os.path.join(ROOT, 'MANIFEST.md')

TRI_LIMIT = 20000
TEX_LIMIT = 1024

FLIP_EXPORT_PREFIXES = ('HO_Bldg_',)   # exported turned 180 deg about up (see export_fbx)

FBX_SETTINGS = dict(
    use_selection=True,
    object_types={'MESH', 'ARMATURE', 'EMPTY'},
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_UNITS',   # raw vertex values == Blender units
    global_scale=1.0,
    axis_forward='-Z',
    axis_up='Y',
    bake_space_transform=True,               # bake axis conversion into data -> no stray 90deg rotations
    use_mesh_modifiers=True,
    mesh_smooth_type='FACE',
    use_tspace=True,
    add_leaf_bones=False,
    path_mode='STRIP',                       # textures are uploaded separately to SurfaceAppearance
    embed_textures=False,
    use_custom_props=False,
)


# ----------------------------------------------------------------------------- scene
def reset():
    TEXSETS.clear()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.unit_settings.system = 'METRIC'
    s.unit_settings.scale_length = 1.0
    return s


def link(obj, coll=None):
    (coll or bpy.context.scene.collection).objects.link(obj)
    return obj


def mesh_from_bm(name, bm, mat_list=()):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mat_list:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    return link(ob)


def join(objs, name):
    objs = [o for o in objs if o is not None]
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = name
    ob.data.name = name
    return ob


def apply_transforms(ob):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def origin_bottom_center(ob, ref_objs=None):
    """Move mesh data so the origin sits at bottom-centre of the bbox (of ref_objs if given)."""
    apply_transforms(ob)
    objs = ref_objs or [ob]
    lo, hi = world_bbox(objs)
    pivot = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    ob.data.transform(Matrix.Translation(ob.location - pivot))
    ob.location = (0, 0, 0)
    return pivot


def finalize(ob, recalc_normals=True):
    apply_transforms(ob)
    if recalc_normals:
        bm = bmesh.new(); bm.from_mesh(ob.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(ob.data); bm.free()
    origin_bottom_center(ob)
    ob.data.update()
    return ob


def world_bbox(objs):
    lo = Vector((1e9, 1e9, 1e9)); hi = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
    return lo, hi


# ----------------------------------------------------------------------------- materials
TEXSETS = {}


def texset_paths(name):
    d = os.path.join(TEX_DIR, name)
    return {ch: os.path.join(d, f'HO_T_{name}_{ch}.png') for ch in ('Color', 'Normal', 'Roughness', 'Metalness')}


def material(name, emission=None, emission_strength=0.0, tint=None):
    """Principled material wired to the shared PBR texture set textures/<name>/."""
    key = (name, emission, emission_strength, tint)
    if key in TEXSETS:
        return TEXSETS[key]
    mname = 'HO_M_' + name + ('' if tint is None else '_%02x%02x%02x' % tuple(int(c * 255) for c in tint))
    m = bpy.data.materials.new(mname)
    m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    bsdf = N['Principled BSDF']
    p = texset_paths(name)

    def img(ch, non_color):
        im = bpy.data.images.load(p[ch], check_existing=True)
        if non_color:
            im.colorspace_settings.name = 'Non-Color'
        t = N.new('ShaderNodeTexImage'); t.image = im
        return t

    col = img('Color', False)
    if tint is not None:
        mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
        mix.inputs['Factor'].default_value = 1.0
        L.new(col.outputs['Color'], mix.inputs[6]); mix.inputs[7].default_value = (*tint, 1)
        L.new(mix.outputs[2], bsdf.inputs['Base Color'])
    else:
        L.new(col.outputs['Color'], bsdf.inputs['Base Color'])
    L.new(img('Roughness', True).outputs['Color'], bsdf.inputs['Roughness'])
    L.new(img('Metalness', True).outputs['Color'], bsdf.inputs['Metallic'])
    nm = N.new('ShaderNodeNormalMap')
    L.new(img('Normal', True).outputs['Color'], nm.inputs['Color'])
    L.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
    if name.startswith('VFX_'):                  # scrolling effect textures: glow, see-through where dark
        glow = {'VFX_Energy': (0.35, 0.75, 1.0), 'VFX_Slash': (0.75, 0.88, 1.0), 'VFX_Water': (0.3, 0.62, 1.0)}.get(name, (1, 1, 1))
        gm = N.new('ShaderNodeMix'); gm.data_type = 'RGBA'; gm.blend_type = 'MULTIPLY'; gm.inputs['Factor'].default_value = 1.0
        L.new(col.outputs['Color'], gm.inputs[6]); gm.inputs[7].default_value = (*glow, 1)
        L.new(gm.outputs[2], bsdf.inputs['Emission Color'])
        bsdf.inputs['Base Color'].default_value = (0, 0, 0, 1)
        for lk in list(bsdf.inputs['Base Color'].links): L.remove(lk)
        bsdf.inputs['Emission Strength'].default_value = 4.0
        bw = N.new('ShaderNodeRGBToBW'); L.new(col.outputs['Color'], bw.inputs['Color'])
        ramp = N.new('ShaderNodeMapRange'); ramp.inputs['From Max'].default_value = 0.35
        L.new(bw.outputs['Val'], ramp.inputs['Value']); L.new(ramp.outputs['Result'], bsdf.inputs['Alpha'])
        if hasattr(m, 'blend_method'): m.blend_method = 'BLEND'
    if emission is not None:
        bsdf.inputs['Emission Color'].default_value = (*emission, 1)
        bsdf.inputs['Emission Strength'].default_value = emission_strength
    m['ho_texset'] = name
    TEXSETS[key] = m
    return m


# ----------------------------------------------------------------------------- UV helpers
def box_uv(bm, density=0.25, offset=(0.0, 0.0)):
    """World-space box projection. density = UV units per stud (0.25 -> texture repeats every 4 studs)."""
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for l in f.loops:
            co = l.vert.co
            if ax == 0:
                u, v = co.y * (1 if n.x > 0 else -1), co.z
            elif ax == 1:
                u, v = co.x * (-1 if n.y > 0 else 1), co.z
            else:
                u, v = co.x, co.y * (1 if n.z > 0 else -1)
            l[uv].uv = (u * density + offset[0], v * density + offset[1])
    return uv


# ----------------------------------------------------------------------------- stats & checks
def mesh_arrays(ob):
    me = ob.data
    co = np.empty(len(me.vertices) * 3, dtype=np.float64); me.vertices.foreach_get('co', co)
    return co.reshape(-1, 3)


def tri_count(ob):
    me = ob.data
    me.calc_loop_triangles()
    return len(me.loop_triangles)


def islands(ob):
    """Return list of vertex-index arrays for connected components."""
    me = ob.data
    n = len(me.vertices)
    parent = np.arange(n)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    ev = np.empty(len(me.edges) * 2, dtype=np.int64); me.edges.foreach_get('vertices', ev)
    for a, b in ev.reshape(-1, 2):
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    roots = np.array([find(i) for i in range(n)])
    order = np.argsort(roots, kind='stable')
    splits = np.flatnonzero(np.diff(roots[order])) + 1
    return np.split(order, splits)


def floating_parts(ob, eps=0.03):
    """Parts whose bbox does not touch any other part and are not resting on the ground (z=min).
    Parts are unioned when their (eps-expanded) bounding boxes overlap; anything not connected to the
    ground cluster is reported as floating."""
    co = mesh_arrays(ob)
    isl = islands(ob)
    if len(isl) <= 1:
        return 0, len(isl)
    lo = np.array([co[i].min(0) for i in isl]) - eps
    hi = np.array([co[i].max(0) for i in isl]) + eps
    zmin = co[:, 2].min()
    k = len(isl)
    grounded = lo[:, 2] <= zmin + 2 * eps
    visited = grounded.copy()
    frontier = list(np.flatnonzero(grounded))
    while frontier:
        i = frontier.pop()
        ov = np.all((lo <= hi[i]) & (hi >= lo[i]), axis=1) & ~visited
        nxt = np.flatnonzero(ov)
        visited[nxt] = True
        frontier.extend(nxt.tolist())
    return int((~visited).sum()), k


def inverted_islands(ob):
    """Closed islands whose signed volume is negative (normals pointing in)."""
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bm.verts.ensure_lookup_table()
    bad = 0; closed = 0; open_ = 0
    seen = set()
    for f0 in bm.faces:
        if f0.index in seen: continue
        stack = [f0]; comp = []
        seen.add(f0.index)
        while stack:
            f = stack.pop(); comp.append(f)
            for e in f.edges:
                for g in e.link_faces:
                    if g.index not in seen:
                        seen.add(g.index); stack.append(g)
        is_closed = all(e.is_manifold for f in comp for e in f.edges)
        if not is_closed:
            open_ += 1; continue
        closed += 1
        vol = 0.0
        for f in comp:
            vs = [v.co for v in f.verts]
            for i in range(1, len(vs) - 1):
                vol += vs[0].dot(vs[i].cross(vs[i + 1]))
        if vol < 0: bad += 1
    bm.free()
    return bad, closed, open_


def check(ob, grid=None, notes=''):
    tris = tri_count(ob)
    lo, hi = world_bbox([ob])
    dims = hi - lo
    flo, parts = floating_parts(ob)
    inv, closed, open_ = inverted_islands(ob)
    texs = sorted({m.get('ho_texset') for m in ob.data.materials if m and m.get('ho_texset')})
    tex_ok = True
    for t in texs:
        for pth in texset_paths(t).values():
            im = bpy.data.images.load(pth, check_existing=True)
            if max(im.size) > TEX_LIMIT: tex_ok = False
    me = ob.data
    per_mat = {}
    for lt in me.loop_triangles:
        m = me.materials[me.polygons[lt.polygon_index].material_index]
        k = (m.get('ho_texset') if m else None) or 'none'
        per_mat[k] = per_mat.get(k, 0) + 1
    res = dict(
        name=ob.name, tris=tris, tris_per_material=per_mat, under_limit=tris <= TRI_LIMIT,
        dims=[round(d, 3) for d in dims], parts=parts, floating=flo,
        closed_parts=closed, open_parts=open_, inverted_parts=inv,
        textures=texs, textures_ok=tex_ok,
        pivot_bottom_center=abs(lo.z) < 1e-3 and abs(lo.x + hi.x) < 1e-3 and abs(lo.y + hi.y) < 1e-3,
    )
    if grid:
        res['grid_ok'] = all(abs(d / grid - round(d / grid)) < 1e-3 for d in (grid_dims(ob) or dims[:2]))
    return res


def grid_dims(ob):
    v = ob.get('ho_footprint')
    return list(v) if v else None


# ----------------------------------------------------------------------------- export
def export_fbx(objs, rel_path):
    path = os.path.join(ASSET_DIR, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    # Roblox import report: HO_Bldg_* arrived with their fronts on +Z, so building files are turned 180 deg
    # about the up axis on export (the Blender scene, checks and previews keep front = +Y).
    flip = os.path.basename(rel_path).startswith(FLIP_EXPORT_PREFIXES)
    turn = Matrix.Rotation(math.pi, 4, 'Z')
    if flip:
        for o in objs: o.data.transform(turn); o.data.update()
    bpy.ops.export_scene.fbx(filepath=path, **FBX_SETTINGS)
    if flip:
        for o in objs: o.data.transform(turn); o.data.update()
    return os.path.relpath(path, ROOT)


# ----------------------------------------------------------------------------- render
def _world_golden(scene, strength=1.0):
    w = bpy.data.worlds.new('HO_World'); scene.world = w
    w.use_nodes = True
    N = w.node_tree.nodes; L = w.node_tree.links
    bg = N['Background']
    grad = N.new('ShaderNodeTexGradient')
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping')
    mp.inputs['Rotation'].default_value = (0, math.radians(90), 0)
    ramp = N.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (1.0, 0.62, 0.35, 1)
    ramp.color_ramp.elements[1].color = (0.30, 0.42, 0.62, 1)
    L.new(tc.outputs['Generated'], mp.inputs['Vector'])
    L.new(mp.outputs['Vector'], grad.inputs['Vector'])
    L.new(grad.outputs['Fac'], ramp.inputs['Fac'])
    L.new(ramp.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = 0.55 * strength


def setup_render(scene, res=(1280, 960), samples=64):
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    try:
        scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception:
        pass
    scene.cycles.max_bounces = 6
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.render.image_settings.file_format = 'PNG'


def _lights(scene, size):
    sun = bpy.data.lights.new('Sun', 'SUN'); sun.energy = 4.2; sun.color = (1.0, 0.80, 0.58)
    sun.angle = math.radians(2.5)
    so = bpy.data.objects.new('Sun', sun); link(so)
    so.rotation_euler = (math.radians(58), 0, math.radians(215))
    fill = bpy.data.lights.new('Fill', 'SUN'); fill.energy = 0.7; fill.color = (0.55, 0.68, 1.0)
    fo = bpy.data.objects.new('Fill', fill); link(fo)
    fo.rotation_euler = (math.radians(60), 0, math.radians(20))
    return [so, fo]


def _ground(size):
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=size * 6)
    m = bpy.data.materials.new('HO_Preview_Ground'); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.32, 0.29, 0.25, 1); b.inputs['Roughness'].default_value = 0.95
    g = mesh_from_bm('_PreviewGround', bm, [m])
    g.location.z = -0.002
    return g


def _look_at(cam, target):
    d = target - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def render_previews(objs, name, subdir='', views=('three_quarter', 'front'), samples=64,
                    res=(1280, 960), ground=True, extra_views=None, cams=None):
    scene = bpy.context.scene
    setup_render(scene, res, samples)
    _world_golden(scene)
    lo, hi = world_bbox(objs)
    ctr = (lo + hi) / 2
    size = max((hi - lo).length, 1.0)
    helpers = _lights(scene, size)
    if ground:
        helpers.append(_ground(size))
    cam_d = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', cam_d); link(cam)
    scene.camera = cam
    cam_d.lens = 50
    cam_d.clip_end = size * 50
    cam_d.clip_start = max(size / 1000, 0.01)
    dirs = {
        'three_quarter': Vector((0.78, 1.0, 0.62)),   # front is +Y
        'front': Vector((0.0, 1.0, 0.12)),
        'back': Vector((-0.5, -1.0, 0.5)),
        'top': Vector((0.0, 0.001, 1.0)),
        'under': Vector((0.55, 0.9, -0.28)),
        'side': Vector((1.0, 0.25, 0.3)),
        'low': Vector((0.7, 1.0, 0.2)),
    }
    if extra_views:
        dirs.update(extra_views)
    out = []
    os.makedirs(os.path.join(RENDER_DIR, subdir), exist_ok=True)
    fov = 2 * math.atan(36 / 2 / cam_d.lens)
    for v in views:
        d = dirs[v].normalized()
        dist = (size * 0.5) / math.tan(fov / 2) * 1.08
        cam.location = ctr + d * dist
        _look_at(cam, ctr)
        if ground:
            helpers[2].hide_render = (v == 'under')
        p = os.path.join(RENDER_DIR, subdir, f'{name}_{v}.png')
        scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        out.append(os.path.relpath(p, ROOT))
    for cname, spec in (cams or {}).items():
        loc, target, lens = spec[:3]
        lamps = []
        for lp in (spec[3] if len(spec) > 3 else []):
            ld = bpy.data.lights.new('Lamp', 'POINT'); ld.energy = 900; ld.color = (1.0, 0.72, 0.45)
            ld.shadow_soft_size = 0.6
            lo_ = bpy.data.objects.new('Lamp', ld); link(lo_); lo_.location = Vector(lp); lamps.append(lo_)
        cam.location = Vector(loc); cam_d.lens = lens
        _look_at(cam, Vector(target))
        if ground: helpers[2].hide_render = False
        p = os.path.join(RENDER_DIR, subdir, f'{name}_{cname}.png')
        scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        out.append(os.path.relpath(p, ROOT))
        cam_d.lens = 50
        for l_ in lamps:
            bpy.data.objects.remove(l_, do_unlink=True)
    for h in helpers + [cam]:
        bpy.data.objects.remove(h, do_unlink=True)
    return out


# ----------------------------------------------------------------------------- manifest
def manifest_add(entry):
    os.makedirs(os.path.dirname(MANIFEST_JSON), exist_ok=True)
    data = []
    if os.path.exists(MANIFEST_JSON):
        with open(MANIFEST_JSON) as f:
            data = json.load(f)
    old = {d['name']: d for d in data}.get(entry['name'])
    if old and not entry.get('renders') and old.get('renders'):
        entry['renders'] = old['renders']
    data = [d for d in data if d['name'] != entry['name']]
    data.append(entry)
    data.sort(key=lambda d: (d.get('phase', ''), d.get('category', ''), d['name']))
    with open(MANIFEST_JSON, 'w') as f:
        json.dump(data, f, indent=1)
    write_manifest_md(data)


def write_manifest_md(data):
    lines = ['# Hollow Oath - Asset Manifest', '',
             'Generated by `tools/ho.py`. 1 unit = 1 stud. Front = Roblox -Z. Pivot = bottom-centre unless noted.',
             'Textures live in `textures/<Set>/HO_T_<Set>_{Color,Normal,Roughness,Metalness}.png` (SurfaceAppearance).', '',
             '| Name | Type | File | Tris | Size (X×Y×H studs) | Texture sets | Pivot | Checks | Notes |',
             '|---|---|---|---:|---|---|---|---|---|']
    for d in data:
        c = d.get('checks', {})
        ok = []
        if c:
            ok.append('✅' if c.get('under_limit') else '❌ tris')
            if c.get('floating'): ok.append(f"⚠ {c['floating']} floating")
            if c.get('inverted_parts'): ok.append(f"⚠ {c['inverted_parts']} inverted")
            if 'grid_ok' in c: ok.append('grid ✅' if c['grid_ok'] else 'grid ❌')
        dims = c.get('dims') or d.get('dims') or []
        lines.append('| {n} | {t} | `{f}` | {tr} | {dm} | {tx} | {pv} | {ck} | {no} |'.format(
            n=d['name'], t=d.get('type', ''), f=d.get('file', ''), tr=d.get('tris', ''),
            dm=' × '.join(f'{x:g}' for x in dims), tx=', '.join(d.get('textures', [])),
            pv=d.get('pivot', 'bottom-centre'), ck=' '.join(ok), no=d.get('notes', '')))
    lines += ['', '## Mesh objects and their texture set', '',
              'Every mesh object uses exactly ONE texture set: give its MeshPart one SurfaceAppearance made from '
              '`textures/<Set>/HO_T_<Set>_*.png`. Multi-material parts were split and are named `<Object>__<Set>`.', '',
              '| Asset | Mesh object (= MeshPart name) | Texture set | Tris |', '|---|---|---|---:|']
    for d in data:
        meshes = d.get('mesh_checks') or [d.get('checks', {})]
        for c in meshes:
            if not c or 'name' not in c: continue
            tex = ', '.join(c.get('textures', [])) or '-'
            lines.append(f"| {d['name']} | `{c['name']}` | {tex} | {c.get('tris', '')} |")
    with open(MANIFEST_MD, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def publish(ob, category, phase='Phase1', grid=None, notes='', type_='Mesh', render=True,
            extra_objs=(), views=('three_quarter', 'front'), samples=64, footprint=None):
    """Finalize-checked export + previews + manifest entry for one asset object."""
    if len(used_sets(ob)) > 1:
        return publish_group([ob], ob.name, category, phase=phase, grid=grid, notes=notes, type_=type_,
                             render=render, views=views, samples=samples, footprint=footprint)
    if footprint:
        ob['ho_footprint'] = footprint
    strip_unused_slots(ob)
    c = check(ob, grid=grid)
    rel = export_fbx([ob], f'{phase}/{category}/{ob.name}.fbx')
    renders = render_previews([ob, *extra_objs], ob.name, subdir=f'{phase}/{category}', views=views,
                              samples=samples) if render else []
    entry = dict(name=ob.name, phase=phase, category=category, type=type_, file=rel, tris=c['tris'],
                 textures=c['textures'], pivot='bottom-centre', checks=c, renders=renders, notes=notes)
    manifest_add(entry)
    print('PUBLISHED', json.dumps(entry))
    return entry


def split_by_material(ob, groups):
    """Split `ob` into several objects. groups = {suffix: [texset names]} (a None entry catches the rest)."""
    out = []
    for suffix, sets in groups.items():
        cp = ob.copy(); cp.data = ob.data.copy(); link(cp)
        cp.name = cp.data.name = ob.name + suffix
        bm = bmesh.new(); bm.from_mesh(cp.data)
        keep_idx = set()
        for i, m in enumerate(cp.data.materials):
            ts = m.get('ho_texset') if m else None
            if sets is None:
                others = {t for v in groups.values() if v for t in v}
                if ts not in others: keep_idx.add(i)
            elif ts in sets:
                keep_idx.add(i)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index not in keep_idx], context='FACES')
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
        bm.to_mesh(cp.data); bm.free()
        # drop unused material slots
        used = sorted({p.material_index for p in cp.data.polygons})
        mats = [cp.data.materials[i] for i in used]
        remap = {o: n for n, o in enumerate(used)}
        idx = [remap[p.material_index] for p in cp.data.polygons]
        cp.data.materials.clear()
        for m in mats: cp.data.materials.append(m)
        cp.data.polygons.foreach_set('material_index', idx)
        cp.data.update()
        out.append(cp)
    bpy.data.objects.remove(ob, do_unlink=True)
    return out


def used_sets(ob):
    return sorted({(ob.data.materials[p.material_index].get('ho_texset') or 'none') for p in ob.data.polygons})


def strip_unused_slots(o):
    """Single-set object: keep only the material slot its faces use (stray empty slots from kit builders
    otherwise travel into the FBX and confuse the one-SurfaceAppearance-per-MeshPart mapping)."""
    me = o.data
    if len(me.materials) <= 1 or not me.polygons:
        return o
    mat = me.materials[me.polygons[0].material_index]
    me.materials.clear()
    me.materials.append(mat)
    for p in me.polygons:
        p.material_index = 0
    me.update()
    return o


def split_single_material(objs):
    """Roblox MeshParts take ONE SurfaceAppearance: split every multi-material object into one object per
    texture set, named <Object>__<TextureSet>. Single-material objects are kept unchanged."""
    out = []
    for o in objs:
        sets = used_sets(o)
        if len(sets) <= 1:
            out.append(strip_unused_slots(o))
        else:
            out += split_by_material(o, {f'__{t}': [t] for t in sets})
    return out


def publish_group(objs, asset_name, category, phase='Phase1', grid=None, notes='', type_='Mesh group', render=True,
                  views=('three_quarter', 'front'), samples=64, footprint=None, cams=None, pivot='bottom-centre',
                  render_objs=None):
    """Export several meshes (sharing one pivot) as one FBX asset; each mesh checked against the limits.
    Every exported mesh object uses exactly one texture set (see split_single_material)."""
    objs = split_single_material(objs)
    checks = []
    for o in objs:
        if footprint: o['ho_footprint'] = footprint
        checks.append(check(o, grid=grid))
    rel = export_fbx(objs, f'{phase}/{category}/{asset_name}.fbx')
    if render and render_objs:                  # preview a re-placed copy: hide the export meshes meanwhile
        for o in objs: o.hide_render = True
    renders = render_previews(render_objs or objs, asset_name, subdir=f'{phase}/{category}', views=views,
                              samples=samples, cams=cams) if render else []
    for o in objs: o.hide_render = False
    lo, hi = world_bbox(objs)
    # floating parts are judged on the whole assembly (a part may rest on geometry in another mesh)
    tmp = [o.copy() for o in objs]
    for t, o in zip(tmp, objs):
        t.data = o.data.copy(); link(t)
    joined = join(tmp, '_assembly_check')
    flo_total, parts_total = floating_parts(joined)
    bpy.data.objects.remove(joined, do_unlink=True)
    agg = dict(under_limit=all(c['under_limit'] for c in checks), floating=flo_total, parts=parts_total,
               inverted_parts=sum(c['inverted_parts'] for c in checks), dims=[round(d, 3) for d in (hi - lo)],
               meshes={c['name']: c['tris'] for c in checks},
               pivot_bottom_center=abs(lo.z) < 1e-3 and abs(lo.x + hi.x) < 1e-3 and abs(lo.y + hi.y) < 1e-3,
               pivot_z0=abs(lo.z) < 1e-3)
    if grid:
        agg['grid_ok'] = all(c.get('grid_ok', True) for c in checks)
    tex = sorted({t for c in checks for t in c['textures']})
    entry = dict(name=asset_name, phase=phase, category=category, type=type_, file=rel,
                 tris=sum(c['tris'] for c in checks), textures=tex, pivot=pivot, checks=agg,
                 mesh_checks=checks, renders=renders,
                 notes=notes + ' | meshes: ' + ', '.join(f"{c['name']} ({c['tris']})" for c in checks))
    manifest_add(entry)
    print('PUBLISHED', json.dumps(entry))
    return entry


def split_by_axis(ob, axis=1, names=('_Front', '_Back')):
    """Split a mesh into two objects by face-centroid sign on `axis` (1 = Y: front (+Y) / back (-Y))."""
    out = []
    for keep_pos, suffix in ((True, names[0]), (False, names[1])):
        cp = ob.copy(); cp.data = ob.data.copy(); link(cp)
        cp.name = cp.data.name = ob.name + suffix
        bm = bmesh.new(); bm.from_mesh(cp.data)
        dele = [f for f in bm.faces if (f.calc_center_median()[axis] >= 0) != keep_pos]
        bmesh.ops.delete(bm, geom=dele, context='FACES')
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
        bm.to_mesh(cp.data); bm.free()
        out.append(cp)
    bpy.data.objects.remove(ob, do_unlink=True)
    return out


def builder_obj(name, b, weld=True):
    """Builder -> Blender object with its materials."""
    if weld:
        bmesh.ops.remove_doubles(b.bm, verts=b.bm.verts, dist=1e-5)
    b.mark_sharp()
    return mesh_from_bm(name, b.bm, [material(m) for m in b.mat_names])


def finalize_group(objs, pivot=None):
    """Apply transforms and move all objects' data so the group's bottom-centre (or `pivot`) is the origin."""
    for o in objs:
        apply_transforms(o)
    if pivot is None:
        lo, hi = world_bbox(objs)
        pivot = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    for o in objs:
        o.data.transform(Matrix.Translation(o.location - Vector(pivot)))
        o.location = (0, 0, 0)
        o.data.update()
    return objs
