"""Chapter 36 with the beheading underscore laid in: the same design as the approved sample (v2), applied to the full chapter."""
import sys, json, subprocess, wave, numpy as np
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tts')); import fullcast as F
D=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + os.sep
SONG_F=D+'music/v17_mono24k.flac'
EQ='equalizer=f=110:t=q:w=0.8:g=2,equalizer=f=450:t=q:w=1.2:g=-3'
SR=F.SR; name='37-chapter-36'
paras=F.file_paragraphs(name+'.md')
raw=json.load(open(name+'.json')); F.NARRATOR=raw.pop('_narrator','Narrator'); who={int(k):v for k,v in raw.items()}
P0=next(i for i,p in enumerate(paras) if p.startswith('Ezra walked first'))
IB=next(i for i,p in enumerate(paras) if p.startswith('He did not feel the sword'))
P1=next(i for i,p in enumerate(paras) if p.startswith('Then Ezra wept'))
pieces=[]; starts=[]; n=0
for i,p in enumerate(paras):
    starts.append(n); seg=F.render_paragraph(p,who.get(i)); pieces+=seg; n+=sum(len(s) for s in seg)
starts.append(n)
a=np.concatenate(pieces); a=np.clip(a/max(1e-6,np.abs(a).max())*0.9,-1,1).astype(np.float32)
v=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-af',EQ,'-ar',str(SR),'-f','f32le','-'],input=a.tobytes(),capture_output=True).stdout,np.float32)[:len(a)].copy()
_act=np.abs(v)>1e-3; v=(v*(0.147/max(1e-6,float(np.sqrt(np.mean(v[_act]**2)))))); v=(v*min(1.0,0.97/max(1e-6,np.abs(v).max()))).astype(np.float32)   # plain gain: ffmpeg's one-pass loudnorm fell back to its dynamic mode and left a crackle (author heard it, Nov 11)
pre=v[:starts[P0]]; A=v[starts[P0]:starts[IB]]; B=v[starts[IB]:starts[IB+1]]; Cv=v[starts[IB+1]:starts[P1+1]]; post=v[starts[P1+1]:]
song=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',SONG_F,'-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout,np.float32)*10**(-2.5/20)
DROP,RET=181.0,199.0; lead=2.0
a0=DROP-(len(A)/SR+0.8)-lead
Tn=RET+2.0+len(Cv)/SR          # song-time of the last word, "wiped his tears away"
print('P0',P0,'IB',IB,'P1',P1,'A',round(len(A)/SR,1),'B',round(len(B)/SR,1),'C',round(len(Cv)/SR,1),'a0',round(a0,1),'last word at song',round(Tn,1))
off=max(0.0,-a0)
# the shofar, cut from v17 (it starts after a stretch of digital silence)
i0=int(289.0*SR); on=i0+int(np.argmax(np.abs(song[i0:])>1e-4)); sh=song[max(0,on-int(0.05*SR)):].copy()
print('v17 shofar onset at song',round(on/SR,2),'length',round(len(sh)/SR,1))
def music(hold,fade,pause):
    m=song[max(0,int(a0*SR)):int((Tn+hold+fade)*SR)].copy()
    f=int(4*SR); m[:f]*=np.linspace(0,1,f)
    fo=int(fade*SR); m[-fo:]*=np.cos(np.linspace(0,np.pi/2,fo))**1.5
    shf=sh.copy(); t=int(2.5*SR); shf[-t:]*=np.linspace(1,0,t)
    return np.concatenate([m,np.zeros(int(pause*SR),np.float32),shf]), Tn+hold+fade+pause
tB=DROP-a0+2.5; tC=RET-a0+2.0
def music_full():
    m=song[max(0,int(a0*SR)):].copy()      # the whole v17 song to its natural end, shofar included, no fade
    f=int(4*SR); m[:f]*=np.linspace(0,1,f)
    return m, 290.09
def build(tag,hold=0,fade=0,pause=0):
    mus,tsh=music_full() if tag=='C' else music(hold,fade,pause)
    nn=max(len(mus)+int(off*SR),int((tC)*SR)+len(Cv))+int(SR*1.0)
    V=np.zeros(nn,np.float32); duck=np.zeros(nn,np.float32)
    def put(x,t):
        s=int(t*SR); V[s:s+len(x)]+=x
    put(A,lead); put(B,tB); put(Cv,tC)
    M=np.zeros(nn,np.float32); M[int(off*SR):int(off*SR)+len(mus)]=mus
    g=np.full(nn,10**(-5/20),np.float32); te=int((tC+len(Cv)/SR+0.2)*SR); r=int(1.5*SR)
    g[te:te+r]=np.linspace(10**(-5/20),1.0,min(r,nn-te)); g[te+r:]=1.0
    mix=V+M*g
    fo=int(1.5*SR); mix[-fo:]*=np.linspace(1,0,fo)
    out=np.concatenate([pre,mix]); out=out/max(1.0,np.abs(out).max()/0.89)
    subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-b:a','192k',f'37-chapter-36-{tag}.mp3'],input=out.astype(np.float32).tobytes(),check=True)
    print(tag,'natural shofar',round(tsh-Tn,1),'s after the last word; total',round(len(out)/SR/60,1),'min')
build('C')
