"""Phase 2: R6 + Golem animations -> assets/Phase2/Animations/HO_Anim_<Name>.{rbxmx,fbx,json} + preview strips."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import ho, bpy
from mathutils import Vector
import animkit as ak
from anims_data import ANIMS
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(ho.ASSET_DIR, 'Phase2', 'Animations')
REN = os.path.join(ho.RENDER_DIR, 'Phase2', 'Animations')
os.makedirs(OUT, exist_ok=True); os.makedirs(REN, exist_ok=True)
render = os.environ.get('HO_RENDER', '1') == '1'
only = set(sys.argv[1:])
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)


def solid(name, rgb):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = 0.6
    return m


index = []
for anim in ANIMS:
    short = anim.name.replace('HO_Anim_', '')
    if only and not any(o in short for o in only): continue
    ak.write_rbxmx(anim, os.path.join(OUT, anim.name + '.rbxmx'))
    ak.write_json(anim, os.path.join(OUT, anim.name + '.json'))
    ho.reset()
    golem = anim.rig.name == 'Golem'
    mats = {p: solid(p, c) for p, c in ({
        'Head': (0.55, 0.5, 0.45) if golem else (0.93, 0.78, 0.62), 'Torso': (0.42, 0.38, 0.33) if golem else (0.12, 0.17, 0.32),
        'Right Arm': (0.5, 0.45, 0.4) if golem else (0.93, 0.78, 0.62), 'Left Arm': (0.5, 0.45, 0.4) if golem else (0.93, 0.78, 0.62),
        'Right Leg': (0.38, 0.34, 0.3) if golem else (0.18, 0.16, 0.2), 'Left Leg': (0.38, 0.34, 0.3) if golem else (0.18, 0.16, 0.2)}).items()}
    if short.startswith('Hollow'):
        for p in mats: mats[p] = solid('hollow', (0.03, 0.03, 0.04))
    arm, meshes = ak.build_armature(anim.rig, name=anim.rig.name, mesh_mats=mats)
    ak.key_anim(arm, anim)
    ak.export_fbx(arm, meshes, os.path.join(OUT, anim.name + '.fbx'))
    strip = None
    if render:
        frames = sorted({0, anim.length, *anim.markers.values(), *[anim.keys[len(anim.keys) * i // 4][0] for i in range(1, 4)]})[:7]
        tiles = []
        scene = bpy.context.scene
        ho.setup_render(scene, (360, 420), 8)
        ho._world_golden(scene)
        lights = ho._lights(scene, 6)
        ground = ho._ground(4 * anim.rig.s)
        cam_d = bpy.data.cameras.new('C'); cam = bpy.data.objects.new('C', cam_d); ho.link(cam); scene.camera = cam
        cam_d.lens = 40
        s = anim.rig.s
        cam.location = Vector((7.5 * s, 9.5 * s, 5.0 * s)); ho._look_at(cam, Vector((0, 0, 2.6 * s)))
        for fr in frames:
            scene.frame_set(fr)
            fp = os.path.join(REN, f'_{short}_{fr}.png')
            scene.render.filepath = fp
            bpy.ops.render.render(write_still=True)
            im = Image.open(fp).convert('RGB'); os.remove(fp)
            d = ImageDraw.Draw(im)
            tag = ' '.join(k for k, v in anim.markers.items() if v == fr)
            d.rectangle((0, 0, 360, 26), fill=(20, 26, 38))
            d.text((8, 3), f'f{fr}  {tag}', font=font, fill=(255, 210, 120) if tag else (255, 255, 255))
            tiles.append(im)
        strip = Image.new('RGB', (360 * len(tiles), 420 + 30), (20, 26, 38))
        for i, t in enumerate(tiles): strip.paste(t, (360 * i, 30))
        ImageDraw.Draw(strip).text((8, 5), short + ('  (loop)' if anim.loop else ''), font=font, fill='white')
        strip.save(os.path.join(REN, anim.name + '.png'))
    index.append(dict(name=anim.name, frames=anim.length, seconds=round(anim.length / ak.FPS, 2), loop=anim.loop, priority=anim.priority,
                      rig=anim.rig.name, markers=anim.markers, notes=anim.notes,
                      files=[f'assets/Phase2/Animations/{anim.name}.{e}' for e in ('rbxmx', 'fbx', 'json')]))
    print('ANIM', anim.name, anim.length, anim.markers)

if not only:
    with open(os.path.join(OUT, 'animations_index.json'), 'w') as f:
        json.dump(index, f, indent=1)
