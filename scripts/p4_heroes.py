"""Phase 4 / Hero models: katanas + scabbards, R6 armour sets, floating stone fists, Earth Golem, the Hollow.

Also writes assets/Phase4/rigs.json (mesh -> body part + centre offsets) used by tools/gen_rig_builder.py.
"""
import sys, os, json, random, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import ho, bpy
import herokit as hk
from mathutils import Vector, Matrix

render = os.environ.get('HO_RENDER', '1') == '1'
only = set(sys.argv[1:])
PH = 'Phase4'
RIGS_JSON = os.path.join(ho.ROOT, 'assets', PH, 'rigs.json')
rigs = json.load(open(RIGS_JSON)) if os.path.exists(RIGS_JSON) else {}

# Roblox rest centres of the R6 parts relative to the HumanoidRootPart centre (scale 1)
R6_REST = {'Torso': (0, 0, 0), 'Head': (0, 1.5, 0), 'Right Arm': (1.5, 0, 0), 'Left Arm': (-1.5, 0, 0),
           'Right Leg': (0.5, -2, 0), 'Left Leg': (-0.5, -2, 0)}
PART_KEY = {'Torso': 'Torso', 'Head': 'Head', 'Right Arm': 'RightArm', 'Left Arm': 'LeftArm',
            'Right Leg': 'RightLeg', 'Left Leg': 'LeftLeg'}


def b2r(v):
    """Blender (X right, Y front, Z up) -> Roblox (X right, Y up, front = -Z)."""
    return [round(v[0], 4), round(v[2], 4), round(-v[1], 4)]


def r2b(v):
    return Vector((v[0], -v[2], v[1]))


def want(name):
    return not only or any(o in name for o in only)


def clone_offset(objs, offset):
    """Copies of objs moved by `offset` (for previews that need a different placement than the export)."""
    out = []
    for o in objs:
        c = o.copy(); c.data = o.data.copy(); ho.link(c)
        c.data.transform(Matrix.Translation(Vector(offset))); c.data.update()
        out.append(c)
    return out


def centres(objs):
    out = {}
    for o in objs:
        lo, hi = ho.world_bbox([o])
        out[o.name] = (lo + hi) / 2
    return out


# ================================================================================================ WEAPONS
WEAPON_NOTES = {
    'IronKatana': 'Iron Katana (starter): plain round iron tsuba, black saya.',
    'TemperedKatana': 'Tempered Katana: longer, deeper curve, squared tsuba with gold fittings.',
    'AshfallSword': 'Ashfall Sword: broad dark-steel blade, heavy octagonal tsuba, smouldering amber edge (_Glow).',
    'CrimsonOath': 'Crimson Oath: ornate gold mokko (flower) tsuba, red lacquer saya, glowing red edge (_Glow).',
    'MoonlitEdge': 'Moonlit Edge: crescent-notched tsuba, navy saya, pale blue glowing edge (_Glow).',
}
W_PIVOT = ('Origin = centre of the grip (hand position). Blade points FRONT (-Z), cutting edge DOWN (-Y); '
           'as a Tool handle it works with Tool.Grip = identity.')
for name in hk.KATANAS:
    aname = f'HO_Weapon_{name}'
    if not want(aname): continue
    ho.reset(); random.seed(1)
    b, s, g = hk.katana(name)
    objs = [ho.builder_obj(aname, b)]
    if g: objs.append(ho.builder_obj(aname + '_Glow', g))
    objs = ho.split_single_material(objs)
    L = hk.KATANAS[name]['L']
    rigs[aname] = dict(kind='weapon', meshes={o: dict(offset=b2r(c)) for o, c in centres(objs).items()})
    lift = clone_offset(objs, (0, -L / 2, 1.2)) if render else None
    ho.publish_group(objs, aname, 'Weapons', phase=PH, render=render, samples=32, render_objs=lift,
                     views=('three_quarter', 'side', 'front'), pivot='grip centre',
                     notes=WEAPON_NOTES[name] + ' ' + W_PIVOT + f' Blade {L} long. Scabbard = {aname}_Saya.')
    ho.reset()
    so = ho.split_single_material([ho.builder_obj(aname + '_Saya', s)])
    rigs[aname + '_Saya'] = dict(kind='weapon', meshes={o: dict(offset=b2r(c)) for o, c in centres(so).items()})
    lift = clone_offset(so, (0, -L / 2, 1.2)) if render else None
    ho.publish_group(so, aname + '_Saya', 'Weapons', phase=PH, render=render, samples=32, render_objs=lift,
                     views=('three_quarter', 'side'), pivot='grip centre',
                     notes=f'Scabbard for {aname}, same origin frame: at the same CFrame as the sword the blade sits '
                           'inside it (sheathed). Weld to the Torso/hip for the sheathed look.')

# ================================================================================================ ARMOUR
PIECES = [('Torso', 'Torso', lambda s: hk.armour_torso(s)),
          ('RightArm', 'Right Arm', lambda s: hk.armour_arm(s, 1)),
          ('LeftArm', 'Left Arm', lambda s: hk.armour_arm(s, -1)),
          ('RightLeg', 'Right Leg', lambda s: hk.armour_leg(s, 1)),
          ('LeftLeg', 'Left Leg', lambda s: hk.armour_leg(s, -1)),
          ('Helmet', 'Head', lambda s: hk.armour_helmet(s))]
ARMOUR_NOTES = {'Ashigaru': 'Ashigaru foot-soldier set: black lacquer lames, navy lacing, iron trim, conical jingasa hat.',
                'Samurai': 'Samurai set: red lacquer plates, black lames, crimson lacing, gold trim, kabuto with kuwagata horns.',
                'Oathguard': 'Oathguard (elite) set: navy lacquer, white lacing, gold trim, kabuto with gold ring crest.'}


def dummy(h=3.0):
    """Grey R6 mannequin for armour previews (Blender coords, standing on z=0)."""
    d = hk.B()
    for part, c in R6_REST.items():
        bc = r2b(c) + Vector((0, 0, h))
        if part == 'Head':
            d.cylinder((bc.x, bc.y, bc.z - 0.6), (bc.x, bc.y, bc.z + 0.6), 0.6, 16, 'Cloth_White')
            continue
        sx, sy, sz = (2, 1, 2) if part == 'Torso' else (1, 1, 2)
        d.box((bc.x - sx / 2, bc.y - sy / 2, bc.z - sz / 2), (bc.x + sx / 2, bc.y + sy / 2, bc.z + sz / 2), 'Cloth_White')
    return ho.builder_obj('_Dummy', d)


for sname in hk.ARMOUR:
    aname = f'HO_Armor_{sname}'
    if not want(aname): continue
    ho.reset()
    objs, placed, mesh_map = [], [], {}
    for key, part, fn in PIECES:
        pobjs = ho.split_single_material([ho.builder_obj(f'{aname}_{key}', fn(sname))])
        for o, c in centres(pobjs).items():
            mesh_map[o] = dict(part=part, offset=b2r(c))
        objs += pobjs
        if render:
            placed += clone_offset(pobjs, r2b(R6_REST[part]) + Vector((0, 0, 3.0)))
    rigs[aname] = dict(kind='armour', meshes=mesh_map)
    if render: placed.append(dummy())
    ho.publish_group(objs, aname, 'Armour', phase=PH, render=render, samples=32, render_objs=placed,
                     views=('three_quarter', 'front', 'back'), pivot='body-part centre',
                     notes=ARMOUR_NOTES[sname] + ' One mesh per R6 body part, each modelled in that part\'s local '
                     'space (part centre = origin). Weld each MeshPart to its body part with the offset listed in '
                     'roblox/HO_RigBuilder.lua (ARMOUR table) - HO_RigBuilder.EquipArmor(character, "' + sname + '") does it.')

# ================================================================================================ STONE FISTS
for side, sname in ((1, 'Right'), (-1, 'Left')):
    aname = f'HO_Hero_StoneFist_{sname}'
    if not want(aname): continue
    ho.reset()
    b, g = hk.stone_fist(side)
    objs = ho.split_single_material([ho.builder_obj(aname, b), ho.builder_obj(aname + '_Glow', g)])
    rigs[aname] = dict(kind='weapon', meshes={o: dict(offset=b2r(c)) for o, c in centres(objs).items()})
    lift = clone_offset(objs, (0, 0, 2.2)) if render else None
    ho.publish_group(objs, aname, 'Heroes', phase=PH, render=render, samples=32, render_objs=lift,
                     views=('three_quarter', 'front', 'side'), pivot='fist centre',
                     notes=f'Floating carved-stone {sname.lower()} fist punching toward FRONT (-Z), glowing amber cracks '
                           'and knuckle joints (_Glow, set Material Neon or a PointLight). Origin = centre of the fist; '
                           'broken forearm stump trails behind (+Z). ~2.6 wide x 4.7 long.')

# ================================================================================================ GOLEM / HOLLOW
CHARS = [('HO_Char_EarthGolem', hk.golem, 'Earth Golem at rig scale 2.4 (about 12 studs tall): stacked granite blocks, '
          'boulder shoulders, huge block fists, glowing yellow eyes and amber chest cracks.'),
         ('HO_Char_Hollow', hk.hollow, 'The Hollow (R6 size): black shadow body, glowing red slit-pupil eye in the chest '
          'with red cracks, swept horns, clawed hands, tattered shadow wisps.')]
for aname, fn, desc in CHARS:
    if not want(aname): continue
    ho.reset()
    parts, s = fn()
    objs, mesh_map = [], {}
    for part, (b, g) in parts.items():
        off = r2b([c * s for c in R6_REST[part]]) + Vector((0, 0, 3.0 * s))     # character space, feet on z=0
        pobjs = [ho.builder_obj(f'{aname}_{PART_KEY[part]}', b)]
        if g: pobjs.append(ho.builder_obj(f'{aname}_{PART_KEY[part]}_Glow', g))
        pobjs = ho.split_single_material(pobjs)
        for o in pobjs:
            o.data.transform(Matrix.Translation(off)); o.data.update()
        for o, c in centres(pobjs).items():
            mesh_map[o] = dict(part=part, offset=b2r(c - off))
        objs += pobjs
    rigs[aname] = dict(kind='character', scale=s, meshes=mesh_map)
    ho.publish_group(objs, aname, 'Characters', phase=PH, render=render, samples=32,
                     views=('three_quarter', 'front', 'back'), pivot='feet (ground) centre',
                     notes=desc + f' Meshes are in character space (feet at y=0, HumanoidRootPart centre at y={3 * s:g}). '
                     f'HO_RigBuilder.BuildCharacter(model, "{aname}") adds a HumanoidRootPart, invisible R6 body parts '
                     'with Motor6Ds (classic R6 C0/C1 x scale) and welds the meshes on, so the Phase 2 KeyframeSequences '
                     '(Golem_* / Hollow_*) play directly.')

os.makedirs(os.path.dirname(RIGS_JSON), exist_ok=True)
json.dump(rigs, open(RIGS_JSON, 'w'), indent=1)
print('wrote', RIGS_JSON)

# ================================================================================================ MAGIC ICONS
if want('HO_Icon_Magic'):
    import subprocess
    subprocess.run([sys.executable, os.path.join(ho.ROOT, 'tools', 'gen_icons.py')], check=True)
    for el, desc in (('Fire', 'three-tongue flame'), ('Water', 'droplet over waves'), ('Earth', 'mountain peaks over a cracked slab')):
        ho.manifest_add(dict(name=f'HO_Icon_Magic_{el}', phase=PH, category='Icons', type='Image 512x512 PNG (alpha)',
                             file=f'assets/{PH}/Icons/HO_Icon_Magic_{el}.png', tris='', textures=[], pivot='-', checks={},
                             renders=['renders/Phase4/Icons/HO_Icon_Magic_sheet.png'],
                             notes=f'{el} magic emblem: navy disc, gold rims, 16-rune band, glowing {desc}. '
                                   'Upload as an Image/Decal for ImageLabels (transparent outside the circle).'))
