"""Phase 1 / Buildings: special gameplay buildings (Tidewatch Inn, Blacksmith, Armory, General Store,
Magic Stall, Kura)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import ho, bpy
import specialkit as sk

L = 'Pivot = footprint centre at ground level; front faces -Z (street). '
JOBS = {
    'TidewatchInn': (sk.tidewatch_inn, 40, 24,
                     L + '2 storeys. GF: genkan, lobby w/ reception counter + key board, dining hall, stair. 2F: corridor + 6 guest rooms '
                         '(tatami, futon, low table, cushions, andon, tansu, sliding door = Door_Room1..6 meshes). Glow mesh = lanterns.',
                     {'lobby': ((-2.0, 10.5, 5.5), (-10.0, 3.0, 3.0), 18, [(-7.0, 5.8, 4.0), (0.0, 4.0, 7.5), (-8.0, -5.0, 6.0)]),
                      'room': ((-1.5, 2.6, 16.8), (-8.0, 9.8, 11.4), 17, [(-7.0, 7.0, 14.0), (-12.0, 9.0, 13.5)])}),
    'Blacksmith': (sk.blacksmith, 20, 24,
                   L + 'Open front. Forge + chimney, bellows, anvil, quench trough, wall + standing sword racks, tool rack. Glow mesh = forge embers.',
                   {'interior': ((6.5, 10.5, 6.0), (-3.5, -7.0, 3.0), 18, [(-4.0, -8.0, 5.5), (2.0, 2.0, 8.0)])}),
    'Armory': (sk.armory, 16, 20,
               L + '2 storeys. Four lacquered samurai armour stands, spear rack, katana stands + wall racks, counter; crates upstairs.',
               {'interior': ((0.0, 8.8, 5.5), (0.0, -6.0, 4.0), 17, [(0.0, 3.0, 7.5), (0.0, -5.0, 7.0)])}),
    'GeneralStore': (sk.general_store, 20, 16,
                     L + '2 storeys, open shop front with counter. Shelves of jars, rice bales, sacks, sake casks, barrels, crates, scale + abacus.',
                     {'interior': ((0.0, 6.8, 6.0), (0.0, -6.0, 3.0), 17, [(0.0, 2.0, 7.5), (-5.0, -3.0, 7.0)])}),
    'MagicStall': (sk.magic_stall, 8, 12,
                   L + 'Open market stall: canopy, counter, tiered shelves with glowing orbs + crystals, paper lanterns, charms. Glow mesh = orbs/crystals/lanterns (Neon + PointLight).',
                   None),
    'Kura': (sk.kura, 20, 24,
             L + 'Fire-proof storehouse: 1.6-thick plaster walls, namako tile-lattice lower walls, heavy plaster doors (open) + inner lattice door (Door1), barred windows, crest on gables.',
             None),
}
which = sys.argv[1:] or list(JOBS)
render = os.environ.get('HO_RENDER', '1') == '1'
for k in which:
    fn, W, D, notes, cams = JOBS[k]
    ho.reset()
    objs = fn()
    ho.publish_group(objs, f'HO_Bldg_{k}', 'Buildings', grid=4, footprint=(W, D), render=render, samples=36,
                     views=('three_quarter', 'front'), cams=cams, notes=f'{W}x{D} footprint. ' + notes)
