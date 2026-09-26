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
- ⬜ Tatami, Cloth (noren / banner, tintable), Red_Lacquer (torii), Bamboo, Pine needles / bark, Rope, Sail cloth

## 2b. Roofs (top priority)
- ✅ Irimoya S (16×12), M (24×16), L (32×24): curved cover-tile rows, stepped pan courses, disc eave tiles, stacked ridges + onigawara, upturned corners, rafters / brackets / purlin / corner beams, plaster gable with timber pattern, barge boards, gegyo
- ⬜ Kirizuma gable roof ×2
- ⬜ Hisashi pent roof / shop awning (4 / 8 / 12 wide)
- ⬜ Chidori gable, Karahafu (castle)
- ⬜ Snap pieces: straight ridge (4/8 studs), ridge end, eave corner, eave straight (4/8)

## 2c. Walls & fronts (8 / 12 / 16 wide, 9-stud floors)
- ⬜ Plaster + timber frame: solid / window / lattice window
- ⬜ Koshi lattice shop front, open shop front + counter, shoji doors, noren (colours), blank signboards
- ⬜ 2nd-floor balcony + railing, mushiko windows, stone foundation plinths

## 2d. Buildings (kit assemblies, also exported whole)
- ⬜ Machiya A–F (12–24 wide, 1–2 storeys, ground-floor interiors)
- ⬜ Tidewatch Inn (lobby, corridor, 6 rooms)
- ⬜ Blacksmith, Armory, General Store, Magic Stall, Kura warehouse

## 2e. Castle & fortifications
- ⬜ Ishigaki modules (straight / corner / stepped, fitted stones)
- ⬜ Castle wall (straight / corner / end), yagura, gatehouse
- ⬜ Keep: 5 tiers, exported per tier, with shachihoko
- ⬜ Academy Hall (dojo + interior)

## 2f. Harbour & props
- ⬜ Quay wall + steps, pier modules, 2 boats, lighthouse, arched bridge, stone stairs, torii, tōrō, chōchin, banner poles, carts, barrels, crates, sake jars, sacks, market stalls, benches, well, bamboo fences, pines ×3, cliff rocks ×3
