"""Build download zips in the repo root (gitignored): models, anims/VFX/heroes, and textures split under ~25 MB."""
import os, glob, zipfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
os.chdir(ROOT)
for z in glob.glob('HollowOath_*.zip'): os.remove(z)


def files_under(*paths):
    out = []
    for p in paths:
        if os.path.isfile(p): out.append(p)
        else: out += sorted(f for f in glob.glob(os.path.join(p, '**', '*'), recursive=True) if os.path.isfile(f))
    return out


def write(name, files):
    with zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in files: z.write(f)
    print(name, len(files), 'files', round(os.path.getsize(name) / 1e6, 1), 'MB')


docs = ['MANIFEST.md', 'README.md', 'docs', 'roblox']
write('HollowOath_Models.zip', files_under('assets/Phase0', 'assets/Phase1', *docs))
# kept under ~20 MB each so every zip opens on phones / in the Claude app
write('HollowOath_Animations.zip', files_under('assets/Phase2', *docs))
write('HollowOath_VFX_Meshes.zip', [f for f in files_under('assets/Phase3') if '/Flipbooks/' not in f])
write('HollowOath_VFX_Flipbooks.zip', files_under('assets/Phase3/VFX/Flipbooks'))
write('HollowOath_Heroes.zip', files_under('assets/Phase4', 'roblox'))
chunk, size, k = [], 0, 1
for f in files_under('textures'):
    s = os.path.getsize(f)
    if chunk and size + s > 24e6:
        write(f'HollowOath_Textures_{k}.zip', chunk); chunk, size, k = [], 0, k + 1
    chunk.append(f); size += s
if chunk: write(f'HollowOath_Textures_{k}.zip', chunk)
