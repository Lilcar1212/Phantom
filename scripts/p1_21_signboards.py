"""Phase 1 / Props: blank signboards (kanban). Each = frame mesh + separate _Face mesh for a SurfaceGui."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import ho, bpy
from geo import Builder
from buildkit import signboard_hanging, ALL_MATS

render = os.environ.get('HO_RENDER', '1') == '1'


def roof_sign():
    """Horizontal board over a door (yane-kanban): 4 x 1.3, small roof; mounts flat on the wall (back = -Y)."""
    b = Builder(ALL_MATS); f = Builder(['Timber_Light'])
    W, Hh = 4.4, 1.3
    b.beam_box((-W / 2, 0, 0), (W / 2, 0.3, 0.2), 'Timber_Dark', along='x')
    b.beam_box((-W / 2, 0, Hh - 0.2), (W / 2, 0.3, Hh), 'Timber_Dark', along='x')
    b.beam_box((-W / 2, 0, 0.2), (-W / 2 + 0.2, 0.3, Hh - 0.2), 'Timber_Dark', along='z')
    b.beam_box((W / 2 - 0.2, 0, 0.2), (W / 2, 0.3, Hh - 0.2), 'Timber_Dark', along='z')
    b.box((-W / 2 + 0.2, 0.0, 0.2), (W / 2 - 0.2, 0.12, Hh - 0.2), 'Timber_Dark')
    f.box((-W / 2 + 0.2, 0.12, 0.2), (W / 2 - 0.2, 0.22, Hh - 0.2), 'Timber_Light', uvd=0.22)
    # little tiled hood
    b.box((-W / 2 - 0.3, 0.0, Hh), (W / 2 + 0.3, 0.7, Hh + 0.12), 'Timber_Dark')
    # sloped tile hood (profile swept along X; sweep 'across' axis = -Y, so negative x = outward)
    b.sweep([(-W / 2 - 0.35, 0, 0), (W / 2 + 0.35, 0, 0)],
            [(0.0, Hh + 0.12), (0.0, Hh + 0.55), (-0.95, Hh + 0.22), (-0.95, Hh + 0.12)], 'RoofTile_Clay')
    return b, f


def standing_sign():
    """Free-standing sign (oki-kanban): board on a base with a small roof; faces +Y."""
    b = Builder(ALL_MATS); f = Builder(['Timber_Light'])
    b.box((-0.9, -0.5, 0), (0.9, 0.5, 0.5), 'Timber_Dark')
    for x in (-0.7, 0.7):
        b.beam_box((x - 0.12, -0.12, 0.5), (x + 0.12, 0.12, 4.0), 'Timber_Dark', along='z')
    b.box((-0.58, -0.08, 0.9), (0.58, 0.08, 3.6), 'Timber_Dark')
    f.box((-0.58, 0.08, 0.9), (0.58, 0.14, 3.6), 'Timber_Light', uvd=0.3)
    f.box((-0.58, -0.14, 0.9), (0.58, -0.08, 3.6), 'Timber_Light', uvd=0.3)
    b.beam_box((-0.85, -0.14, 3.6), (0.85, 0.14, 3.8), 'Timber_Dark', along='x')
    b.sweep([(-1.1, 0, 0), (1.1, 0, 0)], [(-0.55, 3.95), (0.55, 3.95), (0.0, 4.5)], 'RoofTile_Clay')
    b.box((-1.0, -0.5, 3.8), (1.0, 0.5, 3.95), 'Timber_Dark')
    return b, f


def hanging_sign():
    b = Builder(ALL_MATS); f = Builder(['Timber_Light'])
    signboard_hanging(b, f, 0.0, 0.0, 0.0)
    return b, f


for name, fn, notes in (
        ('HO_Prop_Signboard_Hanging', hanging_sign, 'Wall bracket + hanging board perpendicular to the wall; back (rear) plate mounts on the wall face; board faces +-X'),
        ('HO_Prop_Signboard_Roof', roof_sign, 'Over-door board 4.4 x 1.3 with tiled hood; back mounts flat on the wall face'),
        ('HO_Prop_Signboard_Standing', standing_sign, 'Free-standing street sign, 4.5 tall, two blank faces')):
    ho.reset()
    b, f = fn()
    objs = [ho.builder_obj(name, b), ho.builder_obj(name + '_Face', f)]
    ho.finalize_group(objs)
    ho.publish_group(objs, name, 'Props', render=render, samples=32,
                     notes=notes + ' | _Face mesh is the blank writing surface (add a SurfaceGui/Decal in Roblox)')
