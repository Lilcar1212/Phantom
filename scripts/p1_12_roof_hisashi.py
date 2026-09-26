"""Phase 1 / Roofs: HO_Roof_Hisashi_{4,8,12} pent roof / shop awning (back face mounts flush to a wall)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import ho, bpy, bmesh
from roofkit import Hisashi, MATS

which = [int(w) for w in sys.argv[1:]] or [4, 8, 12]
render = os.environ.get('HO_RENDER', '1') == '1'
for W in which:
    ho.reset()
    b = Hisashi(W, P=3.0).build()
    bmesh.ops.remove_doubles(b.bm, verts=b.bm.verts, dist=1e-5)
    asset = f'HO_Roof_Hisashi_{W}'
    ob = ho.mesh_from_bm(asset, b.bm, [ho.material(m) for m in MATS])
    ho.finalize(ob, recalc_normals=False)
    ho.publish(ob, 'Roofs', grid=4, footprint=(W, 4), render=render, samples=40,
               views=('three_quarter', 'front', 'under'),
               notes=f'{W} studs wide, projects 3 studs; back (-Z in Roblox = rear) face mounts flush on a wall face, typically 7-8 studs above street level')
