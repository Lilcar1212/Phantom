--[[
	HOLLOW OATH - Water dragon rig driver (HO_Creature_WaterDragon)

	Import assets/Phase4/Characters/HO_Creature_WaterDragon.fbx with File > Import 3D:
	  * Scale Unit = Stud, Rig General > Rig Type = Custom (keeps the 39 bones and the skinning).
	  * Run require(game.ServerStorage.HO_CityBuilder).ApplyTextures(<the imported model>) for the SurfaceAppearances.
	  * Eyes (..._Eyes) -> Material Neon. WaterFX -> SurfaceAppearance.AlphaMode = Transparency (it is the only
	    translucent piece; everything else is the solid creature).

	Put this ModuleScript in ReplicatedStorage (name HO_DragonRig) and, from a LocalScript or server Script:
	    local DragonRig = require(game.ReplicatedStorage.HO_DragonRig)
	    local stop = DragonRig.Idle(workspace.HO_Creature_WaterDragon)   -- serpentine tail, breathing, neck sway, jaw
	    DragonRig.Roar(workspace.HO_Creature_WaterDragon)                -- one-shot: head up, jaw wide, tail lash
	    stop()                                                           -- stop the idle

	Bones: Root, Spine01-04 (hips -> shoulders), Neck01-04, Head, Jaw, Tail01-16 (hips -> tip),
	FL/FR/RL/RR _Upper/_Lower/_Foot. You can also animate them in the Animation Editor (the model gets an
	AnimationController + Animator) - Bone.Transform is what both drive.
]]

local RunService = game:GetService("RunService")
local DragonRig = {}

local function bones(model)
	local out = {}
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA("Bone") then out[d.Name] = d end
	end
	return out
end
DragonRig.GetBones = bones

-- rest-pose axes of the creature (up = yaw, right = pitch) expressed in each bone's own space
local function axes(model, b)
	local pivot = model:GetPivot()
	local cf = b.WorldCFrame
	return cf:VectorToObjectSpace(pivot.UpVector), cf:VectorToObjectSpace(pivot.RightVector)
end

local function rot(up, right, yaw, pitch)
	return CFrame.fromAxisAngle(up, yaw) * CFrame.fromAxisAngle(right, pitch)
end

-- Continuous idle. Returns a function that stops it (and restores the rest pose).
function DragonRig.Idle(model, opts)
	opts = opts or {}
	local speed, tailAmp = opts.speed or 1.0, opts.tailAmp or math.rad(7)
	local B = bones(model)
	local ax = {}
	for name, b in pairs(B) do
		local up, right = axes(model, b)
		ax[name] = {up, right}
	end
	local t = 0
	local conn = RunService.Heartbeat:Connect(function(dt)
		t = t + dt * speed
		for i = 1, 16 do                                   -- travelling wave down the tail, growing toward the tip
			local n = string.format("Tail%02d", i)
			if B[n] then
				local a = ax[n]
				B[n].Transform = rot(a[1], a[2], math.sin(t * 1.3 - i * 0.4) * tailAmp * (0.4 + i / 16),
					math.sin(t * 0.9 - i * 0.35) * tailAmp * 0.35)
			end
		end
		local breathe = math.sin(t * 1.1)
		for i = 1, 4 do
			local s, nk = string.format("Spine%02d", i), string.format("Neck%02d", i)
			if B[s] then B[s].Transform = rot(ax[s][1], ax[s][2], math.sin(t * 0.6 + i) * math.rad(1.2), breathe * math.rad(0.8)) end
			if B[nk] then B[nk].Transform = rot(ax[nk][1], ax[nk][2], math.sin(t * 0.5 - i * 0.3) * math.rad(3), breathe * math.rad(1.5)) end
		end
		if B.Head then B.Head.Transform = rot(ax.Head[1], ax.Head[2], math.sin(t * 0.7) * math.rad(4), math.sin(t * 0.45) * math.rad(3)) end
		if B.Jaw then B.Jaw.Transform = CFrame.fromAxisAngle(ax.Jaw[2], -math.rad(4) - (breathe * 0.5 + 0.5) * math.rad(5)) end
	end)
	return function()
		conn:Disconnect()
		for _, b in pairs(B) do b.Transform = CFrame.identity end
	end
end

-- One-shot roar (about 2 s). Safe to call while Idle runs (it takes over the head/neck/jaw briefly).
function DragonRig.Roar(model)
	local B = bones(model)
	local t0 = os.clock()
	local conn
	conn = RunService.Heartbeat:Connect(function()
		local k = math.clamp((os.clock() - t0) / 2.0, 0, 1)
		local e = math.sin(k * math.pi)                    -- 0 -> 1 -> 0
		for i = 1, 4 do
			local n = string.format("Neck%02d", i)
			if B[n] then
				local up, right = axes(model, B[n])
				B[n].Transform = CFrame.fromAxisAngle(right, -e * math.rad(7))
			end
		end
		if B.Jaw then
			local _, right = axes(model, B.Jaw)
			B.Jaw.Transform = CFrame.fromAxisAngle(right, -e * math.rad(32))
		end
		for i = 1, 16 do
			local n = string.format("Tail%02d", i)
			if B[n] then
				local up = axes(model, B[n])
				B[n].Transform = CFrame.fromAxisAngle(up, e * math.sin(k * 12 - i * 0.5) * math.rad(10))
			end
		end
		if k >= 1 then conn:Disconnect() end
	end)
end

return DragonRig
