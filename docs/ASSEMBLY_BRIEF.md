# Hollow Oath: Roblox Studio assembly brief

You are the Roblox Studio builder for **Hollow Oath**, an Edo-Japan-inspired anime action RPG. A separate AI is producing the 3D assets in Blender and delivering them as FBX files + PNG textures. **Your job is to import those assets and assemble the capital city in Roblox Studio, following the layout plan exactly.** Asset delivery is ongoing: build what exists now, block out everything else with placeholders, and swap the placeholders when the real assets arrive.

## Files you have

- `assets/Phase0/Test/HO_Test_ScaleCube_1x1x1.fbx`: scale test. **Do this first.**
- `assets/Phase1/Roofs/*.fbx`: finished roof modules (see table below)
- `textures/<Set>/HO_T_<Set>_{Color,Normal,Roughness,Metalness}.png`: shared PBR texture sets
- `MANIFEST.md`: every asset: file, triangle count, size, textures, notes
- `docs/PIPELINE.md`: export conventions
- `docs/layout/HO_City_LayoutPlan.png`: labelled top-down city plan
- `docs/layout/city_layout.json`: the same plan as data. **Build the city from this file.**

## Step 1: verify scale (do not skip)

1. File → Import 3D → `HO_Test_ScaleCube_1x1x1.fbx`.
2. In the import settings set **File Dimensions → Scale Unit = Stud**. Leave "Set Pivot to Origin" off.
3. The MeshPart **Size must read 1, 1, 1**. The red **FRONT** face must point along the part's LookVector (−Z). **TOP** is +Y, the green **RIGHT** face is +X.
4. If the size is anything else, **stop and report the exact Size shown**. Never rescale meshes in Roblox to compensate. The Blender side will fix the export.

## Step 2: import rules (every asset)

- Always Scale Unit = Stud. Never resize or rotate imported meshes, except for the Y rotation used to place them.
- Conventions: **1 stud = 1 unit. Front of every asset = −Z (LookVector). Up = +Y. Pivot = bottom-centre of the asset's bounding box.** After import, set each Model's pivot (`Model.WorldPivot`) to the bottom-centre of its bounding box, if the importer moved it.
- Multi-mesh assets (e.g. a roof = `_Tiles` + `_Frame`) import as one Model. Keep the parts together and don't move them relative to each other.
- **Every mesh object uses exactly ONE texture set**, so every MeshPart gets exactly one SurfaceAppearance. The set is in the part name after `__` (e.g. `HO_Bldg_Machiya_C_Structure__Timber_Dark` → `Timber_Dark`). Parts without `__` use a single set, listed in `MANIFEST.md → Mesh objects and their texture set`. SurfaceAppearance for set `X`: ColorMap = `HO_T_X_Color`, NormalMap = `_Normal`, RoughnessMap = `_Roughness`, MetalnessMap = `_Metalness`. `require(game.ServerStorage.HO_CityBuilder).ApplyTextures()` does this automatically from `ReplicatedStorage/HO_Materials/<Set>` templates.
- Parts that belong together share the name before `__`. For example, a sliding door is `…_Door1__Timber_Light` + `…_Door1__Shoji_Paper`: move/tween all parts of a group together (`HO_CityBuilder.GroupParts(model)` returns them grouped).
- **Upload each texture set once and reuse the same asset IDs everywhere.** Create one template SurfaceAppearance per set in `ReplicatedStorage/HO_Materials/<Set>` and clone it onto parts.
- MeshPart settings: `Anchored = true`. Roof tiles, ornaments and small props: `CanCollide = false`, `CanQuery = false`, `CanTouch = false`, `CollisionFidelity = Box`. For walkable or blocking geometry, add simple invisible collision parts instead of precise mesh collision. `RenderFidelity = Automatic`.
- Store every imported asset as a template in `ReplicatedStorage/HO_Assets/<Category>/<AssetName>` and place clones in Workspace. Never edit the placed copies individually.

## Step 3: world coordinates (from city_layout.json)

The plan uses X = east (0..900), Y = north (0..1200), `elev` = height in studs above sea level. Convert to Roblox with:

```lua
local function planToWorld(x, y, elev)
	return Vector3.new(x - 450, elev, 600 - y) -- north = -Z, city centred on the origin
end
```

Facing (the direction the building's front faces) → rotation about Y (asset fronts point −Z = north by default):

```lua
local FACING_YAW = { N = 0, W = math.rad(90), S = math.rad(180), E = math.rad(-90) }
-- cf = CFrame.new(planToWorld(x, y, elev)) * CFrame.Angles(0, FACING_YAW[facing], 0)
-- model:PivotTo(cf)
```

Put the JSON into a ModuleScript that returns the string, and decode it with `HttpService:JSONDecode`. Then write **one build script** (`ServerScriptService/HO_BuildCity`, plus an editor command/plugin version) that generates the whole city from the data, so it can be rebuilt whenever the layout or assets change. Put everything under `Workspace/City` with sub-folders: `Terrain`, `Walls`, `Streets`, `Buildings`, `Castle`, `Harbour`, `Props`, `Nature`.

### What each JSON section means

| Key | Build |
|---|---|
| `tiers` | Ground platforms: polygon at height `elev` (Harbour +4, Lower Town +8, Middle +20, Upper +32, San-no-maru +46, Ni-no-maru +62, Hon-maru +80). Fill down to sea level. Use Terrain (Ground/Grass/Rock) or large anchored parts. |
| tier edges | Stone retaining walls (ishigaki) wherever a tier drops to a lower one. **Placeholder:** battered (sloped) Slate/granite-coloured wedge parts until `HO_Wall_Ishigaki_*` arrives. |
| `sea`, `inlet` | Terrain Water at height 0. The inlet is a canal with stone walls. |
| `cliffs`, `rocks` | Terrain Rock, rising well above the tiers behind the castle. `rocks` = sea rocks (centre `c`, radius `r`); the largest carries the lighthouse. |
| `streets` | Paths of given `width` along `path` points. Main/cross streets use Cobblestone; alleys use packed dirt. |
| `stairs` | Stone stairs at centre `c`, footprint `size`, rising between the two tier heights in `rise` (e.g. "32→20"). Steps ~1 stud high. |
| `key_buildings` | Special buildings (centre `c`, footprint `size`, `facing`, `elev`). **Placeholder:** a block of the footprint size + a proper roof module on top, with a `BillboardGui` label showing its `label` until the real building arrives. |
| `machiya_lots` | 363 townhouse lots: centre `x,y`, width `w`, depth `d`, `facing`, `elev`, `asset`. **Use the finished `HO_Bldg_Machiya_*` buildings (Step 4b).** Use Machiya A where `d` = 12. Ignore the `storeys` field: each variant has a fixed height. |
| `torii`, `gates`, `yagura` | Red torii, castle gatehouses, corner watchtowers (placeholders for now). |
| `piers` | Wooden piers from x0 = 772 heading east (`length` 92, `width` 12) at plan-y `y`, with a T-end. Deck at +4. |
| `bridge`, `causeway` | Arched bridge over the canal; stone causeway from the quay to the lighthouse rock. |
| `kura`, `wells`, `trees` | Warehouses (24×20 footprint), wells, pine trees (`size` S/M/L). |

## Step 4: roofs (finished, use now)

A roof covers exactly its **footprint** (the outer faces of the walls). Its pivot is at the **wall top**. Place it at `(building centre, elev + wall height)`, rotated to the building's facing; the eaves overhang past the walls automatically. Wall height = 9 studs per storey. The ridge runs along the building's width (local X). The front eave faces the street.

| Asset | Footprint W×D (studs) | Use for |
|---|---|---|
| `HO_Roof_Irimoya_Small` | 16×12 | shops, gatehouses, yagura top tier |
| `HO_Roof_Irimoya_Medium` | 24×16 | Tidewatch Inn, Armory, larger houses |
| `HO_Roof_Irimoya_Large` | 32×24 | Academy Hall, castle buildings |
| `HO_Roof_Kirizuma_Small` | 12×12 | 12-wide machiya (includes the gable end walls) |
| `HO_Roof_Kirizuma_Large` | 20×16 | 16–24-wide machiya |
| `HO_Roof_Hisashi_4 / _8 / _12` | 4 / 8 / 12 wide, 3 deep | awning over shop fronts; back face flush on the front wall, bottom ~7–8 studs above the street |

If a lot's size doesn't match a roof exactly, use the closest roof that is **not smaller** than the footprint. Only if needed, stretch it along X by at most 25% (`Model:ScaleTo` is not allowed; resize the placeholder walls instead). Report any footprints that need a new roof size.

## Step 4b: finished buildings (use instead of placeholders)

**Machiya townhouses**: `assets/Phase1/Buildings/HO_Bldg_Machiya_A…F.fbx`. Each one is complete: stone plinth, walls, doors, ground-floor interior, awning, noren, sign and roof.

- **Pivot = centre of the footprint at ground level.** Place each at `planToWorld(lot.x, lot.y, lot.elev)`, rotated by `FACING_YAW[lot.facing]`. The street side is the building's front (−Z). The roof, awning and noren overhang the footprint; that's intended.
- Sizes (W × D): A 12×12 (1 storey), B 16×20, C 16×20, D 20×20, E 24×20, F 12×20 (2 storeys). The layout's `asset` field already names the right variant by width. **For lots with `d` = 12, use Machiya A** (the others are 20 deep).
- Mesh parts: `_Structure`, `_Interior`, `_Front`, `_RoofTiles`, `_RoofFrame`, `_SignFace`, `_Door1…n`.
  - `_Door*` are sliding doors. To open one, tween it along its local X by its own width (about 1.8–2 studs).
  - `_SignFace` is the blank sign board: put a SurfaceGui on it with the shop name.
  - Add a warm PointLight (Range 14, Brightness 1.5) at the andon lantern in the back room, and one in the doma.
- Collision: give `_Structure` and `_Interior` `CollisionFidelity = PreciseConvexDecomposition`. That keeps walls, floors and the doorway walkable. Make the other parts non-collidable. Doors: CanCollide on, toggled off while open.

**Special buildings**: `assets/Phase1/Buildings/`. Same pivot and facing rules; see `docs/AI_WORKPLAN.md` Phases D–E for placement and gameplay hookup:
`HO_Bldg_TidewatchInn` (40×24), `HO_Bldg_Blacksmith` (20×24), `HO_Bldg_Armory` (16×20), `HO_Bldg_GeneralStore` (20×16), `HO_Bldg_MagicStall` (8×12), `HO_Bldg_Kura` (20×24). The `_Glow` meshes (lanterns, embers, orbs) should be Neon with a PointLight.

**Wall kit** (`assets/Phase1/Walls`, `Fronts`, `Foundations`), for custom buildings:

- Every wall is exactly **L × 1 × 9** (L = 4/8/12/16). The pivot is at the bottom-centre of the wall. The **outside face is the front (−Z)**. Put the wall's centre line **0.5 stud inside** the footprint edge. The wall runs along the footprint edge with its full outer length; walls on adjacent sides overlap at the corners.
- Put `HO_Wall_CornerPost` (1.4 × 1.4 × 9) centred 0.5 inside both edges at every corner. It hides the corner overlap.
- Stack: `HO_Found_Plinth_*` (1 stud tall, same placement as the walls; corner blocks at corners), then ground floor walls starting at y = 1, then upper walls at y = 10, then the roof at the top wall height.
- Types: `Plaster_Solid`, `Plaster_Window` (shoji windows), `Plaster_Lattice`, `Upper_Mushiko` (upper-floor slat windows), `Front_Koshi` (lattice shop front with sliding door), `Front_OpenShop` (open front with counter), `Door_Shoji` (sliding panels are separate meshes).
- `HO_Wall_Balcony_8/12`: the back face goes on the wall; the deck top is pivot + 1.6.
- `HO_Prop_Noren_4/8_<Colour>`: hang the rod just under the door band (7 studs above the floor), 0.3 stud out from the wall.
- `HO_Prop_Signboard_Hanging / Roof / Standing`: each has a `_Face` mesh for the text.

## Step 5: look & lighting (golden hour)

- `Lighting.Technology = Future`, `ClockTime ≈ 17.4`, `GeographicLatitude ≈ 35`, warm `Ambient`/`OutdoorAmbient` (low), `EnvironmentDiffuseScale 1`, `EnvironmentSpecularScale 1`.
- `Atmosphere`: Density ~0.3, warm orange Color, blue-grey Decay, Haze ~1.5. Add `Bloom` (subtle), `SunRays` (subtle) and `ColorCorrection` (slightly warm, +contrast).
- Warm point lights (orange, range ~12) in lanterns along the streets and waterfront. Keep shadows on for large structures only.

## Step 6: performance

- `Workspace.StreamingEnabled = true`. Group each building as a Model with `ModelStreamingMode = Atomic`. Make the castle keep and the city silhouette `Persistent`, so they are always visible from a distance.
- Reuse templates (clones), share SurfaceAppearances, keep props non-collidable. Target under 150k visible triangles in the street view; check the MicroProfiler.

## Step 7: report back after each pass

1. The scale-cube result (Size shown).
2. Screenshots: the full city from the sea (the reference angle), a street-level view in the lower town, and the castle approach.
3. Every problem found: wrong scale, flipped or rotated asset, gaps between roof and walls, z-fighting, missing textures, a footprint with no matching roof.
4. The list of placeholders still in use.

**Never** modify, decimate or rescale the delivered meshes yourself. Report issues and the Blender side will re-export. New assets are listed in `MANIFEST.md` as they are delivered; swap them in by name.
