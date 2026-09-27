"""Phase 1 / Buildings: machiya townhouses A-F assembled from the kit (roof, walls, interior, doors)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import ho, bpy
import buildkit as bk

SPECS = {  # name: W, D, storeys, front, noren colour, sign
    'A': dict(W=12, D=12, storeys=1, front='open', noren='Navy', sign=True),
    'B': dict(W=16, D=20, storeys=2, front='koshi', noren='Indigo', sign=True),
    'C': dict(W=16, D=20, storeys=2, front='open', noren='Crimson', sign=True),
    'D': dict(W=20, D=20, storeys=2, front='mixed', noren='Ochre', sign=True),
    'E': dict(W=24, D=20, storeys=2, front='koshi', noren='Navy', sign=True),
    'F': dict(W=12, D=20, storeys=2, front='koshi', noren='Indigo', sign=False),
}
which = sys.argv[1:] or list(SPECS)
render = os.environ.get('HO_RENDER', '1') == '1'
for k in which:
    sp = SPECS[k]
    ho.reset()
    name = f'HO_Bldg_Machiya_{k}'
    objs = bk.machiya(name, seed=ord(k), **sp)
    W, D = sp['W'], sp['D']
    # interior camera: standing in the doma just inside the front, looking toward the back room
    cams = {'interior': ((-W / 2 + 2.2, D / 2 - 1.6, 5.2), (W / 2 - 3.0, -D / 2 + 3.0, 2.8), 16,
                         [(W / 2 - 2.0, -D / 2 + 2.0, 4.6), (-W / 2 + 3.0, 0.0, 6.5), (2.0, D / 2 - 4.0, 7.0)])}
    ho.publish_group(objs, name, 'Buildings', grid=4, footprint=(W, D), render=render, samples=36,
                     views=('three_quarter', 'front'), cams=cams,
                     notes=f"{W}x{D} footprint, {sp['storeys']} storey(s), {sp['front']} front, {sp['noren']} noren; "
                           f"ground-floor interior (doma, shop floor, tatami room{', stair chest' if sp['storeys'] > 1 else ''}); "
                           f"SignFace mesh = blank board for a SurfaceGui")
