# Phase 1: Capital city build order

Order: materials → modules → assemblies. Each asset is rendered, triangle-counted, checked and entered in `MANIFEST.md` before the next one starts.

Status: ✅ done · 🔨 in progress · ⬜ to do

## 0. Foundation
- ✅ Pipeline (`tools/ho.py`, `tools/geo.py`), FBX inspector, manifest
- ✅ Scale / orientation test cube + FBX settings (`docs/PIPELINE.md`)

## 1. Layout plan
- ✅ `docs/layout/HO_City_LayoutPlan.png`: 900 × 1200 studs, labelled
- ✅ `docs/layout/city_layout.json`: the same plan as data (tiers, streets, stairs, 363 machiya lots, key buildings, piers, trees) for scripted placement

## 2a. Materials (shared texture library)
- ✅ RoofTile_Clay, Timber_Dark, Timber_Light, Plaster_White, Stone_Granite, Stone_Fitted, Cobblestone, Wood_Planks, Gold_Leaf, Iron_Wrought, Shoji_Paper
- ✅ Tatami, Cloth (White/Navy/Indigo/Crimson/Ochre), Red_Lacquer, Earth_Packed
- ✅ Black_Lacquer, Namako_Wall, Straw, Ember, Magic_Glow
- ⬜ Bamboo, Pine needles / bark, Rope, Sail cloth

## 2b. Roofs (top priority)
- ✅ Irimoya S (16×12), M (24×16), L (32×24): curved cover-tile rows, stepped pan courses, disc eave tiles, stacked ridges + onigawara, upturned corners, rafters / brackets / purlin / corner beams, plaster gable with timber pattern, barge boards, gegyo
- ✅ Kirizuma gable roof S (12×12), L (20×16)
- ✅ Hisashi pent roof / shop awning 4 / 8 / 12 wide
- ✅ Chidori gable, Karahafu, tiered skirt roofs, gold shachihoko (castle; in tools/castlekit.py)
- ⬜ Snap pieces: straight ridge (4/8 studs), ridge end, eave corner, eave straight (4/8)

## 2c. Walls & fronts (8 / 12 / 16 wide, 9-stud floors)
- ✅ Plaster + timber frame: solid (8/12/16) / window (8/12) / lattice window (8/12), corner post
- ✅ Koshi lattice shop front (8/12, sliding door), open shop front + counter (8/12), shoji doors (4/8), noren 4/8 × 4 colours, blank signboards (hanging / over-door / standing)
- ✅ 2nd-floor balcony + railing (8/12), mushiko windows (8/12), stone foundation plinths (4/8/12/16 + corner)

## 2d. Buildings (kit assemblies, also exported whole)
- ✅ Machiya A–F (12–24 wide, 1–2 storeys, ground-floor interiors: doma, kamado, shop floor, shelves, tatami room, shoji partition, stair chest)
- ✅ Tidewatch Inn (genkan, lobby + reception, dining hall, stair, corridor, 6 furnished rooms with sliding doors)
- ✅ Blacksmith, Armory, General Store, Magic Stall, Kura warehouse (all with interiors/props)
- ✅ Props library: futon, low table, andon, tansu, barrels, komodaru, tawara, sacks, jars, crates, shelves, counter, katana, sword racks, samurai armour, spear rack, anvil, forge, bellows, quench trough, tool rack, orbs, crystals, ofuda, chochin

## 2e. Castle & fortifications
- ✅ Ishigaki modules: Straight 16/8, Corner Outer/Inner (sangi-zumi interlock), Stepped 16 (fitted stones, fan-slope batter)
- ✅ Castle wall (dobei): straight 16, end, corner (stone footing, plaster, loopholes, tiled coping); yagura (2 tiers); gatehouse (iron-strapped doors, banners)
- ✅ Keep: 5 tiers on a 16-tall ishigaki base, exported whole + per part (Base, Tier1-5), karahafu/chidori gables, balcony, gold shachihoko
- ✅ Academy Hall (raised dojo, veranda, shoji doors; interior: kamidana, weapon racks, taiko, lanterns)

## 2f. Harbour & props
- ⬜ Quay wall + steps, pier modules, 2 boats, lighthouse, arched bridge, stone stairs, torii, tōrō, chōchin, banner poles, carts, barrels, crates, sake jars, sacks, market stalls, benches, well, bamboo fences, pines ×3, cliff rocks ×3
