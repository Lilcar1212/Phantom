"""Minimal binary-FBX reader used to verify exported files (units, axes, raw vertex data).

Usage: python3 tools/fbx_inspect.py file.fbx
"""
import struct, sys, zlib


def _read_prop(f):
    t = f.read(1).decode()
    if t == 'Y': return struct.unpack('<h', f.read(2))[0]
    if t == 'C': return bool(f.read(1)[0])
    if t == 'I': return struct.unpack('<i', f.read(4))[0]
    if t == 'F': return struct.unpack('<f', f.read(4))[0]
    if t == 'D': return struct.unpack('<d', f.read(8))[0]
    if t == 'L': return struct.unpack('<q', f.read(8))[0]
    if t in 'SR':
        n = struct.unpack('<I', f.read(4))[0]
        b = f.read(n)
        return b.decode('utf8', 'replace') if t == 'S' else b
    if t in 'fdlib':
        n, enc, clen = struct.unpack('<III', f.read(12))
        data = f.read(clen)
        if enc: data = zlib.decompress(data)
        fmt = {'f': 'f', 'd': 'd', 'l': 'q', 'i': 'i', 'b': 'B'}[t]
        return list(struct.unpack('<%d%s' % (n, fmt), data))
    raise ValueError('unknown property type %r' % t)


def _read_node(f, ver):
    if ver >= 7500:
        end, nprops, plen = struct.unpack('<QQQ', f.read(24)); null = 25
    else:
        end, nprops, plen = struct.unpack('<III', f.read(12)); null = 13
    if end == 0:
        return None
    name = f.read(f.read(1)[0]).decode()
    props = [_read_prop(f) for _ in range(nprops)]
    kids = []
    while f.tell() < end - null:
        k = _read_node(f, ver)
        if k is None: break
        kids.append(k)
    f.seek(end)
    return (name, props, kids)


def load(path):
    with open(path, 'rb') as f:
        assert f.read(21) == b'Kaydara FBX Binary  \x00', 'not a binary FBX'
        f.read(2)
        ver = struct.unpack('<I', f.read(4))[0]
        nodes = []
        while True:
            n = _read_node(f, ver)
            if n is None: break
            nodes.append(n)
    return ver, nodes


def find(nodes, name):
    for n in nodes:
        if n[0] == name: yield n
        yield from find(n[2], name)


def summary(path):
    ver, nodes = load(path)
    out = {'version': ver}
    for gs in find(nodes, 'GlobalSettings'):
        for p in find(gs[2], 'P'):
            if p[1][0] in ('UpAxis', 'UpAxisSign', 'FrontAxis', 'FrontAxisSign', 'CoordAxis',
                           'CoordAxisSign', 'UnitScaleFactor', 'OriginalUnitScaleFactor'):
                out[p[1][0]] = p[1][-1]
    geoms = []
    for g in find(nodes, 'Geometry'):
        for v in find(g[2], 'Vertices'):
            a = v[1][0]
            xs, ys, zs = a[0::3], a[1::3], a[2::3]
            geoms.append({'name': g[1][1].split('\x00')[0], 'verts': len(xs),
                          'min': (min(xs), min(ys), min(zs)), 'max': (max(xs), max(ys), max(zs))})
    out['geometry'] = geoms
    models = []
    for m in find(nodes, 'Model'):
        d = {'name': m[1][1].split('\x00')[0]}
        for p in find(m[2], 'P'):
            if p[1][0] in ('Lcl Translation', 'Lcl Rotation', 'Lcl Scaling', 'PreRotation'):
                d[p[1][0]] = tuple(round(x, 4) for x in p[1][-3:])
        models.append(d)
    out['models'] = models
    return out


if __name__ == '__main__':
    import json
    print(json.dumps(summary(sys.argv[1]), indent=1))
