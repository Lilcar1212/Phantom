"""Phase 1 / Castle: ishigaki modules, castle walls, keep (whole + per tier), yagura, gatehouse, Academy Hall."""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import ho, bpy
import castlekit as ck

render = os.environ.get('HO_RENDER', '1') == '1'
only = set(sys.argv[1:])
S = 32


def want(name):
    return not only or any(o in name for o in only)


ISH = ('Origin = bottom of the wall directly below the TOP edge of the stone face (the terrace edge); '
       'the battered base flares out toward the front (-Z) by 3 studs; solid fill 4 studs behind. Height 16.')
modules = [
    ('HO_Wall_Ishigaki_Straight_16', lambda: ck.ishigaki_straight(16, seed=11), '16 long. ' + ISH),
    ('HO_Wall_Ishigaki_Straight_8', lambda: ck.ishigaki_straight(8, seed=12), '8 long. ' + ISH),
    ('HO_Wall_Ishigaki_Corner_Outer', lambda: ck.ishigaki_corner(16, seed=13),
     'Convex corner, 16 each way; origin = the corner of the top edge; platform lies behind (+Z) and left (-X); interlocking corner stones. Height 16.'),
    ('HO_Wall_Ishigaki_Corner_Inner', lambda: ck.ishigaki_corner(16, seed=14, inner=True),
     'Concave corner, 16 each way; origin = the re-entrant corner of the top edge. Height 16.'),
    ('HO_Wall_Ishigaki_Stepped_16', lambda: ck.ishigaki_stepped(16, seed=15),
     '16 long; left half 16 tall, right half 12 tall (steps down 4). ' + ISH),
    ('HO_Wall_Castle_Straight_16', lambda: ck.dobei(16, seed=21),
     'Castle wall (dobei) 16 long x 1.6 thick: stone footing, white plaster, loopholes, tiled coping. Origin = bottom centre on the wall centre line; outside face = front (-Z).'),
    ('HO_Wall_Castle_End_16', lambda: ck.dobei(16, kind='end', seed=22), 'As straight, with a capped end pillar at +X.'),
    ('HO_Wall_Castle_Corner', lambda: ck.dobei(16, kind='corner', seed=23),
     'L-shaped corner: legs 16 long toward -X and toward +Z (back); origin = the corner on the wall centre lines.'),
]
for name, fn, notes in modules:
    if not want(name): continue
    ho.reset(); random.seed(hash(name) & 0xffff)
    ob = ho.builder_obj(name, fn())
    ho.apply_transforms(ob)
    ho.publish(ob, 'Castle', render=render, samples=S, notes=notes)

if want('HO_Castle_Keep'):
    ho.reset()
    objs, groups = ck.keep()
    for g, gobjs in groups.items():
        ho.publish_group(gobjs, f'HO_Castle_Keep_{g}', 'Castle', render=False,
                         notes='Keep part exported on its own: shares the keep origin, place at the SAME CFrame as the '
                               'other keep parts (they stack automatically).')
    allobjs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    ho.publish_group(allobjs, 'HO_Castle_Keep', 'Castle', render=render, samples=S, views=('three_quarter', 'front'),
                     notes='Five-tier keep on a 16-tall ishigaki base (base top 44x36, foot 50x42). Origin = bottom centre '
                           'of the stone base; front (karahafu gable) faces -Z. Tiers: white walls + lattice windows, tiled '
                           'skirts, karahafu (tier 1), chidori (tiers 2-3), red-railed balcony + gold shachihoko on top. '
                           'Also exported per part: HO_Castle_Keep_Base / _Tier1 .. _Tier5.')

for name, fn, cams, notes in (
        ('HO_Castle_Yagura', ck.yagura, None,
         '16x12 two-tier watchtower on a stone plinth; pivot = footprint centre at ground; front faces -Z.'),
        ('HO_Castle_Gatehouse', ck.gatehouse, None,
         '28x12 gate: stone gate towers, 12-wide passage, iron-strapped doors (Door1/Door2 groups swing on the hinge posts at x = +-6), '
         'upper floor, castle roof, navy crest banners. Pivot = footprint centre at ground; front faces -Z.'),
        ('HO_Castle_AcademyHall', ck.academy_hall,
         {'interior': ((-19.0, 11.5, 9.0), (6.0, -12.0, 5.0), 16, [(0, 0, 10), (-12, -8, 9), (12, 6, 9)])},
         '44x28 Sword Academy dojo (+2.6 veranda all round): raised floor at +3, front steps, shoji doors in the centre bays, '
         'interior with kamidana shelf, weapon + spear racks, sword stands, taiko drum, lanterns (Glow). Pivot = footprint centre at ground.')):
    if not want(name): continue
    ho.reset()
    objs = fn()
    ho.publish_group(objs, name, 'Castle', render=render, samples=S, views=('three_quarter', 'front'), cams=cams, notes=notes)
