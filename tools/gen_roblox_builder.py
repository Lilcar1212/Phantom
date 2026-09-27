"""Generate roblox/HO_CityBuilder.lua: a ModuleScript that builds the whole capital city in Roblox Studio
from docs/layout/city_layout.json. Real imported assets (by name, in ServerStorage.HO_Assets) replace
placeholders automatically.

Run:  python3 tools/gen_roblox_builder.py
"""
import json, re, os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fbx_inspect

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'roblox'); os.makedirs(OUT, exist_ok=True)


def lua(v, ind=0):
    if isinstance(v, bool): return 'true' if v else 'false'
    if isinstance(v, (int, float)):
        return repr(round(v, 3)) if isinstance(v, float) else str(v)
    if isinstance(v, str): return json.dumps(v, ensure_ascii=False)
    if isinstance(v, (list, tuple)):
        return '{' + ','.join(lua(x) for x in v) + '}'
    if isinstance(v, dict):
        return '{' + ','.join(f'{k}={lua(x)}' if k.isidentifier() else f'[{json.dumps(k)}]={lua(x)}' for k, x in v.items()) + '}'
    raise TypeError(type(v))


layout = json.load(open(os.path.join(ROOT, 'docs', 'layout', 'city_layout.json')))
# asset bounds (Roblox space == FBX space; origin = asset pivot)
bounds = {}
for f in glob.glob(os.path.join(ROOT, 'assets', '**', '*.fbx'), recursive=True):
    name = os.path.splitext(os.path.basename(f))[0]
    s = fbx_inspect.summary(f)
    if not s['geometry']: continue
    lo = [min(g['min'][i] for g in s['geometry']) for i in range(3)]
    hi = [max(g['max'][i] for g in s['geometry']) for i in range(3)]
    bounds[name] = {'c': [(lo[i] + hi[i]) / 2 for i in range(3)], 's': [hi[i] - lo[i] for i in range(3)]}

data = dict(
    tiers=layout['tiers'], sea=layout['sea'], inlet=layout['inlet'], cliffs=layout['cliffs'],
    rocks=layout['rocks'], streets=layout['streets'], stairs=layout['stairs'],
    key=layout['key_buildings'], torii=layout['torii'], gates=layout['gates'], yagura=layout['yagura'],
    piers=layout['piers'], bridge=layout['bridge'], causeway=layout['causeway'], kura=layout['kura'],
    wells=layout['wells'], lots=[{k: l[k] for k in ('asset', 'x', 'y', 'w', 'd', 'facing', 'elev')} for l in layout['machiya_lots']],
    trees=layout['trees'],
)
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'roblox_builder_template.lua')).read()
# mesh object -> texture set, for single-material parts whose names carry no "__<Set>" suffix
# (read from the exported FBX files themselves, so every mesh Roblox sees is covered)
mesh_set = {}
unresolved = []
for f in glob.glob(os.path.join(ROOT, 'assets', '**', '*.fbx'), recursive=True):
    if os.sep + 'Animations' + os.sep in f: continue          # animation files: R6 proxy meshes only
    for mesh, mats in fbx_inspect.mesh_materials(f).items():
        if not mats or '__' in mesh: continue
        sets = {re.sub(r'(_[0-9a-f]{6})?(\.\d+)?$', '', m[len('HO_M_'):]) for m in mats if m.startswith('HO_M_')}
        if len(sets) == 1 and os.path.isdir(os.path.join(ROOT, 'textures', next(iter(sets)))):
            mesh_set[mesh] = sets.pop()
        else:
            unresolved.append((mesh, mats))
if unresolved:
    print('WARNING meshes without a single texture set:', unresolved[:10])
src = src.replace('--[[DATA]]', 'local DATA = ' + lua(data)).replace('--[[BOUNDS]]', 'local BOUNDS = ' + lua(bounds))
src = src.replace('--[[MESHSET]]', 'local MESH_SET = ' + lua(mesh_set))
with open(os.path.join(OUT, 'HO_CityBuilder.lua'), 'w') as f:
    f.write(src)
print('wrote roblox/HO_CityBuilder.lua', len(src), 'chars;', len(bounds), 'asset bounds')
