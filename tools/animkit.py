"""R6 animation toolkit: rig definition (standard Roblox R6 Motor6D joints), pose math, exporters.

Authoring space = Roblox part space: X right, Y up, Z back (the character faces -Z).
A pose gives, per joint, a rotation (pitch about X, yaw about Y, roll about Z, degrees) of Part1 relative to
Part0 about the joint pivot, plus an optional RootJoint translation `d` (studs, HRP space).
  pitch +  : arms / legs swing FORWARD ; torso / head tilt BACK
  yaw   +  : turn to the character's LEFT
  roll  +  : right-side limbs swing outward (right) ; left-side limbs swing inward ; torso leans left
Outputs
  * .rbxmx KeyframeSequence (exact Motor6D Transforms + KeyframeMarkers 'Hit', 'Hit2', ...)
  * .fbx  armature animation (bones named after the R6 parts) for the brief's FBX pipeline
  * .json marker/timing sidecar, and a preview strip rendered in Blender
"""
import math, json, os
from mathutils import Matrix, Vector, Euler

FPS = 30

# ------------------------------------------------------------------------------------------------ rig
def cf(x, y, z, r00, r01, r02, r10, r11, r12, r20, r21, r22):
    return Matrix(((r00, r01, r02, x), (r10, r11, r12, y), (r20, r21, r22, z), (0, 0, 0, 1)))


class Rig:
    """R6-topology rig. `scale` enlarges it (the Earth Golem uses the same joints at ~2.4x)."""
    PARTS = {  # name: (size, rest centre in character space where the HRP centre is the origin)
        'HumanoidRootPart': ((2, 2, 1), (0, 0, 0)), 'Torso': ((2, 2, 1), (0, 0, 0)), 'Head': ((2, 1, 1), (0, 1.5, 0)),
        'Right Arm': ((1, 2, 1), (1.5, 0, 0)), 'Left Arm': ((1, 2, 1), (-1.5, 0, 0)),
        'Right Leg': ((1, 2, 1), (0.5, -2, 0)), 'Left Leg': ((1, 2, 1), (-0.5, -2, 0)),
    }
    # key: (Motor6D name, Part0, Part1, C0, C1)  -- classic R6 values
    JOINTS = {
        'root': ('RootJoint', 'HumanoidRootPart', 'Torso', cf(0, 0, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0), cf(0, 0, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0)),
        'neck': ('Neck', 'Torso', 'Head', cf(0, 1, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0), cf(0, -0.5, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0)),
        'rs': ('Right Shoulder', 'Torso', 'Right Arm', cf(1, 0.5, 0, 0, 0, 1, 0, 1, 0, -1, 0, 0), cf(-0.5, 0.5, 0, 0, 0, 1, 0, 1, 0, -1, 0, 0)),
        'ls': ('Left Shoulder', 'Torso', 'Left Arm', cf(-1, 0.5, 0, 0, 0, -1, 0, 1, 0, 1, 0, 0), cf(0.5, 0.5, 0, 0, 0, -1, 0, 1, 0, 1, 0, 0)),
        'rh': ('Right Hip', 'Torso', 'Right Leg', cf(1, -1, 0, 0, 0, 1, 0, 1, 0, -1, 0, 0), cf(0.5, 1, 0, 0, 0, 1, 0, 1, 0, -1, 0, 0)),
        'lh': ('Left Hip', 'Torso', 'Left Leg', cf(-1, -1, 0, 0, 0, -1, 0, 1, 0, 1, 0, 0), cf(-0.5, 1, 0, 0, 0, -1, 0, 1, 0, 1, 0, 0)),
    }
    ORDER = ['root', 'neck', 'rs', 'ls', 'rh', 'lh']

    def __init__(self, scale=1.0, name='R6'):
        self.s = scale
        self.name = name

    def C0(self, j):
        m = self.JOINTS[j][3].copy(); m.translation *= self.s; return m

    def C1(self, j):
        m = self.JOINTS[j][4].copy(); m.translation *= self.s; return m

    def rest(self, part):
        size, c = self.PARTS[part]
        return Matrix.Translation(Vector(c) * self.s)

    def size(self, part):
        return Vector(self.PARTS[part][0]) * self.s

    @property
    def hip_height(self):
        return 3.0 * self.s          # HRP centre above the ground when standing


def rot(p=0.0, y=0.0, r=0.0):
    """Rotation matrix from pitch (X), yaw (Y), roll (Z) in degrees: R = Ry * Rx * Rz."""
    return (Matrix.Rotation(math.radians(y), 4, 'Y') @ Matrix.Rotation(math.radians(p), 4, 'X') @
            Matrix.Rotation(math.radians(r), 4, 'Z'))


def transform(rig, j, pose):
    """Motor6D.Transform for joint j: Rc0^T * R * Rc0 (+ translation Rc0^T d for the RootJoint)."""
    R = rot(*pose.get(j, (0, 0, 0)))
    Rc0 = rig.C0(j).to_3x3().to_4x4()
    T = Rc0.transposed() @ R @ Rc0
    if j == 'root' and 'd' in pose:
        T.translation = Rc0.to_3x3().transposed() @ (Vector(pose['d']) * rig.s)
    return T


def part_world(rig, pose, hrp=Matrix.Identity(4)):
    """World (character-space) matrices of every part for a pose: Part1 = Part0 * C0 * Transform * C1^-1."""
    out = {'HumanoidRootPart': hrp}
    for j in rig.ORDER:
        _, p0, p1, _, _ = rig.JOINTS[j]
        out[p1] = out[p0] @ rig.C0(j) @ transform(rig, j, pose) @ rig.C1(j).inverted()
    return out


# ------------------------------------------------------------------------------------------------ animation data
class Anim:
    """keys: list of (frame, pose dict, easing) ; markers: {name: frame} ; loop ; priority."""
    def __init__(self, name, keys, loop=False, priority='Action', markers=None, rig=None, notes=''):
        self.name, self.keys, self.loop = name, keys, loop
        self.priority = priority
        self.markers = markers or {}
        self.rig = rig or Rig()
        self.notes = notes

    @property
    def length(self):
        return self.keys[-1][0]


EASING = {'linear': (0, 0), 'constant': (1, 0), 'cubic': (3, 2), 'in': (3, 0), 'out': (3, 1), 'elastic': (2, 1), 'bounce': (4, 1)}
PRIORITY = {'Idle': 0, 'Movement': 1, 'Action': 2, 'Action2': 3, 'Action3': 4, 'Action4': 5, 'Core': 1000}


# ------------------------------------------------------------------------------------------------ rbxmx writer
def _cframe_xml(name, m):
    r = m.to_3x3()
    t = m.translation
    vals = dict(X=t.x, Y=t.y, Z=t.z, R00=r[0][0], R01=r[0][1], R02=r[0][2], R10=r[1][0], R11=r[1][1], R12=r[1][2],
                R20=r[2][0], R21=r[2][1], R22=r[2][2])
    inner = ''.join(f'<{k}>{v:.6f}</{k}>' for k, v in vals.items())
    return f'<CoordinateFrame name="{name}">{inner}</CoordinateFrame>'


def write_rbxmx(anim, path):
    rig = anim.rig
    ref = [0]
    def nref():
        ref[0] += 1; return f'RBX{ref[0]:06d}'
    def pose_item(part, children, T, ease, weight=1.0):
        es, ed = EASING.get(ease, (3, 2))
        props = (f'<string name="Name">{part}</string>{_cframe_xml("CFrame", T)}'
                 f'<token name="EasingDirection">{ed}</token><token name="EasingStyle">{es}</token>'
                 f'<float name="Weight">{weight}</float>')
        return f'<Item class="Pose" referent="{nref()}"><Properties>{props}</Properties>{children}</Item>'
    kf_items = []
    marker_at = {}
    for mname, fr in anim.markers.items():
        marker_at.setdefault(fr, []).append(mname)
    key_frames = sorted({k[0] for k in anim.keys} | set(marker_at))
    keymap = {k[0]: k for k in anim.keys}
    # Roblox eases the segment LEAVING a pose with that pose's EasingStyle; authoring stores the easing on the key
    # being arrived at -> shift each key's easing one key back.
    leave_ease = {k[0]: nk[2] for k, nk in zip(anim.keys, anim.keys[1:])}
    leave_ease[anim.keys[-1][0]] = 'linear'
    for fr in key_frames:
        if fr in keymap:
            _, pose, _ = keymap[fr]
            ease = leave_ease[fr]
        else:                       # marker on a frame without a key: sample the pose
            pose, ease = sample(anim, fr), 'linear'
        child_parts = {'Torso': ['neck', 'rs', 'ls', 'rh', 'lh']}
        torso_children = ''
        for j in child_parts['Torso']:
            torso_children += pose_item(rig.JOINTS[j][2], '', transform(rig, j, pose), ease)
        torso = pose_item('Torso', torso_children, transform(rig, 'root', pose), ease)
        hrp = pose_item('HumanoidRootPart', torso, Matrix.Identity(4), ease, weight=0.0)
        markers = ''.join(f'<Item class="KeyframeMarker" referent="{nref()}"><Properties><string name="Name">{m}</string>'
                          f'<string name="Value">{m}</string></Properties></Item>' for m in marker_at.get(fr, []))
        kf_items.append(f'<Item class="Keyframe" referent="{nref()}"><Properties><string name="Name">Keyframe</string>'
                        f'<float name="Time">{fr / FPS:.6f}</float></Properties>{hrp}{markers}</Item>')
    xml = ('<roblox xmlns:xmime="http://www.w3.org/2005/05/xmlmime" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
           'xsi:noNamespaceSchemaLocation="http://www.roblox.com/roblox.xsd" version="4">'
           f'<Item class="KeyframeSequence" referent="{nref()}"><Properties><string name="Name">{anim.name}</string>'
           f'<bool name="Loop">{"true" if anim.loop else "false"}</bool>'
           f'<token name="Priority">{PRIORITY[anim.priority]}</token></Properties>{"".join(kf_items)}</Item></roblox>')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(xml)


def lerp_pose(a, b, t):
    out = {}
    for j in set(a) | set(b):
        va = a.get(j, (0, 0, 0)); vb = b.get(j, (0, 0, 0))
        if j == 'd' and 'd' not in a: va = (0, 0, 0)
        if j == 'd' and 'd' not in b: vb = (0, 0, 0)
        out[j] = tuple(x + (y - x) * t for x, y in zip(va, vb))
    return out


def ease_t(t, ease):
    if ease == 'linear': return t
    if ease == 'constant': return 0.0
    if ease == 'in': return t * t * t
    if ease == 'out': return 1 - (1 - t) ** 3
    return t * t * (3 - 2 * t)


def sample(anim, fr):
    """Pose at frame fr (the easing of the *target* key shapes the segment, like Roblox's Pose easing)."""
    keys = anim.keys
    if fr <= keys[0][0]: return dict(keys[0][1])
    for (f0, p0, _), (f1, p1, e1) in zip(keys, keys[1:]):
        if f0 <= fr <= f1:
            t = (fr - f0) / max(1e-6, f1 - f0)
            return lerp_pose(p0, p1, ease_t(t, e1))
    return dict(keys[-1][1])


def write_json(anim, path):
    data = dict(name=anim.name, fps=FPS, frames=anim.length, seconds=round(anim.length / FPS, 3), loop=anim.loop,
                priority=anim.priority, rig=anim.rig.name,
                markers={k: dict(frame=v, time=round(v / FPS, 4)) for k, v in anim.markers.items()}, notes=anim.notes)
    with open(path, 'w') as f:
        json.dump(data, f, indent=1)


# ------------------------------------------------------------------------------------------------ Blender side
P_R2B = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))   # Roblox (x,y,z) -> Blender (x,-z,y)


def r2b(m):
    return P_R2B @ m @ P_R2B.inverted()


def build_armature(rig, name='R6', with_mesh=True, mesh_mats=None):
    """Armature with bones named after the parts, heads at the joint pivots, identity rest orientation.
    Box meshes (named like the parts) are parented to their bones for previews and FBX."""
    import bpy, bmesh
    arm_d = bpy.data.armatures.new(name)
    arm = bpy.data.objects.new(name, arm_d)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    hip = rig.hip_height
    def to_b(v):
        return (P_R2B @ Vector((v.x, v.y + hip, v.z, 1.0))).to_3d()
    eb = {}
    e = arm_d.edit_bones.new('HumanoidRootPart'); e.head = to_b(Vector((0, 0, 0))); e.tail = e.head + Vector((0, 0.5 * rig.s, 0)); eb['HumanoidRootPart'] = e
    for j in rig.ORDER:
        _, p0, p1, _, _ = rig.JOINTS[j]
        piv = rig.rest(p0).translation + rig.C0(j).translation
        e = arm_d.edit_bones.new(p1)
        e.head = to_b(piv); e.tail = e.head + Vector((0, 0.5 * rig.s, 0)); e.roll = 0.0
        e.parent = eb[p0]
        eb[p1] = e
    bpy.ops.object.mode_set(mode='OBJECT')
    meshes = []
    if with_mesh:
        bpy.context.view_layer.update()
        for part in rig.PARTS:
            if part == 'HumanoidRootPart': continue
            size = rig.size(part)
            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(size.x, size.z, size.y), verts=bm.verts)
            me = bpy.data.meshes.new(part); bm.to_mesh(me); bm.free()
            if mesh_mats and part in mesh_mats:
                me.materials.append(mesh_mats[part])
            ob = bpy.data.objects.new(part, me)
            bpy.context.scene.collection.objects.link(ob)
            ob.parent = arm; ob.parent_type = 'BONE'; ob.parent_bone = part
            bpy.context.view_layer.update()
            c = rig.rest(part).translation
            ob.matrix_world = Matrix.Translation(to_b(c))
            meshes.append(ob)
    return arm, meshes


def key_anim(arm, anim):
    """Keyframe the armature from an Anim (one Blender action), frames 0..length."""
    import bpy
    rig = anim.rig
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 0, anim.length
    prev = {}
    interp = {'linear': 'LINEAR', 'constant': 'CONSTANT'}
    for fr, pose, ease in anim.keys:
        for j in rig.ORDER:
            p1 = rig.JOINTS[j][2]
            pb = arm.pose.bones[p1]
            pb.rotation_mode = 'QUATERNION'
            M = rot(*pose.get(j, (0, 0, 0)))
            if j == 'root' and 'd' in pose:
                M = Matrix.Translation(Vector(pose['d']) * rig.s) @ M
            Mb = r2b(M)
            loc, q, _ = Mb.decompose()
            if p1 in prev and prev[p1].dot(q) < 0: q.negate()
            prev[p1] = q
            pb.location = loc; pb.rotation_quaternion = q
            pb.keyframe_insert('location', frame=fr); pb.keyframe_insert('rotation_quaternion', frame=fr)
    act = arm.animation_data.action          # created by keyframe_insert (Blender 5 action slots handled internally)
    act.name = anim.name
    for fc in _fcurves(act):
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'
    for name, fr in anim.markers.items():
        scene.timeline_markers.new(name, frame=fr)
    return act


def _fcurves(act):
    """F-curves of an action (Blender 4.4+/5.0 layered actions or legacy)."""
    try:
        return list(act.fcurves)
    except AttributeError:
        out = []
        for layer in act.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    out += list(cb.fcurves)
        return out


def export_fbx(arm, meshes, path):
    import bpy
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    for m in meshes: m.select_set(True)
    bpy.context.view_layer.objects.active = arm
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'ARMATURE', 'MESH'},
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', global_scale=1.0,
                             axis_forward='-Z', axis_up='Y', bake_space_transform=False, add_leaf_bones=False,
                             primary_bone_axis='Y', secondary_bone_axis='X', armature_nodetype='NULL',
                             bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=False,
                             bake_anim_use_all_actions=False, bake_anim_force_startend_keying=True,
                             bake_anim_step=1.0, bake_anim_simplify_factor=0.0, path_mode='STRIP')
