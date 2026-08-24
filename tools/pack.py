from pathlib import Path
import binascii, json, struct, zipfile, subprocess, os, tempfile
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'src/index.html'; DIST=ROOT/'dist/index.html'; RELDIST=ROOT/'dist/release.html'; OUT=ROOT/'SpectrumSprites_13k.zip'

def toolchain():
    roots=[ROOT/'node_modules']
    if os.environ.get('RRBIN'):
        q=Path(os.environ['RRBIN'])
        roots += [q.parent if q.name=='.bin' else q]
    if os.environ.get('TEMP'):
        roots.append(Path(os.environ['TEMP'])/'ss-buildtools/node_modules')
    for n in roots:
        terser=n/'terser/bin/terser'
        rr=n/'roadroller/cli.mjs'
        if terser.exists() and rr.exists(): return terser,rr
    return None,None
TERSER,ROADROLLER=toolchain()

def compact(s:str)->str:
    lines=[ln for ln in s.splitlines() if not ln.lstrip().startswith('//')]
    return '\n'.join(lines).replace('\t','')

def zopfli_zip(data:bytes,path:Path)->bool:
    try: import zopfli.zlib
    except Exception: return False
    stream=zopfli.zlib.compress(data,numiterations=200); raw=stream[2:-4]
    name=b'index.html'; crc=binascii.crc32(data)&0xffffffff
    dostime=0; dosdate=((2026-1980)<<9)|(8<<5)|17
    local=struct.pack('<IHHHHHIIIHH',0x04034b50,20,0,8,dostime,dosdate,crc,len(raw),len(data),len(name),0)+name+raw
    central=struct.pack('<IHHHHHHIIIHHHHHII',0x02014b50,20,20,0,8,dostime,dosdate,crc,len(raw),len(data),len(name),0,0,0,0,0,0)+name
    end=struct.pack('<IHHHHIIH',0x06054b50,0,0,1,1,len(central),len(local),0)
    path.write_bytes(local+central+end); return True

def std_zip(data:bytes,path:Path):
    zi=zipfile.ZipInfo('index.html',(2026,8,17,0,0,0)); zi.compress_type=zipfile.ZIP_DEFLATED; zi.external_attr=0
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:z.writestr(zi,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)

def run(*args):
    return subprocess.run(args,capture_output=True,text=True,encoding='utf-8')

# Pinned Roadroller model parameters. `roadroller -O2` searches for these but is slow AND
# non-deterministic; pinning the winning parameters gives a fast, byte-identical, deterministic
# build. Re-derive with `roadroller -O2 min.js` whenever the source changes materially and paste
# the printed "use `...` to replicate" flags here.
RRFLAGS=os.environ.get('RRFLAGS','-Zab32 -Zlr1333 -Zmd14 -Zpr14 -S0,1,2,3,6,7,13,26,57,226,340,401')
def roadroll(readable:str):
    if not TERSER or not ROADROLLER:return None
    a=readable.index('<script>')+len('<script>'); b=readable.index('</script>')
    head,js,tail=readable[:a],readable[a:b],readable[b:]
    tmp=Path(tempfile.mkdtemp()); (tmp/'in.js').write_text(js,encoding='utf-8')
    r=run('node',str(TERSER),str(tmp/'in.js'),'-c','passes=3,pure_getters=true','-m','toplevel=true','-o',str(tmp/'min.js'))
    if r.returncode:return None
    r=run('node',str(ROADROLLER),*RRFLAGS.split(),str(tmp/'min.js'),'-o',str(tmp/'rr.js'))
    if r.returncode:return None
    return head+(tmp/'rr.js').read_text(encoding='utf-8')+tail

# Submission path is authoritative and clean: current source -> Terser -> Roadroller -> Zopfli.
# The old 0.11-roadrolled compatibility payload has been retired (it cost ~924 bytes and was
# decoupled from the readable source). Terser+Roadroller must be provisioned to build a release.

DIST.parent.mkdir(parents=True,exist_ok=True)
src=SRC.read_text(encoding='utf-8'); readable=compact(src)
DIST.write_text(readable,encoding='utf-8',newline=''); readable_b=readable.encode()
candidates={}
def add(name,payload):
    b=payload.encode() if isinstance(payload,str) else payload
    zp=ROOT/f'.{name}.z'; sp=ROOT/f'.{name}.s'
    if zopfli_zip(b,zp):candidates[name+'_zopfli']=(zp.stat().st_size,b)
    std_zip(b,sp);candidates[name+'_deflate9']=(sp.stat().st_size,b)

add('plain',readable_b)
packed=roadroll(readable)
if packed is None: raise SystemExit('Pinned Terser 5.50.0 + Roadroller 2.1.0 are required for a submission build; refusing to replace the verified release with an oversized fallback.')
add('roadroller',packed)
sel=min(candidates,key=lambda k:candidates[k][0]); selbytes,payload=candidates[sel]
if selbytes>13312:
    raise SystemExit(f'No compliant js13k build: best candidate is {selbytes} bytes ({selbytes-13312} over). Install zopfli and the pinned npm tools; refusing to overwrite the verified release.')
RELDIST.write_bytes(payload)
if not zopfli_zip(payload,OUT):std_zip(payload,OUT)
assert OUT.stat().st_size==selbytes,(OUT.stat().st_size,selbytes)
for f in ROOT.glob('.*.z'):f.unlink(missing_ok=True)
for f in ROOT.glob('.*.s'):f.unlink(missing_ok=True)
receipt={'version':'0.20','sourceBytes':SRC.stat().st_size,'readableBytes':len(readable_b),'packedBytes':len(payload),'releaseBytes':OUT.stat().st_size,'freeBytes':13312-OUT.stat().st_size,'candidates':{k:v[0] for k,v in candidates.items()},'selected':sel,'tools':'pinned npm tools available' if TERSER and ROADROLLER else 'pinned npm tools unavailable'}
(ROOT/'PACK_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
