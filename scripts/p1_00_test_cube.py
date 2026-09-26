"""Step 0: 1x1x1 stud scale/orientation test cube -> assets/Phase0/Test/HO_Test_ScaleCube_1x1x1.fbx"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import ho, bpy, bmesh, json
import fbx_inspect
from PIL import Image, ImageDraw, ImageFont

# --- labelled face atlas (3x2 cells) -------------------------------------------------------------
tex_dir = os.path.join(ho.TEX_DIR, 'Debug_Faces'); os.makedirs(tex_dir, exist_ok=True)
S = 1024; cw, ch = S // 3, S // 2
img = Image.new('RGB', (S, S), (40, 40, 48)); d = ImageDraw.Draw(img)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 44)
small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 26)
faces = [('FRONT', '-Z (Roblox)', (200, 60, 50)), ('BACK', '+Z', (70, 70, 90)), ('RIGHT', '+X', (60, 140, 70)),
         ('LEFT', '-X', (60, 100, 60)), ('TOP', '+Y', (60, 90, 180)), ('BOTTOM', '-Y', (60, 60, 60))]
cells = {}
for i, (lab, ax, col) in enumerate(faces):
    cx, cy = i % 3, i // 3
    box = (cx * cw + 4, cy * ch + 4, (cx + 1) * cw - 4, (cy + 1) * ch - 4)
    d.rectangle(box, fill=col, outline=(240, 240, 240), width=6)
    d.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2 - 20), lab, font=font, fill='white', anchor='mm')
    d.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2 + 30), ax + '  1 stud', font=small, fill='white', anchor='mm')
    d.polygon([((box[0] + box[2]) / 2 - 20, box[1] + 40), ((box[0] + box[2]) / 2 + 20, box[1] + 40),
               ((box[0] + box[2]) / 2, box[1] + 12)], fill='white')   # "up" arrow on each face
    cells[lab] = (cx / 3, 1 - (cy + 1) / 2, (cx + 1) / 3, 1 - cy / 2)
img.save(os.path.join(tex_dir, 'HO_T_Debug_Faces_Color.png'))
Image.new('RGB', (S, S), (128, 128, 255)).save(os.path.join(tex_dir, 'HO_T_Debug_Faces_Normal.png'))
Image.new('L', (S, S), 150).save(os.path.join(tex_dir, 'HO_T_Debug_Faces_Roughness.png'))
Image.new('L', (S, S), 0).save(os.path.join(tex_dir, 'HO_T_Debug_Faces_Metalness.png'))

# --- cube ----------------------------------------------------------------------------------------
ho.reset()
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, 0.5))
uv = bm.loops.layers.uv.verify()
# Blender -> Roblox: +Y = FRONT(-Z), -Y = BACK, +X = RIGHT, -X = LEFT, +Z = TOP, -Z = BOTTOM
for f in bm.faces:
    n = f.normal
    lab = {(0, 1, 0): 'FRONT', (0, -1, 0): 'BACK', (1, 0, 0): 'RIGHT', (-1, 0, 0): 'LEFT',
           (0, 0, 1): 'TOP', (0, 0, -1): 'BOTTOM'}[tuple(int(round(c)) for c in n)]
    u0, v0, u1, v1 = cells[lab]
    # local face basis: 'up' = +Z for side faces, +(-Y)... for top (so arrow points toward back)
    up = (0, 0, 1) if abs(n.z) < 0.5 else ((0, -1, 0) if n.z > 0 else (0, 1, 0))
    from mathutils import Vector
    upv = Vector(up); right = upv.cross(n)
    for l in f.loops:
        c = l.vert.co - Vector((0, 0, 0.5))
        a, b = c.dot(right) + 0.5, c.dot(upv) + 0.5
        l[uv].uv = (u0 + a * (u1 - u0), v0 + b * (v1 - v0))
ob = ho.mesh_from_bm('HO_Test_ScaleCube_1x1x1', bm, [ho.material('Debug_Faces')])
ho.finalize(ob, recalc_normals=False)
entry = ho.publish(ob, 'Test', phase='Phase0', notes='Scale/orientation check: must import as Size 1,1,1 with FRONT facing -Z',
                   views=('three_quarter', 'front'), samples=32, footprint=(1, 1))
s = fbx_inspect.summary(os.path.join(ho.ROOT, entry['file']))
print('FBXCHECK', json.dumps(s))
