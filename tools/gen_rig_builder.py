"""Generate roblox/HO_RigBuilder.lua from tools/rig_builder_template.lua + assets/Phase4/rigs.json."""
import json, os

ROOT = os.path.join(os.path.dirname(__file__), '..')


def lua(v, ind=1):
    pad = '\t' * ind
    if isinstance(v, dict):
        items = []
        for k, x in sorted(v.items()):
            key = k if k.isidentifier() else '[' + json.dumps(k, ensure_ascii=False) + ']'
            items.append(f'{pad}{key} = {lua(x, ind + 1)},')
        return '{\n' + '\n'.join(items) + '\n' + '\t' * (ind - 1) + '}'
    if isinstance(v, (list, tuple)):
        return '{' + ', '.join(lua(x, ind + 1) for x in v) + '}'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, (int, float)):
        return repr(round(v, 4))
    return json.dumps(v, ensure_ascii=False)


rigs = json.load(open(os.path.join(ROOT, 'assets', 'Phase4', 'rigs.json')))
src = open(os.path.join(ROOT, 'tools', 'rig_builder_template.lua')).read()
src = src.replace('--[[RIGS]]', '-- mesh name -> body part + centre offset (Roblox studs, part-local / grip-local)\nlocal RIGS = ' + lua(rigs))
open(os.path.join(ROOT, 'roblox', 'HO_RigBuilder.lua'), 'w').write(src)
print('wrote roblox/HO_RigBuilder.lua', len(src), 'chars;', len(rigs), 'assets')
