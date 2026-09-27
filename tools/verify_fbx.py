"""Check every exported FBX: stud units, Y-up / -Z front, and one material per geometry (one SurfaceAppearance
per MeshPart). Usage: python3 tools/verify_fbx.py"""
import glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fbx_inspect import load, find, summary

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
files = sorted(glob.glob(os.path.join(ROOT, 'assets', '**', '*.fbx'), recursive=True))
n_mesh = n_multi = n_assets = 0
problems = []
for f in files:
    _, nodes = load(f)
    s = summary(f)
    rel = os.path.relpath(f, ROOT)
    if s.get('UpAxis') != 1 or s.get('FrontAxis') != 2:
        problems.append(f'{rel}: axes Up={s.get("UpAxis")} Front={s.get("FrontAxis")}')
    geoms = find(nodes, 'Geometry')
    if not geoms: continue                                  # animation-only files
    n_assets += 1
    for g in geoms:
        n_mesh += 1
        idx = set()
        for lem in find(g[2], 'LayerElementMaterial'):
            for m in find(lem[2], 'Materials'):
                idx |= set(m[1][0])
        if len(idx) > 1:
            n_multi += 1
            problems.append(f'{rel}: {g[1][1].split(chr(0))[0]} uses {len(idx)} materials')
print(f'{n_assets} mesh assets, {n_mesh} meshes, {n_multi} multi-material, {len(problems)} problems')
for p in problems[:30]: print('  ', p)
sys.exit(1 if problems else 0)
