import struct,zipfile,hashlib,datetime,sys
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import rsa,padding
import os
SRC=os.environ.get("TEMPLATE_APK","template.apk")  # APK WebView pembungkus (lihat README)
OUT=sys.argv[1]
z=zipfile.ZipFile(SRC)
# ---- patch manifest string pool
d=bytearray(z.read("AndroidManifest.xml"))
off=8;sc,stc,fl,ss,sts=struct.unpack_from("<IIIII",d,off+8)
assert fl&0x100==0 and stc==0
offs=struct.unpack_from("<%dI"%sc,d,off+28);base=off+ss
strs=[]
for o in offs:
    p=base+o;l=struct.unpack_from("<H",d,p)[0];strs.append(d[p+2:p+2+l*2].decode("utf-16le"))
rep={"ArRahmah":"Tabungan","id.adnan.notadaging":"id.hanip.tabungan",".MainActivity":"id.adnan.notadaging.MainActivity","2.1":"1.2"}
strs=[rep.get(s,s) for s in strs]
pool=bytearray();no=[]
for s in strs:
    no.append(len(pool));b=s.encode("utf-16le");pool+=struct.pack("<H",len(s))+b+b"\0\0"
while len(pool)%4:pool+=b"\0"
hdr_end=28+4*sc
chunk=struct.pack("<HHI",1,28,hdr_end+len(pool))+struct.pack("<IIIII",sc,0,0,hdr_end,0)+struct.pack("<%dI"%sc,*no)+bytes(pool)
oldsz=struct.unpack_from("<I",d,off+4)[0]
new=bytes(d[:off])+chunk+bytes(d[off+oldsz:])
new=new[:4]+struct.pack("<I",len(new))+new[8:]
new=bytearray(new)
for p in range(0,len(new)-20,4):
    ns,nm,raw=struct.unpack_from("<III",new,p);sz,r0,ty,dat=struct.unpack_from("<HBBI",new,p+12)
    if sz==8 and r0==0 and ty==0x10 and nm==6 and dat==10: struct.pack_into("<I",new,p+16,12);print("versionCode 12")
manifest=bytes(new)
icon=open("icon.png","rb").read();html=open("index.html","rb").read()
entries=[("AndroidManifest.xml",manifest,8),("classes.dex",z.read("classes.dex"),8),("resources.arsc",z.read("resources.arsc"),0),("res/drawable/ic_launcher.png",icon,0),("assets/index.html",html,8)]
# ---- write aligned zip
import io,zlib
buf=io.BytesIO();cd=[]
DT=(2026,10,26,0,0,0)
for name,data,method in entries:
    nb=name.encode();crc=zlib.crc32(data)&0xffffffff
    if method==8:
        c=zlib.compressobj(9,zlib.DEFLATED,-15);comp=c.compress(data)+c.flush()
    else: comp=data
    pad=0
    if method==0: pad=(4-(buf.tell()+30+len(nb))%4)%4
    off=buf.tell()
    dosd=((DT[0]-1980)<<9)|(DT[1]<<5)|DT[2];dost=0
    buf.write(struct.pack("<IHHHHHIIIHH",0x04034b50,20,0,method,dost,dosd,crc,len(comp),len(data),len(nb),pad)+nb+b"\0"*pad+comp)
    cd.append((nb,crc,len(comp),len(data),method,off,dosd))
sec1=buf.getvalue()
cdb=b""
for nb,crc,cs,us,m,o,dd in cd:
    cdb+=struct.pack("<IHHHHHHIIIHHHHHII",0x02014b50,20,20,0,m,0,dd,crc,cs,us,len(nb),0,0,0,0,0,o)+nb
cdoff=len(sec1)
eocd=struct.pack("<IHHHHIIH",0x06054b50,0,0,len(cd),len(cd),len(cdb),cdoff,0)
# ---- v2 signature
import os
KP="release.key"
if os.path.exists(KP):key=serialization.load_pem_private_key(open(KP,"rb").read(),None)
else:
    key=rsa.generate_private_key(65537,2048);open(KP,"wb").write(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,"Tabungan Warga Mendungan")])
now=datetime.datetime(2026,10,26)
cert=x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(now).not_valid_after(now+datetime.timedelta(days=36500)).sign(key,hashes.SHA256())
certder=cert.public_bytes(serialization.Encoding.DER)
pub=key.public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
def chunks(b):
    for i in range(0,len(b),1<<20):yield b[i:i+(1<<20)]
digs=[]
for sec in (sec1,cdb,eocd):
    for c in chunks(sec):digs.append(hashlib.sha256(b"\xa5"+struct.pack("<I",len(c))+c).digest())
top=hashlib.sha256(b"\x5a"+struct.pack("<I",len(digs))+b"".join(digs)).digest()
L=lambda b:struct.pack("<I",len(b))+b
digest_entry=L(struct.pack("<I",0x0103)+L(top))
signed=L(digest_entry)+L(L(certder))+L(b"")
sig=key.sign(signed,padding.PKCS1v15(),hashes.SHA256())
signer=L(signed)+L(L(struct.pack("<I",0x0103)+L(sig)))+L(pub)
value=L(L(signer))
pair=struct.pack("<Q",4+len(value))+struct.pack("<I",0x7109871a)+value
blk_size=len(pair)+8+16
block=struct.pack("<Q",blk_size)+pair+struct.pack("<Q",blk_size)+b"APK Sig Block 42"
eocd2=eocd[:16]+struct.pack("<I",cdoff+len(block))+eocd[20:]
open(OUT,"wb").write(sec1+block+cdb+eocd2)
print("ok",len(sec1+block+cdb+eocd2))
