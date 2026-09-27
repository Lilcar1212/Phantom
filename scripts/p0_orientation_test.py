"""Phase 0 / Orientation test (multi-mesh, no textures needed): red arrow points FRONT (-Z in Roblox),
white post stands at the BACK (+Z), green block on the RIGHT (+X). Import it next to the scale cube."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import ho
from geo import Builder

render = os.environ.get('HO_RENDER', '1') == '1'
ho.reset()
b = Builder(['Stone_Granite', 'Red_Lacquer', 'Plaster_White', 'Cloth_Ochre'])
b.box((-3, -3, 0), (3, 3, 0.4), 'Stone_Granite')                                     # base plate 6x6
b.box((-0.5, -1.8, 0.4), (0.5, 1.2, 0.8), 'Red_Lacquer')                             # arrow shaft
b.prism([(-1.4, 1.2), (1.4, 1.2), (0, 2.9)], (0, 0, 0.4), (1, 0, 0), (0, 1, 0), (0, 0, 1), 0.4, 'Red_Lacquer')  # head -> front
b.box((-0.4, -2.8, 0.4), (0.4, -2.0, 4.4), 'Plaster_White')                          # tall post at the back
b.box((2.0, -0.5, 0.4), (2.8, 0.5, 1.6), 'Cloth_Ochre')                              # block on the right
ob = ho.builder_obj('HO_Test_Orientation', b)
ho.publish(ob, 'Test', phase='Phase0', render=render, samples=24, footprint=(6, 6),
           notes='Orientation check (multi-mesh). In Studio the RED ARROW must point to -Z (the Front face / '
                 'LookVector of an unrotated part), the WHITE POST must be at +Z and the YELLOW block at +X. '
                 'If the arrow points +Z instead, report it: the importer is turning multi-mesh files.')
