"""Phase 3: VFX flipbooks, scroll textures and VFX meshes."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import ho, bpy
import vfx_flipbooks as vf
import vfx_meshes as vm

render = os.environ.get('HO_RENDER', '1') == '1'
vf.build_all()
vm.textures()
for fb in vf.META:     # flipbooks into the manifest
    ho.manifest_add(dict(name=fb['name'], phase='Phase3', category='Flipbooks', type=f"Flipbook {fb['layout']}", file=fb['file'],
                         tris='', textures=[], pivot='-', checks={}, notes=f"{fb['description']} Loop: {fb['loop']}; tintable: {fb['tint']}."))
UV = 'UV: U along the effect (scroll this for motion), V across (0 inner/bottom, 1 outer/top). Double-sided. Texture: '
JOBS = [
    ('HO_VFX_Slash_Thin', lambda: vm.slash('thin'), UV + 'HO_VFXT_Slash.png. Crescent radius 5, sweep 170 deg, lies flat (XY) around the origin (= the character).'),
    ('HO_VFX_Slash_Medium', lambda: vm.slash('medium'), UV + 'HO_VFXT_Slash.png. Radius 6.5, sweep 200 deg.'),
    ('HO_VFX_Slash_Heavy', lambda: vm.slash('heavy'), UV + 'HO_VFXT_Slash.png. Radius 8.5, wide 3.4, sweep 230 deg.'),
    ('HO_VFX_Shockwave_Flat', vm.shock_ring_flat, UV + 'HO_VFXT_Energy.png. Flat ring R 8 (scale it up over time).'),
    ('HO_VFX_Shockwave_Dome', vm.shock_dome, UV + 'HO_VFXT_Energy.png. Hemisphere shell R 6.'),
    ('HO_VFX_Vortex', vm.vortex, UV + 'HO_VFXT_Energy.png (or Water/Fire). Twisted flaring tornado shell, 16 tall.'),
    ('HO_VFX_SpiralCone', vm.spiral_cone, UV + 'HO_VFXT_Energy.png. Helical ribbon winding up a cone, 10 tall.'),
    ('HO_VFX_WaterDragon', vm.water_dragon, 'Serpentine water dragon (~40 long) for Twin Dragons: body U runs tail->neck (0..4) - scroll HO_VFXT_Water.png along U; head with horns, whiskers, dorsal fins. Head faces front (-Z).'),
    ('HO_VFX_StoneDrill', vm.stone_drill, 'Stone drill cone with raised spiral ridges (Stone_Granite), 6 tall; spin it about its axis.'),
    ('HO_VFX_FirePillar', vm.fire_pillar, UV + 'HO_VFXT_Fire.png scrolling along V (up). Open tapered cylinder 18 tall.'),
    ('HO_VFX_FireRing_Segment', vm.fire_ring_segment, UV + 'HO_VFXT_Fire.png. 45-deg flame wall segment of a radius-10 ring (8 = full ring; rotate each by 45 deg).'),
]
for name, fn, notes in JOBS:
    ho.reset()
    ob = ho.builder_obj(name, fn(), weld=False)
    ho.publish(ob, 'VFX', phase='Phase3', render=render, samples=16, notes=notes)
ho.reset()
objs = [ho.builder_obj(f'HO_VFX_EnergySphere_{n}', b) for n, b in vm.energy_sphere()]
ho.publish_group(objs, 'HO_VFX_EnergySphere', 'VFX', phase='Phase3', render=render, samples=16,
                 notes=UV + 'HO_VFXT_Energy.png. Three nested shells (Outer r4, Middle r2.8, Core r1.6) sharing one centre; rotate them in opposite directions.')
ho.reset()
objs = []
for k in range(10):
    o = ho.builder_obj(f'HO_VFX_RockShard_{k + 1:02d}', vm.rock_shard(k + 1, size=0.6 + 0.12 * k))
    o.data.transform(__import__('mathutils').Matrix.Translation(((k % 5) * 4.0 - 8.0, (k // 5) * 4.0, 1.5)))
    objs.append(o)
ho.publish_group(objs, 'HO_VFX_RockShards', 'VFX', phase='Phase3', render=render, samples=16,
                 notes='10 rock shards/chunks (Stone_Granite), sizes 0.6-1.7, laid out on a grid - use each MeshPart on its own (debris, earth spikes).')
