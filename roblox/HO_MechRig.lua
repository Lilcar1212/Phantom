--[[
	HOLLOW OATH - Iron samurai mech driver (HO_Mech_Tetsujin)

	Import assets/Phase4/Mechs/HO_Mech_Tetsujin.fbx with File > Import 3D:
	  * Scale Unit = Stud, Rig General > Rig Type = Custom (keeps the bones; every piece is rigid on one bone).
	  * require(game.ServerStorage.HO_CityBuilder).ApplyTextures(<the imported model>).
	  * Eye slit (..__Glow_Red) and cannon core (..__Glow_Amber) -> Material Neon; add a PointLight in the cannon.

	ModuleScript in ReplicatedStorage (name HO_MechRig):
	    local Mech = require(game.ReplicatedStorage.HO_MechRig)
	    local stop = Mech.Idle(mech)                 -- engine idle: breathing sway, head scanning
	    Mech.Swing(mech)                             -- overhead nodachi cut (about 1.4 s); returns when the blade lands
	    local muzzleCF = Mech.FireCannon(mech)       -- recoil; returns the muzzle CFrame -> spawn your projectile / VFX there
	    Mech.Stomp(mech, "R")                        -- heavy foot stomp ("R" or "L") -> shake the camera on landing
	    stop()

	Bones: Root, Pelvis, Torso, Head, Cannon, L/R_UpperArm/Forearm/Hand, Sword, L/R_Thigh/Shin/Foot.
	These only animate the rig - move the mech yourself (PivotTo / AlignPosition, it is ~40 studs tall).
]]

local RunService = game:GetService("RunService")
local Mech = {}

-- muzzle position relative to the model origin (Roblox studs), from the FBX
Mech.MUZZLE_OFFSET = CFrame.new(0, 27.2, -13.0)

local function bones(model)
	local out = {}
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA("Bone") then out[d.Name] = d end
	end
	return out
end
Mech.GetBones = bones

local function axes(model, B)
	local pivot = model:GetPivot()
	local ax = {}
	for name, b in pairs(B) do
		local cf = b.WorldCFrame
		ax[name] = {fwd = cf:VectorToObjectSpace(pivot.LookVector), up = cf:VectorToObjectSpace(pivot.UpVector),
			right = cf:VectorToObjectSpace(pivot.RightVector)}
	end
	return ax
end

local function rot(ax, name, axis, angle)
	return CFrame.fromAxisAngle(ax[name][axis], angle)
end

-- runs step(B, ax, k) for `dur` seconds (k = 0..1), then resets the touched bones; blocks until done
local function play(model, dur, step)
	local B = bones(model)
	local ax = axes(model, B)
	local t0 = os.clock()
	while true do
		local k = math.clamp((os.clock() - t0) / dur, 0, 1)
		step(B, ax, k)
		if k >= 1 then break end
		RunService.Heartbeat:Wait()
	end
end

function Mech.Idle(model)
	local B = bones(model)
	local ax = axes(model, B)
	local t = 0
	local conn = RunService.Heartbeat:Connect(function(dt)
		t = t + dt
		local breathe = math.sin(t * 1.2)
		if B.Torso then B.Torso.Transform = rot(ax, "Torso", "right", breathe * math.rad(1.2)) * rot(ax, "Torso", "up", math.sin(t * 0.3) * math.rad(3)) end
		if B.Head then B.Head.Transform = rot(ax, "Head", "up", math.sin(t * 0.45) * math.rad(18)) end
		if B.R_UpperArm then B.R_UpperArm.Transform = rot(ax, "R_UpperArm", "right", breathe * math.rad(2)) end
		if B.L_UpperArm then B.L_UpperArm.Transform = rot(ax, "L_UpperArm", "right", -breathe * math.rad(2)) end
	end)
	return function()
		conn:Disconnect()
		for _, b in pairs(B) do b.Transform = CFrame.identity end
	end
end

-- overhead cut: wind up (0-0.45), strike (0.45-0.6), recover (0.6-1)
function Mech.Swing(model)
	play(model, 1.4, function(B, ax, k)
		local raise
		if k < 0.45 then raise = math.sin(k / 0.45 * math.pi / 2)
		elseif k < 0.6 then raise = 1 - (k - 0.45) / 0.15 * 1.35
		else raise = -0.35 * (1 - (k - 0.6) / 0.4) end
		if B.R_UpperArm then B.R_UpperArm.Transform = rot(ax, "R_UpperArm", "right", -raise * math.rad(95)) end
		if B.R_Forearm then B.R_Forearm.Transform = rot(ax, "R_Forearm", "right", -math.max(raise, 0) * math.rad(35)) end
		if B.Torso then B.Torso.Transform = rot(ax, "Torso", "up", raise * math.rad(14)) end
		if B.L_UpperArm then B.L_UpperArm.Transform = rot(ax, "L_UpperArm", "right", -math.max(raise, 0) * math.rad(30)) end
	end)
end

function Mech.FireCannon(model)
	local muzzle = model:GetPivot() * Mech.MUZZLE_OFFSET
	task.spawn(function()
		play(model, 0.9, function(B, ax, k)
			local kick = (k < 0.12) and (k / 0.12) or math.max(0, 1 - (k - 0.12) / 0.88)
			if B.Cannon then B.Cannon.Transform = CFrame.new(-ax.Cannon.fwd * 1.4 * kick) end
			if B.Torso then B.Torso.Transform = rot(ax, "Torso", "right", -kick * math.rad(4)) end
		end)
	end)
	return muzzle
end

function Mech.Stomp(model, side)
	side = side or "R"
	play(model, 1.1, function(B, ax, k)
		local lift = math.sin(math.min(1, k / 0.7) * math.pi)
		local thigh, shin = side .. "_Thigh", side .. "_Shin"
		if B[thigh] then B[thigh].Transform = rot(ax, thigh, "right", -lift * math.rad(35)) end
		if B[shin] then B[shin].Transform = rot(ax, shin, "right", lift * math.rad(45)) end
		if B.Torso then B.Torso.Transform = rot(ax, "Torso", "fwd", (side == "R" and -1 or 1) * lift * math.rad(3)) end
	end)
end

return Mech
