"""Phase 1 / Roofs: HO_Roof_Irimoya_{Small,Medium,Large}  (each = _Tiles + _Frame meshes, one pivot)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import ho, bpy, bmesh
from roofkit import Irimoya, MATS

SIZES = {
    'Small': dict(W=16, D=12, overhang=2.5, gable_overhang=0.7),
    'Medium': dict(W=24, D=16, overhang=3.0, gable_overhang=0.8),
    'Large': dict(W=32, D=24, overhang=3.5, gable_overhang=1.0),
}
which = sys.argv[1:] or list(SIZES)
render = os.environ.get('HO_RENDER', '1') == '1'
for name in which:
    ho.reset()
    r = Irimoya(pitch=0.66, t_gable=0.56, **SIZES[name])
    b = r.build()
    bmesh.ops.remove_doubles(b.bm, verts=b.bm.verts, dist=1e-5)
    asset = f'HO_Roof_Irimoya_{name}'
    ob = ho.mesh_from_bm(asset, b.bm, [ho.material(m) for m in MATS])
    ho.finalize(ob, recalc_normals=False)
    parts = ho.split_by_material(ob, {'_Tiles': ['RoofTile_Clay'], '_Frame': None})
    if ho.tri_count(parts[0]) > 18000:          # keep every mesh safely under Roblox's 20k limit
        parts = ho.split_by_axis(parts[0], 1, ('Front', 'Back')) + parts[1:]
    p = SIZES[name]
    ho.publish_group(parts, asset, 'Roofs', grid=4, footprint=(p['W'], p['D']), render=render,
                     views=('three_quarter', 'front', 'side', 'under'), samples=40,
                     notes=f"Footprint {p['W']}x{p['D']} studs (outer wall faces); place on wall top; eave overhang {p['overhang']}")
