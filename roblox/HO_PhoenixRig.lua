--[[
	HOLLOW OATH - Phoenix rig driver (HO_Creature_Phoenix)

	Import assets/Phase4/Characters/HO_Creature_Phoenix.fbx with File > Import 3D:
	  * Scale Unit = Stud, Rig General > Rig Type = Custom (keeps the bones and the skinning).
	  * require(game.ServerStorage.HO_CityBuilder).ApplyTextures(<the imported model>) for the SurfaceAppearances.
	  * Eyes (..._Eyes) -> Material Neon. FireFX -> SurfaceAppearance.AlphaMode = Transparency; add a warm
	    PointLight (Range 30, orange) in the chest and fire/ember ParticleEmitters on the wing tips and tail.

	ModuleScript in ReplicatedStorage (name HO_PhoenixRig):
	    local PhoenixRig = require(game.ReplicatedStorage.HO_PhoenixRig)
	    local stop = PhoenixRig.Fly(workspace.HO_Creature_Phoenix)            -- wing flaps + tail/head motion
	    PhoenixRig.Glide(workspace.HO_Creature_Phoenix)                        -- or: slow soaring (wings held, gentle sway)
	    PhoenixRig.Screech(workspace.HO_Creature_Phoenix)                      -- one-shot: head up, beak open, wings flare
	    stop()

	Bones: Root, Spine01-03, Neck01-02, Head, Beak, L/R_Wing1-3 (shoulder, forearm, hand), Tail01-06,
	L/R_Thigh/Shin/Foot. Move the whole bird yourself (PivotTo / AlignPosition); these only animate the rig.
]]

local RunService = game:GetService("RunService")
local PhoenixRig = {}

local function bones(model)
	local out = {}
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA("Bone") then out[d.Name] = d end
	end
	return out
end
PhoenixRig.GetBones = bones

-- creature axes (forward, up, right) in each bone's own space, measured at rest
local function axes(model, B)
	local pivot = model:GetPivot()
	local ax = {}
	for name, b in pairs(B) do
		local cf = b.WorldCFrame
		ax[name] = {
			fwd = cf:VectorToObjectSpace(pivot.LookVector),
			up = cf:VectorToObjectSpace(pivot.UpVector),
			right = cf:VectorToObjectSpace(pivot.RightVector),
		}
	end
	return ax
end

local function run(model, step)
	local B = bones(model)
	local ax = axes(model, B)
	local t = 0
	local conn = RunService.Heartbeat:Connect(function(dt)
		t = t + dt
		step(B, ax, t)
	end)
	return function()
		conn:Disconnect()
		for _, b in pairs(B) do b.Transform = CFrame.identity end
	end
end

local function set(B, ax, name, axis, angle)
	local b = B[name]
	if b then b.Transform = CFrame.fromAxisAngle(ax[name][axis], angle) end
end

-- Flapping flight. opts.rate = flaps per second (default 0.9), opts.amp = degrees (default 38).
function PhoenixRig.Fly(model, opts)
	opts = opts or {}
	local rate, amp = opts.rate or 0.9, math.rad(opts.amp or 38)
	return run(model, function(B, ax, t)
		local ph = t * rate * 2 * math.pi
		local flap = math.sin(ph)
		for _, side in ipairs({"R", "L"}) do
			local s = (side == "R") and 1 or -1
			-- roll each wing segment about the creature's forward axis; outer segments lag for a whip-like stroke
			set(B, ax, side .. "_Wing1", "fwd", -s * flap * amp)
			set(B, ax, side .. "_Wing2", "fwd", -s * math.sin(ph - 0.5) * amp * 0.45)
			set(B, ax, side .. "_Wing3", "fwd", -s * math.sin(ph - 1.0) * amp * 0.35)
		end
		for i = 1, 6 do
			set(B, ax, string.format("Tail%02d", i), "right", math.sin(ph - i * 0.5) * math.rad(3))
		end
		set(B, ax, "Spine02", "right", -flap * math.rad(2))
		set(B, ax, "Neck01", "right", flap * math.rad(3))
		set(B, ax, "Head", "up", math.sin(t * 0.6) * math.rad(8))
	end)
end

-- Soaring: wings held out with a slow breathing sway, tail streamers undulating.
function PhoenixRig.Glide(model)
	return run(model, function(B, ax, t)
		local sway = math.sin(t * 0.8)
		for _, side in ipairs({"R", "L"}) do
			local s = (side == "R") and 1 or -1
			set(B, ax, side .. "_Wing1", "fwd", -s * (math.rad(6) + sway * math.rad(4)))
			set(B, ax, side .. "_Wing3", "fwd", -s * math.sin(t * 0.8 - 0.8) * math.rad(5))
		end
		for i = 1, 6 do
			set(B, ax, string.format("Tail%02d", i), "up", math.sin(t * 1.2 - i * 0.6) * math.rad(4))
		end
		set(B, ax, "Head", "up", math.sin(t * 0.4) * math.rad(10))
		set(B, ax, "Neck02", "right", math.sin(t * 0.5) * math.rad(4))
	end)
end

-- One-shot screech (about 1.6 s).
function PhoenixRig.Screech(model)
	local stop
	local t0 = os.clock()
	stop = run(model, function(B, ax)
		local k = math.clamp((os.clock() - t0) / 1.6, 0, 1)
		local e = math.sin(k * math.pi)
		set(B, ax, "Neck01", "right", -e * math.rad(12))
		set(B, ax, "Neck02", "right", -e * math.rad(10))
		set(B, ax, "Beak", "right", e * math.rad(28))
		for _, side in ipairs({"R", "L"}) do
			local s = (side == "R") and 1 or -1
			set(B, ax, side .. "_Wing1", "fwd", -s * e * math.rad(30))
		end
		if k >= 1 then stop() end
	end)
end

return PhoenixRig
