# Hollow Oath: using the harbour, props, animations, VFX and hero assets

This guide continues `docs/ASSEMBLY_BRIEF.md` (city, buildings, castle). Import rules are the same:
**File → Import 3D, Scale Unit = Stud, keep the file names**. Move each imported Model into
`ServerStorage.HO_Assets`, then run `require(game.ServerStorage.HO_CityBuilder).ApplyTextures()`. Every MeshPart
gets its one SurfaceAppearance: from the `__<Set>` suffix of its name, or from the manifest table for
single-material meshes. `MANIFEST.md` lists every file, its triangle count, pivot and texture set.

## 1. Harbour, street props and nature (`assets/Phase1/Harbour`, `Props`, `Nature`)

`Build()` in `HO_CityBuilder` already places these where the layout wants them. It uses each asset's real bounds,
so the importer's pivot doesn't matter. For hand placement, the pivots are:

| Asset | Pivot / placement |
|---|---|
| `HO_Harbour_Quay_16`, `_Quay_Steps_16` | Bottom of the wall under the top face edge. Put the pivot at y = −4.6 on the shoreline so the cap meets the +4 promenade; the face looks out to sea (−Z). Tile every 16 studs. |
| `HO_Harbour_Pier` | Shore-end centre at **sea level**; deck top +4. Extends toward −Z. `HO_Harbour_Pier_Deck_8` is one 8-long segment to build custom piers. |
| `HO_Harbour_Boat_Small` / `_Boat_Cargo` | Keel bottom centre. Waterline about +1.0 / +2.2, so sink the pivot by that much below the sea surface. Bob them gently with a TweenService loop (±0.3 stud, 3 s). |
| `HO_Harbour_Lighthouse` | Base centre. Stand it on the sea rock. `_Glow` = lantern room: Neon + PointLight (Range 40, warm). |
| `HO_Harbour_ArchBridge` | Centre at deck-end level (both ends at y = 0). Span 64 along Z. |
| `HO_Prop_StoneStairs_*` | Ground centre. The steps climb away from the front (−Z side = bottom step). |
| Torii, stone lantern, chōchin, banner, carts, stalls, benches, well, fences, barrels, casks, crates, sacks, bales, jars | Bottom centre at ground; front = −Z. `_Glow` meshes: Neon + small PointLight. `_Face` = blank plaque/sign (SurfaceGui). |
| `HO_Tree_Pine_S/M/L` | Trunk base. Rotate randomly around Y and scale 0.9–1.1 for variety. |
| `HO_Rock_Cliff_S/M/L` | Base centre. Sink 10–20 % into the ground. Rotate freely. |

Collision: make props non-collidable except the quay, pier, bridge, stairs and rocks. Use `CollisionFidelity = Hull` for props you do want solid, and `PreciseConvexDecomposition` for stairs, pier and bridge.

## 2. Animations (`assets/Phase2/Animations`): 42 R6 animations at 30 fps

Each animation ships in three forms:

* **`HO_Anim_<Name>.rbxmx`** (use this one): a ready `KeyframeSequence` with the easing styles and the hit markers.
* `.fbx`: an armature with the same bones, for re-editing in Blender/Moon Animator.
* `.json`: raw data.

`animations_index.json` lists length, loop, priority and markers for all of them.

### Upload the animations

1. In Studio, right-click Workspace, choose **Insert from File…**, and pick an `.rbxmx`. A KeyframeSequence appears.
2. Right-click it, choose **Save to Roblox**, and publish it (under the group if the game is a group game). Copy the asset id.
3. Put the ids in a table:

   ```lua
   ANIMS = { Sword_Combo1 = "rbxassetid://…", … }
   ```

   Or open the KeyframeSequence in the Animation Editor first if you want to tweak it.

### Play an animation and use its markers

```lua
local anim = Instance.new("Animation"); anim.AnimationId = ANIMS.Sword_Combo1
local track = humanoid:FindFirstChildOfClass("Animator"):LoadAnimation(anim)
track:GetMarkerReachedSignal("Hit"):Connect(function() -- do the hitbox / damage / VFX here
end)
track:Play(0.05)
```

### Markers

* **Markers** are `Hit`, `Hit2` and `Hit3`, placed on the impact frame of each swing. Combo finishers and multi-hit moves use all three.
* Cast animations fire `Hit` on the release frame, and `Cast_BeamChannel` fires `Hit` at the start of the channel.
* The finisher pairs (`Finisher_*_Attacker` / `_Victim`) share markers and frame counts. Play both on the same frame, with the victim placed 5 studs in front of the attacker, facing them. `Sword_Parry`'s `Hit` is the parry-window frame. `Hollow_Death` and the victims end lying down: freeze the last frame (`track:AdjustSpeed(0)` near the end) or swap to a ragdoll.

### Priorities, looping and rigs

* **Priorities** are already set:
  * Idle: idles.
  * Movement: Run, Jump, Landing, Golem_Walk, Hollow_Stalk.
  * Action: attacks, dashes and casts.
  * Action2: ClashLock, Hollow_HitReaction.
  * Action4: finishers, Hollow_Death.
  * Dashes only animate: move the character in game code.
* **Looping** anims: every Idle, Run, Sword_Block, Fist_Block, Sword_ClashLock, Cast_BeamChannel, Golem_Walk and Hollow_Stalk. Stop them yourself.
* **Rigs:**
  * Player animations are made for standard R6 characters.
  * `Golem_*` animations are made for the Earth Golem rig (R6 topology at scale 2.4).
  * `Hollow_*` animations are made for the Hollow rig.
  * Build those two rigs with `HO_RigBuilder` (section 4) and the animations play on them without changes.

## 3. VFX (`assets/Phase3/VFX`)

### Flipbooks (`Flipbooks/*.png`, 1024², alpha)

1. Upload each sheet as an image.
2. In a ParticleEmitter, set `FlipbookLayout = Grid4x4` or `Grid8x8` (listed in `flipbooks.json` and `MANIFEST.md`).
3. Set `FlipbookMode = OneShot` for bursts, or `Loop` for loops. Use `Random` for Droplets, Crackle and Embers.
4. Set `FlipbookFramerate` to 30 (or use `FlipbookStartRandom` for loops).

**Tintable** sheets are white or greyscale: colour them with `Color`. Pre-coloured sheets (fire, explosion, embers) keep `Color` white. Use `LightEmission` 1 for fire, magic and sparks, and 0 for smoke and dust. `HO_VFX_Ground_Crack_Decal` is a single decal image.

### VFX meshes (`HO_VFX_*.fbx`)

* **UV layout:** U runs along the effect and V runs across it (0 = inner/bottom, 1 = outer/top). The meshes are double-sided.
* **Scrolling:**
  1. Put a `Texture` (not a SurfaceAppearance) on each face you need, or use a SurfaceAppearance with `ColorMap` = `Textures/HO_VFXT_*.png` and `AlphaMode = Transparency`.
  2. Animate `Texture.OffsetStudsU` every frame for motion.
* **Materials:**
  * Make meshes Neon/ForceField-looking by setting `Material = Neon`, `Transparency` 0.2–0.5 and tweening the size.
  * Rock shards and the stone drill are solid Stone_Granite: texture them with ApplyTextures.
* **Mesh behaviour:**
  * **Slashes** (Thin, Medium, Heavy) lie flat around their origin. Weld one to the HumanoidRootPart at the swing height, rotate it to the swing plane, and fade Transparency 0 → 1 over 0.25 s while scaling 0.9 → 1.1.
  * **Shockwave_Flat / Dome** and **FireRing_Segment**: 8 segments rotated by 45° make a full ring. For **FirePillar**, **Vortex** and **SpiralCone**: spawn them at the ground, scale them up and fade them out.
  * **EnergySphere**: the Outer, Middle and Core shells share one centre. Spin them in opposite directions.
  * **WaterDragon**: the head faces −Z. Scroll `HO_VFXT_Water.png` along U so the water flows tail → head. Move it along a path with CFrame lerps.

## 4. Hero models (`assets/Phase4`) and `roblox/HO_RigBuilder.lua`

Put `roblox/HO_RigBuilder.lua` in **ReplicatedStorage** as a ModuleScript named `HO_RigBuilder`, and import the Phase 4 FBX files into `ServerStorage.HO_Assets`.

**Why the module:** Roblox re-centres every imported MeshPart on its own bounding box, so the Blender pivots are lost. The module stores every mesh's offset from its body part or grip and rebuilds everything exactly.

```lua
local Rig = require(game.ReplicatedStorage.HO_RigBuilder)
local golem  = Rig.BuildCharacter("HO_Char_EarthGolem", CFrame.new(0, 0, 0))  -- CFrame of the feet
local hollow = Rig.BuildCharacter("HO_Char_Hollow", CFrame.new(12, 0, 0))
Rig.EquipArmor(character, "Samurai")            -- "Ashigaru" | "Samurai" | "Oathguard"; Rig.RemoveArmor(character)
local tool = Rig.MakeWeaponTool("MoonlitEdge")  -- a Tool with a Handle at the grip
tool.Parent = player.Backpack
Rig.AttachSheath(character, "MoonlitEdge")      -- scabbard on the left hip (Rig.SHEATH_C0 to adjust)
local welds = Rig.AttachStoneFists(character)   -- floating fists; tween welds.Right[i].C0 to punch
```

| Asset | What it is |
|---|---|
| `HO_Weapon_IronKatana`, `_TemperedKatana`, `_AshfallSword`, `_CrimsonOath`, `_MoonlitEdge` | Katanas with tsuba, silk-wrapped grip, habaki. The pivot is the grip centre, the blade points −Z and the edge points down. `_Glow` = glowing edge (Ashfall amber, Crimson red, Moonlit pale blue): Neon (the module sets it). Add a PointLight in the glow colour for Crimson Oath and Moonlit Edge. |
| `HO_Weapon_<Name>_Saya` | Scabbard in the same frame as its sword: at the same CFrame, the blade is sheathed. |
| `HO_Armor_Ashigaru / _Samurai / _Oathguard` | One mesh per R6 part: Torso, Right/Left Arm, Right/Left Leg, Helmet (on the Head). Each fits over the standard R6 body parts. |
| `HO_Hero_StoneFist_Right / _Left` | Floating carved-stone fists with glowing amber cracks (`_Glow`). The pivot is the fist centre; the fist punches toward −Z. |
| `HO_Char_EarthGolem` | Golem at R6 scale 2.4 (about 12 studs tall). `BuildCharacter` adds the HumanoidRootPart, invisible R6 body parts, Motor6Ds and a Humanoid with an Animator. The Golem animations play directly. |
| `HO_Char_Hollow` | The Hollow (R6 size), with a glowing red chest eye and cracks. Build it the same way and use the `Hollow_*` animations. |
| `assets/Phase4/Icons/HO_Icon_Magic_Fire/Water/Earth.png` | 512×512 transparent circular emblems for the magic UI (ImageLabel, `ScaleType = Fit`). |

After `BuildCharacter`:

* The NPC is a normal R6 Humanoid model, so `Humanoid:MoveTo`, `PathfindingService` and `Animator:LoadAnimation` all work.
* The golem's invisible Torso and Head collide. The visual meshes are massless and non-collidable.
* Give the golem `WalkSpeed` ≈ 8 and `HipHeight` 0 (R6 uses its leg length). If it sinks or floats, set `Humanoid.HipHeight` to 0 and check that nothing is Anchored.
