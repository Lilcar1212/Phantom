"""Phase 1 / Roofs: HO_Roof_Kirizuma_{Small,Large}  (plain gable, machiya)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import ho, bpy, bmesh
from roofkit import Kirizuma, MATS

SIZES = {
    'Small': dict(W=12, D=12, overhang=2.0, gable_overhang=0.9),
    'Large': dict(W=20, D=16, overhang=2.5, gable_overhang=1.0),
}
which = sys.argv[1:] or list(SIZES)
render = os.environ.get('HO_RENDER', '1') == '1'
for name in which:
    ho.reset()
    r = Kirizuma(**SIZES[name])
    b = r.build()
    bmesh.ops.remove_doubles(b.bm, verts=b.bm.verts, dist=1e-5)
    asset = f'HO_Roof_Kirizuma_{name}'
    ob = ho.mesh_from_bm(asset, b.bm, [ho.material(m) for m in MATS])
    ho.finalize(ob, recalc_normals=False)
    parts = ho.split_by_material(ob, {'_Tiles': ['RoofTile_Clay'], '_Frame': None})
    p = SIZES[name]
    ho.publish_group(parts, asset, 'Roofs', grid=4, footprint=(p['W'], p['D']), render=render,
                     views=('three_quarter', 'front', 'side', 'under'), samples=40,
                     notes=f"Footprint {p['W']}x{p['D']} (outer wall faces); gable ends include the plaster gable walls; eave overhang {p['overhang']}")
