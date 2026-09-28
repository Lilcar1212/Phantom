"""Phase 4 / Fishing: three Edo-period rods, float, hook, creel, and eight Japanese fish."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import ho
import fishkit as fk
from mathutils import Matrix

render = os.environ.get('HO_RENDER', '1') == '1'
PH = 'Phase4'


def lifted(objs, off):
    out = []
    for o in objs:
        c = o.copy(); c.data = o.data.copy(); ho.link(c)
        c.data.transform(Matrix.Translation(off)); c.data.update(); out.append(c)
    return out


def rb(tip):
    """Blender -> Roblox coordinates of the rod tip."""
    return f'({tip.x:.2f}, {tip.z:.2f}, {-tip.y:.2f})'


RODS = [
    ('HO_Tool_FishingRod_Bamboo', fk.rod_bamboo, 'Starter rod (takezao): one natural bamboo pole ~7 long with nodes, rope-bound grip and a '
                                                 'white line tie at the tip.'),
    ('HO_Tool_FishingRod_Lacquered', fk.rod_lacquered, 'Edo jointed rod (wazao) ~9 long: four bamboo sections in black lacquer, red lacquer '
                                                       'bands, silk-wrapped ferrules with gold rings, braided silk grip, gold butt cap, red tip.'),
    ('HO_Tool_FishingRod_Master', fk.rod_master, 'Master rod ~10 long: red lacquer with black bands and gold-leaf rings, cherry-bark grip, '
                                                 'gold guide rings and a wooden hand reel (tebata) with wound line and crank.'),
]
for name, fn, desc in RODS:
    ho.reset()
    b, tip = fn()
    objs = ho.split_single_material([ho.builder_obj(name, b)])
    ho.publish_group(objs, name, 'Tools', phase=PH, render=render, samples=32, pivot='grip centre',
                     render_objs=lifted(objs, (0, -tip.y / 2, 1.4)) if render else None, views=('three_quarter', 'side'),
                     notes=desc + ' Origin = centre of the grip (the hand). The rod points FRONT (-Z) and droops at the tip; '
                                  f'line-tie point (tip) in Roblox studs relative to the origin: {rb(tip)} - put an Attachment '
                                  'there and hang HO_Tool_Fishing_Float / _Hook on a RopeConstraint or Beam. As a Tool: Handle '
                                  'at the grip, Tool.Grip = CFrame.Angles(math.rad(-30), 0, 0) to hold it raised.')

PROPS = [
    ('HO_Tool_Fishing_Float', fk.float_uki, 'Red-and-white float (uki) 0.6 tall with antenna; origin = line eye at the bottom.'),
    ('HO_Tool_Fishing_Hook', fk.hook, 'Hand-forged iron J hook with barb and eye, lead sinker and a short snood; origin = hook eye.'),
    ('HO_Prop_FishCreel', fk.creel, 'Woven bamboo fish creel (biku) 1.4 tall with lid and rope strap; origin = bottom centre. '
                                    'Wear it on the hip or put caught fish in it.'),
]
for name, fn, desc in PROPS:
    ho.reset()
    objs = ho.split_single_material([ho.builder_obj(name, fn())])
    lo, hi = ho.world_bbox(objs)
    ho.publish_group(objs, name, 'Tools' if 'Tool' in name else 'Props', phase=PH, render=render, samples=32,
                     pivot='see notes', render_objs=lifted(objs, (0, 0, -lo.z + 0.3)) if render and lo.z < 0 else None,
                     views=('three_quarter', 'front'), notes=desc)

FISH = {
    'Ayu': 'Ayu (sweetfish), 1.1 long: olive back, silver flanks, yellow gill spot. Common river catch.',
    'Koi': 'Koi, 1.8 long: white with red-orange patches, barbels, red fins. Pond / castle moat.',
    'Koi_Gold': 'Golden koi (ogon), 1.8 long: metallic gold body and fins. Rare catch.',
    'Tai': 'Tai (red sea bream), 1.6 long: deep red body with blue spots, spiny dorsal, red fins. Prized sea catch.',
    'Saba': 'Saba (mackerel), 1.4 long: blue-green back with black wavy stripes, silver belly, finlets, deep forked tail.',
    'Maguro': 'Maguro (bluefin tuna), 5 long: navy back, silver belly, yellow finlets, crescent tail. Legendary big catch.',
    'Fugu': 'Fugu (pufferfish), 0.9 long: round spotted body, dark blotch behind the fins, white belly, big eyes.',
    'Unagi': 'Unagi (eel), 3 long: dark olive back, yellow belly, long ribbon fins; S-curved body.',
}
for key, desc in FISH.items():
    name = f'HO_Fish_{key}'
    ho.reset()
    objs = ho.split_single_material([ho.builder_obj(name, fk.fish(key))])
    lo, hi = ho.world_bbox(objs)
    ho.publish_group(objs, name, 'Fish', phase=PH, render=render, samples=32, pivot='body centre',
                     render_objs=lifted(objs, (0, 0, -lo.z + 0.25)) if render else None, views=('three_quarter', 'side'),
                     notes=desc + ' Origin = centre of the body; head FRONT (-Z), back up. Fins use Fish_Fin* sets (colour map '
                                  'has alpha: SurfaceAppearance AlphaMode = Transparency). Eyes = Fish_Eye.')
