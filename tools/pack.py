from pathlib import Path
import binascii, json, struct, zipfile, subprocess, os, tempfile
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'src/index.html'; DIST=ROOT/'dist/index.html'; RELDIST=ROOT/'dist/release.html'; OUT=ROOT/'SpectrumSprites_13k.zip'

def toolbin():
    opts=[ROOT/'node_modules/.bin']
    if os.environ.get('RRBIN'): opts.append(Path(os.environ['RRBIN']))
    if os.environ.get('TEMP'): opts.append(Path(os.environ['TEMP'])/'ss-buildtools/node_modules/.bin')
    for p in opts:
        if (p/'terser').exists() and (p/'roadroller').exists(): return p
        if (p/'terser.cmd').exists() and (p/'roadroller.cmd').exists(): return p
    return None
BIN=toolbin()

def compact(s:str)->str:
    lines=[ln for ln in s.splitlines() if not ln.lstrip().startswith('//')]
    return '\n'.join(lines).replace('\t','')

def zopfli_zip(data:bytes,path:Path)->bool:
    try: import zopfli.zlib
    except Exception: return False
    stream=zopfli.zlib.compress(data,numiterations=50); raw=stream[2:-4]
    name=b'index.html'; crc=binascii.crc32(data)&0xffffffff
    dostime=0; dosdate=((2026-1980)<<9)|(8<<5)|17
    local=struct.pack('<IHHHHHIIIHH',0x04034b50,20,0,8,dostime,dosdate,crc,len(raw),len(data),len(name),0)+name+raw
    central=struct.pack('<IHHHHHHIIIHHHHHII',0x02014b50,20,20,0,8,dostime,dosdate,crc,len(raw),len(data),len(name),0,0,0,0,0,0)+name
    end=struct.pack('<IHHHHIIH',0x06054b50,0,0,1,1,len(central),len(local),0)
    path.write_bytes(local+central+end); return True

def std_zip(data:bytes,path:Path):
    zi=zipfile.ZipInfo('index.html',(2026,8,17,0,0,0)); zi.compress_type=zipfile.ZIP_DEFLATED; zi.external_attr=0
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:z.writestr(zi,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)

def sh(c):return subprocess.run(c,shell=True,capture_output=True,text=True,encoding='utf-8')

def exe(name):
    if not BIN:return None
    for n in [name,name+'.cmd']:
        p=BIN/n
        if p.exists():return p

# Pinned Roadroller model parameters. `roadroller -O2` searches for these but is slow AND
# non-deterministic; pinning the winning parameters gives a fast, byte-identical, deterministic
# build. Re-derive with `roadroller -O2 min.js` whenever the source changes materially and paste
# the printed "use `...` to replicate" flags here.
RRFLAGS=os.environ.get('RRFLAGS','-Zab32 -Zlr1333 -Zmd14 -Zpr14 -S0,1,2,3,6,7,13,26,57,226,340,401')
def roadroll(readable:str):
    terser,rr=exe('terser'),exe('roadroller')
    if not terser or not rr:return None
    a=readable.index('<script>')+len('<script>'); b=readable.index('</script>')
    head,js,tail=readable[:a],readable[a:b],readable[b:]
    tmp=Path(tempfile.mkdtemp()); (tmp/'in.js').write_text(js,encoding='utf-8')
    r=sh(f'"{terser}" "{tmp}/in.js" -c passes=3,pure_getters=true -m toplevel=true -o "{tmp}/min.js"')
    if r.returncode:return None
    r=sh(f'"{rr}" {RRFLAGS} "{tmp}/min.js" -o "{tmp}/rr.js"')
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
RELDIST.write_bytes(payload)
if not zopfli_zip(payload,OUT):std_zip(payload,OUT)
assert OUT.stat().st_size==selbytes,(OUT.stat().st_size,selbytes)
for f in ROOT.glob('.*.z'):f.unlink(missing_ok=True)
for f in ROOT.glob('.*.s'):f.unlink(missing_ok=True)
receipt={'version':'0.18','sourceBytes':SRC.stat().st_size,'readableBytes':len(readable_b),'packedBytes':len(payload),'releaseBytes':OUT.stat().st_size,'freeBytes':13312-OUT.stat().st_size,'candidates':{k:v[0] for k,v in candidates.items()},'selected':sel,'tools':'pinned npm tools available' if BIN else 'pinned npm tools unavailable'}
(ROOT/'PACK_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
