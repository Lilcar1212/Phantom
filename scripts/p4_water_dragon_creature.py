"""Phase 4 / Hero creature: rigged Eastern water dragon (HO_Creature_WaterDragon).

Exports one FBX with the armature and every skinned mesh piece (each piece split per texture set, < 20k tris),
previews (3/4, front, side, back, head close-up, a bent test pose) and a manifest entry.
"""
import sys, os, json, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import bpy
import ho
import creaturekit as ck
from mathutils import Vector

render = os.environ.get('HO_RENDER', '1') == '1'
NAME = 'HO_Creature_WaterDragon'
PH, CAT = 'Phase4', 'Characters'

ho.reset()
pieces, rig = ck.build()
objs = []
for pname in ck.PIECES:
    b = pieces[pname]
    if not b.bm.faces: continue
    ob = ho.builder_obj(f'{NAME}_{pname}', b)
    objs += ho.split_single_material([ob])
checks = [ho.check(o) for o in objs]
for c in checks:
    print('MESH', c['name'], c['tris'])
over = [c['name'] for c in checks if c['tris'] > 20000]
assert not over, f'pieces over 20k tris: {over}'

# ---------------------------------------------------------------- armature
arm_d = bpy.data.armatures.new(NAME + '_Rig')
arm = bpy.data.objects.new(NAME + '_Rig', arm_d)
bpy.context.scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
eb = {}
for name, head, tail, parent in rig['bones']:
    e = arm_d.edit_bones.new(name)
    e.head, e.tail = head, tail
    if (e.tail - e.head).length < 1e-3: e.tail = e.head + Vector((0, 0.3, 0))
    if parent: e.parent = eb[parent]
    eb[name] = e
bpy.ops.object.mode_set(mode='OBJECT')
bone_names = [b[0] for b in rig['bones']]

# ---------------------------------------------------------------- skin weights (max 4 influences)
for o in objs:
    piece = o.name[len(NAME) + 1:].split('__')[0]
    groups = {}
    for v in o.data.vertices:
        w = ck.weights_for(rig, piece, v.co)
        for bn, val in sorted(w.items(), key=lambda kv: -kv[1])[:4]:
            if bn not in groups: groups[bn] = o.vertex_groups.new(name=bn)
            groups[bn].add([v.index], val, 'REPLACE')
    mod = o.modifiers.new('Rig', 'ARMATURE'); mod.object = arm
    o.parent = arm

# ---------------------------------------------------------------- export (skinned: armature + meshes)
path = os.path.join(ho.ASSET_DIR, PH, CAT, NAME + '.fbx')
os.makedirs(os.path.dirname(path), exist_ok=True)
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
for o in objs: o.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'ARMATURE', 'MESH'}, apply_unit_scale=True,
                         apply_scale_options='FBX_SCALE_UNITS', global_scale=1.0, axis_forward='-Z', axis_up='Y',
                         bake_space_transform=False, add_leaf_bones=False, primary_bone_axis='Y', secondary_bone_axis='X',
                         armature_nodetype='NULL', use_mesh_modifiers=False, mesh_smooth_type='FACE', use_tspace=True,
                         use_armature_deform_only=True, bake_anim=False, path_mode='STRIP', embed_textures=False)
rel = os.path.relpath(path, ho.ROOT)

# ---------------------------------------------------------------- previews
renders = []
if render:
    lo, hi = ho.world_bbox(objs)
    ctr = (lo + hi) / 2
    H = Vector(rig['bones'][[b[0] for b in rig['bones']].index('Head')][1])
    cams = {'head': (H + Vector((10.5, 13.5, -1.2)), H + Vector((0, 2.6, -0.4)), 45),
            'hero': (ctr + Vector((-0.62, 0.72, 0.2)).normalized() * (hi - lo).length * 1.05, ctr + Vector((0, 0, -1.5)), 38)}
    renders = ho.render_previews(objs, NAME, subdir=f'{PH}/{CAT}', views=('three_quarter', 'front', 'side', 'back'), samples=32,
                                 cams=cams)
    # bent test pose: neck turned, jaw open, tail swept - proves the skinning
    bpy.context.view_layer.objects.active = arm
    pb = arm.pose.bones
    for b in pb: b.rotation_mode = 'XYZ'
    for i in range(1, 17):
        pb[f'Tail{i:02d}'].rotation_euler = (0, 0, math.radians(10 * math.sin(i * 0.45)))
    for i in range(1, 5):
        pb[f'Neck{i:02d}'].rotation_euler = (math.radians(6), 0, math.radians(-11))
    pb['Jaw'].rotation_euler = (math.radians(26), 0, 0)
    pb['FR_Upper'].rotation_euler = (math.radians(-35), 0, 0)
    pb['FR_Lower'].rotation_euler = (math.radians(40), 0, 0)
    bpy.context.view_layer.update()
    renders += ho.render_previews(objs, NAME + '_PoseTest', subdir=f'{PH}/{CAT}', views=('three_quarter',), samples=24)
    for b in pb: b.rotation_euler = (0, 0, 0)

# ---------------------------------------------------------------- manifest + rig description
lo, hi = ho.world_bbox(objs)
json.dump({'bones': [[n, list(h), list(t), p] for n, h, t, p in rig['bones']]},
          open(os.path.join(ho.ASSET_DIR, PH, CAT, NAME + '_bones.json'), 'w'), indent=1)
entry = dict(name=NAME, phase=PH, category=CAT, type='Skinned mesh group + armature', file=rel,
             tris=sum(c['tris'] for c in checks), textures=sorted({t for c in checks for t in c['textures']}),
             pivot='ground between the front feet', renders=renders, mesh_checks=checks,
             checks=dict(under_limit=all(c['tris'] <= 20000 for c in checks), dims=[round(d, 2) for d in (hi - lo)],
                         meshes={c['name']: c['tris'] for c in checks}, bones=len(rig['bones'])),
             notes=('Rigged Eastern water dragon, the hero creature (~%.0f long, head at ~%.0f studs). Long straight bind pose, faces '
                    'FRONT (-Z), feet on the ground at the origin. Pieces: Head, Jaw, Horns, Eyes, Whiskers, Mane, Neck, Body, '
                    'Tail, Limbs, Claws, Fins, WaterFX (each split per texture set). Solid PBR creature (Dragon_Scales, '
                    'Dragon_Belly, Dragon_Horn, Dragon_Fin, Dragon_Claw, Dragon_Eye = Neon); only WaterFX is translucent '
                    '(Water_Flame, AlphaMode Transparency). %d bones: Root, Spine01-04, Neck01-04, Head, Jaw, Tail01-16, '
                    'FL/FR/RL/RR_Upper/_Lower/_Foot; skinned (max 4 weights). Import with File > Import 3D (Scale Unit = Stud, '
                    'Rig General > Rig Type = Custom). roblox/HO_DragonRig.lua animates it (tail wave, breathing, neck sway, jaw).'
                    % (max(hi.x - lo.x, hi.y - lo.y), hi.z, len(rig['bones']))))
ho.manifest_add(entry)
print('PUBLISHED', json.dumps({k: entry[k] for k in ('name', 'tris', 'file')}))
