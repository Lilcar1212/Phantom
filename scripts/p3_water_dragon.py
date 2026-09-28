"""Phase 3 / Detailed water dragon (Twin Dragons) + whirlpool."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import ho
import dragonkit as dk
from mathutils import Matrix, Vector

render = os.environ.get('HO_RENDER', '1') == '1'
PH, CAT = 'Phase3', 'VFX'


def lifted(objs, dz):
    out = []
    for o in objs:
        c = o.copy(); c.data = o.data.copy(); ho.link(c)
        c.data.transform(Matrix.Translation((0, 0, dz))); c.data.update(); out.append(c)
    return out


NOTE_COMMON = ('Fine glossy scales (Dragon_Scales), silver belly plates (Dragon_Belly), horned head with open jaws, teeth, '
               'tongue, glowing blue-white eyes (Glow_Blue -> Neon), long whiskers. Living-water parts use Water_Flame, whose '
               'colour map has ALPHA: set the SurfaceAppearance AlphaMode = Transparency (or MeshPart Transparency 0.2) so '
               'the water looks see-through. Meshes: <name> (body/head/legs, split per texture set), <name>_Fins '
               '(spine crest, elbow tufts, tail plume), <name>_Mane (head mane, splash tendrils, whiskers, water crowns), '
               '<name>_Droplets (loose drops; delete if not wanted). Horns/claws/teeth = Dragon_Horn.')
for pose, name, extra in (
        ('flight', 'HO_VFX_WaterDragon', 'Flight pose (~44 long) for Twin Dragons: head faces FRONT (-Z), origin = centre of '
                                          'its bounding box. Move it along a path with CFrame lerps; 2 of them = Twin Dragons. '),
        ('rearing', 'HO_VFX_WaterDragon_Rearing', 'Rearing pose (~45 wide, ~34 tall): coiled on the water with chest and head '
                                                 'raised, front claws reaching forward, splash crowns where it touches the water. '
                                                 'Origin = water line under the chest (place it at the water surface); faces FRONT '
                                                 '(-Z). Use for the summon / boss reveal, rising out of HO_VFX_Whirlpool. ')):
    ho.reset()
    bs = dk.water_dragon(pose)
    objs = ho.split_single_material([ho.builder_obj(name + suf, b) for suf, b in zip(('', '_Fins', '_Mane', '_Droplets'), bs)])
    lo, hi = ho.world_bbox(objs)
    dz = (-lo.z + 1.0) if pose == 'flight' else 0.0
    tip = max((v.co for o in objs for v in o.data.vertices if o.name.startswith(name + '__')), key=lambda c: c.y)
    head = Vector((tip.x, tip.y - 3.0, tip.z + dz))
    size = (hi - lo).length
    ctr = (lo + hi) / 2 + Vector((0, 0, dz))
    cams = {'head': (head + Vector((0.55, 1.0, 0.18)).normalized() * size * 0.3, head, 50),
            'hero': (ctr + Vector((0.15, 1.0, 0.12)).normalized() * size * 1.05, ctr, 40)}
    ho.publish_group(objs, name, CAT, phase=PH, render=render, samples=32,
                     pivot='bounding-box centre' if pose == 'flight' else 'water line under the chest',
                     render_objs=(lifted(objs, dz) if (render and dz) else None), views=('three_quarter', 'side'), cams=cams,
                     notes=extra + NOTE_COMMON)
ho.reset()
w = ho.builder_obj('HO_VFX_Whirlpool', dk.whirlpool())
ho.publish_group([w], 'HO_VFX_Whirlpool', CAT, phase=PH, render=render, samples=24, pivot='rim centre',
           render_objs=lifted([w], 3.0) if render else None,
           notes='Whirlpool funnel R 10, 2.6 deep (VFX_Water / HO_VFXT_Water.png). U spirals around - scroll OffsetStudsU '
                 'to spin it; V centre -> rim. Origin = rim centre at water level; the dragon can rise out of it.')
