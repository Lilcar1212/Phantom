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
- The importer creates **one MeshPart per material**. Give each MeshPart a **SurfaceAppearance** using the texture set named by its material (`HO_M_<Set>` → `textures/<Set>/`): ColorMap = `_Color`, NormalMap = `_Normal`, RoughnessMap = `_Roughness`, MetalnessMap = `_Metalness`.
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
| `machiya_lots` | 363 townhouse lots: centre `x,y`, width `w`, depth `d`, `facing`, `storeys` (1–2), `elev`, `asset` (HO_Bldg_Machiya_A–F, still in production). **Placeholder:** walls 9 studs per storey (white-plaster colour, dark wood trim) + the matching roof (below). |
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
