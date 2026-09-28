"""Phase 4 / Hero unit: anime real-robot mech (HO_Mech_Raijin), rigid-rigged.

Exports one FBX with the armature and every skinned mesh piece (each piece split per texture set, < 20k tris),
previews (3/4, front, side, back, head close-up, a bent test pose) and a manifest entry.
"""
import sys, os, json, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import bpy
import ho
import robotkit as ck
from mathutils import Vector

render = os.environ.get('HO_RENDER', '1') == '1'
NAME = 'HO_Mech_Raijin'
PH, CAT = 'Phase4', 'Mechs'

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
    size = (hi - lo).length
    H = ck.J['neck'] + Vector((0, 0.8, 3.6))
    cams = {'head': (H + Vector((8.0, 12.0, 1.0)), H + Vector((0, 1.0, -0.8)), 45),
            'hero': (ctr + Vector((0.55, 0.85, 0.05)).normalized() * size * 1.05, ctr + Vector((0, 0, -2)), 38),
            'cannon': (ck.J['cannon'] + Vector((6.0, 14.0, -1.0)), ck.J['cannon'] + Vector((0, 3.0, 0)), 45)}
    renders = ho.render_previews(objs, NAME, subdir=f'{PH}/{CAT}', views=('three_quarter', 'front', 'side', 'back'), samples=32, cams=cams)
    # action test pose: sword raised overhead, cannon recoiled, head turned, left arm forward
    pb = arm.pose.bones
    for bb in pb: bb.rotation_mode = 'XYZ'
    pb['R_UpperArm'].rotation_euler = (math.radians(-95), 0, 0)
    pb['R_Forearm'].rotation_euler = (math.radians(-30), 0, 0)
    pb['L_UpperArm'].rotation_euler = (math.radians(-40), 0, 0)
    pb['Head'].rotation_euler = (0, math.radians(20), 0)
    pb['Cannon'].location = (0, -1.2, 0)
    pb['R_Wing'].rotation_euler = (math.radians(15), 0, 0)
    pb['L_Wing'].rotation_euler = (math.radians(15), 0, 0)
    pb['Torso'].rotation_euler = (0, math.radians(-12), 0)
    bpy.context.view_layer.update()
    renders += ho.render_previews(objs, NAME + '_PoseTest', subdir=f'{PH}/{CAT}', views=('three_quarter',), samples=24)
    for bb in pb: bb.rotation_euler = (0, 0, 0); bb.location = (0, 0, 0)

# ---------------------------------------------------------------- manifest + rig description
lo, hi = ho.world_bbox(objs)
json.dump({'bones': [[n, list(h), list(t), p] for n, h, t, p in rig['bones']]},
          open(os.path.join(ho.ASSET_DIR, PH, CAT, NAME + '_bones.json'), 'w'), indent=1)
entry = dict(name=NAME, phase=PH, category=CAT, type='Skinned mesh group + armature', file=rel,
             tris=sum(c['tris'] for c in checks), textures=sorted({t for c in checks for t in c['textures']}),
             pivot='ground between the feet', renders=renders, mesh_checks=checks,
             checks=dict(under_limit=all(c['tris'] <= 20000 for c in checks), dims=[round(d, 2) for d in (hi - lo)],
                         meshes={c['name']: c['tris'] for c in checks}, bones=len(rig['bones'])),
             notes=('Original anime real-robot style mech "Raijin" (~%.0f tall to the crest). Faces FRONT (-Z), feet on the ground at '
                    'the origin. White panelled armour (Mech_White) with Mech_Blue / Mech_Red / Mech_Grey accents over a dark frame '
                    '(Mech_Frame), yellow vents (Mech_Vent), faceted helmet with an original three-blade gold crest, twin glowing eyes '
                    '(Glow_Yellow -> Neon) and forehead sensor (Glow_Blue); broad shoulders with upswept red fins, front/side skirts, '
                    'heavy knees and feet, four wing plates on the back (L/R_Wing bones). Chest cannon with glowing core (Glow_Amber), '
                    'muzzle at %s (Roblox studs from the origin). Huge katana (steel, pale blue glowing edge) in the right hand, tip at %s. '
                    '%d bones, every piece rigid: Root, Pelvis, Torso, Head, Cannon, L/R_Wing, L/R_UpperArm/Forearm/Hand, Sword, '
                    'L/R_Thigh/Shin/Foot. Import with File > Import 3D (Scale Unit = Stud, Rig Type = Custom). '
                    'roblox/HO_MechRig.lua drives it (Idle, Swing, FireCannon, Stomp) - set Mech.MUZZLE_OFFSET to the muzzle above.'
                    % (hi.z - lo.z, '(%.1f, %.1f, %.1f)' % (rig['muzzle'].x, rig['muzzle'].z, -rig['muzzle'].y),
                       '(%.1f, %.1f, %.1f)' % (rig['tip'].x, rig['tip'].z, -rig['tip'].y), len(rig['bones']))))
ho.manifest_add(entry)
print('PUBLISHED', json.dumps({k: entry[k] for k in ('name', 'tris', 'file')}))
