# Hollow Oath: Roblox Studio work plan (while the 3D models are being made)

**For the Roblox Studio builder AI.** Read `docs/ASSEMBLY_BRIEF.md` first; it covers the technical rules for importing and placing assets. This file lists **what to do, in what order**, so the city in Studio matches the reference art (the golden-hour coastal castle city image) while the remaining models are still in production. Everything built now must be easy to swap for the real models later. Use the exact asset names listed below.

**The target look** (from the reference image): a coastal Edo-era castle city at sunset.
- A 5-tier castle keep crowns a hill in the north, on terraces of massive curved stone walls.
- White plaster walls, dark timber and blue-grey tile roofs, with navy banners bearing a white crest.
- The town steps down in tiers to the sea in the east.
- The waterfront has piers and sailing boats, a lighthouse on sea rocks, an arched bridge and a red torii.
- Pine trees everywhere. Warm lanterns glow in the streets.

---

## Phase A: setup (do first, once)

1. **Scale check.** Import `assets/Phase0/Test/HO_Test_ScaleCube_1x1x1.fbx` (File → Import 3D, **Scale Unit = Stud**). Size must be 1,1,1, with the FRONT face on −Z. Report the result.
2. **Folders.**
   - `ServerStorage/HO_Assets/` holds the imported templates, sorted into sub-folders `Buildings`, `Roofs`, `Walls`, `Props`, `Castle`, `Harbour`, `Nature`.
   - `ReplicatedStorage/HO_Materials/` holds one SurfaceAppearance template per texture set.
3. **Upload the textures.** Use Asset Manager → Bulk Import on every PNG in `textures/`. For each set `X` there are four maps, `HO_T_X_Color / _Normal / _Roughness / _Metalness`. Create a SurfaceAppearance named `X` in `HO_Materials` with ColorMap / NormalMap / RoughnessMap / MetalnessMap set to the uploaded ids. Also paste the ids into the `TEXTURES` table at the top of `roblox/HO_CityBuilder.lua`.
4. **Texture the terrain and plain parts with MaterialVariants.** In `MaterialService`, create one MaterialVariant per row below from our PNGs and set it as the override for that base material. The whole city (terrain, streets, stairs, placeholders) then uses our look automatically:

   | Base material | MaterialVariant from set | StudsPerTile | Used for |
   |---|---|---|---|
   | Slate | `Stone_Fitted` | 4 | terrace retaining walls (ishigaki), stairs, quay |
   | Cobblestone | `Cobblestone` | 4 | streets, market square, promenade |
   | Ground | `Earth_Packed` | 6 | town ground, alleys, yards |
   | Rock | `Stone_Granite` | 8 | cliffs, sea rocks |
   | WoodPlanks | `Wood_Planks` | 4 | piers, decks, bridge |
   | Wood | `Timber_Dark` | 4 | posts, beams on placeholders |
   | Sand | (keep default; tint warm) | – | beach, training yard |
   | Grass | (keep default; colour `#5E7A45`) | – | castle baileys, slopes |

   Terrain colours (Terrain → MaterialColors): Grass `#5E7A45`, Ground `#8C7456`, Slate `#8E887C`, Rock `#6D675C`, Sand `#C8B48C`.
5. **Water** (Terrain properties): WaterColor `#2F6F8F`, WaterReflectance 0.6, WaterTransparency 0.35, WaveSize 0.12, WaveSpeed 8.

## Phase B: build the city blockout (today)

1. Put `roblox/HO_CityBuilder.lua` in a ModuleScript `ServerStorage/HO_CityBuilder`. Run `require(game.ServerStorage.HO_CityBuilder).Build()` from the Command Bar. It creates terrain tiers, the sea, cliffs, streets, stairs, castle walls, the harbour, the lighthouse, torii, trees and all 363 house lots from `docs/layout/city_layout.json`, and sets golden-hour lighting.
2. **Import all finished models** and drop them into `HO_Assets`. **Keep the file names as the Model names.** Run `Build()` again: every lot or building whose asset exists is replaced by the real model; everything else stays a placeholder.
3. **Hand-polish the terrain** to match the reference image. The script's terrain is a clean blockout:
   - **Terrace walls:** batter (slope) the retaining walls between tiers slightly outward at the base, like castle ishigaki. Keep the slate faces visible. Add a little grass on the ledges.
   - **Castle hill:** make the three bailey walls read as massive curved stone walls (+46, +62, +80), steepest under the keep. Round the corners outward.
   - **Coast:** rocky shoreline under the castle on the east side, a small sand beach at the south end of the promenade, and scattered sea rocks.
   - **Mountain backdrop:** rolling forested ridges to the north and west, higher than the keep. Add mist with Atmosphere haze.
   - Do not move streets, stairs or lots. The layout is shared with the model production side.

## Phase C: look and lighting (golden hour)

- Use the lighting the script sets (`Technology Future`, ClockTime 17.4, warm Atmosphere, Bloom, SunRays, ColorCorrection) as the base. Tune it until a screenshot from the sea looking west at the castle matches the reference image: sun low over the sea, warm orange rim light on the walls, cool blue shadows.
- Add a **Sky** with a warm sunset skybox. Set `Lighting.ShadowSoftness` to 0.2.
- **Lights:** every mesh named `…_Glow` (lanterns, forge embers, magic orbs, crystals) should get `Material = Neon` plus a PointLight:
  - paper lanterns: Color `#FFB36B`, Range 14, Brightness 1.5
  - embers: `#FF7A2A`, Range 16, Brightness 2
  - magic orbs: `#9FD8FF`, Range 10
- Until the lantern props arrive, place simple glowing street lanterns (small Neon part + PointLight) about every 24 studs along the main streets and the promenade.
- **Banners:** navy (`#1E2C52`) banners with a white circle crest on the castle walls, gatehouses and keep, as in the reference. Use a Decal or a SurfaceGui with a white ring on a navy part for now; real banner models come later (`HO_Prop_Banner`).

## Phase D: place the finished buildings (use the real models)

Pivot = footprint centre at ground level, front = −Z. Rotate the front toward the street; the facing is given in `city_layout.json`.

| Asset | Size W×D | Where (layout key) | Notes |
|---|---|---|---|
| `HO_Bldg_Machiya_A…F` | 12–24 × 12/20 | all `machiya_lots` | A for lots with `d` = 12 |
| `HO_Bldg_TidewatchInn` | 40 × 24 | `tidewatch_inn` (faces E, the sea) | 6 rentable rooms upstairs; doors `Door_Room1…6` |
| `HO_Bldg_Blacksmith` | 20 × 24 | `blacksmith` (faces W) | forge `_Glow` = embers |
| `HO_Bldg_Armory` | 16 × 20 | `armory` (faces W) | |
| `HO_Bldg_GeneralStore` | 20 × 16 | `general_store` (faces W) | side shoji door is the entrance |
| `HO_Bldg_MagicStall` | 8 × 12 | `magic_stall` in the Market Square (faces E) | orbs/crystals `_Glow` |
| `HO_Bldg_Kura` | 20 × 24 | `kura` ×4 by the piers | |
| Roofs / walls kit | see MANIFEST | castle placeholders, custom builds | |

## Phase E: gameplay setup on the finished buildings

The model parts are named, so hook them up now:

1. **Doors.** Every `_Door*` part group is a sliding door (a door is split by material into e.g. `…_Door1__Timber_Light` + `…_Door1__Shoji_Paper`; weld them or tween the whole group). Add a ProximityPrompt ("Open") that tweens it along its local X by its own width (0.4 s, Quad Out) and back, with CanCollide off while open.
2. **Tidewatch Inn rooms.** For each `Door_Room1…6`, add a ProximityPrompt "Rent room". It opens a rent UI (stub), then unlocks that door for the renting player only (client-side unlock). Put an Attachment `RoomSpawn_n` on each futon for respawn/rest.
3. **Shops.** Add an Attachment `ShopNPC` behind each counter: the inn reception, blacksmith anvil, armory counter, general store counter, magic stall counter. Add a placeholder R6 NPC and a ProximityPrompt that opens the shop UI stub. Put the shop name on each `_SignFace` with a SurfaceGui (vertical Japanese-style text plus English):
   - 潮見屋 Tidewatch Inn
   - 鍛冶 Blacksmith
   - 武具 Armory
   - 万屋 General Store
   - 魔具 Magic Stall
4. **Sword Academy.** The Training Yard placeholder (sand rectangle inside the castle) is where training happens. Add training dummies (placeholders) and a spawn plate. The Academy Hall model comes later as `HO_Castle_AcademyHall`.
5. **Player spawn.** The player is a "shard" who wakes with no memory. Put the first spawn at the Hill Shrine (upper town, west) by the red torii, looking east over the town to the sea.
6. **Collisions.** `_Structure` and `_Interior` use `CollisionFidelity = PreciseConvexDecomposition`. Roof, front, glow, sign and prop meshes get `CanCollide = false`. Add invisible block colliders on stairs if characters snag.
7. **Streaming.** Turn on `StreamingEnabled`. Each building is a Model with `ModelStreamingMode = Atomic`. Mark the keep, castle walls and the town silhouette `Persistent`.

## Phase F: ambience

- Sounds (Roblox audio library, looping, 3D where noted):
  - waves and gulls along the promenade
  - wind on the castle hill
  - market chatter at the Market Square
  - forge hammering at the blacksmith (3D, range 60)
  - a temple bell every few minutes from the Hill Shrine
- ParticleEmitters: smoke from the blacksmith chimney (top of the chimney); a faint sparkle around the Magic Stall orbs.
- Moored boats will come as models (`HO_Harbour_Boat_Small`, `HO_Harbour_Boat_Cargo`). Until then, place simple hull placeholders along the piers with a gentle bobbing tween.

## Phase G: placeholders to keep (models still in production; swap by name)

| Coming model | Placeholder the script makes now |
|---|---|
| `HO_Castle_Keep` (5 tiers, per-tier parts) | stacked white blocks with dark skirts and gold ornaments |
| `HO_Castle_Yagura`, `HO_Castle_Gatehouse` | white/dark blocks with roofs |
| `HO_Castle_AcademyHall` | labelled block in Ni-no-maru |
| `HO_Wall_Ishigaki_*`, castle wall modules | terrain slate faces + white wall parts |
| `HO_Harbour_Pier`, `HO_Harbour_ArchBridge`, `HO_Harbour_Lighthouse` | plank/part versions |
| `HO_Prop_Torii`, `HO_Prop_Well`, `HO_Prop_StoneLantern`, `HO_Prop_Chochin`, `HO_Prop_Banner` | part versions |
| `HO_Tree_Pine_S/M/L`, rocks | trunk + disc pines |

When a new FBX arrives, import it into `HO_Assets` with the same name and run `Build()` again. Don't edit the placeholders by hand; changes would be lost on rebuild. Put hand-made additions (lights, prompts, sounds, NPCs) in a separate folder `Workspace/HO_Gameplay` so rebuilds never delete them.

## Phase H: report back after each session

1. The scale-cube result (first time only).
2. Screenshots:
   - the full city from the sea, matching the reference image angle
   - the Market Square at street level
   - inside the Tidewatch Inn lobby and one room
   - the castle approach up the Grand Stair
3. Problems: wrong size, rotated or flipped models, gaps, z-fighting, missing textures, placeholders that don't match their lot, performance numbers (MicroProfiler, triangle count in view).
4. **Never** rescale, decimate or edit the delivered meshes yourself. Report the problem instead; the model side re-exports from source.
