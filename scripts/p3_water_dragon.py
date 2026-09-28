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


ho.reset()
b, d = dk.water_dragon()
objs = ho.split_single_material([ho.builder_obj('HO_VFX_WaterDragon', b), ho.builder_obj('HO_VFX_WaterDragon_Droplets', d)])
lo, hi = ho.world_bbox(objs)
dz = -lo.z + 1.0
tip = max((v.co for o in objs for v in o.data.vertices), key=lambda c: c.y)
head = Vector((tip.x, tip.y - 3.0, tip.z + dz))
cams = {'head': (head + Vector((9.0, 8.0, 3.0)), head, 50),
        'hero': (Vector((34.0, 36.0, 16.0 + dz)), Vector((0, 1.0, dz)), 40)}
ho.publish_group(objs, 'HO_VFX_WaterDragon', CAT, phase=PH, render=render, samples=32, pivot='bounding-box centre',
                 render_objs=lifted(objs, dz) if render else None, views=('three_quarter', 'side', 'front'), cams=cams,
                 notes='Detailed Eastern water dragon for Twin Dragons, about 44 long (head faces FRONT, -Z; origin = centre '
                       'of its bounding box). Scaled body (Dragon_Scales) with a plated belly (Dragon_Belly); horned head with '
                       'open jaws, teeth, forked tongue, glowing eyes (Glow_Yellow -> Neon), long whiskers and a water-flame '
                       'mane; flowing water fins along the spine, four clawed legs with water tufts at the elbows, splashing '
                       'tail plume (Water_Flame: V root -> tip, looks best at Transparency 0.1-0.2), plus loose droplets '
                       '(_Droplets, delete if not wanted). Horns/claws/teeth = Dragon_Horn. Move it along a path with CFrame '
                       'lerps; 2 of them = Twin Dragons.')
ho.reset()
w = ho.builder_obj('HO_VFX_Whirlpool', dk.whirlpool())
ho.publish_group([w], 'HO_VFX_Whirlpool', CAT, phase=PH, render=render, samples=24, pivot='rim centre',
           render_objs=lifted([w], 3.0) if render else None,
           notes='Whirlpool funnel R 10, 2.6 deep (VFX_Water / HO_VFXT_Water.png). U spirals around - scroll OffsetStudsU '
                 'to spin it; V centre -> rim. Origin = rim centre at water level; the dragon can rise out of it.')
