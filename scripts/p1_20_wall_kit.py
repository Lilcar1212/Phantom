"""Phase 1 / Walls & fronts kit + foundations + balconies + noren."""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import ho, bpy
import wallkit as wk

render = os.environ.get('HO_RENDER', '1') == '1'
only = set(sys.argv[1:])
V = ('three_quarter', 'front')
S = 32


def pub(name, w_or_b, category, notes, footprint=None, grid=4, views=V):
    if only and not any(name.startswith(o) or o in name for o in only):
        return
    ho.reset()
    random.seed(hash(name) & 0xffff)
    if isinstance(w_or_b, wk.WallBuilder):
        objs = [ho.builder_obj(name, w_or_b.b)] + [ho.builder_obj(f'{name}_{dn}', db) for dn, db in w_or_b.doors]
    else:
        objs = [ho.builder_obj(name, w_or_b)]
    ho.finalize_group(objs)
    if len(objs) == 1:
        ho.publish(objs[0], category, grid=grid, footprint=footprint, render=render, views=views, samples=S, notes=notes)
    else:
        ho.publish_group(objs, name, category, grid=grid, footprint=footprint, render=render, views=views, samples=S,
                         notes=notes + ' | door panels are separate meshes (slide along local X to open)')


WALLN = 'L x 1 x 9 studs; outside face = front (-Z); centre line 0.5 inside the footprint edge'
jobs = []
for L in (8, 12, 16):
    jobs.append((f'HO_Wall_Plaster_Solid_{L}', lambda L=L: wk.wall(L, ['plaster'] * (L // 4)), 'Walls', WALLN, (L, 1)))
for L in (8, 12):
    n = L // 4
    win = ['window'] * n if L == 8 else ['plaster', 'window', 'plaster']
    lat = ['lattice'] * n if L == 8 else ['plaster', 'lattice', 'plaster']
    mus = ['mushiko'] * n if L == 8 else ['plaster', 'mushiko', 'mushiko']
    kos = ['koshi', 'door'] if L == 8 else ['koshi', 'door', 'koshi']
    jobs += [
        (f'HO_Wall_Plaster_Window_{L}', lambda win=win, L=L: wk.wall(L, win), 'Walls', WALLN + '; shoji windows', (L, 1)),
        (f'HO_Wall_Plaster_Lattice_{L}', lambda lat=lat, L=L: wk.wall(L, lat), 'Walls', WALLN + '; lattice windows', (L, 1)),
        (f'HO_Wall_Upper_Mushiko_{L}', lambda mus=mus, L=L: wk.wall(L, mus), 'Walls', WALLN + '; upper floor, mushiko slat windows', (L, 1)),
        (f'HO_Wall_Front_Koshi_{L}', lambda kos=kos, L=L: wk.wall(L, kos), 'Fronts', WALLN + '; koshi lattice shop front with sliding lattice door (7-stud opening)', (L, 1)),
        (f'HO_Wall_Front_OpenShop_{L}', lambda L=L: wk.open_shop(L), 'Fronts', WALLN + '; open shop front with counter; hang noren under the door band (z = 7)', (L, 1)),
    ]
for L in (4, 8):
    jobs.append((f'HO_Wall_Door_Shoji_{L}', lambda L=L: wk.wall(L, ['shoji'] * (L // 4)), 'Fronts', WALLN + '; sliding shoji doors (interior or exterior)', (L, 1)))
jobs.append(('HO_Wall_CornerPost', lambda: wk.corner_post(), 'Walls', '1.3 x 1.3 x 9; place centred on each building corner, 0.5 inside both footprint edges', None))
for L in (4, 8, 12, 16):
    jobs.append((f'HO_Found_Plinth_{L}', lambda L=L: wk.plinth(L, seed=L), 'Foundations', 'L x 1.6 x 1 stone plinth under walls (walls start at z = 1); centred on the wall centre line', (L, None)))
jobs.append(('HO_Found_Plinth_Corner', lambda: wk.plinth(1.6, corner=True), 'Foundations', '1.6 x 1.6 x 1 corner block', None))
for L in (8, 12):
    jobs.append((f'HO_Wall_Balcony_{L}', lambda L=L: wk.balcony(L), 'Fronts', f'{L} wide, projects 2.5; back face mounts on the wall; deck top = pivot + 1.6 (put the deck at the 2nd-floor level)', (L, None)))
for col in ('Navy', 'Indigo', 'Crimson', 'Ochre'):
    for W in (4, 8):
        jobs.append((f'HO_Prop_Noren_{W}_{col}', lambda W=W, col=col: wk.noren(W, mat='Cloth_' + col), 'Props', f'{W} wide curtain, 3.55 tall; hang so the rod sits just under the door band (rod top at z = 7 above floor)', None))

for name, fn, cat, notes, fp in jobs:
    grid = 4 if fp and fp[0] and fp[0] % 4 == 0 else None
    fpx = (fp[0], fp[1] or 1) if fp else None
    if only and not any(name.startswith(o) or o in name for o in only):
        continue
    pub(name, fn(), cat, notes, footprint=(fp[0], 4) if fp else None, grid=None)
