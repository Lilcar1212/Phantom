"""Phase 1 / Harbour, street props and nature."""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import ho, bpy
import harborkit as hk
import propkit as pk
from castlekit import banner

render = os.environ.get('HO_RENDER', '1') == '1'
only = set(sys.argv[1:])
GROUND = 'Origin = centre at ground level; front faces -Z.'


def single(fn):
    def f():
        b = pk.B(); fn(b); return b
    return f


JOBS = [
    # name, category, builder fn -> Builder | (Builder, glow) | (Builder, face), notes
    ('HO_Harbour_Quay_16', 'Harbour', lambda: hk.quay(16), 'Quay wall 16 long, 8 tall fitted stone + cap stones (top at +8.6). Origin = bottom of the wall under the top face edge; put the origin at z = -4.6 so the cap meets the +4 promenade; the face looks out to sea (-Z).'),
    ('HO_Harbour_Quay_Steps_16', 'Harbour', lambda: hk.quay(16, steps=True), 'Quay wall with a flight of stone steps down the face to the water (same origin as Quay_16).'),
    ('HO_Harbour_Pier', 'Harbour', hk.pier_full, 'Whole pier 92 long x 12 wide with a 28x16 T-head, rope rails, bollards, cargo. Origin = shore end centre at SEA LEVEL; deck top +4; extends toward the front (-Z); piles to -8.'),
    ('HO_Harbour_Pier_Deck_8', 'Harbour', lambda: (lambda b: (hk.pier_segment(b, 0.0, 8.0), b)[1])(hk.B()), 'Pier segment 8 long x 12 wide (tile along the front axis). Origin = segment start centre at sea level; deck top +4.'),
    ('HO_Harbour_Boat_Small', 'Harbour', hk.boat_small, 'Small sailing/fishing boat ~16 long, square sail, oar. Origin = keel bottom centre; waterline about +1.0; bow = front.'),
    ('HO_Harbour_Boat_Cargo', 'Harbour', hk.boat_cargo, 'Cargo ship ~36 long: deck house, 30-tall mast, big stitched sail, rudder, cargo. Origin = keel bottom centre; waterline about +2.2; bow = front.'),
    ('HO_Harbour_Lighthouse', 'Harbour', hk.lighthouse, 'Lighthouse ~34 tall: stone base, white tower, red-railed gallery, glowing lantern room (_Glow), tiled roof, gold finial. Origin = base centre (stand it on the sea rock at +12).'),
    ('HO_Harbour_ArchBridge', 'Harbour', hk.arch_bridge, 'Arched wooden bridge, span 64 along the front axis, 12 wide, rise 6, vermilion rails with gold finials, pile bents. Origin = centre at DECK-END level (both ends at z = 0); piles to -10.'),
    ('HO_Prop_StoneStairs_Straight', 'Props', lambda: hk.stone_stairs(), '8 wide, 5 steps (rise 0.8, run 1.2): climbs away from the front. ' + GROUND),
    ('HO_Prop_StoneStairs_Turning', 'Props', lambda: hk.stone_stairs(turning=True), '8 wide: 5 steps up to an 8x8 landing, then 5 more turning 90 deg. ' + GROUND),
    ('HO_Prop_Torii', 'Props', hk.torii, 'Red torii 12 wide x 13 tall, passage along the front axis; _Face = blank plaque. ' + GROUND),
    ('HO_Prop_StoneLantern', 'Props', hk.stone_lantern, 'Kasuga stone lantern 5.4 tall; fire-box windows glow (_Glow). ' + GROUND),
    ('HO_Prop_Chochin_Red', 'Props', lambda: hk.chochin_prop('Red_Lacquer'), 'Hanging paper lantern on a wall bracket (back = rear, on the wall); body = _Glow. Origin = bracket foot.'),
    ('HO_Prop_Chochin_Black', 'Props', lambda: hk.chochin_prop('Black_Lacquer'), 'As Chochin_Red with black caps.'),
    ('HO_Prop_Banner', 'Props', lambda: (lambda b: (banner(b, 1.1, 0.0, 0.0, h=12.0), b)[1])(hk.B()), 'Nobori banner pole 12 tall, navy cloth with white crest. ' + GROUND),
    ('HO_Prop_Cart', 'Props', lambda: hk.cart(False), 'Two-wheeled handcart, handles toward the front. ' + GROUND),
    ('HO_Prop_Cart_Loaded', 'Props', lambda: hk.cart(True), 'Handcart loaded with rice bales and sacks. ' + GROUND),
    ('HO_Prop_MarketStall_A', 'Props', lambda: hk.market_stall('Cloth_Crimson', 1), 'Market stall 8x5, crimson canopy, produce baskets, jars. ' + GROUND),
    ('HO_Prop_MarketStall_B', 'Props', lambda: hk.market_stall('Cloth_Indigo', 2), 'Market stall 8x5, indigo canopy. ' + GROUND),
    ('HO_Prop_Bench', 'Props', lambda: hk.bench(False), 'Plank bench 6 long. ' + GROUND),
    ('HO_Prop_Bench_Tea', 'Props', lambda: hk.bench(True), 'Tea-house bench with red felt and a big red parasol. ' + GROUND),
    ('HO_Prop_Well', 'Props', hk.well, 'Village well: stone ring, water, A-frame with tiled roof, pulley, bucket. ' + GROUND),
    ('HO_Prop_BambooFence_8', 'Props', lambda: hk.bamboo_fence(8.0), 'Bamboo fence module 8 long x 4 tall (tiles along X). ' + GROUND),
    ('HO_Prop_Barrel', 'Props', single(lambda b: pk.barrel(b)), 'Stave barrel. ' + GROUND),
    ('HO_Prop_SakeCask', 'Props', single(lambda b: pk.barrel(b, straw=True)), 'Straw-wrapped sake cask (komodaru). ' + GROUND),
    ('HO_Prop_Crate', 'Props', single(lambda b: pk.crate(b)), 'Wooden crate. ' + GROUND),
    ('HO_Prop_Sack', 'Props', single(lambda b: pk.sack(b)), 'Cloth sack. ' + GROUND),
    ('HO_Prop_RiceBale', 'Props', single(lambda b: pk.tawara(b)), 'Straw rice bale (tawara), lying along X. ' + GROUND),
    ('HO_Prop_SakeJar', 'Props', single(lambda b: pk.jar(b, h=1.8, r=0.8)), 'Ceramic sake / storage jar with lid. ' + GROUND),
    ('HO_Tree_Pine_S', 'Nature', lambda: hk.pine('S', 1), 'Sculpted pine ~10 tall. Origin = trunk base.'),
    ('HO_Tree_Pine_M', 'Nature', lambda: hk.pine('M', 2), 'Sculpted pine ~16 tall. Origin = trunk base.'),
    ('HO_Tree_Pine_L', 'Nature', lambda: hk.pine('L', 3), 'Sculpted pine ~24 tall. Origin = trunk base.'),
    ('HO_Rock_Cliff_S', 'Nature', lambda: hk.cliff_rock('S', 1), 'Rock ~6 across. Origin = base centre (sink it a little into the ground).'),
    ('HO_Rock_Cliff_M', 'Nature', lambda: hk.cliff_rock('M', 2), 'Rock ~14 across. Origin = base centre.'),
    ('HO_Rock_Cliff_L', 'Nature', lambda: hk.cliff_rock('L', 3), 'Rock ~28 across. Origin = base centre.'),
]
for name, cat, fn, notes in JOBS:
    if only and not any(o in name for o in only): continue
    ho.reset(); random.seed(hash(name) & 0xffff)
    res = fn()
    if isinstance(res, tuple):
        main, extra = res
        suffix = '_Face' if extra.mat_names == ['Timber_Light'] else '_Glow'
        objs = [ho.builder_obj(name, main), ho.builder_obj(name + suffix, extra)]
        ho.publish_group(objs, name, cat, render=render, samples=24, notes=notes)
    else:
        ob = ho.builder_obj(name, res)
        ho.publish(ob, cat, render=render, samples=24, notes=notes)
