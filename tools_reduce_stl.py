"""Make a web-safe binary STL by vertex clustering (no source file is altered)."""
import os, struct, math

src = r"G:\learn_context\URDF模型\天枢无人机完整版(更换悬垂式绝缘子串)\meshes\dianxiangan.STL"
dst = os.path.join(os.path.dirname(__file__), 'public', 'robot', 'meshes', 'dianxiangan.STL')
with open(src, 'rb') as f:
    header=f.read(80); total=struct.unpack('<I',f.read(4))[0]
    lo=[float('inf')]*3; hi=[-float('inf')]*3
    for _ in range(total):
        raw=f.read(50)
        vals=struct.unpack('<12fH',raw)
        for k in (3,6,9):
            for a in range(3): lo[a]=min(lo[a],vals[k+a]); hi[a]=max(hi[a],vals[k+a])
span=[hi[i]-lo[i] for i in range(3)]; largest=max(span)
print('triangles:',total,'bounds:',lo,hi)

def key(p, cells):
    return tuple(int((p[i]-lo[i])/largest*cells) for i in range(3))

# Try decreasing grid resolutions until the mesh fits GitHub's browser-upload limit.
for cells in (768, 512, 384, 320, 256, 192, 160, 128):
    kept=0
    with open(src, 'rb') as f:
        f.seek(84)
        for _ in range(total):
            vals=struct.unpack('<12fH',f.read(50)); p=[vals[3:6],vals[6:9],vals[9:12]]
            if len({key(x,cells) for x in p})==3: kept+=1
    print('cells:',cells,'kept:',kept,'estimated MB:',(84+50*kept)/1024/1024)
    if 84+50*kept < 23*1024*1024: break
else: raise RuntimeError('could not reduce STL sufficiently')

with open(src,'rb') as inp, open(dst,'wb') as out:
    out.write(header); out.write(struct.pack('<I',kept)); inp.seek(84)
    for _ in range(total):
        raw=inp.read(50); vals=struct.unpack('<12fH',raw); p=[vals[3:6],vals[6:9],vals[9:12]]
        if len({key(x,cells) for x in p})==3: out.write(raw)
print('wrote',dst,'bytes:',os.path.getsize(dst),'grid cells:',cells)
